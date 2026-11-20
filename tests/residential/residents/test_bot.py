from __future__ import annotations

from conftest import GROUP, OWNER, event

from pylos.residential.residents.pylos.message_handler import BUDGET_NOTICE, ERROR_REPLY, NON_TEXT_REPLY
from pylos.lobby.dispatch.clock.vietnam_time import now_ms


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


async def test_non_owner_commands_need_role_and_do_nothing(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    await send(bot, event("/mode all", from_id="stranger"))
    await send(bot, event("/deny", from_id="stranger"))
    assert bot.groups.get(GROUP).mode == "default"
    assert bot.groups.get(GROUP).allowed
    assert agent.calls == []
    assert all("cần quyền owner" in t for t in zalo.texts(GROUP)) and len(zalo.texts(GROUP)) == 2
    # Nhóm chưa được phép: bot im lặng như trước.
    zalo.sent.clear()
    await send(bot, event("/mode all", from_id="stranger", chat_id="g-khac"))
    assert zalo.sent == []


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
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, REPLY_SPLIT="off")  # test này chỉ kiểm làm sạch markdown
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
        from pylos.residential.residents.pylos import AgentReply

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
    from pylos.residential.residents.pylos import PromptBuilder
    from pylos.residential.residents.pylos.message_handler import Bot
    from pylos.gate.main_gate.zalo.personal_account import to_incoming

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
    assert not bot.groups.get(GROUP).leaders_all and "cần quyền owner" in zalo.texts(GROUP)[-1]
    await send(bot, event("/leader all", from_id=OWNER, chat_id=OWNER, chat_type="PRIVATE"))
    assert "trong nhóm" in zalo.texts(OWNER)[-1]


async def test_assign_allowed_all_still_opens_everyone(make_bot, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP, ASSIGN_ALLOWED="all")
    await send(bot, event("/bot giao lịch", from_id="ai-do"))
    assert agent.calls[-1][2].can_assign


def test_pick_people_prefers_real_tags_and_skips_bot():
    from pylos.gate.side_gate.owner_commands.owner_commands import _pick_people
    assert _pick_people("@an @bot", ("u-an", "bot-id"), {}, "bot-id") == (["u-an"], [])
    assert _pick_people("an, chi", (), {"u-an": "An", "u-an2": "An Nhiên", "u-chi": "Chi"}, "") == (["u-an", "u-chi"], [])


async def test_roles_help_and_commands(make_bot, zalo, agent):
    zalo.members = lambda chat_id: {"u-an": "Nguyễn An", "u-binh": "Trần Bình", "u-chi": "Lê Chi"}
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)

    await send(bot, event("/vaitro", from_id="u-an"))
    assert "basic-user" in zalo.texts(GROUP)[-1]
    await send(bot, event("/help", from_id="u-an"))
    assert "/id" in zalo.texts(GROUP)[-1] and "/mode" not in zalo.texts(GROUP)[-1] and "/add leader" not in zalo.texts(GROUP)[-1]
    await send(bot, event("/add leader @Chi", from_id="u-an"))
    assert "cần quyền leader" in zalo.texts(GROUP)[-1] and bot.groups.get(GROUP).leaders == []

    # Owner cho An làm leader; An cho Bình làm leader, nhưng không gỡ được ai.
    await send(bot, event("/add leader @An", from_id=OWNER))
    assert bot.groups.get(GROUP).leaders == ["u-an"] and bot.groups.get(GROUP).leader_added_by == {"u-an": OWNER}
    await send(bot, event("/vaitro", from_id="u-an"))
    assert "leader" in zalo.texts(GROUP)[-1] and "basic" not in zalo.texts(GROUP)[-1]
    await send(bot, event("/add leader Bình", from_id="u-an"))
    assert bot.groups.get(GROUP).leaders == ["u-an", "u-binh"] and bot.groups.get(GROUP).leader_added_by["u-binh"] == "u-an"
    await send(bot, event("/remove leader Bình", from_id="u-an"))
    assert "cần quyền owner" in zalo.texts(GROUP)[-1] and "u-binh" in bot.groups.get(GROUP).leaders
    await send(bot, event("/help", from_id="u-an"))
    assert "/add leader" in zalo.texts(GROUP)[-1] and "/remove leader" not in zalo.texts(GROUP)[-1]
    await send(bot, event("/remove leader Bình", from_id=OWNER))
    assert bot.groups.get(GROUP).leaders == ["u-an"]
    await send(bot, event("/add", from_id="u-an"))  # "/add" không kèm leader là lệnh của bot khác: im lặng
    n = len(zalo.sent)
    await send(bot, event("/add gì đó", from_id="u-an"))
    assert len(zalo.sent) == n

    # Đội: leader tạo, mọi người xem, basic không sửa được.
    await send(bot, event("/team thietke @An @Chi", from_id="u-an"))
    assert bot.groups.get(GROUP).teams["thietke"]["members"] == ["u-an", "u-chi"]
    await send(bot, event("/team", from_id="u-binh"))
    assert "thietke (2)" in zalo.texts(GROUP)[-1]
    await send(bot, event("/team thietke", from_id="u-binh"))
    assert "Nguyễn An, Lê Chi" in zalo.texts(GROUP)[-1]
    await send(bot, event("/team thietke bo @Chi", from_id="u-binh"))
    assert "cần quyền leader" in zalo.texts(GROUP)[-1]
    await send(bot, event("/team thietke bo @Chi", from_id="u-an"))
    assert bot.groups.get(GROUP).teams["thietke"]["members"] == ["u-an"]
    await send(bot, event("/team xoa thietke", from_id="u-an"))
    assert bot.groups.get(GROUP).teams == {}


async def test_tool_context_carries_role_and_teams(make_bot, zalo, agent):
    bot = make_bot(ALLOWED_CHAT_IDS=GROUP)
    bot.groups.set_team(GROUP, "Thiết kế", add=["u-an"])
    bot.groups.set_leaders(GROUP, add=["lead"])
    for sender, role in (("user-1", "basic"), ("lead", "leader"), (OWNER, "owner")):
        await send(bot, event("/bot giao lịch", from_id=sender))
        ctx = agent.calls[-1][2]
        assert (ctx.role, ctx.can_assign, ctx.teams) == (role, role != "basic", {"thiet ke": ["u-an"]}), sender


def shift_bot(make_bot, **env):
    return make_bot(MODEL_SHIFT="true", GEMINI_MODEL="gemini-3.1-flash-lite", THINKING_LEVEL="low", **env)


PRIVATE = dict(chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE")


async def test_chat_holds_model_until_filter_switches(make_bot, agent):
    bot = shift_bot(make_bot)
    answers = []
    for profile in ("coding", "", "coding", "reflective", "routine"):  # "" = bộ lọc không phân loại được
        agent.filter_profile = profile
        await send(bot, event("hỏi gì đó", **PRIVATE))
        answers.append(agent.overrides[-1])
    coding = {"model": "gemini-4-hydrogen", "thinking_level": "medium",
              "fallbacks": ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite")}
    assert answers == [
        coding,
        coding,  # phân loại lỗi: giữ nguyên hồ sơ đang giữ, không nhảy về model chính
        coding,
        {"model": "gemini-3.1-flash-lite", "thinking_level": "medium", "fallbacks": ("gemini-3.5-flash-lite",)},
        {"model": "gemini-3.1-flash-lite", "thinking_level": "low", "fallbacks": ("gemini-3.5-flash-lite",)},
    ]
    assert bot.active_models.get(OWNER)["profile"] == "routine"


async def test_chats_hold_models_separately_and_filter_sees_held_profile(make_bot, agent):
    bot = shift_bot(make_bot)
    agent.filter_profile = "coding"
    await send(bot, event("sửa hàm", **PRIVATE))
    agent.filter_profile = ""
    other = dict(chat_id="u2", from_id="u2", chat_type="PRIVATE")
    await bot.handle_payload(event("chào", **other))
    await bot.drain()
    assert bot.active_models.get(OWNER)["profile"] == "coding" and bot.active_models.get("u2") == {}
    assert "Hồ sơ đang giữ của cuộc trò chuyện: chưa có" in agent.classify_calls[-1]


async def test_every_switch_is_logged_with_only_what_changed(make_bot, agent, caplog):
    import logging

    caplog.set_level(logging.INFO)
    bot = shift_bot(make_bot)
    agent.filter_profile = "reflective"
    await send(bot, event("nghĩ sao về cuộc sống", **PRIVATE))
    assert "Chuyển model ở chat" in caplog.text
    assert "hồ sơ chưa có -> reflective" in caplog.text and "thinking low -> medium" in caplog.text
    assert "model gemini-3.1-flash-lite ->" not in caplog.text  # model không đổi nên không in

    caplog.clear()
    agent.filter_profile = "coding"
    await send(bot, event("sửa hàm này", **PRIVATE))
    assert "hồ sơ reflective -> coding" in caplog.text
    assert "model gemini-3.1-flash-lite -> gemini-4-hydrogen" in caplog.text

    caplog.clear()
    await send(bot, event("tiếp đi", **PRIVATE))  # cùng hồ sơ: không có dòng chuyển
    assert "Chuyển model ở chat" not in caplog.text


async def test_model_command_fixed_stops_switching_and_flexible_resumes(make_bot, zalo, agent):
    bot = shift_bot(make_bot)
    agent.filter_profile = "coding"
    await send(bot, event("sửa hàm", **PRIVATE))
    classify_before = len(agent.classify_calls)

    await send(bot, event("/model fixed", **PRIVATE))
    assert "fixed" in zalo.texts(OWNER)[-1] and "gemini-4-hydrogen" in zalo.texts(OWNER)[-1]
    agent.filter_profile = "routine"
    await send(bot, event("mai họp mấy giờ", **PRIVATE))
    assert agent.overrides[-1]["model"] == "gemini-4-hydrogen"  # giữ nguyên model đang dùng
    assert len(agent.classify_calls) == classify_before  # chat khóa: không tốn lượt phân loại

    await send(bot, event("/model flexible", **PRIVATE))
    await send(bot, event("mai họp mấy giờ", **PRIVATE))
    assert agent.overrides[-1]["thinking_level"] == "low" and agent.overrides[-1]["model"] == "gemini-3.1-flash-lite"
    await send(bot, event("/model", **PRIVATE))
    assert "flexible" in zalo.texts(OWNER)[-1]


async def test_model_command_is_owner_only_and_validates(make_bot, zalo, agent):
    bot = shift_bot(make_bot)
    await send(bot, event("/allow", from_id=OWNER))
    await send(bot, event("/model fixed", from_id="user-1"))
    assert "quyền" in zalo.texts(GROUP)[-1] and bot.groups.get(GROUP).model_mode == "flexible"
    await send(bot, event("/model lung tung", from_id=OWNER))
    assert "flexible" in zalo.texts(GROUP)[-1] and bot.groups.get(GROUP).model_mode == "flexible"


async def test_model_shift_off_ignores_profiles_and_records_model(make_bot, agent):
    bot = make_bot(MODEL_SHIFT="false", GEMINI_MODEL="gemini-3.1-flash-lite")
    agent.filter_profile = "coding"
    await send(bot, event("sửa hàm", **PRIVATE))
    assert agent.overrides == [{}] and bot.active_models.get(OWNER) == {}


async def test_status_records_last_model_and_flags_fallback(make_bot, agent):
    from pylos.gate.side_gate.vps import bot_process

    bot = shift_bot(make_bot)
    agent.filter_profile = "coding"
    await send(bot, event("sửa hàm", **PRIVATE))
    info = bot_process.status_info(bot.settings)
    assert info["last_model"] == "gemini-4-hydrogen" and info["last_profile"] == "coding"
    assert info["last_chat"] == OWNER and info["fallback_models"] == ["gemini-3.5-flash-lite"]


def test_apply_settings_passes_new_keys_to_the_agents_model_calls(make_bot, agent, tmp_path):
    from conftest import make_settings

    class Calls:
        updated = None

        def update(self, settings):
            self.updated = settings

    agent.model_calls = Calls()
    bot = make_bot()
    new = make_settings(tmp_path, CLOUDFLARE_API_TOKEN="cf-new", CLOUDFLARE_ACCOUNT_ID="acc")
    bot.apply_settings(new)
    assert agent.model_calls.updated is new and new.cloudflare_api_token == "cf-new"


# ---------- gửi ảnh bot tạo (tool tao_anh -> ToolContext.outbox) ----------

class ImageAgent:
    """Giống FakeAgent nhưng như thể model vừa gọi tao_anh: đưa ảnh vào ctx.outbox rồi trả lời."""

    def __init__(self, paths, reply="đây nhé"):
        self.paths, self.reply_text = paths, reply

    async def reply(self, system, turns, ctx, **overrides):
        from pylos.lobby.office.agent_tools import OutgoingImage
        from pylos.residential.residents.pylos import AgentReply

        ctx.outbox.extend(OutgoingImage(p, "chú thích") for p in self.paths)
        return AgentReply(self.reply_text, 5)

    async def classify(self, *a, **k):  # bộ lọc AI không dùng trong các test này
        raise AssertionError("không được gọi")


class ImageZalo:
    def __init__(self, fail=None):
        self.events, self.fail = [], fail

    async def send_message(self, chat_id, text):
        self.events.append(("text", text))
        return {}

    async def send_image(self, chat_id, path, caption=""):
        if self.fail:
            raise self.fail
        self.events.append(("image", path.name, caption))
        return {}

    async def send_chat_action(self, chat_id, action="typing"):
        return None


def image_bot(tmp_path, zalo, agent):
    from conftest import make_settings
    from pylos.residential.residents.pylos import PromptBuilder
    from pylos.residential.residents.pylos.message_handler import Bot

    settings = make_settings(tmp_path, ALLOW_ALL_CHATS="true")
    return Bot(settings, zalo, agent, PromptBuilder(settings.workspace_dir), retry_delay=0)


def pictures(tmp_path, count=2):
    paths = []
    for i in range(count):
        path = tmp_path / f"gen_{i}.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\n")
        paths.append(path)
    return paths


async def test_generated_images_are_sent_before_the_text_and_counted(tmp_path):
    zalo = ImageZalo()
    bot = image_bot(tmp_path, zalo, ImageAgent(pictures(tmp_path)))
    await send(bot, event("vẽ con mèo", **PRIVATE))
    assert zalo.events == [("image", "gen_0.png", "chú thích"), ("image", "gen_1.png", "chú thích"), ("text", "đây nhé")]
    assert bot.stats.today()["images"] == 2
    assert "(đã gửi 2 ảnh)" in bot.history.recent(OWNER, 5)[-1]["text"]


async def test_image_send_failure_is_retried_dead_lettered_and_the_user_is_told(tmp_path):
    from pylos.gate.main_gate.zalo import ZaloError

    zalo = ImageZalo(fail=ZaloError("temporary", 500))
    bot = image_bot(tmp_path, zalo, ImageAgent(pictures(tmp_path)))
    await send(bot, event("vẽ con mèo", **PRIVATE))
    texts = [e[1] for e in zalo.events if e[0] == "text"]
    assert texts == [bot.IMAGE_FAILED, "đây nhé"] and not [e for e in zalo.events if e[0] == "image"]
    assert "(ảnh) gen_0.png" in (tmp_path / "data" / "failed_replies.txt").read_text(encoding="utf-8")
    assert "(đã gửi" not in bot.history.recent(OWNER, 5)[-1]["text"]


async def test_zalo_without_image_support_gets_a_clear_notice_without_retries(tmp_path):
    from pylos.gate.main_gate.zalo import ZaloUnsupported

    zalo = ImageZalo(fail=ZaloUnsupported("Zalo Bot"))
    bot = image_bot(tmp_path, zalo, ImageAgent(pictures(tmp_path, 1)))
    await send(bot, event("vẽ con mèo", **PRIVATE))
    assert [e[1] for e in zalo.events if e[0] == "text"] == [bot.IMAGE_UNSUPPORTED, "đây nhé"]

    class NoImages(ImageZalo):
        send_image = None  # client cũ không có send_image

    legacy = NoImages()
    bot2 = image_bot(tmp_path / "b", legacy, ImageAgent(pictures(tmp_path, 1)))
    await send(bot2, event("vẽ", **PRIVATE))
    assert bot2.IMAGE_UNSUPPORTED in [e[1] for e in legacy.events if e[0] == "text"]


async def test_replies_without_images_are_unchanged(tmp_path):
    zalo = ImageZalo()
    bot = image_bot(tmp_path, zalo, ImageAgent([]))
    await send(bot, event("chào", **PRIVATE))
    assert zalo.events == [("text", "đây nhé")] and bot.stats.today()["images"] == 0
