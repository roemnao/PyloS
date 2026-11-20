"""Bot: tim_web chuyển sang Brave khi Gemini hết hạn mức Google Search; Gemini xem video YouTube."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from conftest import OWNER, event, make_settings
from test_agent import FakeModels, response
from test_media_flow import SearchingAgent, push

from pylos.lobby.dispatch.shared.config import ConfigError
from pylos.lobby.office.agent_tools import web_reader
from pylos.residential.residents.pylos import GeminiAgent, ToolRegistry


class QuotaError(Exception):
    code = 429


class GroundingDownAgent(SearchingAgent):
    """Gemini Google Search luôn báo 429 (key miễn phí không có hạn mức tìm kiếm)."""

    async def search(self, query):
        self.queries.append(query)
        raise QuotaError("429 RESOURCE_EXHAUSTED")


def private(text):
    return event(text, chat_id=OWNER, from_id=OWNER, chat_type="PRIVATE")


@pytest.fixture
def brave(monkeypatch):
    calls = []

    async def fake_brave(query, key):
        calls.append((query, key))
        return {"results": [{"title": "T", "url": "https://a.example", "snippet": "s"}]}

    monkeypatch.setattr(web_reader, "brave_search", fake_brave)
    return calls


async def test_search_falls_back_to_brave_and_rests_gemini(make_bot, agent, brave):
    down = GroundingDownAgent(agent)
    bot = make_bot(BRAVE_API_KEY="BK")
    bot.agent = down
    for _ in range(2):
        await push(bot, private("hỏi"))
    assert down.queries == ["giá vàng"]  # lần 2 không gọi lại Gemini (đang nghỉ 1 giờ)
    assert brave == [("giá vàng", "BK"), ("giá vàng", "BK")]
    assert agent.search_result["results"][0]["url"] == "https://a.example"


async def test_search_without_brave_key_explains_quota(make_bot, agent):
    down = GroundingDownAgent(agent)
    bot = make_bot()
    bot.agent = down
    await push(bot, private("hỏi"))
    error = agent.search_result["error"]
    assert "hết hạn mức" in error and "gửi link" in error


async def test_brave_only_provider_never_calls_gemini(make_bot, agent, brave):
    searching = SearchingAgent(agent)
    bot = make_bot(WEB_SEARCH_PROVIDER="brave", BRAVE_API_KEY="BK")
    bot.agent = searching
    await push(bot, private("hỏi"))
    assert searching.queries == [] and agent.search_result["results"][0]["url"] == "https://a.example"


async def test_gemini_only_provider_ignores_brave_key(make_bot, agent, brave):
    down = GroundingDownAgent(agent)
    bot = make_bot(WEB_SEARCH_PROVIDER="gemini", BRAVE_API_KEY="BK")
    bot.agent = down
    await push(bot, private("hỏi"))
    assert brave == [] and "error" in agent.search_result


class Watcher(SearchingAgent):
    fail = False

    async def watch_video(self, url, question):
        if self.fail:
            raise RuntimeError("private video")
        return {"summary": f"xem {url}"}, 70

    async def reply(self, system, turns, ctx, **overrides):
        self.fake.search_result = await ctx.video_reader("https://www.youtube.com/watch?v=abcdefghijk", "")
        return await self.fake.reply(system, turns, ctx, **overrides)


async def test_video_reader_counts_tokens_and_reports_errors(make_bot, agent):
    watcher = Watcher(agent)
    bot = make_bot()
    bot.agent = watcher
    used = bot.usage.used_today()
    await push(bot, private("xem video"))
    assert agent.search_result == {"summary": "xem https://www.youtube.com/watch?v=abcdefghijk"}
    assert bot.usage.used_today() - used >= 70
    watcher.fail = True
    await push(bot, private("xem lại"))
    assert "Không xem được video" in agent.search_result["error"]


def test_invalid_search_provider_is_rejected(tmp_path):
    with pytest.raises(ConfigError):
        make_settings(tmp_path, WEB_SEARCH_PROVIDER="bing")


async def test_watch_video_sends_youtube_uri_at_low_resolution():
    models = FakeModels([response("Video về Gauss", tokens=99)])
    client = SimpleNamespace(aio=SimpleNamespace(models=models))
    agent = GeminiAgent("key", "gemini-test", ToolRegistry(), client=client)
    result, tokens = await agent.watch_video("https://www.youtube.com/watch?v=abcdefghijk", "ai trong video?")
    assert result == {"summary": "Video về Gauss"} and tokens == 99
    _, contents, config = models.requests[0]
    assert contents[0].parts[0].file_data.file_uri == "https://www.youtube.com/watch?v=abcdefghijk"
    assert "ai trong video?" in contents[0].parts[1].text
    assert config.media_resolution.name == "MEDIA_RESOLUTION_LOW" and not config.tools
