"""check_url: bot chỉ được đọc trang công khai."""

import socket

import pytest

from pylos.gate.fence.web_limit import url_guard
from pylos.gate.fence.web_limit.url_guard import check_url


@pytest.fixture(autouse=True)
def fake_dns(monkeypatch):
    """Tên miền giả -> IP cho trước; không gọi DNS thật."""
    table = {"example.com": "93.184.216.34", "intranet.corp": "10.1.2.3", "rebind.evil": "127.0.0.1",
             "v6.example": "2606:2800:220:1:248:1893:25c8:1946", "mapped.evil": "::ffff:10.0.0.1"}

    async def getaddrinfo(self, host, port, **kwargs):
        if host not in table:
            raise socket.gaierror("no such host")
        ip = table[host]
        return [(socket.AF_INET6 if ":" in ip else socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port or 0))]

    monkeypatch.setattr("asyncio.base_events.BaseEventLoop.getaddrinfo", getaddrinfo)


@pytest.mark.parametrize("url", [
    "https://example.com/bai-viet?id=1",
    "http://example.com:8080/",
    "https://93.184.216.34/",
    "https://v6.example/",
])
async def test_public_urls_are_allowed(url):
    assert await check_url(url) is None


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:8081/admin",
    "http://localhost/",
    "http://LOCALHOST./",
    "http://app.localhost/",
    "http://10.0.0.5/",
    "http://192.168.1.1/",
    "http://172.16.0.1/",
    "http://169.254.169.254/latest/meta-data/",
    "http://metadata.google.internal/",
    "http://0.0.0.0/",
    "http://[::1]/",
    "http://[::ffff:127.0.0.1]/",
    "http://intranet.corp/",      # DNS trỏ về 10.x
    "http://rebind.evil/",        # DNS trỏ về 127.0.0.1
    "http://mapped.evil/",
    "http://printer.local/",
    "http://user:pass@example.com/",
    "file:///etc/passwd",
    "ftp://example.com/x",
    "javascript:alert(1)",
    "http:///nohost",
    "",
    "https://example.com/" + "a" * 2100,
])
async def test_internal_or_odd_urls_are_blocked(url):
    assert await check_url(url) is not None


async def test_unresolvable_host_is_reported():
    reason = await check_url("https://khong-ton-tai.example.invalid/")
    assert reason and "phân giải" in reason


async def test_module_exposes_check_url():
    assert url_guard.check_url is check_url
