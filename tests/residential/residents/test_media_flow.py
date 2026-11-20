"""Ảnh, video, tin thoại: từ tin Zalo cá nhân tới lúc Gemini nhận được tệp."""

from __future__ import annotations

import httpx
import pytest
from conftest import GROUP, OWNER, event

from pylos.gate.main_gate.media import media_fetch
from pylos.gate.main_gate.zalo.personal_account import to_incoming
from pylos.lobby.dispatch.clock.vietnam_time import now_ms
from pylos.residential.residents.pylos.message_handler import (
    MEDIA_FAILED_REPLY,
    MEDIA_TOO_LARGE_REPLY,
    NON_TEXT_REPLY,
)

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 200
AAC = b"\xff\xf1" + b"0" * 200


@pytest.fixture
def cdn(monkeypatch):
    """CDN giả: /big là tệp 2 MB, /gone trả 404, còn lại là ảnh hoặc tin thoại nhỏ."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("big.jpg"):
            return httpx.Response(200, content=b"\xff\xd8\xff" + b"x" * (2 * 1024 * 1024), headers={"content-type": "image/jpeg"})
        if path.endswith("gone.jpg"):
            return httpx.Response(404)
        if path.endswith(".aac"):
            return httpx.Response(200, content=AAC, headers={"content-type": "audio/aac"})
        return httpx.Response(200, content=JPEG, headers={"content-type": "image/jpeg"})

    monkeypatch.setattr(media_fetch, "transport", httpx.MockTransport(handler))


_counter = [0]


def media_msg(msg_type: str, href: str, *, caption: str = "", chat_id: str = OWNER, from_id: str = OWNER, group: bool = False):
    _counter[0] += 1
    content = {"href": href, "title": caption}
    obj = {"msgType": msg_type, "dName": "An", "ts": str(now_ms() + 1000)}
    return to_incoming(f"mm{_counter[0]}", from_id, content, obj, chat_id, group, "bot-self")


async def push(bot, msg) -> None:
    """Tin Zalo cá nhân (IncomingMessage) vào handle_message; payload Bot Platform vào handle_payload."""
    if isinstance(msg, dict):
        await bot.handle_payload(msg)
    else:
        await bot.handle_message(msg)
    await bot.drain()


async def test_private_photo_reaches_agent_with_media(make_bot, zalo, agent, cdn):
    bot = make_bot()
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg", caption="ảnh con mèo"))
    assert len(agent.calls) == 1
    turn = agent.calls[0][1][-1]
    assert turn.text == "ảnh con mèo"
    assert len(turn.media) == 1 and turn.media[0].mime == "image/jpeg" and turn.media[0].path.read_bytes() == JPEG
    assert zalo.texts(OWNER) == ["trả lời"]


async def test_voice_without_caption_gets_placeholder_prompt(make_bot, agent, cdn):
    bot = make_bot()
    await push(bot, media_msg("chat.voice", "https://cdn.zalo/v.aac"))
    turn = agent.calls[0][1][-1]
    assert "tin nhắn thoại" in turn.text and turn.media[0].kind == "voice" and turn.media[0].mime == "audio/aac"


async def test_followup_reattaches_recent_media_only(make_bot, agent, cdn):
    bot = make_bot(MEDIA_FOLLOWUP_TURNS="2")
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg", caption="ảnh 1"))
    await push(bot, event("trong ảnh còn gì nữa?", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    first = agent.calls[1][1][0]
    assert first.text == "ảnh 1" and len(first.media) == 1  # còn trong 2 lượt gần nhất
    await push(bot, event("cảm ơn", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    old = agent.calls[2][1][0]
    assert old.media == () and "hết hạn" in old.text  # đã ngoài 2 lượt gần nhất


async def test_followup_disabled_by_zero_turns(make_bot, agent, cdn):
    bot = make_bot(MEDIA_FOLLOWUP_TURNS="0")
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg", caption="ảnh"))
    await push(bot, event("hỏi tiếp", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    assert agent.calls[1][1][0].media == ()


async def test_too_large_file_gets_notice_and_no_agent_call(make_bot, zalo, agent, cdn):
    bot = make_bot(MEDIA_MAX_MB_PHOTO="1")
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/big.jpg"))
    assert agent.calls == []
    assert zalo.texts(OWNER) == [MEDIA_TOO_LARGE_REPLY.format(mb=1)]


async def test_download_failure_gets_notice(make_bot, zalo, agent, cdn):
    bot = make_bot()
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/gone.jpg"))
    assert agent.calls == [] and zalo.texts(OWNER) == [MEDIA_FAILED_REPLY]


async def test_media_input_off_keeps_old_behaviour(make_bot, zalo, agent, cdn):
    bot = make_bot(MEDIA_INPUT="false")
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg"))
    assert agent.calls == [] and zalo.texts(OWNER) == [NON_TEXT_REPLY]


async def test_sticker_is_still_rejected(make_bot, zalo, agent, cdn):
    bot = make_bot()
    msg = to_incoming("s1", OWNER, {"id": 1}, {"msgType": "chat.sticker", "ts": str(now_ms() + 1000)}, OWNER, False, "bot-self")
    await push(bot, msg)
    assert agent.calls == [] and zalo.texts(OWNER) == [NON_TEXT_REPLY]


async def test_user_media_rate_limit(make_bot, zalo, agent, cdn):
    bot = make_bot(USER_MEDIA_PER_HOUR="1", USER_RATE_PER_MIN="0", CHAT_RATE_PER_MIN="0")
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg"))
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/b.jpg"))
    assert len(agent.calls) == 1


# ---------- nhóm ----------


async def test_group_media_without_call_is_ignored(make_bot, zalo, agent, cdn):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg", chat_id=GROUP, from_id="u1", group=True))
    assert agent.calls == [] and zalo.sent == []
    assert not list((bot.media.dir_for(GROUP)).glob("*.jpg"))  # tin bị chặn thì không tải tệp


async def test_group_caption_with_trigger_passes(make_bot, agent, cdn):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await push(bot, media_msg("chat.photo", "https://cdn.zalo/a.jpg", caption="/bot ảnh gì đây", chat_id=GROUP,
                              from_id="u1", group=True))
    assert agent.calls[0][1][-1].text == "ảnh gì đây" and len(agent.calls[0][1][-1].media) == 1


async def test_group_voice_right_after_calling_bot_passes(make_bot, agent, cdn):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await push(bot, event("/bot nghe cái này nhé", from_id="u1"))
    assert len(agent.calls) == 1
    await push(bot, media_msg("chat.voice", "https://cdn.zalo/v.aac", chat_id=GROUP, from_id="u1", group=True))
    assert len(agent.calls) == 2 and agent.calls[1][1][-1].media[0].kind == "voice"


async def test_group_media_from_someone_else_after_call_is_ignored(make_bot, agent, cdn):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await push(bot, event("/bot nghe cái này nhé", from_id="u1"))
    await push(bot, media_msg("chat.voice", "https://cdn.zalo/v.aac", chat_id=GROUP, from_id="u2", group=True))
    assert len(agent.calls) == 1


# ---------- tim_web qua Bot ----------


class SearchingAgent:
    """FakeAgent có search(): gọi tool tim_web ngay trong reply, như model thật."""

    def __init__(self, fake):
        self.fake, self.queries, self.tokens = fake, [], 25

    def __getattr__(self, name):
        return getattr(self.fake, name)

    async def search(self, query):
        self.queries.append(query)
        return {"answer": "kết quả", "sources": []}, self.tokens

    async def reply(self, system, turns, ctx, **overrides):
        self.fake.search_result = await ctx.web_search("giá vàng") if ctx.web_search else None
        return await self.fake.reply(system, turns, ctx, **overrides)


async def test_web_search_counts_tokens_and_daily_limit(make_bot, agent):
    searching = SearchingAgent(agent)
    bot = make_bot(WEB_SEARCH_PER_DAY="2")
    bot.agent = searching
    used = bot.usage.used_today()
    for _ in range(3):
        await push(bot, event("hỏi", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    assert searching.queries == ["giá vàng", "giá vàng"]  # lượt thứ 3 vượt giới hạn ngày
    assert "hết lượt" in agent.search_result["error"]
    assert bot.web_searches.today() == 2
    assert bot.usage.used_today() - used >= 2 * 25  # token tìm web tính vào hạn mức ngày


async def test_web_search_disabled_gives_no_function(make_bot, agent):
    searching = SearchingAgent(agent)
    bot = make_bot(WEB_SEARCH="false")
    bot.agent = searching
    await push(bot, event("hỏi", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    assert agent.search_result is None and searching.queries == []
