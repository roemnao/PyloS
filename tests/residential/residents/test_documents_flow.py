"""Tài liệu qua Zalo: nhận tệp người dùng gửi vào huts/<chat>/docs/ và gửi tệp bot tạo / sửa."""

from __future__ import annotations

import json

import httpx
import pytest
from conftest import OWNER, event, make_settings

from pylos.gate.main_gate.media import document_fetch
from pylos.gate.main_gate.zalo import ZaloError, ZaloUnsupported
from pylos.gate.main_gate.zalo.personal_account import to_incoming
from pylos.lobby.dispatch.clock.vietnam_time import now_ms
from pylos.lobby.office.agent_tools import OutgoingFile
from pylos.lobby.office.documents import writer
from pylos.residential.residents.pylos import AgentReply, PromptBuilder
from pylos.residential.residents.pylos.message_handler import MEDIA_TOO_LARGE_REPLY, Bot

_n = [0]


def file_msg(name: str, *, size: int = 0, chat_id: str = OWNER, group: bool = False, caption: str = ""):
    _n[0] += 1
    content = {"href": f"https://cdn.zalo/{name}", "title": caption or name,
               "params": json.dumps({"fileName": name, "fileSize": size})}
    obj = {"msgType": "share.file", "dName": "An", "ts": str(now_ms() + 1000)}
    return to_incoming(f"ff{_n[0]}", OWNER, content, obj, chat_id, group, "bot-self")


@pytest.fixture
def cdn(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("big.docx"):
            return httpx.Response(200, content=b"x" * (2 * 1024 * 1024))
        return httpx.Response(200, content="# Tiêu đề\nnội dung".encode("utf-8"))

    monkeypatch.setattr(document_fetch, "transport", httpx.MockTransport(handler))


class RecordingAgent:
    def __init__(self, outbox_paths=(), reply="xong"):
        self.outbox_paths, self.reply_text, self.prompts = list(outbox_paths), reply, []

    async def reply(self, system, turns, ctx, **overrides):
        self.prompts.append(turns[-1].text)
        ctx.outbox.extend(OutgoingFile(p, "") for p in self.outbox_paths)
        return AgentReply(self.reply_text, 5)

    async def classify(self, *a, **k):
        raise AssertionError("không được gọi")


class DocZalo:
    def __init__(self, send_file="ok"):
        self.events, self.mode = [], send_file

    async def send_message(self, chat_id, text):
        self.events.append(("text", text))
        return {}

    async def send_file(self, chat_id, path, caption=""):
        if self.mode == "unsupported":
            raise ZaloUnsupported("Zalo Bot")
        if self.mode == "fail":
            raise ZaloError("temporary", 500)
        self.events.append(("file", path.name))
        return {}

    async def send_chat_action(self, chat_id, action="typing"):
        return None


class NoFileZalo(DocZalo):
    send_file = None  # Zalo Bot Platform / bản cũ: không có gửi tệp


def make(tmp_path, zalo, agent, **env):
    settings = make_settings(tmp_path, ALLOW_ALL_CHATS="true", HUTS_DIR=str(tmp_path / "huts"), **env)
    return Bot(settings, zalo, agent, PromptBuilder(settings.workspace_dir), retry_delay=0)


async def push(bot, msg):
    """Tin Zalo cá nhân (IncomingMessage) vào handle_message; payload Bot Platform vào handle_payload."""
    await (bot.handle_payload(msg) if isinstance(msg, dict) else bot.handle_message(msg))
    await bot.drain()


def docs(tmp_path, chat=OWNER):
    return tmp_path / "huts" / chat / "docs"


async def test_private_document_is_saved_in_the_hut_and_announced_to_the_model(tmp_path, cdn):
    agent = RecordingAgent()
    bot = make(tmp_path, DocZalo(), agent)
    await push(bot, file_msg("ke-hoach.md", size=20))
    assert (docs(tmp_path) / "ke-hoach.md").read_text(encoding="utf-8").startswith("# Tiêu đề")
    assert "(gửi một tệp tài liệu)" in agent.prompts[0] and "[Tệp đã nhận: ke-hoach.md]" in agent.prompts[0]
    await push(bot, file_msg("ke-hoach.md", size=20))
    assert (docs(tmp_path) / "ke-hoach-2.md").exists() and "[Tệp đã nhận: ke-hoach-2.md]" in agent.prompts[1]


async def test_unsupported_and_oversized_documents_get_a_short_notice(tmp_path, cdn):
    zalo, agent = DocZalo(), RecordingAgent()
    bot = make(tmp_path, zalo, agent, DOC_MAX_MB="1")
    await push(bot, file_msg("bang.xlsx"))  # đuôi không hỗ trợ: như trước đây, báo không phải tin chữ
    await push(bot, file_msg("big.docx", size=2 * 1024 * 1024))
    texts = [e[1] for e in zalo.events]
    assert texts[0] == "Hiện mình chỉ đọc được tin nhắn chữ."
    assert texts[1] == MEDIA_TOO_LARGE_REPLY.format(mb=1)
    assert not agent.prompts and not docs(tmp_path).exists()


async def test_documents_off_means_files_are_ignored_like_before(tmp_path, cdn):
    zalo, agent = DocZalo(), RecordingAgent()
    bot = make(tmp_path, zalo, agent, DOC_TOOLS="false")
    await push(bot, file_msg("ke-hoach.md"))
    assert [e[1] for e in zalo.events] == ["Hiện mình chỉ đọc được tin nhắn chữ."] and not agent.prompts


async def test_group_document_needs_a_call_to_the_bot(tmp_path, cdn):
    agent = RecordingAgent()
    bot = make(tmp_path, DocZalo(), agent)
    await push(bot, file_msg("a.md", chat_id="g1", group=True))
    assert not agent.prompts and not docs(tmp_path, "g1").exists()
    # Zalo không cho chú thích khi gửi tệp: người dùng gọi bot bằng tin chữ rồi gửi tệp ngay sau đó (trong 2 phút)
    await push(bot, event("bot đọc giúp tệp này", chat_id="g1", from_id=OWNER, chat_type="GROUP"))
    await push(bot, file_msg("a.md", chat_id="g1", group=True))
    assert (docs(tmp_path, "g1") / "a.md").exists() and "[Tệp đã nhận: a.md]" in agent.prompts[-1]


async def test_file_event_order_and_history(tmp_path):
    path = docs(tmp_path) / "bao-cao.docx"
    path.parent.mkdir(parents=True)
    writer.markdown_to_docx("# a", path)
    zalo = DocZalo()
    bot = make(tmp_path, zalo, RecordingAgent([path, path]))
    await bot.handle_payload(event("soạn báo cáo", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    await bot.drain()
    assert zalo.events == [("file", "bao-cao.docx"), ("text", "xong")]
    assert "(đã gửi tệp: bao-cao.docx)" in bot.history.recent(OWNER, 5)[-1]["text"]


async def test_zalo_without_file_support_gets_the_content_as_text(tmp_path):
    path = docs(tmp_path) / "ghi-chu.md"
    path.parent.mkdir(parents=True)
    path.write_text("# Việc cần làm\n- một", encoding="utf-8")
    for zalo in (NoFileZalo(), DocZalo(send_file="unsupported")):
        bot = make(tmp_path, zalo, RecordingAgent([path]))
        await bot.handle_payload(event("gửi ghi chú", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
        await bot.drain()
        texts = [e[1] for e in zalo.events]
        assert "chưa gửi được tệp ghi-chu.md" in texts[0] and "# Việc cần làm" in texts[0] and texts[1] == "xong"


async def test_file_send_failure_is_dead_lettered_and_the_user_is_told(tmp_path):
    path = docs(tmp_path) / "ghi-chu.md"
    path.parent.mkdir(parents=True)
    path.write_text("x", encoding="utf-8")
    zalo = DocZalo(send_file="fail")
    bot = make(tmp_path, zalo, RecordingAgent([path]))
    await bot.handle_payload(event("gửi ghi chú", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    await bot.drain()
    assert [e[1] for e in zalo.events] == [bot.FILE_FAILED.format(name="ghi-chu.md"), "xong"]
    assert "(tệp) ghi-chu.md" in (tmp_path / "data" / "failed_replies.txt").read_text(encoding="utf-8")
    assert "(đã gửi" not in bot.history.recent(OWNER, 5)[-1]["text"]


def test_model_faked_file_note_is_stripped_from_the_reply():
    from pylos.residential.residents.pylos.message_handler import strip_fake_notes

    assert strip_fake_notes("Xong rồi.\n(đã gửi tệp: a.docx)") == "Xong rồi."
    assert strip_fake_notes("(đã gửi 2 ảnh)\nOk") == "Ok"
    assert strip_fake_notes("Tệp (đã gửi tệp: x) giữa câu") == "Tệp (đã gửi tệp: x) giữa câu"



class FakingAgent(RecordingAgent):
    """Lần đầu bắt chước ghi chú lịch sử mà không gọi tool; sau lời nhắc mới tạo tệp thật."""

    def __init__(self, path):
        super().__init__([])
        self.path = path

    async def reply(self, system, turns, ctx, **overrides):
        self.prompts.append(turns[-1].text)
        if len(self.prompts) == 1:
            return AgentReply("Xong.\n(đã gửi tệp: a.docx)", 4)
        ctx.outbox.append(OutgoingFile(self.path, ""))
        return AgentReply("Đây.", 4)


async def test_faked_sent_note_without_a_tool_call_is_retried_once(tmp_path):
    path = docs(tmp_path) / "a.docx"
    path.parent.mkdir(parents=True)
    writer.markdown_to_docx("# a", path)
    zalo = DocZalo()
    agent = FakingAgent(path)
    bot = make(tmp_path, zalo, agent)
    await bot.handle_payload(event("tạo file", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    await bot.drain()
    assert len(agent.prompts) == 2 and agent.prompts[1].startswith("[Hệ thống]")
    assert zalo.events == [("file", "a.docx"), ("text", "Đây.")]


async def test_faked_note_that_stays_faked_tells_the_truth(tmp_path):
    zalo = DocZalo()
    bot = make(tmp_path, zalo, RecordingAgent([], reply="Xong.\n(đã gửi tệp: a.docx)"))
    await bot.handle_payload(event("tạo file", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    await bot.drain()
    assert zalo.events == [("text", "Xong."), ("text", "Mình chưa tạo được tệp lần này, bạn nhờ lại giúp mình nhé.")]
