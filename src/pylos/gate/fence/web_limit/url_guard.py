"""Luật an toàn cho link người dùng gửi: bot chỉ được đọc trang công khai trên internet.

Chặn link tới máy nội bộ (localhost, mạng LAN, link-local, metadata đám mây), vì nếu không ai cũng nhờ bot
đọc hộ trang quản lý hay dịch vụ nội bộ của chủ bot (SSRF). Gọi `check_url` cho URL đầu tiên và cho MỌI bước chuyển hướng.
"""

from __future__ import annotations

import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit

ALLOWED_SCHEMES = ("http", "https")
BLOCKED_HOSTS = ("localhost", "localhost.localdomain", "ip6-localhost", "metadata.google.internal")
BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".lan", ".home.arpa")
MAX_URL_LENGTH = 2000


def _forbidden(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped  # ::ffff:127.0.0.1 vẫn là máy nội bộ
    return not ip.is_global or ip.is_multicast


async def check_url(url: str) -> str | None:
    """Lý do chặn (tiếng Việt), hoặc None nếu được phép đọc."""
    if not url or len(url) > MAX_URL_LENGTH:
        return "Link trống hoặc quá dài."
    try:
        parts = urlsplit(url.strip())
        host = (parts.hostname or "").lower().rstrip(".")
        parts.port  # noqa: B018 - cổng sai thì ném ValueError
    except ValueError:
        return "Link không hợp lệ."
    if parts.scheme not in ALLOWED_SCHEMES:
        return "Chỉ đọc được link http hoặc https."
    if parts.username or parts.password:
        return "Link có kèm tài khoản, mình không mở."
    if not host:
        return "Link không có tên miền."
    if host in BLOCKED_HOSTS or host.endswith(BLOCKED_SUFFIXES):
        return "Link trỏ tới máy nội bộ, mình không mở."
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        return "Link trỏ tới địa chỉ nội bộ, mình không mở." if _forbidden(literal) else None
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(host, parts.port or None, type=socket.SOCK_STREAM)
    except OSError:
        return "Không tìm thấy trang này (tên miền không phân giải được)."
    for info in infos:
        address = info[4][0].split("%")[0]  # bỏ zone id của IPv6
        try:
            if _forbidden(ipaddress.ip_address(address)):
                return "Link trỏ tới địa chỉ nội bộ, mình không mở."
        except ValueError:
            return "Link không hợp lệ."
    return None
