"""Agent: gọi Gemini, tự chạy vòng lặp function calling có giới hạn số vòng."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol

from pylos.lobby.office.agent_tools import ToolContext, ToolRegistry

log = logging.getLogger(__name__)

EMPTY_REPLY = "Xin lỗi, mình chưa trả lời được câu này."
CLASSIFY_TIMEOUT = 30  # giây chờ bộ lọc AI mỗi lần gọi
TOO_MANY_STEPS = "Xin lỗi, việc này cần quá nhiều bước, bạn thử hỏi cụ thể hơn nhé."


@dataclass(frozen=True)
class Turn:
    role: str  # "user" hoặc "model"
    text: str
    name: str = ""


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


class Agent(Protocol):
    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext, *,
                    model: str | None = None, thinking_level: str | None = None) -> AgentReply: ...


def _usage_tokens(response: Any) -> int:
    usage = getattr(response, "usage_metadata", None)
    return int(getattr(usage, "total_token_count", 0) or 0) if usage else 0


def _rejects_thinking(exc: BaseException) -> bool:
    """Lỗi 400 do model không hỗ trợ tham số thinking (ví dụ model cũ)."""
    return getattr(exc, "code", None) == 400 and "think" in str(exc).lower()


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
        self._classify_thinking = True  # tắt khi model báo không nhận thinking_level
        self._thinking_level = thinking_level  # mức suy nghĩ khi trả lời: low | medium | high ("" = để model tự quyết)
        self._no_thinking: set[str] = set()  # các model đã báo không nhận thinking_level khi trả lời

    def configure(self, *, model: str, max_tool_rounds: int, max_output_tokens: int, timeout_seconds: int,
                  thinking_level: str | None = None) -> None:
        """Đổi model / giới hạn khi bot đang chạy (cấu hình mới từ web), không cần khởi động lại."""
        if model != self._model:
            log.info("Đổi model của agent: %s -> %s", self._model, model)
            self._classify_thinking = True
        if thinking_level is not None:
            self._thinking_level = thinking_level
        self._model = model
        self._max_rounds = max_tool_rounds
        self._max_output_tokens = max_output_tokens
        self._timeout = timeout_seconds

    def _contents(self, turns: list[Turn]) -> list[Any]:
        types = self._types
        contents = []
        for turn in turns:
            if turn.role == "model":
                contents.append(types.Content(role="model", parts=[types.Part.from_text(text=turn.text)]))
            else:
                text = f"{turn.name}: {turn.text}" if turn.name else turn.text
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
        return contents

    async def _generate(self, contents: Any, config: Any, model: str | None = None, timeout: float | None = None,
                        *, retry_timeout: bool = True) -> Any:
        """Gọi Gemini, thử lại tối đa 2 lần nếu lỗi mạng tạm thời hoặc lỗi 5xx của Google.

        Hết giờ (Gemini quá tải hay suy nghĩ lâu) thì thử thêm 1 lần; `retry_timeout=False` để bên gọi tự xử lý.
        """
        name = model or self._model
        seconds = timeout or self._timeout
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
                if failures > self.RETRIES or not _is_transient(exc):
                    raise
                log.warning("Gemini lỗi tạm thời (lần %d), thử lại: %s", failures, type(exc).__name__)
                await asyncio.sleep(self.retry_delay * failures)

    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext, *,
                    model: str | None = None, thinking_level: str | None = None) -> AgentReply:
        """`model` / `thinking_level`: ghi đè cho riêng lượt này (đổi theo loại việc), không đổi cấu hình chung."""
        types = self._types
        declarations = self._tools.declarations()
        model = model or self._model
        level = self._thinking_level if thinking_level is None else thinking_level
        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=self._max_output_tokens,
            tools=[types.Tool(function_declarations=declarations)] if declarations else None,
            # Tự chạy vòng lặp để kiểm soát số vòng và quyền của từng tool.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            thinking_config=(types.ThinkingConfig(thinking_level=level)
                             if level and model not in self._no_thinking else None),
        )
        contents = self._contents(turns)
        tokens = 0
        steps: list[ToolStep] = []
        started = time.monotonic()

        def done(text: str) -> AgentReply:
            return AgentReply(text, tokens, tuple(steps), model, int((time.monotonic() - started) * 1000))

        for round_number in range(self._max_rounds + 1):
            while True:
                try:
                    response = await self._generate(contents, config, model=model)
                    break
                except Exception as exc:  # noqa: BLE001 - chỉ xử lý riêng lỗi do tham số thinking
                    if config.thinking_config is None or not _rejects_thinking(exc):
                        raise
                    log.info("Model không nhận thinking_level, gọi lại không có tham số này: %s", exc)
                    self._no_thinking.add(model)
                    config.thinking_config = None
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


    async def classify(self, system: str, text: str, *, model: str | None = None,
                       timeout: float = CLASSIFY_TIMEOUT) -> tuple[dict[str, Any], int]:
        """Câu hỏi có/không ngắn, trả JSON (dùng cho bộ lọc tin). Lỗi thì ném ngoại lệ cho bên gọi xử lý.

        Gemini quá tải hay trả chậm: chờ tới `timeout` giây, hết giờ thì thử thêm một lần.
        Tắt bớt "suy nghĩ" (thinking) cho câu hỏi đơn giản này để nhanh và rẻ; model nào không nhận
        tham số đó (lỗi 400) thì bỏ hẳn và gọi lại.
        """
        attempts = 0
        while True:
            attempts += 1
            config = self._types.GenerateContentConfig(
                system_instruction=system,
                temperature=0,
                max_output_tokens=256,
                response_mime_type="application/json",
                thinking_config=self._types.ThinkingConfig(thinking_level="low") if self._classify_thinking else None,
            )
            try:
                response = await self._generate(text, config, model=model, timeout=timeout, retry_timeout=False)
                break
            except asyncio.TimeoutError:
                if attempts >= 2:
                    raise TimeoutError(f"Gemini không trả lời sau {timeout:.0f} giây (đã thử {attempts} lần)") from None
                log.warning("Bộ lọc: Gemini chưa trả lời sau %.0f giây, thử lại", timeout)
            except Exception as exc:  # noqa: BLE001 - chỉ xử lý riêng lỗi do tham số thinking
                if self._classify_thinking and _rejects_thinking(exc) and attempts < 3:
                    log.info("Model không nhận thinking_level, gọi lại không có tham số này: %s", exc)
                    self._classify_thinking = False
                    continue
                raise
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
