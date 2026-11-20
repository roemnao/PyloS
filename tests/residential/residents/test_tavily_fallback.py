"""Bot: thứ tự nguồn tìm web Gemini -> Tavily -> Brave."""

from __future__ import annotations

import pytest
from conftest import OWNER, event
from test_media_flow import SearchingAgent, push
from test_web_fallback import GroundingDownAgent

from pylos.lobby.office.agent_tools import web_reader


def private(text):
    return event(text, chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE")


@pytest.fixture
def backends(monkeypatch):
    calls = []
    fail = set()

    def make(name):
        async def search(query, key):
            calls.append((name, key))
            if name in fail:
                raise web_reader.SearchError(f"{name} hết hạn mức")
            return {"results": [], "nguon_tim": name}

        return search

    monkeypatch.setattr(web_reader, "tavily_search", make("tavily"))
    monkeypatch.setattr(web_reader, "brave_search", make("brave"))
    return calls, fail


async def test_auto_uses_tavily_after_gemini_quota(make_bot, agent, backends):
    calls, _ = backends
    bot = make_bot(TAVILY_API_KEY="TK", BRAVE_API_KEY="BK")
    bot.agent = GroundingDownAgent(agent)
    await push(bot, private("hỏi"))
    assert calls == [("tavily", "TK")] and agent.search_result["nguon_tim"] == "tavily"


async def test_auto_falls_through_to_brave_when_tavily_fails(make_bot, agent, backends):
    calls, fail = backends
    fail.add("tavily")
    bot = make_bot(TAVILY_API_KEY="TK", BRAVE_API_KEY="BK")
    bot.agent = GroundingDownAgent(agent)
    await push(bot, private("hỏi"))
    assert calls == [("tavily", "TK"), ("brave", "BK")] and agent.search_result["nguon_tim"] == "brave"


async def test_all_sources_failing_lists_reasons(make_bot, agent, backends):
    _, fail = backends
    fail.update({"tavily", "brave"})
    bot = make_bot(TAVILY_API_KEY="TK", BRAVE_API_KEY="BK")
    bot.agent = GroundingDownAgent(agent)
    await push(bot, private("hỏi"))
    error = agent.search_result["error"]
    assert "tavily hết hạn mức" in error and "brave hết hạn mức" in error and "gửi link" in error


async def test_tavily_only_provider(make_bot, agent, backends):
    calls, _ = backends
    searching = SearchingAgent(agent)
    bot = make_bot(WEB_SEARCH_PROVIDER="tavily", TAVILY_API_KEY="TK", BRAVE_API_KEY="BK")
    bot.agent = searching
    await push(bot, private("hỏi"))
    assert searching.queries == [] and calls == [("tavily", "TK")]


async def test_gemini_working_never_touches_tavily(make_bot, agent, backends):
    calls, _ = backends
    searching = SearchingAgent(agent)
    bot = make_bot(TAVILY_API_KEY="TK")
    bot.agent = searching
    await push(bot, private("hỏi"))
    assert searching.queries == ["giá vàng"] and calls == []


async def test_tavily_counts_toward_daily_limit(make_bot, agent, backends):
    calls, _ = backends
    bot = make_bot(WEB_SEARCH_PROVIDER="tavily", TAVILY_API_KEY="TK", WEB_SEARCH_PER_DAY="1")
    bot.agent = SearchingAgent(agent)
    await push(bot, private("một"))
    await push(bot, private("hai"))
    assert calls == [("tavily", "TK")] and "hết lượt" in agent.search_result["error"]


async def test_no_key_and_tavily_provider_means_no_search_function(make_bot, agent):
    searching = SearchingAgent(agent)
    bot = make_bot(WEB_SEARCH_PROVIDER="tavily")
    bot.agent = searching
    await push(bot, private("hỏi"))
    assert agent.search_result is None
