"""Đăng nhập trang quản lý bằng Google (OAuth riêng của PyloS, không qua web bot lịch).

PyloS không phân quyền: chỉ một Gmail (ADMIN_EMAIL) được vào. Luồng "thiết bị": trang quản lý xin một mã,
mở link Google ở tab mới, người dùng đăng nhập, callback đánh dấu mã đã duyệt, trang quản lý hỏi lại để nhận token phiên.
Mọi thứ nằm trong bộ nhớ tiến trình (khởi động lại là mất, ADMIN_TOKEN vẫn dùng được).
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import threading
import time
from typing import Any, Callable
from urllib.parse import urlencode

import httpx

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
TTL_SECONDS = 600
MAX_PENDING = 50


class PendingLogins:
    def __init__(self, ttl: float = TTL_SECONDS, clock: Callable[[], float] = time.monotonic) -> None:
        self._ttl = ttl
        self._clock = clock
        self._lock = threading.Lock()
        self._items: dict[str, dict[str, Any]] = {}

    def _purge(self, now: float) -> None:
        self._items = {k: v for k, v in self._items.items() if v["expires"] > now}

    def start(self) -> str:
        code = secrets.token_hex(16)
        now = self._clock()
        with self._lock:
            self._purge(now)
            while len(self._items) >= MAX_PENDING:
                self._items.pop(min(self._items, key=lambda k: self._items[k]["expires"]))
            self._items[code] = {"status": "pending", "verifier": secrets.token_urlsafe(48), "nonce": secrets.token_hex(8),
                                 "email": "", "expires": now + self._ttl}
        return code

    def get(self, code: str) -> dict[str, Any] | None:
        with self._lock:
            self._purge(self._clock())
            item = self._items.get(code)
            return dict(item) if item else None

    def finish(self, code: str, status: str, email: str = "") -> None:
        with self._lock:
            if code in self._items:
                self._items[code].update(status=status, email=email)

    def take(self, code: str) -> dict[str, Any] | None:
        """Lấy kết quả; mã đã xong (approved/denied) chỉ đọc được một lần."""
        with self._lock:
            self._purge(self._clock())
            item = self._items.get(code)
            if item is None:
                return None
            if item["status"] != "pending":
                del self._items[code]
            return dict(item)


def challenge(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()


def auth_url(client_id: str, redirect_uri: str, state: str, verifier: str, login_hint: str = "") -> str:
    params = {
        "client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code", "scope": "openid email",
        "state": state, "prompt": "select_account", "code_challenge": challenge(verifier), "code_challenge_method": "S256",
    }
    if login_hint:
        params["login_hint"] = login_hint
    return f"{AUTH_URL}?{urlencode(params)}"


def decode_id_token(id_token: str, client_id: str, now: float | None = None) -> dict[str, Any]:
    """id_token nhận trực tiếp từ Google qua HTTPS (bước đổi mã) nên chỉ kiểm tra người nhận, nơi cấp, hạn dùng."""
    try:
        part = id_token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
    except (IndexError, ValueError) as exc:
        raise ValueError("Google không trả về id_token hợp lệ") from exc
    if claims.get("aud") != client_id:
        raise ValueError("id_token không dành cho ứng dụng này")
    if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise ValueError("id_token không phải do Google cấp")
    if not claims.get("exp") or float(claims["exp"]) < (now if now is not None else time.time()):
        raise ValueError("id_token đã hết hạn")
    if not claims.get("email_verified"):
        raise ValueError("Email Google chưa được xác minh")
    return claims


def email_allowed(email: str, admin_email: str) -> bool:
    return bool(admin_email) and email.strip().lower() == admin_email.strip().lower()


async def exchange(code: str, verifier: str, redirect_uri: str, client_id: str, client_secret: str,
                   client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    data = {"code": code, "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri,
            "grant_type": "authorization_code", "code_verifier": verifier}
    owned = client is None
    client = client or httpx.AsyncClient(timeout=15)
    try:
        res = await client.post(TOKEN_URL, data=data)
        body = res.json() if res.content else {}
        if res.status_code != 200:
            raise ValueError(f"Google: {body.get('error_description') or body.get('error') or res.status_code}")
        return decode_id_token(str(body.get("id_token") or ""), client_id)
    finally:
        if owned:
            await client.aclose()
