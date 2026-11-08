"""Câu trả lời nhiều dòng đi thành nhiều tin."""

from __future__ import annotations

import asyncio

from conftest import GROUP, event

from pylos.gate.main_gate.zalo import ZaloError


async def send(bot, payload) -> None:
    await bot.handle_payload(payload)
    await bot.drain()


async def test_multiline_reply_goes_as_separate_messages(make_bot, zalo, agent):
    agent.reply_text = "A\nB\nC"
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot hỏi"))
    assert zalo.texts(GROUP) == ["A", "B", "C"]
    memory = [r["text"] for r in bot.memory.recent(GROUP, 10) if r.get("role") == "model"]
    session = [r["text"] for r in bot.history.recent(GROUP, 10) if r.get("role") == "model"]
    assert memory == ["A\nB\nC"] and session == ["A\nB\nC"]  # lưu một bản đầy đủ


async def test_reply_split_off_sends_one_message(make_bot, zalo, agent):
    agent.reply_text = "A\nB\nC"
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, REPLY_SPLIT="off")
    await send(bot, event("/bot hỏi"))
    assert zalo.texts(GROUP) == ["A\nB\nC"]


async def test_failed_part_stops_and_keeps_the_rest(make_bot, zalo, agent, tmp_path):
    agent.reply_text = "A\nB\nC"
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    real = zalo.send_message

    async def flaky(chat_id, text):
        if text == "B":
            raise ZaloError("down", 500)
        return await real(chat_id, text)

    zalo.send_message = flaky
    await send(bot, event("/bot hỏi"))
    assert zalo.texts(GROUP) == ["A"]
    failed = (tmp_path / "data" / "failed_replies.txt").read_text(encoding="utf-8")
    assert "B" in failed and "C" in failed


async def test_two_sends_to_one_chat_do_not_interleave(make_bot, zalo):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, REPLY_PART_DELAY_MS="5")
    await asyncio.gather(bot._send(GROUP, "1\n2\n3"), bot._send(GROUP, "a\nb\nc"))
    assert zalo.texts(GROUP) in (["1", "2", "3", "a", "b", "c"], ["a", "b", "c", "1", "2", "3"])
