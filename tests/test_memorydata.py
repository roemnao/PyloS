from __future__ import annotations

import json

from conftest import GROUP, event

from bot.agent import ToolContext
from bot.agent.tools.memorydata import _read
from bot.storage import MemoryDataStore


async def send(bot, payload) -> None:
    await bot.handle_payload(payload)
    await bot.drain()


def lines(bot, chat_id=GROUP):
    return [json.loads(x) for x in bot.memory.path(chat_id).read_text(encoding="utf-8").splitlines()]


async def test_every_message_logged_but_only_passed_ones_reach_session(make_bot, agent, zalo):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("tối nay đi ăn lẩu nhé", name="Bình"))  # AI: không nhờ bot
    await send(bot, event("haha", name="An"))                      # quy tắc: cảm thán
    agent.filter_reply = True
    await send(bot, event("tóm tắt giúp mình kế hoạch tối nay"))  # AI: nhờ bot
    await send(bot, event("/bot cảm ơn"))                          # quy tắc: /bot

    records = lines(bot)
    assert [(r["role"], r.get("text")) for r in records] == [
        ("user", "tối nay đi ăn lẩu nhé"), ("user", "haha"),
        ("user", "tóm tắt giúp mình kế hoạch tối nay"), ("model", "trả lời"),
        ("user", "/bot cảm ơn"), ("model", "trả lời"),
    ]
    assert [r["filter"]["stage"] for r in records if r["role"] == "user"] == ["ai", "rule", "ai", "rule"]
    assert [r["filter"]["passed"] for r in records if r["role"] == "user"] == [False, False, True, True]

    session = bot.history.recent(GROUP, 50)
    assert [(r["role"], r["text"]) for r in session] == [
        ("user", "tóm tắt giúp mình kế hoạch tối nay"), ("model", "trả lời"), ("user", "cảm ơn"), ("model", "trả lời"),
    ]
    assert bot.stats.today()["filter_pass"] == 2 and bot.stats.today()["filter_block"] == 2
    assert bot.usage.used_today() >= 10  # token của bộ lọc AI cũng được tính


async def test_not_allowed_chat_is_not_logged(make_bot):
    bot = make_bot()
    await send(bot, event("bí mật", chat_id="lạ"))
    assert not bot.memory.path("lạ").exists()


def test_store_trims_when_over_keep(tmp_path):
    store = MemoryDataStore(tmp_path, keep=3)
    for i in range(7):
        store.add_model("c", f"tin {i}")
    assert [r["text"] for r in store.recent("c", 10)] == ["tin 4", "tin 5", "tin 6"]


def test_tool_reads_only_own_chat_and_filters_keyword(tmp_path):
    store = MemoryDataStore(tmp_path / "memorydata")
    decision = {"passed": False, "stage": "ai", "reason": ""}
    store.add_user("g1", msg_id="1", uid="u", name="Bình", text="7h tối hẹn ở quán Lẩu", is_text=True, decision=decision)
    store.add_user("g1", msg_id="2", uid="u", name="An", text="ok", is_text=True, decision=decision)
    store.add_user("g2", msg_id="3", uid="u", name="Lan", text="nhóm khác", is_text=True, decision=decision)

    res = _read({}, ToolContext("g1", "u", "An", False, tmp_path))
    assert res["count"] == 2 and all("nhóm khác" not in m for m in res["messages"])
    res = _read({"tu_khoa": "lau"}, ToolContext("g1", "u", "An", False, tmp_path))
    assert res["count"] == 1 and "Bình: 7h tối hẹn ở quán Lẩu" in res["messages"][0]
    assert "error" in _read({}, ToolContext("g1", "u", "An", False, None))
