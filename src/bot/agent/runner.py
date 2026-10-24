"""Agent: gọi Gemini, tự chạy vòng lặp function calling có giới hạn số vòng."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Protocol

from bot.agent.tools import ToolContext, ToolRegistry

log = logging.getLogger(__name__)

EMPTY_REPLY = "Xin lỗi, mình chưa trả lời được câu này."
TOO_MANY_STEPS = "Xin lỗi, việc này cần quá nhiều bước, bạn thử hỏi cụ thể hơn nhé."


@dataclass(frozen=True)
class Turn:
    role: str  # "user" hoặc "model"
    text: str
    name: str = ""


@dataclass(frozen=True)
class AgentReply:
    text: str
    tokens: int


class Agent(Protocol):
    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext) -> AgentReply: ...


def _usage_tokens(response: Any) -> int:
    usage = getattr(response, "usage_metadata", None)
    return int(getattr(usage, "total_token_count", 0) or 0) if usage else 0


def _is_transient(exc: BaseException) -> bool:
    """Lỗi mạng (kết nối bị ngắt...) hoặc lỗi phía server Google (5xx): đáng thử lại."""
    import httpx

    if isinstance(exc, httpx.TransportError):
        return True
    code = getattr(exc, "code", None)
    return isinstance(code, int) and code >= 500


class GeminiAgent:
    RETRIES = 2
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

    async def _generate(self, contents: list[Any], config: Any) -> Any:
        """Gọi Gemini, thử lại tối đa 2 lần nếu lỗi mạng tạm thời hoặc lỗi 5xx của Google."""
        for attempt in range(1, self.RETRIES + 2):
            try:
                return await asyncio.wait_for(
                    self._client.aio.models.generate_content(model=self._model, contents=contents, config=config),
                    timeout=self._timeout,
                )
            except Exception as exc:  # noqa: BLE001 - lọc lỗi tạm thời bên dưới
                if attempt > self.RETRIES or not _is_transient(exc):
                    raise
                log.warning("Gemini lỗi tạm thời (lần %d), thử lại: %s", attempt, type(exc).__name__)
                await asyncio.sleep(self.retry_delay * attempt)
        raise AssertionError("unreachable")

    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext) -> AgentReply:
        types = self._types
        declarations = self._tools.declarations()
        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=self._max_output_tokens,
            tools=[types.Tool(function_declarations=declarations)] if declarations else None,
            # Tự chạy vòng lặp để kiểm soát số vòng và quyền của từng tool.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        contents = self._contents(turns)
        tokens = 0
        for round_number in range(self._max_rounds + 1):
            response = await self._generate(contents, config)
            tokens += _usage_tokens(response)
            calls = response.function_calls or []
            if not calls:
                return AgentReply((response.text or "").strip() or EMPTY_REPLY, tokens)
            if round_number == self._max_rounds:
                log.warning("Hết %d vòng tool mà model vẫn muốn gọi tiếp", self._max_rounds)
                return AgentReply(TOO_MANY_STEPS, tokens)
            # Giữ nguyên content của model (kể cả thought signature) trước khi trả kết quả tool.
            contents.append(response.candidates[0].content)
            parts = []
            for call in calls:
                args = dict(call.args or {})
                log.info("Tool %s(%s)", call.name, args)
                result = await self._tools.call(call.name, args, ctx)
                parts.append(types.Part.from_function_response(name=call.name, response=result))
            contents.append(types.Content(role="user", parts=parts))
        return AgentReply(TOO_MANY_STEPS, tokens)  # không tới được, để type checker yên tâm


class EchoAgent:
    """Agent giả cho chế độ console khi chưa có GEMINI_API_KEY."""

    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext) -> AgentReply:
        last = turns[-1].text if turns else ""
        return AgentReply(f"(echo, chưa có GEMINI_API_KEY) {last}", 0)
