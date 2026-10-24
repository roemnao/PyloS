"""Đọc/ghi file .env cho trang Cài đặt.

- Giữ nguyên chú thích và thứ tự dòng; chỉ thay dòng KEY=... cần đổi (hoặc thêm vào cuối).
- Lưu bản cũ vào .env.bak trước khi ghi, ghi nguyên tử.
- Chỉ cho sửa các khóa trong danh sách cho phép; khóa bí mật chỉ được ghi, không bao giờ đọc ra.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

from bot.config import ConfigError, Settings
from bot.storage import atomic_write_text


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    help: str = ""
    kind: str = "text"  # text | int | bool | choice
    choices: tuple[str, ...] = field(default_factory=tuple)
    group: str = "Chung"


FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("OWNER_ZALO_ID", "ID Zalo của chủ bot", "Người được dùng /mode, /allow... Xem bằng lệnh /id."),
    FieldSpec("ALLOW_ALL_CHATS", "Cho phép mọi cuộc trò chuyện",
              "Bật: bot trả lời ở mọi nhóm và chat riêng, không cần /allow (chat bị /deny vẫn bị chặn). "
              "Tắt: chỉ các chat đã /allow.", kind="bool"),
    FieldSpec("BOT_TRIGGERS", "Từ gọi bot", "Ở chế độ default, chỉ trả lời tin bắt đầu bằng các từ này (cách nhau dấu phẩy)."),
    FieldSpec("GEMINI_MODEL", "Model Gemini", "Ví dụ gemini-3.1-flash-lite.", group="Gemini"),
    FieldSpec("MAX_OUTPUT_TOKENS", "Token tối đa mỗi câu trả lời", kind="int", group="Gemini"),
    FieldSpec("LLM_TIMEOUT_SECONDS", "Thời gian chờ Gemini (giây)", kind="int", group="Gemini"),
    FieldSpec("HISTORY_TURNS", "Số lượt hội thoại đưa vào prompt", kind="int", group="Gemini"),
    FieldSpec("MAX_TOOL_ROUNDS", "Số vòng gọi tool tối đa", kind="int", group="Gemini"),
    FieldSpec("DAILY_TOKEN_BUDGET", "Hạn mức token mỗi ngày", "0 = không giới hạn.", kind="int", group="Giới hạn"),
    FieldSpec("USER_RATE_PER_MIN", "Số tin mỗi phút / người", "0 = không giới hạn.", kind="int", group="Giới hạn"),
    FieldSpec("CHAT_RATE_PER_MIN", "Số tin mỗi phút / nhóm", "0 = không giới hạn.", kind="int", group="Giới hạn"),
    FieldSpec("RECEIVE_MODE", "Cách nhận tin", "polling: không cần domain. webhook: cần URL HTTPS công khai.",
              kind="choice", choices=("polling", "webhook"), group="Kết nối"),
    FieldSpec("WEBHOOK_HOST", "Webhook: địa chỉ lắng nghe", group="Kết nối"),
    FieldSpec("WEBHOOK_PORT", "Webhook: cổng", kind="int", group="Kết nối"),
    FieldSpec("LOG_LEVEL", "Mức log", kind="choice", choices=("DEBUG", "INFO", "WARNING", "ERROR"), group="Kết nối"),
    FieldSpec("ADMIN_SHOW_HISTORY", "Hiện trang Hội thoại", kind="bool", group="Giao diện"),
)
FIELD_KEYS = {f.key for f in FIELDS}

SECRETS: dict[str, str] = {
    "ZALO_BOT_TOKEN": "Bot token Zalo",
    "GEMINI_API_KEY": "API key Gemini",
    "WEBHOOK_SECRET": "Webhook secret (8–256 ký tự)",
}

_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
# Ký tự làm sai cách python-dotenv đọc giá trị không có ngoặc, hoặc chèn thêm dòng.
_FORBIDDEN = re.compile(r"[\r\n\"'#\\\x00]")


def read_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return {k: (v or "") for k, v in dotenv_values(path).items()}


def clean_value(key: str, value: str) -> str:
    value = str(value).strip()
    if _FORBIDDEN.search(value):
        raise ConfigError(f"{key}: không được chứa xuống dòng, dấu nháy, # hoặc \\")
    if len(value) > 4096:
        raise ConfigError(f"{key}: quá dài")
    return value


def validate(path: Path, changes: dict[str, str], base_dir: Path) -> dict[str, str]:
    """Làm sạch và kiểm tra thay đổi bằng chính quy tắc của bot (Settings.from_env)."""
    cleaned = {key: clean_value(key, value) for key, value in changes.items()}
    for spec in FIELDS:
        if spec.key in cleaned and spec.kind == "choice" and cleaned[spec.key] and cleaned[spec.key] not in spec.choices:
            raise ConfigError(f"{spec.label}: phải là một trong {', '.join(spec.choices)}")
    if "WEBHOOK_SECRET" in cleaned and cleaned["WEBHOOK_SECRET"] and not 8 <= len(cleaned["WEBHOOK_SECRET"]) <= 256:
        raise ConfigError("WEBHOOK_SECRET phải dài 8–256 ký tự")
    Settings.from_env({**read_values(path), **cleaned}, base_dir=base_dir)  # ném ConfigError nếu sai
    return cleaned


def update(path: Path, changes: dict[str, str]) -> None:
    """Ghi các thay đổi đã kiểm tra vào .env, giữ chú thích, sao lưu bản cũ vào .env.bak."""
    old_text = path.read_text(encoding="utf-8") if path.is_file() else ""
    lines = old_text.splitlines()
    pending = dict(changes)
    for index, line in enumerate(lines):
        match = _LINE.match(line)
        if match and match.group(1) in pending:
            key = match.group(1)
            lines[index] = f"{key}={pending.pop(key)}"
    lines.extend(f"{key}={value}" for key, value in pending.items())
    if old_text:
        atomic_write_text(path.with_name(path.name + ".bak"), old_text)
    atomic_write_text(path, "\n".join(lines) + "\n")
