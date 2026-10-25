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


DEVICE_TTL_SECONDS = 180 * 24 * 3600
MAX_DEVICES = 10


class AdminDevices:
    """Khoá thiết bị: ứng dụng ở máy khác (ZaloBot.exe) đăng nhập Gmail một lần để điều khiển trang quản lý này.

    Khác phiên trình duyệt: sống 180 ngày kể từ lần dùng cuối, còn sau khi khởi động lại (VPS tự cập nhật là
    khởi động lại). Chỉ lưu SHA-256 của khoá trong userdata/system/admin_devices.json, lộ file này không dùng được.
    """

    def __init__(self, path, ttl: float = DEVICE_TTL_SECONDS, clock=time.time) -> None:
        self._path = path
        self._ttl = ttl
        self._clock = clock
        self._lock = threading.Lock()

    @staticmethod
    def _hash(token: str) -> str:
        import hashlib

        return hashlib.sha256(token.encode()).hexdigest()

    def _load(self) -> dict[str, dict]:
        import json

        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        now = self._clock()
        return {k: v for k, v in data.items() if isinstance(v, dict) and float(v.get("last_used", 0)) + self._ttl > now} \
            if isinstance(data, dict) else {}

    def _save(self, devices: dict[str, dict]) -> None:
        import json

        from bot.storage import atomic_write_text

        atomic_write_text(self._path, json.dumps(devices, ensure_ascii=False, indent=2))

    def issue(self, email: str, name: str) -> str:
        token = "dev_" + secrets.token_urlsafe(32)
        now = self._clock()
        with self._lock:
            devices = self._load()
            # Cùng một máy đăng nhập lại thì thay khoá cũ của máy đó.
            devices = {k: v for k, v in devices.items() if not (v.get("name") == name and v.get("email") == email)}
            while len(devices) >= MAX_DEVICES:
                devices.pop(min(devices, key=lambda k: float(devices[k].get("last_used", 0))))
            devices[self._hash(token)] = {"id": secrets.token_hex(4), "email": email, "name": name[:80],
                                          "created": now, "last_used": now}
            self._save(devices)
        return token

    def valid(self, token: str) -> bool:
        if not token.startswith("dev_"):
            return False
        key = self._hash(token)
        with self._lock:
            devices = self._load()
            entry = devices.get(key)
            if entry is None:
                return False
            now = self._clock()
            if now - float(entry.get("last_used", 0)) > 3600:  # ghi file tối đa mỗi giờ một lần
                entry["last_used"] = now
                self._save(devices)
            return True

    def list(self) -> list[dict]:
        with self._lock:
            return sorted(({k: v[k] for k in ("id", "email", "name", "created", "last_used")}
                           for v in self._load().values()), key=lambda d: -d["last_used"])

    def revoke(self, device_id: str) -> bool:
        with self._lock:
            devices = self._load()
            kept = {k: v for k, v in devices.items() if v.get("id") != device_id}
            if len(kept) == len(devices):
                return False
            self._save(kept)
            return True
