"""Chuẩn bị userdata/ ở lần chạy đầu: tạo thư mục và file mẫu còn thiếu, không ghi đè (xem bot/userdata_paths.py)."""

from __future__ import annotations

import dataclasses
import logging
import secrets
import shutil
from pathlib import Path

from bot.config import APP_HOME, ENV_FILE, Settings
from bot.userdata_paths import CONFIG_REL, DATA_REL, ENV_REL, LOGS_REL, SYSTEM_REL, TOOLS_REL, WORKSPACE_REL

log = logging.getLogger(__name__)

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"

_DIRS = (CONFIG_REL, DATA_REL, WORKSPACE_REL, TOOLS_REL, SYSTEM_REL, LOGS_REL)
# (file mẫu trong src/bot/templates, đích so với APP_HOME)
_FILES = (
    ("env.example", ENV_REL),
    ("SYSTEM.md", WORKSPACE_REL + "/SYSTEM.md"),
    ("MEMORY.md", WORKSPACE_REL + "/MEMORY.md"),
    ("tool_example.py.tmpl", TOOLS_REL + "/_example.py"),
)


def ensure_home(home: Path = APP_HOME) -> list[str]:
    """Tạo userdata/config, data, system... và các file mẫu còn thiếu. Trả về danh sách file vừa tạo."""
    created: list[str] = []
    for directory in _DIRS:
        (home / directory).mkdir(parents=True, exist_ok=True)
    for template, target in _FILES:
        destination = home / target
        if not destination.exists():
            shutil.copyfile(TEMPLATES / template, destination)
            created.append(target)
    if created:
        log.info("Đã tạo file mẫu: %s", ", ".join(created))
    return created


def ensure_admin_token(settings: Settings, env_path: Path | None = None) -> tuple[Settings, bool]:
    """Không bao giờ chạy giao diện khi chưa có mã truy cập: tạo mã ngẫu nhiên và lưu vào .env.

    Trả về (settings mới, có vừa tạo mã hay không).
    """
    if settings.admin_token:
        return settings, False
    from bot.ui.admin import settings_file

    token = secrets.token_urlsafe(32)
    settings_file.update(env_path or ENV_FILE, {"ADMIN_TOKEN": token})
    return dataclasses.replace(settings, admin_token=token), True
