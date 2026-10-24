from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from bot.agent import AgentReply, PromptBuilder, ToolContext, Turn
from bot.core.message_handler import Bot
from bot.config import Settings
from bot.core.vietnam_time import now_ms
from bot.zalo import ZaloError

OWNER = "owner-1"
GROUP = "group-1"


class FakeZalo:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []
        self.fail_times = 0

    async def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        if self.fail_times > 0:
            self.fail_times -= 1
            raise ZaloError("temporary", 500)
        self.sent.append((chat_id, text))
        return {"message_id": str(len(self.sent))}

    async def send_chat_action(self, chat_id: str, action: str = "typing") -> None:
        return None

    def texts(self, chat_id: str | None = None) -> list[str]:
        return [t for c, t in self.sent if chat_id is None or c == chat_id]


class FakeAgent:
    def __init__(self, reply: str = "trả lời", tokens: int = 10) -> None:
        self.reply_text = reply
        self.tokens = tokens
        self.calls: list[tuple[str, list[Turn], ToolContext]] = []
        self.classify_calls: list[str] = []

    async def reply(self, system: str, turns: list[Turn], ctx: ToolContext) -> AgentReply:
        self.calls.append((system, turns, ctx))
        return AgentReply(self.reply_text, self.tokens)

    # Bộ lọc AI giả: mặc định "không nhờ bot"; test đặt filter_reply/filter_error để đổi kịch bản.
    filter_reply = False
    filter_error: Exception | None = None

    async def classify(self, system: str, text: str, **kwargs: Any) -> tuple[dict[str, Any], int]:
        self.classify_calls.append(text)
        if self.filter_error is not None:
            raise self.filter_error
        return {"reply": self.filter_reply, "reason": "giả lập"}, 5


def make_settings(tmp_path: Path, **overrides: str) -> Settings:
    env = {
        "ZALO_BOT_TOKEN": "",
        "GEMINI_API_KEY": "",
        "OWNER_ZALO_ID": OWNER,
        "DATA_DIR": str(tmp_path / "data"),
        "WORKSPACE_DIR": str(tmp_path / "workspace"),
        "LOG_DIR": str(tmp_path / "logs"),
        "USER_RATE_PER_MIN": "0",
        "CHAT_RATE_PER_MIN": "0",
        "DAILY_TOKEN_BUDGET": "0",
    }
    env.update(overrides)
    return Settings.from_env(env, base_dir=tmp_path)


def event(
    text: str | None,
    *,
    chat_id: str = GROUP,
    from_id: str = "user-1",
    name: str = "An",
    chat_type: str = "GROUP",
    message_id: str | None = None,
    date: int | None = None,
    event_name: str = "message.text.received",
    is_bot: bool = False,
) -> dict[str, Any]:
    event.counter += 1  # type: ignore[attr-defined]
    message: dict[str, Any] = {
        "from": {"id": from_id, "display_name": name, "is_bot": is_bot},
        "chat": {"id": chat_id, "chat_type": chat_type},
        "message_id": message_id or f"m{event.counter}",  # type: ignore[attr-defined]
        "date": date if date is not None else now_ms() + 1000,
    }
    if text is not None:
        message["text"] = text
    return {"ok": True, "result": {"event_name": event_name, "message": message}}


event.counter = 0  # type: ignore[attr-defined]


@pytest.fixture
def zalo() -> FakeZalo:
    return FakeZalo()


@pytest.fixture
def agent() -> FakeAgent:
    return FakeAgent()


@pytest.fixture
def make_bot(tmp_path: Path, zalo: FakeZalo, agent: FakeAgent):
    bots: list[Bot] = []

    def factory(**overrides: str) -> Bot:
        settings = make_settings(tmp_path, **overrides)
        bot = Bot(settings, zalo, agent, PromptBuilder(settings.workspace_dir), retry_delay=0)
        bots.append(bot)
        return bot

    yield factory


class FakeWeb:
    """Web iforgotmywayhome giả (API /api/agent/*): trả lời theo bảng route, ghi lại các yêu cầu."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Any]] = []
        self.routes: dict[tuple[str, str], Any] = {}
        self.offline = False

    def on(self, method: str, path: str, reply: Any) -> None:
        """reply: dict/list (HTTP 200), (mã, dict), hoặc hàm(body) -> một trong hai."""
        self.routes[(method, path)] = reply

    def bodies(self, method: str, path: str) -> list[Any]:
        return [b for m, p, b in self.calls if m == method and p == path]

    def handler(self, request: httpx.Request) -> httpx.Response:
        if self.offline:
            raise httpx.ConnectError("offline", request=request)
        if request.headers.get("authorization") != "Bearer k3y":
            return httpx.Response(401, json={"error": "Sai khoá"})
        path = request.url.path.removeprefix("/api/agent")
        body = json.loads(request.content) if request.content else None
        self.calls.append((request.method, path, body))
        reply = self.routes.get((request.method, path))
        if callable(reply):
            reply = reply(body)
        if reply is None:
            return httpx.Response(404, json={"error": "Không có API này"})
        status, data = reply if isinstance(reply, tuple) else (200, reply)
        return httpx.Response(status, json=data)


@pytest.fixture
def web(monkeypatch, tmp_path) -> FakeWeb:
    from bot.system import server_client

    fake = FakeWeb()
    real = httpx.AsyncClient
    monkeypatch.setattr(server_client.httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(fake.handler), **kw))
    monkeypatch.setattr("bot.config.APP_HOME", tmp_path)  # không đọc settings.env thật của máy
    monkeypatch.setenv("SCHEDULE_API_URL", "https://web.example")
    monkeypatch.setenv("SCHEDULE_API_KEY", "k3y")
    return fake
