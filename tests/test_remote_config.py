from __future__ import annotations

import asyncio
import json

from conftest import GROUP, OWNER, event

from bot.agent import AgentReply, ToolStep
from bot.system.remote_config import RemoteConfig, RemoteSync, overrides, read_cached
from bot.system.session_upload import SessionUploader


async def send(bot, payload) -> None:
    await bot.handle_payload(payload)
    await bot.drain()


def test_only_allowed_keys_are_taken_from_web():
    fields, ignored = overrides({
        "GEMINI_MODEL": "gemini-3.1-pro", "FILTER_MODEL": "gemini-3.1-flash-lite", "FILTER_AI": "false",
        "BOT_NAMES": "roemnao, bot", "HISTORY_TURNS": 30, "ASSIGN_ALLOWED": "all", "SESSION_UPLOAD": False,
        # Không bao giờ nhận khoá bí mật hay thông số nguy hiểm, kể cả khi web gửi xuống.
        "GEMINI_API_KEY": "k", "ZALO_BOT_TOKEN": "t", "ADMIN_TOKEN": "a", "OWNER_ZALO_ID": "ke-la", "ZALO_IMEI": "i",
        "SCHEDULE_API_KEY": "s", "DATA_DIR": "/etc",
        # Sai kiểu thì bỏ qua.
        "MAX_OUTPUT_TOKENS": "nhiều", "GEMINI_MODEL_X": "x",
    })
    assert fields == {
        "gemini_model": "gemini-3.1-pro", "filter_model": "gemini-3.1-flash-lite", "filter_ai": False,
        "bot_names": ("roemnao", "bot"), "history_turns": 30, "assign_allowed": "all", "session_upload": False,
    }
    assert {"GEMINI_API_KEY", "ZALO_BOT_TOKEN", "ADMIN_TOKEN", "OWNER_ZALO_ID", "MAX_OUTPUT_TOKENS"} <= set(ignored)


class Configurable:
    """Agent giả có configure() như GeminiAgent."""

    def __init__(self, inner) -> None:
        self.inner = inner
        self.configured: dict = {}

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def configure(self, **kwargs) -> None:
        self.configured = kwargs


async def test_web_config_applies_live_and_survives_restart(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, BOT_NAMES="bot")
    bot.agent = Configurable(agent)
    remote = RemoteConfig(bot.settings, bot.apply_settings)
    assert remote.version == 0

    changed = remote.update({"version": 3, "values": {"GEMINI_MODEL": "gemini-3.1-pro", "BOT_NAMES": "roemnao",
                                                      "USER_RATE_PER_MIN": 2, "MEMORYDATA_KEEP": 300, "HISTORY_TURNS": 100,
                                                      "GEMINI_API_KEY": "lo-khoa"},
                             "files": {"SYSTEM.md": "Bạn là roemnao.", "../evil.md": "x"}})
    assert changed
    assert bot.settings.gemini_model == "gemini-3.1-pro" and bot.settings.bot_names == ("roemnao",)
    assert bot.settings.gemini_api_key == ""  # khoá không đổi theo web
    assert bot.filter.settings is bot.settings and bot.user_limiter.per_minute == 2
    assert bot.memory.keep == 300 and bot.history.keep == 400
    assert bot.agent.configured["model"] == "gemini-3.1-pro"
    assert (bot.settings.workspace_dir / "SYSTEM.md").read_text(encoding="utf-8") == "Bạn là roemnao."
    assert not (bot.settings.workspace_dir.parent / "evil.md").exists()
    # Tên bot mới có hiệu lực ngay với bộ lọc.
    await send(bot, event("roemnao ơi mấy giờ rồi"))
    assert len(agent.calls) == 1

    # Lưu lại để dùng khi mất mạng; bản cũ của SYSTEM.md được giữ trong .backup khi web đổi tiếp.
    cached = read_cached(bot.settings)
    assert cached["version"] == 3 and "GEMINI_API_KEY" not in cached["values"]
    assert remote.update({"version": 3, "values": cached["values"], "files": cached["files"]}) is False
    remote.update({"version": 4, "values": {}, "files": {"SYSTEM.md": "Bản mới."}})
    assert bot.settings.gemini_model == "gemini-3.1-flash-lite"  # web bỏ thông số → quay về settings.env
    assert list((bot.settings.workspace_dir / ".backup").glob("SYSTEM-*.md"))

    fresh = make_bot(ALLOWED_CHAT_IDS=GROUP)
    again = RemoteConfig(fresh.settings, fresh.apply_settings)
    assert again.version == 4 and again.files == {"SYSTEM.md": "Bản mới."}


async def test_heartbeat_fetches_new_config_and_tolerates_network_errors(make_bot, web):
    bot = make_bot()
    remote = RemoteConfig(bot.settings, bot.apply_settings)
    web.on("GET", "/config", {"version": 1, "values": {"FILTER_MODEL": "gemini-3.1-flash-lite"}, "files": {}})
    web.on("POST", "/heartbeat", lambda body: {"ok": True, "version": 2, "config": {
        "version": 2, "values": {"FILTER_MODEL": "gemini-3.5-flash"}, "files": {}}} if body["configVersion"] != 2 else
        {"ok": True, "version": 2, "config": None})
    sync = RemoteSync(remote, lambda: {"version": "0.1.0", "tokensToday": 12})
    assert await sync.fetch_config()
    assert bot.settings.filter_model == "gemini-3.1-flash-lite"
    assert await sync.beat()
    assert web.bodies("POST", "/heartbeat")[0] == {"version": "0.1.0", "tokensToday": 12, "configVersion": 1}
    assert bot.settings.filter_model == "gemini-3.5-flash" and remote.version == 2
    assert await sync.beat()
    assert web.bodies("POST", "/heartbeat")[1]["configVersion"] == 2

    web.offline = True
    assert await sync.beat() is False
    assert not await sync.fetch_config()
    assert bot.settings.filter_model == "gemini-3.5-flash"  # vẫn dùng bản đang có

    # Vòng chạy nền dừng gọn khi được báo dừng.
    stop = asyncio.Event()
    task = asyncio.create_task(RemoteSync(remote, dict, interval=0.01).run(stop))
    await asyncio.sleep(0.05)
    stop.set()
    await asyncio.wait_for(task, 1)


async def test_session_uploader_batches_retries_and_respects_switch(web):
    enabled = {"on": True}
    up = SessionUploader(lambda: enabled["on"], batch=2, buffer=5)
    web.on("POST", "/sessions", lambda body: {"saved": len(body["events"])})
    for i in range(3):
        up.record("g1", "message", text=f"tin {i}", empty=None)
    assert len(up) == 3
    assert await up.flush()
    sent = web.bodies("POST", "/sessions")[0]["events"]
    assert [e["text"] for e in sent] == ["tin 0", "tin 1"] and "empty" not in sent[0] and sent[0]["chatId"] == "g1"

    web.offline = True
    assert await up.flush() is False
    assert len(up) == 1  # gửi lỗi: giữ lại để gửi sau
    for i in range(10):
        up.record("g1", "message", text=f"thêm {i}")
    assert len(up) == 5  # đầy thì bỏ bước cũ nhất

    enabled["on"] = False
    up.record("g1", "message", text="không ghi")
    web.offline = False
    assert await up.flush() and len(up) == 0  # tắt gửi session thì bỏ hết, không gửi gì


class Recorder:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def record(self, chat_id: str, kind: str, **fields) -> None:
        self.events.append((chat_id, kind, fields))


async def test_bot_records_the_whole_chain(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    bot.sessions = Recorder()

    async def reply(system, turns, ctx):
        return AgentReply("Đã giao cho An.", 120, (ToolStep("giao_lich", {"tieu_de": "Họp"}, {
            "ok": True, "event": {"title": "Họp"}, "assigned": [{"name": "An"}], "unlinked": [{"name": "Dũng"}]}, 35),),
            "gemini-3.1-flash-lite", 900)

    agent.reply = reply
    await send(bot, event("/bot giao @An họp 9h mai", name="Sếp"))
    await send(bot, event("chuyện riêng", name="Bình"))
    kinds = [k for _, k, _ in bot.sessions.events]
    assert kinds == ["message", "filter", "agent", "tool", "calbot", "reply", "message", "filter"]
    by_kind = {k: f for _, k, f in bot.sessions.events[:6]}
    assert by_kind["message"]["senderName"] == "Sếp" and by_kind["filter"]["decision"] == "reply"
    assert by_kind["agent"]["tokens"] == 120 and by_kind["agent"]["ms"] == 900
    assert by_kind["calbot"] == {"op": "create", "title": "Họp", "summary": "1 người nhận, 1 chưa liên kết"}
    assert bot.sessions.events[-1][2]["decision"] == "skip"

    # Tắt gửi session (trên web hoặc settings.env) thì không ghi gì.
    bot.sessions.events.clear()
    bot.apply_settings(bot.settings.__class__(**{**bot.settings.__dict__, "session_upload": False}))
    await send(bot, event("/bot nữa"))
    assert bot.sessions.events == []


async def test_private_link_code_goes_to_web_before_anything_else(make_bot, zalo, agent, web):
    bot = make_bot()
    web.on("POST", "/zalo-link", lambda body: (200, {"ok": True, "member": {"name": "Nguyễn Văn An", "email": "an…@gmail.com"}})
           if body["code"] == "123456" else (404, {"error": "Mã không đúng hoặc đã hết hạn. Mở app, lấy mã mới rồi gửi lại."}))
    await send(bot, event("123456", chat_type="PRIVATE", chat_id="u-an", from_id="u-an", name="An Zalo"))
    assert web.bodies("POST", "/zalo-link") == [{"code": "123456", "zaloUid": "u-an", "zaloName": "An Zalo"}]
    assert "Đã liên kết" in zalo.texts("u-an")[-1] and "Nguyễn Văn An" in zalo.texts("u-an")[-1]
    await send(bot, event("/lienket 654321", chat_type="PRIVATE", chat_id="u-an", from_id="u-an"))
    assert zalo.texts("u-an")[-1].startswith("Mã không đúng")
    assert agent.calls == [] and agent.classify_calls == []  # không tốn token

    # Trong nhóm, hoặc tin không phải đúng 6 số: không coi là mã.
    await send(bot, event("123456", chat_id=GROUP))
    await send(bot, event("mã 1234567", chat_type="PRIVATE", chat_id=OWNER, from_id=OWNER))
    assert len(web.bodies("POST", "/zalo-link")) == 2
    web.offline = True
    await send(bot, event("111111", chat_type="PRIVATE", chat_id="u-x", from_id="u-x"))
    assert "không kết nối được máy chủ" in zalo.texts("u-x")[-1]


async def test_link_code_ignored_without_web_key(make_bot, zalo, monkeypatch, tmp_path):
    monkeypatch.setattr("bot.config.APP_HOME", tmp_path)
    monkeypatch.delenv("SCHEDULE_API_KEY", raising=False)
    bot = make_bot()
    await send(bot, event("123456", chat_type="PRIVATE", chat_id="u-an", from_id="u-an"))
    assert not any("liên kết" in t for t in zalo.texts("u-an"))


def test_cache_file_is_plain_json(make_bot):
    bot = make_bot()
    RemoteConfig(bot.settings, bot.apply_settings).update({"version": 1, "values": {"FILTER_AI": True}, "files": {}})
    data = json.loads((bot.settings.system_dir / "remote_config.json").read_text(encoding="utf-8"))
    assert data["values"] == {"FILTER_AI": True} and data["version"] == 1
