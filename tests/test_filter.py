from __future__ import annotations

import pytest

from bot.filter import MessageFilter, is_chatter
from bot.zalo.personal import to_incoming
from bot.timeutil import now_ms

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
    d = await decide(f, msg("còn New Zealand thì sao?"), recent=recent)
    assert (d.passed, d.stage, d.prompt, d.tokens) == (True, "ai", "còn New Zealand thì sao?", 5)
    sent = agent.classify_calls[-1]
    assert "[Trợ lý] Canberra" in sent and "cũ lắm" not in sent  # chỉ 2 dòng gần nhất
    agent.filter_reply = False
    assert (await decide(f, msg("tối nay ăn gì mọi người"))).passed is False


async def test_ai_error_budget_mode_all_and_disabled(make_filter, agent):
    agent.filter_error = RuntimeError("down")
    d = await decide(make_filter(), msg("ai biết cách nấu phở?"))
    assert (d.passed, d.stage) == (False, "error")

    agent.filter_error = None
    d = await decide(make_filter(), msg("ai biết cách nấu phở?"), over_budget=True)
    assert (d.passed, d.stage) == (False, "budget")

    d = await decide(make_filter(), msg("chuyện gì cũng được"), mode="all")
    assert (d.passed, d.stage) == (True, "mode_all")

    calls = len(agent.classify_calls)
    d = await decide(make_filter(FILTER_AI="false"), msg("ai biết cách nấu phở?"))
    assert not d.passed and len(agent.classify_calls) == calls


async def test_gemini_classify_requests_json_and_counts_tokens():
    from google.genai import types

    from bot.agent import GeminiAgent, ToolRegistry

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
