"""Phiên đăng nhập của trang quản lý bot khi vào bằng Gmail (xem /api/auth/gmail/* ở admin_web_server.py).

Chỉ nằm trong bộ nhớ của tiến trình quản lý: tắt hoặc khởi động lại là hết phiên, và ADMIN_TOKEN vẫn dùng được
như đường dự phòng. Token phiên ngẫu nhiên 256 bit, không đoán được, hết hạn sau 12 giờ.
"""

from __future__ import annotations

import secrets
import threading
import time

TTL_SECONDS = 12 * 3600
MAX_SESSIONS = 20


class AdminSessions:
    def __init__(self, ttl: float = TTL_SECONDS, clock=time.monotonic) -> None:
        self._ttl = ttl
        self._clock = clock
        self._lock = threading.Lock()
        self._sessions: dict[str, tuple[float, str]] = {}

    def issue(self, email: str = "") -> str:
        token = secrets.token_urlsafe(32)
        now = self._clock()
        with self._lock:
            self._sessions = {t: v for t, v in self._sessions.items() if v[0] > now}
            while len(self._sessions) >= MAX_SESSIONS:  # giữ ít phiên: bỏ phiên cũ nhất
                self._sessions.pop(min(self._sessions, key=lambda t: self._sessions[t][0]))
            self._sessions[token] = (now + self._ttl, email)
        return token

    def valid(self, token: str) -> bool:
        if not token:
            return False
        with self._lock:
            entry = self._sessions.get(token)
            if entry is None:
                return False
            if entry[0] <= self._clock():
                del self._sessions[token]
                return False
            return True
