from __future__ import annotations

import pytest

from pylos.gate.fence.speech_limit.message_filter import MessageFilter, is_chatter
from pylos.gate.main_gate.zalo.personal_account import to_incoming
from pylos.lobby.dispatch.clock.vietnam_time import now_ms

from conftest import FakeAgent, make_settings


def msg(text, *, group=True, mentions=None, is_text=True):
    obj = {"dName": "An", "ts": str(now_ms())}
    if mentions:
        obj["mentions"] = [{"uid": m} for m in mentions]
    content = text if is_text else {"href": "sticker"}
    return to_incoming(f"m{now_ms()}", "u1", content, obj, "g1" if group else "u1", group, "me-1")


@pytest.fixture
def agent():
    return FakeAgent()


@pytest.fixture
def make_filter(tmp_path, agent):
    def factory(identity=("", ""), **env):
        return MessageFilter(make_settings(tmp_path, **env), agent, lambda: identity)
    return factory


async def decide(f, m, mode="default", over_budget=False, recent=()):
    return await f.decide(m, mode=mode, over_budget=over_budget, recent=list(recent))


async def test_private_always_passes_without_ai(make_filter, agent):
    d = await decide(make_filter(), msg("ok", group=False))
    assert (d.passed, d.stage, d.prompt) == (True, "private", "ok")
    assert agent.classify_calls == []


async def test_rules_pass_trigger_tag_and_name_without_ai(make_filter, agent):
    f = make_filter(identity=("me-1", "Mèo Ú"))
    assert (await decide(f, msg("/bot thời tiết?"))).prompt == "thời tiết?"
    tagged = await decide(f, msg("@Mèo Ú tóm tắt", mentions=["me-1"]))
    assert (tagged.passed, tagged.stage, tagged.prompt) == (True, "rule", "tóm tắt")
    assert (await decide(f, msg("bot ơi giúp với"))).stage == "rule"
    assert agent.classify_calls == []


async def test_chatter_and_non_text_blocked_without_ai(make_filter, agent):
    f = make_filter()
    for text in ("haha", "Okeee", "ừ", "😂😂", "hihi!!"):
        d = await decide(f, msg(text))
        assert (d.passed, d.stage) == (False, "rule"), text
    assert not (await decide(f, msg(None, is_text=False))).passed
    assert agent.classify_calls == []
    assert not is_chatter("mai mấy giờ họp?")


async def test_other_messages_ask_ai_with_recent_context(make_filter, agent):
    f = make_filter(FILTER_CONTEXT_LINES="2")
    recent = [{"role": "user", "name": "Bình", "text": "cũ lắm"}, {"role": "user", "name": "Bình", "text": "thủ đô Úc?"},
              {"role": "model", "text": "Canberra"}]
    agent.filter_reply = True
    d = await decide(f, msg("còn New Zealand thì sao?"), mode="all", recent=recent)
    assert (d.passed, d.stage, d.prompt, d.tokens) == (True, "ai", "còn New Zealand thì sao?", 5)
    sent = agent.classify_calls[-1]
    assert "[Trợ lý] Canberra" in sent and "cũ lắm" not in sent  # chỉ 2 dòng gần nhất
    agent.filter_reply = False
    assert (await decide(f, msg("tối nay ăn gì mọi người"), mode="all")).passed is False


async def test_default_mode_only_rules_never_ai(make_filter, agent):
    agent.filter_reply = True
    d = await decide(make_filter(), msg("còn New Zealand thì sao?"), mode="default")
    assert (d.passed, d.stage) == (False, "mode_default")
    assert agent.classify_calls == []


async def test_tagging_other_people_is_blocked_without_ai(make_filter, agent):
    f = make_filter(identity=("me-1", "Roemnao"))
    agent.filter_reply = True
    for text, mentions in (("@Thái Toàn", ["u9"]), ("@All nhiệm vụ tối ưu code", ["-1"])):
        d = await decide(f, msg(text, mentions=mentions), mode="all")
        assert (d.passed, d.reason) == (False, "tag người khác, không gọi bot"), text
    assert agent.classify_calls == []
    # Tag người khác nhưng có gọi bot thì vẫn qua.
    assert (await decide(f, msg("@Thái Toàn bot ơi nhắc bạn ấy", mentions=["u9"]), mode="all")).passed


async def test_ai_error_budget_and_disabled_in_mode_all(make_filter, agent):
    agent.filter_error = RuntimeError("down")
    d = await decide(make_filter(), msg("ai biết cách nấu phở?"), mode="all")
    assert (d.passed, d.stage) == (False, "error")

    agent.filter_error = None
    d = await decide(make_filter(), msg("ai biết cách nấu phở?"), mode="all", over_budget=True)
    assert (d.passed, d.stage) == (False, "budget")

    calls = len(agent.classify_calls)
    d = await decide(make_filter(FILTER_AI="false"), msg("ai biết cách nấu phở?"), mode="all")
    assert not d.passed and len(agent.classify_calls) == calls


async def test_gemini_classify_requests_json_and_counts_tokens():
    from google.genai import types

    from pylos.residential.residents.pylos import GeminiAgent, ToolRegistry

    seen = {}

    class Response:
        text = '{"reply": true, "reason": "gọi trợ lý"}'
        usage_metadata = type("Usage", (), {"total_token_count": 42})()

    class Models:
        async def generate_content(self, model, contents, config):
            seen.update(model=model, config=config)
            return Response()

    client = type("Client", (), {"aio": type("Aio", (), {"models": Models()})()})()
    agent = GeminiAgent("k", "gemini-main", ToolRegistry(), client=client)
    assert await agent.classify("sys", "tin", model="gemini-lite") == ({"reply": True, "reason": "gọi trợ lý"}, 42)
    assert seen["model"] == "gemini-lite"
    assert isinstance(seen["config"], types.GenerateContentConfig)
    assert seen["config"].response_mime_type == "application/json" and seen["config"].temperature == 0

    Response.text = "không phải json"
    with pytest.raises(ValueError):
        await agent.classify("sys", "tin")


def _gemini(models):
    from pylos.residential.residents.pylos import GeminiAgent, ToolRegistry

    client = type("Client", (), {"aio": type("Aio", (), {"models": models})()})()
    agent = GeminiAgent("k", "gemini-main", ToolRegistry(), client=client)
    agent.retry_delay = 0
    return agent


class _Ok:
    text = '{"reply": false, "reason": "x"}'
    usage_metadata = None


async def test_classify_retries_once_on_timeout_then_reports_clearly():
    import asyncio

    calls = []

    class Slow:
        async def generate_content(self, model, contents, config):
            calls.append(1)
            if len(calls) == 1:
                await asyncio.sleep(1)
            return _Ok()

    agent = _gemini(Slow())
    assert (await agent.classify("s", "t", timeout=0.05))[0]["reply"] is False and len(calls) == 2

    class AlwaysSlow:
        async def generate_content(self, model, contents, config):
            await asyncio.sleep(1)

    with pytest.raises(TimeoutError, match="không trả lời sau"):
        await _gemini(AlwaysSlow()).classify("s", "t", timeout=0.05)


async def test_classify_drops_thinking_when_model_rejects_it():
    seen = []

    class Rejects:
        async def generate_content(self, model, contents, config):
            seen.append(config.thinking_config)
            if config.thinking_config is not None:
                err = RuntimeError("400 INVALID_ARGUMENT: thinking_level is not supported for this model")
                err.code = 400
                raise err
            return _Ok()

    agent = _gemini(Rejects())
    await agent.classify("s", "t")
    await agent.classify("s", "t")
    assert seen[0] is not None and seen[1:] == [None, None]  # nhớ lại, lần sau không thử nữa


async def test_filter_logs_error_type_even_without_message(make_filter, agent, caplog):
    import asyncio
    import logging

    agent.filter_error = asyncio.TimeoutError()
    with caplog.at_level(logging.WARNING):
        d = await decide(make_filter(), msg("ai biết cách nấu phở?"), mode="all")
    assert d.stage == "error" and "TimeoutError" in d.reason and "TimeoutError" in caplog.text


# ---------- phân loại việc để đổi model / thinking (MODEL_SHIFT) ----------

async def test_ai_stage_returns_profile_in_same_call(make_filter, agent):
    f = make_filter(MODEL_SHIFT="true")
    agent.filter_reply, agent.filter_profile = True, "coding"
    d = await decide(f, msg("sao hàm này báo lỗi nhỉ?"), mode="all")
    assert (d.passed, d.stage, d.profile) == (True, "ai", "coding")
    assert len(agent.classify_calls) == 1  # không tốn thêm lần gọi
    assert '"profile"' in agent.classify_systems[-1]
    assert d.as_record()["profile"] == "coding"

    agent.filter_profile = "không-có-loại-này"
    assert (await decide(f, msg("hỏi gì đó nữa"), mode="all")).profile == ""


async def test_direct_calls_ask_profile_separately(make_filter, agent):
    f = make_filter(identity=("me-1", "Mèo Ú"), MODEL_SHIFT="true")
    agent.filter_profile = "reflective"
    for m, stage in ((msg("bạn nghĩ sao về tự do ý chí?", group=False), "private"), (msg("/bot ý nghĩa cuộc sống?"), "rule")):
        d = await decide(f, m)
        assert (d.passed, d.stage, d.profile) == (True, stage, "reflective")
    assert len(agent.classify_calls) == 2


async def test_profile_uses_model_shift_doc_and_survives_errors(make_filter, agent):
    f = make_filter(MODEL_SHIFT="true")
    f.shift_instructions = lambda: "GUIDE FROM modelShift.md"
    agent.filter_profile = "routine"
    await decide(f, msg("mai họp mấy giờ?", group=False))
    assert "GUIDE FROM modelShift.md" in agent.classify_systems[-1]

    agent.filter_error = RuntimeError("down")
    d = await decide(f, msg("viết hàm sort", group=False))
    assert (d.passed, d.profile, d.prompt) == (True, "", "viết hàm sort")  # lỗi phân loại không chặn bot trả lời


async def test_model_shift_off_means_no_profile_and_no_extra_call(make_filter, agent):
    f = make_filter(MODEL_SHIFT="false")
    agent.filter_reply, agent.filter_profile = True, "coding"
    assert (await decide(f, msg("ok", group=False))).profile == ""
    assert (await decide(f, msg("sao hàm này lỗi?"), mode="all")).profile == ""
    assert len(agent.classify_calls) == 1  # chỉ lần hỏi AI của nhóm all


async def test_filter_tells_ai_which_profile_the_chat_holds_and_skips_when_locked(make_filter, agent):
    f = make_filter(identity=("me-1", "Mèo Ú"), MODEL_SHIFT="true")
    agent.filter_profile = "coding"
    await decide_with(f, msg("/bot tiếp đi", group=True), current_profile="coding")
    assert "Hồ sơ đang giữ của cuộc trò chuyện: coding" in agent.classify_calls[-1]
    await decide_with(f, msg("bạn nghĩ sao?", group=False), current_profile="")
    assert "Hồ sơ đang giữ của cuộc trò chuyện: chưa có" in agent.classify_calls[-1]

    calls = len(agent.classify_calls)
    d = await decide_with(f, msg("/bot sửa lỗi này"), shift=False)  # chat đặt /model fixed
    assert (d.passed, d.profile) == (True, "") and len(agent.classify_calls) == calls
    agent.filter_reply = True
    d = await decide_with(f, msg("sửa lỗi này giúp"), mode="all", shift=False)
    assert (d.passed, d.profile) == (True, "") and "profile" not in agent.classify_systems[-1]


async def decide_with(f, m, mode="default", **kwargs):
    return await f.decide(m, mode=mode, over_budget=False, recent=[], **kwargs)


def test_parse_profiles_table_and_defaults():
    from pylos.residential.residents.filter.instructions import DEFAULT_PROFILES, parse_profiles

    table = """
| profile | model | thinking | fallbacks |
|---|---|---|---|
| routine | `m-lite` | HIGH | a, b |
| coding | m-big | medium | - |
| reflective | m-x | ultra | a |
| lạ | m-y | low | a |
"""
    got = parse_profiles(table)
    assert (got["routine"].model, got["routine"].thinking, got["routine"].fallbacks) == ("m-lite", "high", ("a", "b"))
    assert (got["coding"].model, got["coding"].fallbacks) == ("m-big", ())
    assert got["reflective"] == DEFAULT_PROFILES["reflective"]  # thinking sai: bỏ dòng, dùng mặc định
    assert parse_profiles("") == DEFAULT_PROFILES


def test_shipped_profile_table_is_valid_and_matches_defaults():
    from pylos.lobby.dispatch.shared.config import PROJECT_ROOT
    from pylos.residential.residents.filter.instructions import DEFAULT_PROFILES, FilterInstructions

    workspace = FilterInstructions(PROJECT_ROOT / "src/pylos/residential/residents/filter/workspace")
    assert workspace.profiles() == DEFAULT_PROFILES  # bảng trong modelShift.md và mặc định trong code không lệch nhau


def test_fallback_models_setting(tmp_path):
    assert make_settings(tmp_path).fallback_models == ("gemini-3.5-flash-lite",)
    assert make_settings(tmp_path, FALLBACK_MODELS="a, b").fallback_models == ("a", "b")
    assert make_settings(tmp_path, FALLBACK_MODELS="").fallback_models == ()
