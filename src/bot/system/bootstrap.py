"""Chuẩn bị thư mục ứng dụng (APP_HOME) ở lần chạy đầu: tạo file mẫu nếu còn thiếu, không ghi đè."""

from __future__ import annotations

import dataclasses
import logging
import secrets
import shutil
from pathlib import Path

from bot.config import APP_HOME, Settings, is_frozen

log = logging.getLogger(__name__)

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"

# (file mẫu trong exe, đích trong APP_HOME)
_FILES = (
    ("env.example", ".env"),
    ("SYSTEM.md", "workspace/SYSTEM.md"),
    ("MEMORY.md", "workspace/MEMORY.md"),
)


def ensure_home(home: Path = APP_HOME, frozen: bool | None = None) -> list[str]:
    """Tạo data/, logs/, workspace/ và các file mẫu còn thiếu. Trả về danh sách file vừa tạo."""
    created: list[str] = []
    for directory in ("data", "logs", "workspace"):
        (home / directory).mkdir(parents=True, exist_ok=True)
    for template, target in _FILES:
        destination = home / target
        if not destination.exists():
            shutil.copyfile(TEMPLATES / template, destination)
            created.append(target)
    # Khi chạy từ exe, tool người dùng thêm vào nằm ở tools/ cạnh exe; đặt sẵn file mẫu ở đó.
    if (is_frozen() if frozen is None else frozen) and not (home / "tools").exists():
        (home / "tools").mkdir(parents=True)
        shutil.copyfile(TEMPLATES / "tool_example.py.tmpl", home / "tools" / "_example.py")
        created.append("tools/_example.py")
    if created:
        log.info("Đã tạo file mẫu: %s", ", ".join(created))
    return created


def ensure_admin_token(settings: Settings, env_path: Path | None = None) -> tuple[Settings, bool]:
    """Không bao giờ chạy giao diện khi chưa có mã truy cập: tạo mã ngẫu nhiên và lưu vào .env.

    Trả về (settings mới, có vừa tạo mã hay không).
    """
    if settings.admin_token:
        return settings, False
    from bot.ui.admin import envfile

    token = secrets.token_urlsafe(32)
    envfile.update(env_path or APP_HOME / ".env", {"ADMIN_TOKEN": token})
    return dataclasses.replace(settings, admin_token=token), True
