"""doc_trang_web và tim_web."""

from __future__ import annotations

import socket
from types import SimpleNamespace

import httpx
import pytest

from pylos.lobby.office.agent_tools import ToolContext, ToolRegistry, web_reader

CTX = ToolContext("g", "u", "An", is_owner=False)

PAGE = """<html><head><title>Giá vàng hôm nay</title><style>.x{color:red}</style></head>
<body><nav>Trang chủ | Tin tức</nav><script>alert('xin chao')</script>
<article><h1>Giá vàng tăng mạnh</h1><p>Vàng SJC tăng 500 nghìn đồng mỗi lượng trong phiên sáng nay.</p>
<p>Chuyên gia dự báo giá còn biến động.</p></article><footer>Bản quyền</footer></body></html>"""


@pytest.fixture(autouse=True)
def public_dns(monkeypatch):
    async def getaddrinfo(self, host, port, **kwargs):
        ip = {"internal.corp": "10.0.0.9"}.get(host, "93.184.216.34")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port or 0))]

    monkeypatch.setattr("asyncio.base_events.BaseEventLoop.getaddrinfo", getaddrinfo)
    monkeypatch.setattr(web_reader, "CONFIG", web_reader.WebConfig())


def serve(monkeypatch, handler):
    monkeypatch.setattr(web_reader, "transport", httpx.MockTransport(handler))


def html_response(body=PAGE, status=200, content_type="text/html; charset=utf-8", headers=None):
    return httpx.Response(status, content=body.encode("utf-8"), headers={"content-type": content_type, **(headers or {})})


async def read(url, **args):
    return await ToolRegistry(web_reader.TOOLS).call("doc_trang_web", {"url": url, **args}, CTX)


async def test_reads_main_text_and_drops_menu_and_script(monkeypatch):
    serve(monkeypatch, lambda request: html_response())
    result = await read("https://news.example/vang", cau_hoi="giá vàng?")
    # trafilatura lấy tiêu đề bài (h1), bộ đọc dự phòng lấy thẻ <title>: cả hai đều đúng
    assert result["title"] in ("Giá vàng hôm nay", "Giá vàng tăng mạnh") and result["truncated"] is False
    assert "Vàng SJC tăng 500 nghìn" in result["text"]
    assert "alert" not in result["text"] and "Bản quyền" not in result["text"] and "Trang chủ" not in result["text"]
    assert result["cau_hoi"] == "giá vàng?" and "DỮ LIỆU" in result["note"]


async def test_long_text_is_truncated(monkeypatch):
    web_reader.CONFIG.max_chars = 600
    serve(monkeypatch, lambda request: html_response("<html><body><p>" + "chữ " * 1000 + "</p></body></html>"))
    result = await read("https://news.example/dai")
    assert len(result["text"]) == 600 and result["truncated"] is True


async def test_plain_text_and_json_are_returned_as_is(monkeypatch):
    serve(monkeypatch, lambda request: html_response('{"a": 1}', content_type="application/json"))
    assert (await read("https://api.example/x"))["text"] == '{"a": 1}'


async def test_other_content_types_are_refused(monkeypatch):
    serve(monkeypatch, lambda request: html_response("%PDF", content_type="application/pdf"))
    assert "error" in await read("https://x.example/a.pdf")


async def test_http_error_is_reported(monkeypatch):
    serve(monkeypatch, lambda request: httpx.Response(404))
    assert "404" in (await read("https://x.example/none"))["error"]


async def test_internal_url_is_blocked_without_a_request(monkeypatch):
    called = []
    serve(monkeypatch, lambda request: called.append(request) or html_response())
    for url in ("http://127.0.0.1:8081/", "http://internal.corp/x", "file:///etc/passwd"):
        assert "error" in await read(url)
    assert called == []


async def test_redirect_to_internal_address_is_blocked(monkeypatch):
    seen = []

    def handler(request):
        seen.append(str(request.url))
        if request.url.host == "short.example":
            return httpx.Response(302, headers={"location": "http://127.0.0.1:8081/admin"})
        return html_response()

    serve(monkeypatch, handler)
    result = await read("https://short.example/abc")
    assert "error" in result and seen == ["https://short.example/abc"]


async def test_public_redirect_is_followed_and_final_url_reported(monkeypatch):
    def handler(request):
        if request.url.path == "/go":
            return httpx.Response(301, headers={"location": "/vang"})
        return html_response()

    serve(monkeypatch, handler)
    result = await read("https://news.example/go")
    assert result["url"] == "https://news.example/vang" and "Vàng SJC" in result["text"]


async def test_redirect_loop_gives_up(monkeypatch):
    serve(monkeypatch, lambda request: httpx.Response(302, headers={"location": "/again"}))
    assert "quá nhiều" in (await read("https://loop.example/"))["error"]


async def test_network_error_and_timeout(monkeypatch):
    def refuse(request):
        raise httpx.ConnectError("down")

    serve(monkeypatch, refuse)
    assert "error" in await read("https://down.example/")

    def slow(request):
        raise httpx.ReadTimeout("slow")

    serve(monkeypatch, slow)
    assert "chậm" in (await read("https://slow.example/"))["error"]


async def test_huge_page_is_cut_not_loaded_whole(monkeypatch):
    big = "<html><body><p>" + "a" * (6 * 1024 * 1024) + "</p></body></html>"
    serve(monkeypatch, lambda request: html_response(big))
    result = await read("https://big.example/")
    assert result["truncated"] is True and len(result["text"]) <= web_reader.CONFIG.max_chars


async def test_missing_url():
    assert "error" in await ToolRegistry(web_reader.TOOLS).call("doc_trang_web", {}, CTX)


def test_basic_extractor_works_without_trafilatura():
    title, text = web_reader.extract_basic(PAGE)
    assert title == "Giá vàng hôm nay" and "Vàng SJC tăng" in text and "alert" not in text


# ---------- tim_web ----------


async def search_call(ctx, query="giá vàng"):
    return await ToolRegistry(web_reader.TOOLS).call("tim_web", {"truy_van": query}, ctx)


async def test_tim_web_uses_context_search():
    async def fake(query):
        return {"answer": f"kết quả cho {query}", "sources": [{"title": "T", "uri": "https://a.example"}]}

    ctx = ToolContext("g", "u", "An", is_owner=False, web_search=fake)
    result = await search_call(ctx)
    assert result["answer"] == "kết quả cho giá vàng" and result["sources"][0]["uri"] == "https://a.example"
    assert "DỮ LIỆU" in result["note"]


async def test_tim_web_without_search_function_reports_error():
    assert "error" in await search_call(CTX)


async def test_tim_web_error_is_passed_through_without_note():
    async def fake(query):
        return {"error": "hết lượt"}

    ctx = ToolContext("g", "u", "An", is_owner=False, web_search=fake)
    assert await search_call(ctx) == {"error": "hết lượt"}


def test_tools_hidden_when_disabled():
    registry = ToolRegistry(web_reader.TOOLS)
    assert registry.names() == ["doc_trang_web", "tim_web"]
    web_reader.CONFIG.search_enabled = False
    assert registry.names() == ["doc_trang_web"]
    web_reader.CONFIG.enabled = False
    assert registry.names() == [] and registry.declarations() == []


async def test_disabled_tool_cannot_be_called():
    web_reader.CONFIG.enabled = False
    assert "error" in await read("https://news.example/")


def test_configure_reads_settings():
    settings = SimpleNamespace(web_tools=False, web_search=True, web_max_chars=1234, web_fetch_timeout=9, web_search_per_day=5)
    web_reader.configure(settings)
    assert (web_reader.CONFIG.enabled, web_reader.CONFIG.max_chars, web_reader.CONFIG.fetch_timeout) == (False, 1234, 9)
