from __future__ import annotations

from conftest import GROUP, OWNER, event

from bot.core.message_handler import BUDGET_NOTICE, ERROR_REPLY, NON_TEXT_REPLY
from bot.core.vietnam_time import now_ms


async def send(bot, payload) -> None:
    await bot.handle_payload(payload)
    await bot.drain()


async def test_group_not_allowed_is_ignored(make_bot, zalo, agent):
    bot = make_bot()
    await send(bot, event("/bot xin chào"))
    assert zalo.sent == [] and agent.calls == []


async def test_owner_allow_then_default_mode_only_answers_trigger(make_bot, zalo, agent):
    bot = make_bot()
    await send(bot, event("/allow", from_id=OWNER))
    assert "Đã cho phép" in zalo.texts(GROUP)[-1]
    assert bot.groups.get(GROUP).mode == "default"

    await send(bot, event("chuyện phiếm không gọi ai"))
    assert len(agent.calls) == 0

    await send(bot, event("/bot thủ đô Úc là gì?", name="Bình"))
    assert len(agent.calls) == 1
    _, turns, ctx = agent.calls[0]
    assert turns[-1].text == "thủ đô Úc là gì?"
    assert turns[-1].name == "Bình"
    assert ctx.chat_id == GROUP and not ctx.is_owner
    assert zalo.texts(GROUP)[-1] == "trả lời"


async def test_trigger_is_case_insensitive_and_needs_word_boundary(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/BOT: hello"))
    await send(bot, event("/botany is a science"))
    assert [c[1][-1].text for c in agent.calls] == ["hello"]


async def test_bare_trigger_asks_what_to_do(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot"))
    assert agent.calls == []
    assert zalo.texts(GROUP) == ["Bạn cần mình giúp gì?"]


async def test_mode_all_lets_ai_filter_decide(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/mode all", from_id=OWNER))
    assert bot.groups.get(GROUP).mode == "all"
    await send(bot, event("tin thường AI bảo không"))  # FakeAgent.filter_reply mặc định False
    agent.filter_reply = True
    await send(bot, event("tin thường 1"))
    await send(bot, event("/bot tin có gọi"))
    assert [c[1][-1].text for c in agent.calls] == ["tin thường 1", "tin có gọi"]
    assert len(agent.classify_calls) == 2  # tin /bot qua bằng quy tắc, không hỏi AI


async def test_default_mode_never_asks_ai(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    agent.filter_reply = True
    await send(bot, event("mai mấy giờ họp nhỉ"))
    assert agent.calls == [] and agent.classify_calls == []


async def test_reply_name_prefix_is_removed(make_bot, agent, zalo):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    agent.reply_text = "An: chào bạn nhé"
    await send(bot, event("/bot chào", name="An"))
    assert zalo.texts(GROUP)[-1] == "chào bạn nhé"
    assert bot.history.recent(GROUP, 5)[-1]["text"] == "chào bạn nhé"


async def test_non_owner_commands_are_ignored(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/mode all", from_id="stranger"))
    await send(bot, event("/deny", from_id="stranger"))
    assert bot.groups.get(GROUP).mode == "default"
    assert bot.groups.get(GROUP).allowed
    assert zalo.sent == [] and agent.calls == []


async def test_id_command_open_only_while_owner_unset(make_bot, zalo):
    bot = make_bot(OWNER_ZALO_ID="")
    await send(bot, event("/id", from_id="someone"))
    assert "user_id của bạn: someone" in zalo.texts(GROUP)[-1]

    zalo.sent.clear()
    bot2 = make_bot(DATA_DIR="data2")
    await send(bot2, event("/id", from_id="someone"))
    assert zalo.sent == []


async def test_private_chat_without_owner_gets_setup_hint_once(make_bot, zalo, agent):
    bot = make_bot(OWNER_ZALO_ID="")
    for _ in range(2):
        await send(bot, event("chào", chat_id="u7", from_id="u7", chat_type="PRIVATE"))
    assert len(zalo.texts("u7")) == 1 and "OWNER_ZALO_ID=u7" in zalo.texts("u7")[0]
    assert agent.calls == []
    await send(bot, event("chào", chat_id=GROUP, from_id="u7"))  # nhóm: vẫn im lặng
    assert zalo.texts(GROUP) == []


async def test_allow_all_chats_answers_everywhere_but_deny_still_blocks(make_bot, zalo, agent):
    bot = make_bot(ALLOW_ALL_CHATS="true")
    await send(bot, event("/bot nhóm lạ chưa /allow", chat_id="new-group"))
    assert len(agent.calls) == 1  # không cần /allow

    await send(bot, event("chào", chat_id="u9", from_id="u9", chat_type="PRIVATE"))
    assert len(agent.calls) == 2  # chat riêng của người lạ cũng được trả lời

    await send(bot, event("/deny", chat_id="new-group", from_id=OWNER))
    await send(bot, event("/bot còn đó không", chat_id="new-group"))
    assert len(agent.calls) == 2  # /deny vẫn chặn riêng được

    await send(bot, event("/allow", chat_id="new-group", from_id=OWNER))
    await send(bot, event("/bot lại được", chat_id="new-group"))
    assert len(agent.calls) == 3

    await send(bot, event("tin thường không gọi ai", chat_id="other-group"))
    assert len(agent.calls) == 3  # chế độ default vẫn áp dụng


async def test_allow_all_off_by_default(make_bot, agent):
    bot = make_bot()
    await send(bot, event("/bot hi", chat_id="new-group"))
    assert agent.calls == []


async def test_deny_stops_replies(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/deny", from_id=OWNER))
    await send(bot, event("/bot còn đó không?"))
    assert agent.calls == []


async def test_state_survives_restart(make_bot):
    bot = make_bot()
    await send(bot, event("/allow", from_id=OWNER))
    await send(bot, event("/mode all", from_id=OWNER))
    restarted = make_bot()
    state = restarted.groups.get(GROUP)
    assert state.allowed and state.mode == "all"


async def test_message_from_before_start_is_skipped(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot tin cũ", date=bot.started_at_ms - 60_000))
    assert agent.calls == []


async def test_seconds_timestamp_is_understood(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot tin cũ", date=(bot.started_at_ms - 60_000) // 1000))
    assert agent.calls == []


async def test_duplicate_message_is_answered_once(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    payload = event("/bot một lần thôi", message_id="dup-1")
    await send(bot, payload)
    await send(bot, payload)
    assert len(agent.calls) == 1


async def test_dedupe_survives_restart(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    payload = event("/bot một lần thôi", message_id="dup-2")
    await send(bot, payload)
    restarted = make_bot(ALLOWED_CHAT_IDS=GROUP)
    restarted.started_at_ms = 0
    await send(restarted, payload)
    assert len(agent.calls) == 1


async def test_messages_from_bots_are_ignored(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot hi", is_bot=True))
    assert agent.calls == []


async def test_private_chat_with_owner_always_answers(make_bot, agent):
    bot = make_bot()
    await send(bot, event("chào", chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE"))
    assert len(agent.calls) == 1


async def test_private_chat_with_stranger_needs_allow(make_bot, agent):
    bot = make_bot()
    await send(bot, event("chào", chat_id="u9", from_id="u9", chat_type="PRIVATE"))
    assert agent.calls == []


async def test_non_text_in_group_is_silent_but_private_gets_notice(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/mode all", from_id=OWNER))
    zalo.sent.clear()
    await send(bot, event(None, event_name="message.sticker.received"))
    assert zalo.sent == []
    await send(bot, event(None, chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE", event_name="message.image.received"))
    assert zalo.texts(OWNER) == [NON_TEXT_REPLY]
    assert agent.calls == []


async def test_long_reply_is_split_under_limit(make_bot, zalo, agent):
    agent.reply_text = ("Câu dài. " * 500).strip()
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot viết dài"))
    chunks = zalo.texts(GROUP)
    assert len(chunks) >= 2
    assert all(len(c) <= 2000 for c in chunks)


async def test_markdown_is_stripped(make_bot, zalo, agent):
    agent.reply_text = "## Tiêu đề\n**đậm** và\n- ý một"
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot định dạng"))
    assert zalo.texts(GROUP)[-1] == "Tiêu đề\nđậm và\n• ý một"


async def test_history_is_kept_per_chat_and_passed_to_agent(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=f"{GROUP},group-2")
    await send(bot, event("/bot câu 1"))
    await send(bot, event("/bot câu ở nhóm khác", chat_id="group-2"))
    await send(bot, event("/bot câu 2"))
    _, turns, _ = agent.calls[-1]
    assert [(t.role, t.text) for t in turns] == [
        ("user", "câu 1"), ("model", "trả lời"), ("user", "câu 2"),
    ]


async def test_reset_clears_history(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot câu 1"))
    await send(bot, event("/reset", from_id=OWNER))
    await send(bot, event("/bot câu 2"))
    assert [t.text for t in agent.calls[-1][1]] == ["câu 2"]


async def test_agent_error_sends_apology(make_bot, zalo, agent):
    async def boom(*args, **kwargs):
        raise RuntimeError("gemini down")

    agent.reply = boom
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/bot hi"))
    assert zalo.texts(GROUP) == [ERROR_REPLY]


async def test_send_is_retried_then_dead_lettered(make_bot, zalo, tmp_path):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    zalo.fail_times = 2
    await send(bot, event("/bot hi"))
    assert zalo.texts(GROUP) == ["trả lời"]

    zalo.fail_times = 99
    await send(bot, event("/bot hi again"))
    failed = (tmp_path / "data" / "failed_replies.txt").read_text(encoding="utf-8")
    assert "trả lời" in failed


async def test_rate_limit_per_user(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, USER_RATE_PER_MIN="2")
    for i in range(4):
        await send(bot, event(f"/bot {i}"))
    assert len(agent.calls) == 2
    await send(bot, event("/bot từ người khác", from_id="user-2"))
    assert len(agent.calls) == 3


async def test_budget_exceeded_turns_all_into_default_and_notifies_once(make_bot, zalo, agent):
    agent.tokens = 60
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, DAILY_TOKEN_BUDGET="100")
    await send(bot, event("/mode all", from_id=OWNER))
    agent.filter_reply = True
    await send(bot, event("tin 1"))
    await send(bot, event("tin 2"))  # vượt hạn mức sau tin này
    assert zalo.texts(GROUP).count(BUDGET_NOTICE) == 1

    await send(bot, event("tin 3 không gọi ai"))
    assert len(agent.calls) == 2
    await send(bot, event("/bot vẫn gọi được"))
    assert len(agent.calls) == 3
    assert zalo.texts(GROUP).count(BUDGET_NOTICE) == 1


async def test_messages_in_same_chat_are_processed_in_order(make_bot, agent):
    import asyncio

    order = []

    async def slow_reply(system, turns, ctx):
        text = turns[-1].text
        await asyncio.sleep(0.02 if text == "1" else 0)
        order.append(text)
        from bot.agent import AgentReply

        return AgentReply("ok", 1)

    agent.reply = slow_reply
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await bot.handle_payload(event("/bot 1"))
    await bot.handle_payload(event("/bot 2"))
    await bot.drain()
    assert order == ["1", "2"]


async def test_payload_as_list_and_unwrapped(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    a = event("/bot a")["result"]
    b = event("/bot b")["result"]
    await send(bot, [a, b])
    await send(bot, {"ok": True, "result": [event("/bot c")["result"]]})
    assert [c[1][-1].text for c in agent.calls] == ["a", "b", "c"]


async def test_garbage_payload_is_ignored(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    for payload in (None, {}, [], "x", {"result": {"message": "not a dict"}}, {"message": {"chat": {}}}):
        await send(bot, payload)
    assert agent.calls == []


def test_now_ms_is_milliseconds():
    assert now_ms() > 1_600_000_000_000


# ---------- gọi bot bằng tên / @tag, ngữ cảnh nhóm ----------

async def test_mentioning_bot_name_answers_without_trigger(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, BOT_NAMES="bot,Trợ lý")
    await send(bot, event("Bot ơi mai trời có mưa không?"))
    await send(bot, event("hỏi tro ly giúp mình với"))  # không dấu vẫn nhận
    await send(bot, event("robot hút bụi nào tốt?"))  # "bot" nằm trong từ khác: không gọi
    assert [c[1][-1].text for c in agent.calls] == ["Bot ơi mai trời có mưa không?", "hỏi tro ly giúp mình với"]


async def test_empty_bot_names_disables_name_calls(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, BOT_NAMES="")
    await send(bot, event("bot ơi"))
    assert agent.calls == []


async def test_tagging_personal_account_answers_and_strips_tag(tmp_path, agent):
    from bot.agent import PromptBuilder
    from bot.core.message_handler import Bot
    from bot.zalo.personal_account import to_incoming

    from conftest import FakeZalo, make_settings

    class PersonalFake(FakeZalo):
        self_id, self_name = "me-1", "Mèo Ú"

    settings = make_settings(tmp_path, ALLOWED_CHAT_IDS=GROUP, BOT_NAMES="")
    bot = Bot(settings, PersonalFake(), agent, PromptBuilder(settings.workspace_dir), retry_delay=0)
    obj = {"dName": "An", "ts": str(now_ms() + 1000), "mentions": [{"uid": "me-1", "pos": 0, "len": 6}]}
    await bot.handle_message(to_incoming("m1", "u1", "@Mèo Ú tóm tắt giúp", obj, GROUP, True, "me-1"))
    # Tên acc Zalo của bot cũng được tính là tên gọi, kể cả khi không @tag.
    await bot.handle_message(to_incoming("m2", "u1", "meo u nghĩ sao?", {"ts": str(now_ms() + 1000)}, GROUP, True, "me-1"))
    await bot.drain()
    assert [c[1][-1].text for c in agent.calls] == ["tóm tắt giúp", "meo u nghĩ sao?"]


async def test_leader_lets_chosen_people_assign_in_that_group_only(make_bot, zalo, agent):
    zalo.members = lambda chat_id: {"u-an": "Nguyễn An", "u-binh": "Trần Bình", "u-chi": "Lê Chi"}
    bot = make_bot(ALLOWED_CHAT_IDS=f"{GROUP},group-2")
    await send(bot, event("/leader", from_id=OWNER))
    assert "chưa có leader" in zalo.texts(GROUP)[-1]

    await send(bot, event("/leader @An @Bình @Không Ai", from_id=OWNER))
    assert "Nguyễn An, Trần Bình" in zalo.texts(GROUP)[-1] and "Không tìm thấy: không ai" in zalo.texts(GROUP)[-1]
    assert bot.groups.get(GROUP).leaders == ["u-an", "u-binh"]

    async def can_assign(from_id, chat_id=GROUP):
        await send(bot, event("/bot giao lịch", from_id=from_id, chat_id=chat_id))
        return agent.calls[-1][2].can_assign

    assert await can_assign("u-an") and await can_assign("u-binh")
    assert not await can_assign("u-chi")
    assert not await can_assign("u-an", chat_id="group-2")  # leader chỉ trong nhóm đã đặt
    assert await can_assign(OWNER)

    await send(bot, event("/leader bo @Bình", from_id=OWNER))
    assert bot.groups.get(GROUP).leaders == ["u-an"]
    await send(bot, event("/leader 123456789", from_id=OWNER))  # Zalo ID gõ thẳng
    assert bot.groups.get(GROUP).leaders == ["u-an", "123456789"]
    await send(bot, event("/leader", from_id=OWNER))
    assert "Nguyễn An, 123456789" in zalo.texts(GROUP)[-1]


async def test_leader_all_and_off(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/leader all", from_id=OWNER))
    await send(bot, event("/bot giao lịch", from_id="ai-cung-duoc"))
    assert agent.calls[-1][2].can_assign
    await send(bot, event("/leader off", from_id=OWNER))
    await send(bot, event("/bot giao lịch", from_id="ai-cung-duoc"))
    assert not agent.calls[-1][2].can_assign


async def test_leader_only_owner_and_only_in_groups(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/leader all", from_id="stranger"))
    assert not bot.groups.get(GROUP).leaders_all and zalo.sent == []
    await send(bot, event("/leader all", from_id=OWNER, chat_id=OWNER, chat_type="PRIVATE"))
    assert "trong nhóm" in zalo.texts(OWNER)[-1]


async def test_assign_allowed_all_still_opens_everyone(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, ASSIGN_ALLOWED="all")
    await send(bot, event("/bot giao lịch", from_id="ai-do"))
    assert agent.calls[-1][2].can_assign


def test_pick_people_prefers_real_tags_and_skips_bot():
    from bot.core.owner_commands import _pick_people
    assert _pick_people("@an @bot", ("u-an", "bot-id"), {}, "bot-id") == (["u-an"], [])
    assert _pick_people("an, chi", (), {"u-an": "An", "u-an2": "An Nhiên", "u-chi": "Chi"}, "") == (["u-an", "u-chi"], [])
