"""doc_trang_web với trang chặn bot và link YouTube; Brave Search."""

from __future__ import annotations

import socket

import httpx
import pytest

from pylos.lobby.office.agent_tools import ToolContext, ToolRegistry, web_reader

CTX = ToolContext("g", "u", "An", is_owner=False)


@pytest.fixture(autouse=True)
def public_dns(monkeypatch):
    async def getaddrinfo(self, host, port, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port or 0))]

    monkeypatch.setattr("asyncio.base_events.BaseEventLoop.getaddrinfo", getaddrinfo)
    monkeypatch.setattr(web_reader, "CONFIG", web_reader.WebConfig())


def serve(monkeypatch, handler):
    monkeypatch.setattr(web_reader, "transport", httpx.MockTransport(handler))


async def read(url, ctx=CTX, **args):
    return await ToolRegistry(web_reader.TOOLS).call("doc_trang_web", {"url": url, **args}, ctx)


# ---------- trang chặn bot, User-Agent ----------


async def test_blocked_site_gets_clear_message(monkeypatch):
    serve(monkeypatch, lambda request: httpx.Response(403, text="Please respect our robot policy"))
    error = (await read("https://vi.wikipedia.example/wiki/X"))["error"]
    assert "chặn bot" in error and "403" in error


async def test_user_agent_carries_contact_only_when_set(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request.headers["user-agent"])
        return httpx.Response(200, text="<p>" + "nội dung " * 20 + "</p>", headers={"content-type": "text/html"})

    serve(monkeypatch, handler)
    await read("https://news.example/a")
    web_reader.CONFIG.contact = "https://bot.example/lien-he"
    await read("https://news.example/b")
    assert seen == ["PyloSBot/1.0", "PyloSBot/1.0 (+https://bot.example/lien-he)"]


# ---------- YouTube ----------


@pytest.mark.parametrize("url,vid", [
    ("https://youtube.com/shorts/z0qkD-fEu2k?si=FeBmZM1WbKJ-6ICh", "z0qkD-fEu2k"),
    ("https://www.youtube.com/watch?v=z0qkD-fEu2k&t=10", "z0qkD-fEu2k"),
    ("https://m.youtube.com/watch?v=z0qkD-fEu2k", "z0qkD-fEu2k"),
    ("https://youtu.be/z0qkD-fEu2k", "z0qkD-fEu2k"),
    ("https://www.youtube.com/embed/z0qkD-fEu2k", "z0qkD-fEu2k"),
    ("https://www.youtube.com/@kenh", ""),
    ("https://notyoutube.com/watch?v=z0qkD-fEu2k", ""),
    ("https://www.youtube.com/watch?v=short", ""),
])
def test_youtube_id(url, vid):
    assert web_reader.youtube_id(url) == vid


def oembed(request):
    if "oembed" in request.url.path:
        return httpx.Response(200, json={"title": "Thiên tài Gauss", "author_name": "Khai Sáng"})
    raise AssertionError("không được tải trang YouTube")


async def test_youtube_link_is_watched_by_gemini(monkeypatch):
    serve(monkeypatch, oembed)
    asked = []

    async def reader(url, question):
        asked.append((url, question))
        return {"summary": "Video kể về Gauss."}

    ctx = ToolContext("g", "u", "An", is_owner=False, video_reader=reader)
    result = await read("https://youtube.com/shorts/z0qkD-fEu2k?si=x", ctx, cau_hoi="video nói gì?")
    assert asked == [("https://www.youtube.com/watch?v=z0qkD-fEu2k", "video nói gì?")]
    assert result["title"] == "Thiên tài Gauss" and result["kenh"] == "Khai Sáng"
    assert result["noi_dung"] == "Video kể về Gauss."


async def test_youtube_without_reader_gives_title_only(monkeypatch):
    serve(monkeypatch, oembed)
    result = await read("https://youtu.be/z0qkD-fEu2k")
    assert result["title"] == "Thiên tài Gauss" and "Chưa xem được" in result["noi_dung"]


async def test_youtube_watch_error_keeps_title(monkeypatch):
    serve(monkeypatch, oembed)

    async def reader(url, question):
        return {"error": "Không xem được video"}

    ctx = ToolContext("g", "u", "An", is_owner=False, video_reader=reader)
    result = await read("https://youtu.be/z0qkD-fEu2k", ctx)
    assert result["title"] == "Thiên tài Gauss" and result["loi_xem_video"] == "Không xem được video"


# ---------- Brave Search ----------


async def test_brave_search_parses_results(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"web": {"results": [
            {"title": "Giá <strong>vàng</strong>", "url": "https://a.example", "description": "SJC &amp; PNJ"},
            {"title": "Không link"},
        ]}})

    serve(monkeypatch, handler)
    result = await web_reader.brave_search("giá vàng", "KEY")
    assert result["results"] == [{"title": "Giá vàng", "url": "https://a.example", "snippet": "SJC & PNJ"}]
    assert seen[0].headers["x-subscription-token"] == "KEY" and seen[0].url.params["q"] == "giá vàng"


@pytest.mark.parametrize("status,word", [(401, "sai"), (429, "hạn mức"), (500, "500")])
async def test_brave_search_errors(monkeypatch, status, word):
    serve(monkeypatch, lambda request: httpx.Response(status))
    with pytest.raises(web_reader.SearchError, match=word):
        await web_reader.brave_search("x", "KEY")
