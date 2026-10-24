from __future__ import annotations

import asyncio
import enum
import json

import pytest

from bot.config import ConfigError
from bot.storage import ActivityStore
from bot.zalo import ZaloError
from bot.zalo.personal import PersonalZalo, _is_network_error, load_session, to_incoming

from conftest import make_settings


class ThreadType(enum.Enum):
    USER = 0
    GROUP = 1


class FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeApi:
    def __init__(self, result=None) -> None:
        self.sent: list[tuple[str, str, ThreadType]] = []
        self.typing: list[tuple[str, ThreadType]] = []
        self.result = result

    def send(self, message, thread_id, thread_type):
        self.sent.append((thread_id, message.text, thread_type))
        return self.result

    def setTyping(self, thread_id, thread_type):  # noqa: N802
        self.typing.append((thread_id, thread_type))


def make_personal(tmp_path, api=None) -> PersonalZalo:
    zalo = PersonalZalo(make_settings(tmp_path, RECEIVE_MODE="personal"))
    zalo._api = api or FakeApi()
    zalo._message_cls = FakeMessage
    zalo._thread_type_cls = ThreadType
    zalo.self_id = "me-1"
    return zalo


def test_load_session_reads_qr_file_and_manual_cookies(tmp_path):
    qr = tmp_path / "s.json"
    qr.write_text(json.dumps({"imei": "imei-qr", "user_agent": "UA", "cookies": {"zpw_sek": "x"}}), encoding="utf-8")
    assert load_session(qr, imei="imei-env") == ({"zpw_sek": "x"}, "imei-qr", "UA")

    flat = tmp_path / "a.json"
    flat.write_text(json.dumps({"zpw_sek": "x", "zpsid": "y"}), encoding="utf-8")
    assert load_session(flat, imei="imei-env") == ({"zpw_sek": "x", "zpsid": "y"}, "imei-env", "")

    listed = tmp_path / "b.json"
    listed.write_text(json.dumps([{"name": "zpw_sek", "value": "x", "domain": ".zalo.me"}]), encoding="utf-8")
    assert load_session(listed, imei="i")[0] == {"zpw_sek": "x"}

    with pytest.raises(ConfigError, match="zalo-login"):
        load_session(tmp_path / "missing.json")
    with pytest.raises(ConfigError, match="IMEI"):
        load_session(flat)
    bad = tmp_path / "c.json"
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_session(bad, imei="i")


def test_to_incoming_maps_fields_and_marks_own_messages():
    msg = to_incoming("m1", "u1", "chào", {"dName": "An", "ts": "1700000000000"}, "g1", True, "me-1")
    assert (msg.chat_id, msg.chat_type, msg.from_id, msg.from_name) == ("g1", "GROUP", "u1", "An")
    assert msg.is_group and msg.is_text and not msg.from_is_bot
    assert msg.dedupe_key == "g1:m1" and msg.date_ms == 1700000000000

    own = to_incoming("m2", "me-1", "bot trả lời", {}, "u1", False, "me-1")
    assert own.from_is_bot and own.chat_type == "PRIVATE"

    sticker = to_incoming("m3", "u1", {"href": "..."}, {}, "u1", False, "me-1")
    assert not sticker.is_text
    assert to_incoming("m4", None, "x", {}, "u1", False, "me-1") is None


def test_require_personal_needs_qr_session(tmp_path):
    settings = make_settings(tmp_path, RECEIVE_MODE="personal", GEMINI_API_KEY="k")
    with pytest.raises(ConfigError, match="Chưa đăng nhập"):
        settings.require()
    session = tmp_path / "data" / "zalo_session.json"
    session.parent.mkdir(parents=True, exist_ok=True)
    session.write_text(json.dumps({"imei": "i", "cookies": {"zpw_sek": "x"}}), encoding="utf-8")
    settings.require()  # không cần ZALO_BOT_TOKEN


async def test_send_picks_thread_type_from_activity(tmp_path):
    zalo = make_personal(tmp_path)
    ActivityStore(zalo.settings.data_dir / "activity.txt").touch("g1", "GROUP", "An")
    await zalo.send_message("g1", "a")
    await zalo.send_message("u9", "b")
    await zalo.send_chat_action("g1")
    assert zalo._api.sent == [("g1", "a", ThreadType.GROUP), ("u9", "b", ThreadType.USER)]
    assert zalo._api.typing == [("g1", ThreadType.GROUP)]


async def test_send_error_becomes_zalo_error(tmp_path):
    zalo = make_personal(tmp_path, FakeApi(result={"error_code": 114, "error_message": "blocked"}))
    with pytest.raises(ZaloError):
        await zalo.send_message("u1", "x")


async def test_listener_thread_dispatches_to_event_loop(tmp_path):
    zalo = make_personal(tmp_path)
    received = []

    async def handle(msg):
        received.append(msg)

    zalo._handler, zalo._loop = handle, asyncio.get_running_loop()
    # onMessage của zlapi chạy ở luồng websocket, không phải luồng event loop.
    await asyncio.to_thread(zalo._on_message, "m1", "u1", "hi", {}, "g1", ThreadType.GROUP)
    await asyncio.sleep(0.05)
    assert [(m.chat_id, m.chat_type, m.text) for m in received] == [("g1", "GROUP", "hi")]


def test_network_errors_are_detected_through_zlapi_wrapping():
    import requests

    try:
        try:
            raise requests.ConnectionError("down")
        except requests.ConnectionError as inner:
            raise RuntimeError("An error occurred while logging in!") from inner
    except RuntimeError as wrapped:
        assert _is_network_error(wrapped)
    assert _is_network_error(RuntimeError("HTTPSConnectionPool(host='wpa.chat.zalo.me'): Max retries exceeded"))
    assert not _is_network_error(RuntimeError("Login failed: invalid cookies"))
