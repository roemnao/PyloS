"""Thông số bot do chủ hệ thống chỉnh trên web (iforgotmywayhome → Hệ thống → Cấu hình bot).

Bot hỏi web lúc khởi động và mỗi phút (cùng lúc gửi nhịp tim). Giá trị từ web đè lên settings.env, có hiệu lực
ngay không cần khởi động lại. Chỉ nhận các khoá trong REMOTE_KEYS: khoá bí mật (Gemini, Zalo, phiên đăng nhập,
mã quản trị) không bao giờ được lấy từ web, kể cả khi web gửi xuống. Mất mạng thì dùng bản lấy được gần nhất,
lưu ở userdata/system/remote_config.json (giao diện quản lý cũng đọc file này để biết thông số nào do web đặt).
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
from pathlib import Path
from typing import Any, Callable

from bot.config import Settings
from bot.storage.text_files import atomic_write_text
from bot.system import server_client
from bot.userdata_paths import REMOTE_CONFIG_FILE

log = logging.getLogger(__name__)

HEARTBEAT_SECONDS = 60


def _int(minimum: int) -> Callable[[Any], int]:
    def parse(value: Any) -> int:
        number = int(value)
        if number < minimum:
            raise ValueError(f"phải >= {minimum}")
        return number
    return parse


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on", "có"):
        return True
    if text in ("0", "false", "no", "off", "không"):
        return False
    raise ValueError("phải là true/false")


def _csv(value: Any) -> tuple[str, ...]:
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


def _model(value: Any) -> str:
    text = str(value).strip()
    if not text or any(c.isspace() for c in text) or len(text) > 200:
        raise ValueError("tên model không hợp lệ")
    return text


def _assign(value: Any) -> str:
    text = str(value).strip().lower()
    if text not in ("owner", "all"):
        raise ValueError("phải là owner hoặc all")
    return text


# Khoá trên web → (trường trong Settings, hàm đổi kiểu). Không có khoá bí mật nào ở đây.
REMOTE_KEYS: dict[str, tuple[str, Callable[[Any], Any]]] = {
    "GEMINI_MODEL": ("gemini_model", _model),
    "FILTER_MODEL": ("filter_model", _model),
    "MAX_OUTPUT_TOKENS": ("max_output_tokens", _int(1)),
    "MAX_TOOL_ROUNDS": ("max_tool_rounds", _int(0)),
    "LLM_TIMEOUT_SECONDS": ("llm_timeout_seconds", _int(1)),
    "HISTORY_TURNS": ("history_turns", _int(1)),
    "FILTER_AI": ("filter_ai", _bool),
    "FILTER_CONTEXT_LINES": ("filter_context_lines", _int(0)),
    "BOT_NAMES": ("bot_names", _csv),
    "BOT_TRIGGERS": ("bot_triggers", _csv),
    "MEMORYDATA_KEEP": ("memorydata_keep", _int(0)),
    "USER_RATE_PER_MIN": ("user_rate_per_min", _int(0)),
    "CHAT_RATE_PER_MIN": ("chat_rate_per_min", _int(0)),
    "DAILY_TOKEN_BUDGET": ("daily_token_budget", _int(0)),
    "ALLOW_ALL_CHATS": ("allow_all_chats", _bool),
    "ALLOWED_CHAT_IDS": ("allowed_chat_ids", _csv),
    "ASSIGN_ALLOWED": ("assign_allowed", _assign),
    "SESSION_UPLOAD": ("session_upload", _bool),
}
WORKSPACE_FILES = ("SYSTEM.md", "MEMORY.md")


def overrides(values: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """{trường Settings: giá trị} từ thông số web, và danh sách khoá bị bỏ qua (không được phép hoặc sai kiểu)."""
    fields: dict[str, Any] = {}
    ignored: list[str] = []
    for key, raw in (values or {}).items():
        spec = REMOTE_KEYS.get(key)
        if spec is None or raw is None:
            ignored.append(key)
            continue
        field, parse = spec
        try:
            value = parse(raw)
        except (TypeError, ValueError) as exc:
            log.warning("Bỏ qua thông số %s từ web: %s", key, exc)
            ignored.append(key)
            continue
        if field == "bot_triggers" and not value:
            value = ("/bot",)
        fields[field] = value
    return fields, ignored


def cache_path(settings: Settings) -> Path:
    return settings.system_dir / REMOTE_CONFIG_FILE


def read_cached(settings: Settings) -> dict[str, Any]:
    """Bản cấu hình từ web gần nhất ({version, values, files, fetched_at}); {} nếu chưa có."""
    try:
        data = json.loads(cache_path(settings).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


class RemoteConfig:
    """Giữ bản cấu hình web mới nhất và áp vào bot đang chạy (qua hàm apply)."""

    def __init__(self, base: Settings, apply: Callable[[Settings], None]) -> None:
        self.base = base  # cấu hình từ settings.env (khi web bỏ một thông số, quay về giá trị này)
        self._apply = apply
        cached = read_cached(base)
        self.version = int(cached.get("version") or 0)
        self.values: dict[str, Any] = dict(cached.get("values") or {})
        self.files: dict[str, str] = dict(cached.get("files") or {})
        self.current = base

    def settings(self) -> Settings:
        fields, _ = overrides(self.values)
        return dataclasses.replace(self.base, **fields)

    def apply(self) -> Settings:
        self.current = self.settings()
        self._write_files()
        self._apply(self.current)
        return self.current

    def update(self, payload: dict[str, Any] | None) -> bool:
        """Nhận cấu hình từ web. Trả về True nếu có bản mới (đã áp và lưu)."""
        if not isinstance(payload, dict) or "version" not in payload:
            return False
        version = int(payload.get("version") or 0)
        values = payload.get("values") if isinstance(payload.get("values"), dict) else {}
        files = payload.get("files") if isinstance(payload.get("files"), dict) else {}
        if version == self.version and values == self.values and files == self.files:
            return False
        _, ignored = overrides(values)
        secret_like = [k for k in ignored if k not in REMOTE_KEYS]
        if secret_like:
            log.warning("Web gửi thông số không được phép đổi từ xa, đã bỏ qua: %s", ", ".join(secret_like))
        self.version, self.values = version, {k: v for k, v in values.items() if k in REMOTE_KEYS}
        self.files = {k: str(v) for k, v in files.items() if k in WORKSPACE_FILES and isinstance(v, str)}
        self._save()
        self.apply()
        log.info("Đã áp cấu hình từ web (bản %d): %s", version, ", ".join(sorted(self.values)) or "không có thông số")
        return True

    def _save(self) -> None:
        from bot.core.vietnam_time import now_ms

        data = {"version": self.version, "values": self.values, "files": self.files, "fetched_at": now_ms()}
        try:
            atomic_write_text(cache_path(self.base), json.dumps(data, ensure_ascii=False, indent=2))
        except OSError:
            log.exception("Không lưu được %s", REMOTE_CONFIG_FILE)

    def _write_files(self) -> None:
        """SYSTEM.md / MEMORY.md do web đặt: ghi vào workspace (bot tự nạp lại), giữ bản cũ trong .backup."""
        from bot.core.vietnam_time import now_vn

        for name, text in self.files.items():
            path = self.base.workspace_dir / name
            try:
                old = path.read_text(encoding="utf-8") if path.exists() else None
                if old == text:
                    continue
                if old:
                    atomic_write_text(path.parent / ".backup" / f"{path.stem}-{now_vn():%Y%m%d-%H%M%S}-truoc-khi-web-doi.md", old)
                atomic_write_text(path, text)
                log.info("Đã cập nhật %s theo cấu hình trên web", name)
            except OSError:
                log.exception("Không ghi được %s", path)


class LastError(logging.Handler):
    """Giữ lỗi gần nhất trong log để báo lên web qua nhịp tim."""

    def __init__(self) -> None:
        super().__init__(level=logging.ERROR)
        self.message: str | None = None
        self.at_ms: int | None = None

    def emit(self, record: logging.LogRecord) -> None:
        from bot.core.vietnam_time import now_ms

        try:
            self.message = record.getMessage()[:300]
            self.at_ms = now_ms()
        except Exception:  # noqa: BLE001 - không được làm hỏng việc ghi log
            pass


class RemoteSync:
    """Nhịp tim mỗi phút + nhận cấu hình mới. Lỗi mạng chỉ ghi log, bot vẫn chạy với bản cấu hình đang có."""

    def __init__(self, remote: RemoteConfig, status: Callable[[], dict[str, Any]], *,
                 interval: float = HEARTBEAT_SECONDS) -> None:
        self.remote = remote
        self.status = status
        self.interval = interval
        self.last_ok: bool | None = None

    async def fetch_config(self) -> bool:
        result = await server_client.request("GET", "/config", timeout=15)
        if isinstance(result, dict) and "error" in result:
            log.warning("Chưa lấy được cấu hình từ web (%s), dùng bản đang có", result["error"])
            return False
        return self.remote.update(result)

    async def beat(self) -> bool:
        body = {**self.status(), "configVersion": self.remote.version}
        result = await server_client.request("POST", "/heartbeat", json=body, timeout=15)
        ok = not (isinstance(result, dict) and "error" in result)
        if ok != self.last_ok:
            (log.info if ok else log.warning)("Kết nối web: %s", "ổn" if ok else result.get("error"))
            self.last_ok = ok
        if ok and isinstance(result, dict) and result.get("config"):
            self.remote.update(result["config"])
        return ok

    async def run(self, stop: asyncio.Event) -> None:
        await self.fetch_config()
        while not stop.is_set():
            try:
                await self.beat()
            except Exception:  # noqa: BLE001 - nhịp tim lỗi không được làm sập bot
                log.exception("Nhịp tim lỗi")
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
