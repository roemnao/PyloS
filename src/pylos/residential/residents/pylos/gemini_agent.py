"""Agent: gọi Gemini, tự chạy vòng lặp function calling có giới hạn số vòng."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from pylos.lobby.office.agent_tools import ToolContext, ToolRegistry

log = logging.getLogger(__name__)

EMPTY_REPLY = "Xin lỗi, mình chưa trả lời được câu này."
CLASSIFY_TIMEOUT = 30  # giây chờ bộ lọc AI mỗi lần gọi
SEARCH_SYSTEM = (
    "Trả lời ngắn gọn, chính xác bằng tiếng Việt dựa trên kết quả tìm kiếm. Nêu số liệu và ngày tháng nếu có. "
    "Không bịa: không tìm thấy thì nói không tìm thấy."
)
TOO_MANY_STEPS = "Xin lỗi, việc này cần quá nhiều bước, bạn thử hỏi cụ thể hơn nhé."


@dataclass
class MediaRef:
    """Tệp ảnh/video/tin thoại đính kèm một lượt của người dùng (đã tải về đĩa).

    Sau khi agent tải video/tệp lớn lên Files API, `file_uri` và `file_uri_expires` (epoch giây) được điền để
    bên gọi lưu lại, lần hỏi tiếp không phải tải lên nữa."""
    path: Path
    mime: str
    kind: str  # photo | video | voice
    msg_id: str = ""
    file_uri: str = ""
    file_uri_expires: float = 0


@dataclass(frozen=True)
class Turn:
    role: str  # "user" hoặc "model"
    text: str
    name: str = ""
    media: tuple[MediaRef, ...] = ()


@dataclass(frozen=True)
class ToolStep:
    """Một lần model gọi tool: tên, tham số, kết quả, thời gian chạy (để xem lại trong session)."""
    name: str
    args: dict[str, Any]
    result: dict[str, Any]
    ms: int = 0


@dataclass(frozen=True)
class AgentReply:
    text: str
    tokens: int
    steps: tuple[ToolStep, ...] = ()
    model: str = ""
    ms: int = 0
    thinking: str = ""  # mức suy nghĩ đã gửi cho model ("" = không gửi)


class Agent(Protocol):
    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext, *, model: str | None = None,
                    thinking_level: str | None = None, fallbacks: tuple[str, ...] = ()) -> AgentReply: ...


def _usage_tokens(response: Any) -> int:
    usage = getattr(response, "usage_metadata", None)
    return int(getattr(usage, "total_token_count", 0) or 0) if usage else 0


def _rejects_thinking(exc: BaseException) -> bool:
    """Lỗi 400 do model không hỗ trợ tham số thinking (ví dụ model cũ)."""
    return getattr(exc, "code", None) == 400 and "think" in str(exc).lower()


def _fails_over(exc: BaseException) -> bool:
    """Lỗi của riêng model hoặc của lúc này (hết giờ, 5xx, mạng, 429 hết hạn mức, 404 không tồn tại): thử model dự phòng."""
    return (isinstance(exc, asyncio.TimeoutError) or _is_transient(exc)
            or getattr(exc, "code", None) in (404, 429))


def _is_transient(exc: BaseException) -> bool:
    """Lỗi mạng (kết nối bị ngắt...) hoặc lỗi phía server Google (5xx): đáng thử lại."""
    import httpx

    if isinstance(exc, httpx.TransportError):
        return True
    code = getattr(exc, "code", None)
    return isinstance(code, int) and code >= 500


class GeminiAgent:
    RETRIES = 2
    TIMEOUT_RETRIES = 1  # hết giờ thì chỉ thử thêm 1 lần: mỗi lần chờ đã lâu
    FAILOVER_RETRIES = 1  # model chưa phải cuối chuỗi: lỗi 5xx chỉ thử lại 1 lần rồi sang model dự phòng
    COOLDOWN_SECONDS = 60  # model vừa lỗi bị đẩy xuống cuối chuỗi trong khoảng này, khỏi chờ nó hết giờ ở mỗi tin
    retry_delay = 1.0

    def __init__(
        self,
        api_key: str,
        model: str,
        tools: ToolRegistry,
        *,
        max_tool_rounds: int = 4,
        max_output_tokens: int = 1024,
        timeout_seconds: int = 60,
        thinking_level: str = "low",
        fallback_models: tuple[str, ...] = (),
        media_inline_max_mb: float = 15,
        media_upload_timeout: float = 120,
        client: Any = None,
    ) -> None:
        from google import genai
        from google.genai import types

        self._types = types
        self._client = client or genai.Client(api_key=api_key)
        self._model = model
        self._tools = tools
        self._max_rounds = max_tool_rounds
        self._max_output_tokens = max_output_tokens
        self._timeout = timeout_seconds
        self._inline_max = int(media_inline_max_mb * 1024 * 1024)
        self._upload_timeout = media_upload_timeout
        self._thinking_level = thinking_level  # mức suy nghĩ khi trả lời: low | medium | high ("" = để model tự quyết)
        self._fallbacks = tuple(fallback_models)  # model dự phòng chung, đứng cuối mọi chuỗi
        self._no_thinking: set[str] = set()  # các model đã báo không nhận thinking_level
        self._missing: set[str] = set()  # các model đã báo 404: bỏ khỏi chuỗi cho tới khi đổi cấu hình
        self._cooling: dict[str, float] = {}  # model vừa lỗi -> thời điểm (monotonic) hết bị đẩy xuống cuối chuỗi

    def configure(self, *, model: str, max_tool_rounds: int, max_output_tokens: int, timeout_seconds: int,
                  thinking_level: str | None = None, fallback_models: tuple[str, ...] | None = None) -> None:
        """Đổi model / giới hạn khi bot đang chạy (cấu hình mới từ web), không cần khởi động lại."""
        if model != self._model:
            log.info("Đổi model của agent: %s -> %s", self._model, model)
        if thinking_level is not None:
            self._thinking_level = thinking_level
        if fallback_models is not None:
            self._fallbacks = tuple(fallback_models)
        self._no_thinking.clear()
        self._missing.clear()  # cấu hình đổi: cho thử lại các model từng báo lỗi
        self._cooling.clear()
        self._model = model
        self._max_rounds = max_tool_rounds
        self._max_output_tokens = max_output_tokens
        self._timeout = timeout_seconds

    def chain(self, model: str | None = None, extra: tuple[str, ...] = ()) -> list[str]:
        """Thứ tự thử: `model`, các model dự phòng riêng (`extra`), model chính, rồi model dự phòng chung.

        Bỏ trùng và bỏ model đã báo 404; model vừa lỗi (đang nghỉ) bị đẩy xuống cuối nhưng không bị bỏ;
        nếu hết sạch thì vẫn thử model đầu tiên."""
        names: list[str] = []
        for name in (model or self._model, *extra, self._model, *self._fallbacks):
            if name and name not in names:
                names.append(name)
        names = [n for n in names if n not in self._missing] or names[:1]
        now = time.monotonic()
        resting = [n for n in names if self._cooling.get(n, 0) > now]
        return [n for n in names if n not in resting] + resting

    FILE_URI_TTL = 47 * 3600  # Files API giữ tệp 48 giờ; dùng lại nếu còn dưới 47 giờ

    async def _media_part(self, ref: MediaRef, inline_left: list[int]) -> Any:
        """Part cho một tệp: nhúng thẳng nếu nhỏ (tổng còn trong hạn mức), ngược lại tải lên Files API."""
        types = self._types
        if ref.file_uri and ref.file_uri_expires > time.time():
            return types.Part.from_uri(file_uri=ref.file_uri, mime_type=ref.mime)
        size = ref.path.stat().st_size
        if ref.kind != "video" and size <= inline_left[0]:
            inline_left[0] -= size
            data = await asyncio.to_thread(ref.path.read_bytes)
            return types.Part.from_bytes(data=data, mime_type=ref.mime)
        uploaded = await self._client.aio.files.upload(file=str(ref.path), config={"mime_type": ref.mime})
        deadline = time.monotonic() + self._upload_timeout
        while getattr(getattr(uploaded, "state", None), "name", "ACTIVE") == "PROCESSING":
            if time.monotonic() > deadline:
                raise TimeoutError(f"Files API xử lý {ref.path.name} quá {self._upload_timeout:.0f}s")
            await asyncio.sleep(2)
            uploaded = await self._client.aio.files.get(name=uploaded.name)
        if getattr(getattr(uploaded, "state", None), "name", "") == "FAILED":
            raise RuntimeError(f"Files API không xử lý được {ref.path.name}")
        ref.file_uri, ref.file_uri_expires = uploaded.uri, time.time() + self.FILE_URI_TTL
        return types.Part.from_uri(file_uri=uploaded.uri, mime_type=ref.mime)

    async def _build_contents(self, turns: list[Turn]) -> list[Any]:
        """Như _contents nhưng lượt của người dùng có thể kèm ảnh/video/tin thoại. Gọi một lần mỗi lượt trả lời."""
        types = self._types
        inline_left = [self._inline_max]
        contents = []
        for turn in turns:
            if turn.role == "model":
                contents.append(types.Content(role="model", parts=[types.Part.from_text(text=turn.text)]))
                continue
            text = f"{turn.name}: {turn.text}" if turn.name else turn.text
            parts = [types.Part.from_text(text=text)]
            for ref in turn.media:
                parts.append(await self._media_part(ref, inline_left))
            contents.append(types.Content(role="user", parts=parts))
        return contents

    async def _generate(self, contents: Any, config: Any, model: str | None = None, timeout: float | None = None,
                        *, retry_timeout: bool = True, retries: int | None = None) -> Any:
        """Gọi Gemini, thử lại tối đa 2 lần nếu lỗi mạng tạm thời hoặc lỗi 5xx của Google.

        Hết giờ (Gemini quá tải hay suy nghĩ lâu) thì thử thêm 1 lần; `retry_timeout=False` để bên gọi tự xử lý.
        """
        name = model or self._model
        seconds = timeout or self._timeout
        max_failures = self.RETRIES if retries is None else retries
        failures = timeouts = 0
        while True:
            try:
                return await asyncio.wait_for(
                    self._client.aio.models.generate_content(model=name, contents=contents, config=config),
                    timeout=seconds,
                )
            except asyncio.TimeoutError:
                if not retry_timeout:
                    raise
                timeouts += 1
                if timeouts > self.TIMEOUT_RETRIES:
                    raise TimeoutError(
                        f"Gemini ({name}) không trả lời sau {seconds:.0f} giây (đã thử {timeouts} lần)") from None
                log.warning("Gemini (%s) chưa trả lời sau %.0f giây, thử lại", name, seconds)
            except Exception as exc:  # noqa: BLE001 - lọc lỗi tạm thời bên dưới
                failures += 1
                if failures > max_failures or not _is_transient(exc):
                    raise
                log.warning("Gemini (%s) lỗi tạm thời (lần %d), thử lại: %s", name, failures, type(exc).__name__)
                await asyncio.sleep(self.retry_delay * failures)

    async def _generate_any(self, contents: Any, config: Any, models: list[str], *, level: str = "",
                            timeout: float | None = None, retry_timeout: bool = True) -> tuple[Any, str]:
        """Thử lần lượt các model trong `models`; trả (kết quả, model đã trả lời).

        Model chưa phải cuối: lỗi 5xx thử lại 1 lần, hết giờ không thử lại, rồi sang model kế. 429, 404 sang ngay.
        Mỗi model có `thinking_level` riêng: model nào không nhận (lỗi 400) thì nhớ lại và gọi lại không có tham số này."""
        types = self._types
        for index, name in enumerate(models):
            final = index == len(models) - 1
            while True:
                config.thinking_config = (types.ThinkingConfig(thinking_level=level)
                                          if level and name not in self._no_thinking else None)
                try:
                    result = await self._generate(
                        contents, config, model=name, timeout=timeout, retry_timeout=retry_timeout and final,
                        retries=None if final else self.FAILOVER_RETRIES)
                    self._cooling.pop(name, None)
                    return result, name
                except Exception as exc:  # noqa: BLE001 - phân loại lỗi bên dưới
                    if config.thinking_config is not None and _rejects_thinking(exc):
                        log.info("Model %s không nhận thinking_level, gọi lại không có tham số này: %s", name, exc)
                        self._no_thinking.add(name)
                        continue
                    if getattr(exc, "code", None) == 404 and name not in self._missing:
                        self._missing.add(name)
                        log.warning("Model %s không tồn tại (404): bỏ khỏi chuỗi model cho tới khi đổi cấu hình", name)
                    if final or not _fails_over(exc):
                        raise
                    self._cooling[name] = time.monotonic() + self.COOLDOWN_SECONDS
                    log.warning("Model %s lỗi (%s: %s), chuyển sang model dự phòng %s", name, type(exc).__name__,
                                str(exc)[:120], models[index + 1])
                    break
        raise AssertionError("unreachable")

    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext, *, model: str | None = None,
                    thinking_level: str | None = None, fallbacks: tuple[str, ...] = ()) -> AgentReply:
        """`model` / `thinking_level` / `fallbacks`: ghi đè cho riêng lượt này (model hồ sơ của chat), không đổi cấu hình chung."""
        types = self._types
        declarations = self._tools.declarations()
        models = self.chain(model, fallbacks)
        level = self._thinking_level if thinking_level is None else thinking_level
        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=self._max_output_tokens,
            tools=[types.Tool(function_declarations=declarations)] if declarations else None,
            # Tự chạy vòng lặp để kiểm soát số vòng và quyền của từng tool.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        if any(t.media and t.role != "model" and any(m.kind == "video" for m in t.media) for t in turns):
            config.media_resolution = types.MediaResolution.MEDIA_RESOLUTION_LOW  # video: ít token hơn
        contents = await self._build_contents(turns)
        tokens = 0
        steps: list[ToolStep] = []
        started = time.monotonic()
        used = models[0]

        def done(text: str) -> AgentReply:
            thinking = level if config.thinking_config is not None else ""
            return AgentReply(text, tokens, tuple(steps), used, int((time.monotonic() - started) * 1000), thinking)

        for round_number in range(self._max_rounds + 1):
            response, used = await self._generate_any(contents, config, models, level=level)
            models = [used]  # các vòng tool sau ở lại đúng model đã trả lời (không trộn model giữa chừng)
            tokens += _usage_tokens(response)
            calls = response.function_calls or []
            if not calls:
                return done((response.text or "").strip() or EMPTY_REPLY)
            if round_number == self._max_rounds:
                log.warning("Hết %d vòng tool mà model vẫn muốn gọi tiếp", self._max_rounds)
                return done(TOO_MANY_STEPS)
            # Giữ nguyên content của model (kể cả thought signature) trước khi trả kết quả tool.
            contents.append(response.candidates[0].content)
            parts = []
            for call in calls:
                args = dict(call.args or {})
                log.info("Tool %s(%s)", call.name, args)
                tool_started = time.monotonic()
                result = await self._tools.call(call.name, args, ctx)
                steps.append(ToolStep(call.name, args, result, int((time.monotonic() - tool_started) * 1000)))
                parts.append(types.Part.from_function_response(name=call.name, response=result))
            contents.append(types.Content(role="user", parts=parts))
        return done(TOO_MANY_STEPS)  # không tới được, để type checker yên tâm

    async def search(self, query: str) -> tuple[dict[str, Any], int]:
        """Tìm web bằng Google Search của Gemini, trong một request RIÊNG (không trộn với function calling).

        Trả ({"answer", "sources": [{"title", "uri"}]}, số token). Lỗi thì ném ngoại lệ cho bên gọi xử lý."""
        types = self._types
        config = types.GenerateContentConfig(
            system_instruction=SEARCH_SYSTEM,
            max_output_tokens=self._max_output_tokens,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=query)])]
        response, _ = await self._generate_any(contents, config, self.chain(), level=self._thinking_level)
        sources: list[dict[str, str]] = []
        seen: set[str] = set()
        for candidate in response.candidates or []:
            metadata = getattr(candidate, "grounding_metadata", None)
            for chunk in getattr(metadata, "grounding_chunks", None) or []:
                web = getattr(chunk, "web", None)
                uri = str(getattr(web, "uri", "") or "")
                if uri and uri not in seen:
                    seen.add(uri)
                    sources.append({"title": str(getattr(web, "title", "") or ""), "uri": uri})
        answer = (response.text or "").strip()
        return {"answer": answer or "Không tìm thấy kết quả.", "sources": sources[:5]}, _usage_tokens(response)

    async def watch_video(self, url: str, question: str = "") -> tuple[dict[str, Any], int]:
        """Gemini xem thẳng video YouTube công khai (request riêng, độ phân giải thấp cho rẻ).

        Trả ({"summary"}, số token). Lỗi thì ném ngoại lệ cho bên gọi xử lý."""
        types = self._types
        ask = question or "Tóm tắt nội dung video: ai, nói gì, diễn ra những gì."
        contents = [types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(file_uri=url)),
            types.Part.from_text(text=f"{ask}\nTrả lời bằng tiếng Việt, ngắn gọn, đúng nội dung video."),
        ])]
        config = types.GenerateContentConfig(
            max_output_tokens=self._max_output_tokens,
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
        )
        response, _ = await self._generate_any(contents, config, self.chain(), level=self._thinking_level)
        return {"summary": (response.text or "").strip() or "Không xem được video."}, _usage_tokens(response)

    async def classify(self, system: str, text: str, *, model: str | None = None,
                       timeout: float = CLASSIFY_TIMEOUT) -> tuple[dict[str, Any], int]:
        """Câu hỏi có/không ngắn, trả JSON (dùng cho bộ lọc tin). Lỗi thì ném ngoại lệ cho bên gọi xử lý.

        Thử lần lượt `model` (hoặc model chính) rồi các model dự phòng. Gemini quá tải hay trả chậm: chờ tới
        `timeout` giây mỗi lần, hết giờ ở model cuối thì thử thêm một lần. Tắt bớt "suy nghĩ" (thinking) cho câu hỏi
        đơn giản này để nhanh và rẻ; model nào không nhận tham số đó (lỗi 400) thì bỏ và gọi lại.
        """
        models = self.chain(model)
        config = self._types.GenerateContentConfig(
            system_instruction=system,
            temperature=0,
            max_output_tokens=256,
            response_mime_type="application/json",
        )
        attempts = 0
        while True:
            attempts += 1
            try:
                response, _ = await self._generate_any(text, config, models, level="low", timeout=timeout,
                                                       retry_timeout=False)
                break
            except asyncio.TimeoutError:
                if attempts >= 2:
                    raise TimeoutError(f"Gemini không trả lời sau {timeout:.0f} giây (đã thử {attempts} lần)") from None
                log.warning("Bộ lọc: Gemini chưa trả lời sau %.0f giây, thử lại", timeout)
        raw = (response.text or "").strip()
        if not raw:
            raise ValueError("Gemini trả về rỗng (có thể bị chặn bởi bộ lọc an toàn hoặc hết token)")
        try:
            data = json.loads(raw)
        except ValueError:
            raise ValueError(f"Gemini không trả JSON: {raw[:80]!r}") from None
        if not isinstance(data, dict):
            raise ValueError(f"Gemini trả JSON không phải object: {raw[:80]!r}")
        return data, _usage_tokens(response)


class EchoAgent:
    """Agent giả cho chế độ console khi chưa có GEMINI_API_KEY."""

    async def classify(self, system: str, text: str, **_: Any) -> tuple[dict[str, Any], int]:
        return {"reply": False, "reason": "chưa có GEMINI_API_KEY nên bộ lọc AI không chạy"}, 0

    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext, **_: Any) -> AgentReply:
        last = turns[-1].text if turns else ""
        return AgentReply(f"(echo, chưa có GEMINI_API_KEY) {last}", 0)
