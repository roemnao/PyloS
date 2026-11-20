"""Tavily: nguồn tìm web miễn phí (khoảng 1.000 lượt/tháng) khi Gemini không có hạn mức Google Search."""

from __future__ import annotations

import json

import httpx
import pytest

from pylos.lobby.office.agent_tools import web_reader


@pytest.fixture(autouse=True)
def fresh_config(monkeypatch):
    monkeypatch.setattr(web_reader, "CONFIG", web_reader.WebConfig())


def serve(monkeypatch, handler):
    monkeypatch.setattr(web_reader, "transport", httpx.MockTransport(handler))


async def test_tavily_sends_bearer_key_and_parses_results(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={
            "answer": "Thủ đô của Úc là Canberra.",
            "results": [
                {"title": "Canberra", "url": "https://a.example", "content": "Canberra là thủ đô...", "score": 0.9},
                {"title": "không có link"},
            ],
        })

    serve(monkeypatch, handler)
    result = await web_reader.tavily_search("thủ đô Úc", "tvly-KEY")
    assert result["answer"] == "Thủ đô của Úc là Canberra." and result["nguon_tim"] == "Tavily"
    assert result["results"] == [{"title": "Canberra", "url": "https://a.example", "snippet": "Canberra là thủ đô..."}]
    request = seen[0]
    assert request.method == "POST" and str(request.url) == web_reader.TAVILY_URL
    assert request.headers["authorization"] == "Bearer tvly-KEY"
    body = json.loads(request.content)
    assert body["query"] == "thủ đô Úc" and body["include_answer"] is True and body["max_results"] == 5
    assert "tvly-KEY" not in request.content.decode()  # khoá chỉ nằm trong header


async def test_tavily_without_answer_has_no_answer_key(monkeypatch):
    serve(monkeypatch, lambda request: httpx.Response(200, json={"results": []}))
    result = await web_reader.tavily_search("x", "K")
    assert "answer" not in result and result["results"] == []


@pytest.mark.parametrize("status,word", [(401, "sai"), (432, "hạn mức"), (429, "hạn mức"), (500, "500")])
async def test_tavily_errors(monkeypatch, status, word):
    serve(monkeypatch, lambda request: httpx.Response(status))
    with pytest.raises(web_reader.SearchError, match=word):
        await web_reader.tavily_search("x", "K")


async def test_tavily_network_error(monkeypatch):
    def boom(request):
        raise httpx.ConnectError("down")

    serve(monkeypatch, boom)
    with pytest.raises(web_reader.SearchError, match="Không gọi được Tavily"):
        await web_reader.tavily_search("x", "K")
