"""Đọc cấu hình từ biến môi trường / file .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

from bot.userdata_paths import (  # noqa: F401 - các tên này được import từ bot.config ở nhiều nơi
    APP_HOME,
    APP_NAME,
    DATA_REL,
    ENV_FILE,
    ENV_REL,
    LOGS_REL,
    SESSION_REL,
    SYSTEM_REL,
    WORKSPACE_REL,
    app_home,
    is_frozen,
)

# Giữ tên PROJECT_ROOT cho code cũ; khi chạy từ exe nó là thư mục chứa exe.
PROJECT_ROOT = APP_HOME

# Các biến được nạp từ .env (không phải biến môi trường thật). Khi bật tiến trình con,
# gateway bỏ chúng đi để tiến trình con đọc .env mới nhất thay vì thừa hưởng giá trị cũ.
LOADED_FROM_DOTENV: set[str] = set()


class ConfigError(Exception):
    """Cấu hình thiếu hoặc sai; thông báo đã sẵn sàng để in cho người dùng."""


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _int(env: dict[str, str], name: str, default: int, minimum: int = 0) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} phải là số nguyên, đang là {raw!r}") from exc
    if value < minimum:
        raise ConfigError(f"{name} phải >= {minimum}, đang là {value}")
    return value


def _bool(env: dict[str, str], name: str, default: bool) -> bool:
    raw = env.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in ("1", "true", "yes", "on", "có"):
        return True
    if raw in ("0", "false", "no", "off", "không"):
        return False
    raise ConfigError(f"{name} phải là true hoặc false, đang là {raw!r}")


@dataclass(frozen=True)
class Settings:
    zalo_bot_token: str
    gemini_api_key: str
    gemini_model: str
    owner_zalo_id: str
    allowed_chat_ids: tuple[str, ...]
    bot_triggers: tuple[str, ...]
    receive_mode: str
    webhook_secret: str
    webhook_host: str
    webhook_port: int
    data_dir: Path
    workspace_dir: Path
    log_dir: Path
    log_level: str
    history_turns: int
    max_tool_rounds: int
    max_output_tokens: int
    llm_timeout_seconds: int
    user_rate_per_min: int
    chat_rate_per_min: int
    daily_token_budget: int
    admin_token: str = ""
    admin_port: int = 8081
    admin_show_history: bool = True
    allow_all_chats: bool = False
    # RECEIVE_MODE=personal: chạy trên acc Zalo cá nhân thay cho Zalo Bot (xem bot/zalo/personal_account.py)
    zalo_imei: str = ""
    # Tên gọi bot: tin trong nhóm nhắc tới một trong các tên này (hoặc @tag acc bot) thì bot trả lời, không cần /bot
    bot_names: tuple[str, ...] = ("bot",)
    # Bộ lọc tin nhóm (bot/core/message_filter.py) và memorydata (mọi tin của từng hội thoại)
    filter_ai: bool = True
    filter_model: str = ""
    filter_context_lines: int = 6
    memorydata_keep: int = 5000
    schedule_api_key: str = ""
    # Ai được giao lịch cho người khác qua bot lịch: "owner" (chỉ chủ bot) hoặc "all"
    assign_allowed: str = "owner"
    # Gửi session bộ lọc ↔ agent lên web để chủ hệ thống xem lại (trang Hệ thống → Session)
    session_upload: bool = True
    zalo_session_file: Path = Path(SESSION_REL)
    # Thư mục hệ thống tự quản lý: log, khoá tiến trình, trạng thái (xem bot/userdata_paths.py)
    system_dir: Path = Path(SYSTEM_REL)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None, base_dir: Path | None = None) -> Settings:
        if env is None:
            # Chỉ đọc userdata/config/settings.env: exe được Windows bật lúc đăng nhập có thư mục làm việc bất kỳ,
            # tìm .env theo thư mục làm việc có thể đọc nhầm file của chương trình khác.
            candidate = APP_HOME / ENV_REL
            if candidate.is_file():
                for key, value in dotenv_values(candidate).items():
                    if key not in os.environ and value is not None:
                        os.environ[key] = value
                        LOADED_FROM_DOTENV.add(key)
            env = dict(os.environ)
        # Đường dẫn tương đối tính từ APP_HOME (thư mục chứa userdata/), không phụ thuộc nơi chạy.
        base = base_dir or PROJECT_ROOT

        def path(name: str, default: str) -> Path:
            p = Path(env.get(name, "").strip() or default)
            return p if p.is_absolute() else base / p

        receive_mode = env.get("RECEIVE_MODE", "").strip().lower() or "polling"
        if receive_mode not in ("polling", "webhook", "personal"):
            raise ConfigError(
                f"RECEIVE_MODE phải là 'polling', 'webhook' hoặc 'personal', đang là {receive_mode!r}"
            )

        assign_allowed = env.get("ASSIGN_ALLOWED", "").strip().lower() or "owner"
        if assign_allowed not in ("owner", "all"):
            raise ConfigError(f"ASSIGN_ALLOWED phải là 'owner' hoặc 'all', đang là {assign_allowed!r}")

        return cls(
            zalo_bot_token=env.get("ZALO_BOT_TOKEN", "").strip(),
            gemini_api_key=env.get("GEMINI_API_KEY", "").strip(),
            gemini_model=env.get("GEMINI_MODEL", "").strip() or "gemini-3.1-flash-lite",
            owner_zalo_id=env.get("OWNER_ZALO_ID", "").strip(),
            allowed_chat_ids=_csv(env.get("ALLOWED_CHAT_IDS", "")),
            bot_triggers=_csv(env.get("BOT_TRIGGERS", "")) or ("/bot",),
            receive_mode=receive_mode,
            webhook_secret=env.get("WEBHOOK_SECRET", "").strip(),
            webhook_host=env.get("WEBHOOK_HOST", "").strip() or "127.0.0.1",
            webhook_port=_int(env, "WEBHOOK_PORT", 8080, minimum=1),
            data_dir=path("DATA_DIR", DATA_REL),
            workspace_dir=path("WORKSPACE_DIR", WORKSPACE_REL),
            log_dir=path("LOG_DIR", LOGS_REL),
            system_dir=path("SYSTEM_DIR", SYSTEM_REL),
            log_level=env.get("LOG_LEVEL", "").strip().upper() or "INFO",
            history_turns=_int(env, "HISTORY_TURNS", 20, minimum=1),
            max_tool_rounds=_int(env, "MAX_TOOL_ROUNDS", 4),
            max_output_tokens=_int(env, "MAX_OUTPUT_TOKENS", 1024, minimum=1),
            llm_timeout_seconds=_int(env, "LLM_TIMEOUT_SECONDS", 60, minimum=1),
            user_rate_per_min=_int(env, "USER_RATE_PER_MIN", 6),
            chat_rate_per_min=_int(env, "CHAT_RATE_PER_MIN", 20),
            daily_token_budget=_int(env, "DAILY_TOKEN_BUDGET", 200000),
            admin_token=env.get("ADMIN_TOKEN", "").strip(),
            admin_port=_int(env, "ADMIN_PORT", 8081, minimum=1),
            admin_show_history=_bool(env, "ADMIN_SHOW_HISTORY", True),
            allow_all_chats=_bool(env, "ALLOW_ALL_CHATS", False),
            zalo_imei=env.get("ZALO_IMEI", "").strip(),
            bot_names=_csv(env["BOT_NAMES"]) if "BOT_NAMES" in env else ("bot",),
            filter_ai=_bool(env, "FILTER_AI", True),
            filter_model=env.get("FILTER_MODEL", "").strip(),
            filter_context_lines=_int(env, "FILTER_CONTEXT_LINES", 6),
            memorydata_keep=_int(env, "MEMORYDATA_KEEP", 5000),
            schedule_api_key=env.get("SCHEDULE_API_KEY", "").strip(),
            assign_allowed=assign_allowed,
            session_upload=_bool(env, "SESSION_UPLOAD", True),
            zalo_session_file=path("ZALO_SESSION_FILE", SESSION_REL),
        )

    @property
    def personal(self) -> bool:
        return self.receive_mode == "personal"

    def require(self, *, zalo: bool = True, gemini: bool = True) -> None:
        """Dừng với thông báo rõ ràng nếu thiếu bí mật cần cho lệnh đang chạy."""
        missing = []
        if zalo and self.personal:
            from bot.zalo.personal_account import load_session

            load_session(self.zalo_session_file, self.zalo_imei)  # ném ConfigError nếu chưa đăng nhập bằng QR
        elif zalo and not self.zalo_bot_token:
            missing.append("ZALO_BOT_TOKEN")
        if gemini and not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if missing:
            raise ConfigError(
                "Thiếu biến môi trường: " + ", ".join(missing)
                + ". Hãy điền vào userdata/config/settings.env (hoặc trang Cài đặt của ứng dụng quản lý)."
            )
        if zalo and self.receive_mode == "webhook" and not (8 <= len(self.webhook_secret) <= 256):
            raise ConfigError("RECEIVE_MODE=webhook cần WEBHOOK_SECRET dài 8–256 ký tự.")

    @property
    def secrets(self) -> list[str]:
        return [
            s for s in (self.zalo_bot_token, self.gemini_api_key, self.webhook_secret, self.admin_token, self.zalo_imei,
                        self.schedule_api_key)
            if s
        ]
