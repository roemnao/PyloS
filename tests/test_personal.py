from __future__ import annotations

import asyncio
import enum
import json

import pytest

from bot.config import ConfigError
from bot.storage import ActivityStore
from bot.zalo import ZaloError
from bot.core.mentions import add_tags, build_mentions
from bot.zalo.personal import PersonalZalo, _is_network_error, load_session, mention_names, to_incoming

from conftest import make_settings


class ThreadType(enum.Enum):
    USER = 0
    GROUP = 1


class FakeMessage:
    def __init__(self, text: str, mention: str | None = None) -> None:
        self.text = text
        self.mention = mention


class FakeApi:
    def __init__(self, result=None) -> None:
        self.sent: list[tuple[str, str, ThreadType]] = []
        self.typing: list[tuple[str, ThreadType]] = []
        self.result = result

    group_info: dict = {}
    profiles: dict = {}
    info_calls = 0

    def send(self, message, thread_id, thread_type):
        self.sent.append((thread_id, message.text, thread_type))
        self.mentions = getattr(message, "mention", None)
        return self.result

    def fetchGroupInfo(self, group_id):  # noqa: N802
        self.info_calls += 1
        return {"gridInfoMap": {group_id: self.group_info}}

    def fetchUserInfo(self, uids):  # noqa: N802
        return {"changed_profiles": {u: self.profiles[u] for u in uids if u in self.profiles}}

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
    session = tmp_path / "userdata" / "config" / "zalo_session.json"
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


# ---------- tag người trong nhóm ----------

def test_build_mentions_matches_known_names_longest_first():
    members = {"u1": "Thái", "u2": "Thái Toàn", "u3": "Thu Hồng"}
    text = "@Thái Toàn và @thu hồng nhớ nộp bài, còn @Lan thì chưa có trong nhóm"
    assert build_mentions(text, members) == [
        {"pos": 0, "len": 10, "uid": "u2", "type": 0},
        {"pos": 14, "len": 9, "uid": "u3", "type": 0},
    ]
    assert build_mentions("@Tháiii ơi", members) == []  # phải hết tên ở ranh giới từ
    # emoji ngoài BMP tính 2 đơn vị UTF-16 như Zalo (JavaScript)
    assert build_mentions("😀 @Thái ơi", members) == [{"pos": 3, "len": 5, "uid": "u1", "type": 0}]


async def test_members_merge_group_list_and_recent_speakers(tmp_path):
    api = FakeApi()
    api.group_info = {"memVerList": ["u1_0", "u2_0", "me-1_0"], "currentMems": [{"id": "u1", "dName": "An"}]}
    api.profiles = {"u2": {"displayName": "Bình"}, "me-1": {"displayName": "Bot"}}
    zalo = make_personal(tmp_path, api)
    ActivityStore(zalo.settings.data_dir / "activity.txt").touch("g1", "GROUP", "An")
    zalo._memory.add_user("g1", msg_id="1", uid="u3", name="Lan", text="hi", is_text=True, decision={})
    assert zalo.members("g1") == {"u1": "An", "u2": "Bình", "u3": "Lan"}  # không có chính acc bot
    zalo.members("g1")
    assert api.info_calls == 1  # lưu tạm, không hỏi Zalo mỗi tin


async def test_send_in_group_attaches_mentions_but_not_in_private(tmp_path):
    api = FakeApi()
    api.group_info = {"currentMems": [{"id": "u2", "dName": "Thái Toàn"}]}
    zalo = make_personal(tmp_path, api)
    ActivityStore(zalo.settings.data_dir / "activity.txt").touch("g1", "GROUP", "An")
    await zalo.send_message("g1", "@Thái Toàn ơi nộp bài nhé")
    assert json.loads(api.mentions) == [{"pos": 0, "len": 10, "uid": "u2", "type": 0}]
    await zalo.send_message("u9", "@Thái Toàn ơi")
    assert api.mentions is None


async def test_bot_tells_model_member_names(tmp_path):
    from bot.agent import PromptBuilder
    from bot.core.app import Bot

    from conftest import GROUP, FakeAgent, FakeZalo, event

    class WithMembers(FakeZalo):
        def members(self, chat_id):
            return {"u2": "Thái Toàn", "u3": "Thu Hồng"}

    agent = FakeAgent()
    settings = make_settings(tmp_path, ALLOWED_CHAT_IDS=GROUP)
    bot = Bot(settings, WithMembers(), agent, PromptBuilder(settings.workspace_dir), retry_delay=0)
    await bot.handle_payload(event("/bot nhắc Thái Toàn nộp bài"))
    await bot.drain()
    system = agent.calls[0][0]
    assert "@Thái Toàn" in system or "Thái Toàn" in system
    assert "Thu Hồng" in system and "tag" in system


def test_build_mentions_ignores_case_and_diacritics():
    members = {"u5": "Phúc Xo"}
    assert build_mentions("@phuc xo làm bài nhé", members) == [{"pos": 0, "len": 8, "uid": "u5", "type": 0}]


def test_add_tags_only_for_names_requested_with_tag_intent():
    members = {"u5": "Phúc Xo", "u6": "Bình", "u7": "Thái", "u8": "Thái Toàn"}
    reply = "Phúc Xo ơi, bạn nhớ làm bài tập train C nhé"
    assert add_tags(reply, "roemnao tag phúc xo kêu làm bài tập train c", members) == "@" + reply
    # không có ý tag/nhắc/gọi: giữ nguyên (tránh làm người khác nhận thông báo khi chỉ nói về họ)
    assert add_tags("Bình nói 7h nhé", "Bình nói mấy giờ vậy?", members) == "Bình nói 7h nhé"
    # chỉ tag người được nhờ, không tag người khác có trong câu trả lời
    assert add_tags("Bình ơi, Thái Toàn nhờ bạn", "nhắc Bình giúp", members) == "@Bình ơi, Thái Toàn nhờ bạn"
    # tên dài khớp trước; đã có "@" thì không thêm nữa
    assert add_tags("Thái Toàn ơi", "gọi thái toàn", members) == "@Thái Toàn ơi"
    assert add_tags("@Thái Toàn ơi", "gọi thái toàn", members) == "@Thái Toàn ơi"


async def test_bot_adds_missing_at_sign_end_to_end(tmp_path):
    from bot.agent import PromptBuilder
    from bot.core.app import Bot

    from conftest import GROUP, FakeAgent, FakeZalo, event

    class WithMembers(FakeZalo):
        def members(self, chat_id):
            return {"u5": "Phúc Xo"}

    agent = FakeAgent(reply="Phúc Xo ơi, bạn nhớ làm bài tập train C nhé")
    zalo = WithMembers()
    settings = make_settings(tmp_path, ALLOWED_CHAT_IDS=GROUP, BOT_NAMES="roemnao")
    bot = Bot(settings, zalo, agent, PromptBuilder(settings.workspace_dir), retry_delay=0)
    await bot.handle_payload(event("roemnao tag phúc xo kêu làm bài tập train c"))
    await bot.drain()
    assert zalo.texts(GROUP)[-1] == "@Phúc Xo ơi, bạn nhớ làm bài tập train C nhé"


def test_names_learned_from_incoming_tags(tmp_path):
    text = "😀 roemnao tag @Phúc Xo với @All nhé"
    mentions = [{"uid": "u5", "pos": 15, "len": 8, "type": 0}, {"uid": "-1", "pos": 28, "len": 4, "type": 1}]
    assert mention_names(text, mentions) == {"u5": "Phúc Xo"}

    zalo = make_personal(tmp_path)
    zalo._on_message("m1", "u1", text, {"ts": "1", "mentions": mentions}, "g1", ThreadType.GROUP)
    assert zalo._learned["g1"] == {"u5": "Phúc Xo"}
    ActivityStore(zalo.settings.data_dir / "activity.txt").touch("g1", "GROUP", "An")
    assert zalo.members("g1")["u5"] == "Phúc Xo"
