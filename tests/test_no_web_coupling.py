"""PyloS chỉ nói chuyện với web bot lịch để giao lịch và liên kết Zalo, không còn việc nào khác."""

from __future__ import annotations

import re
from pathlib import Path

from conftest import event

SRC = Path(__file__).resolve().parents[1] / "src"
ALLOWED = {"/zalo-link", "/assign", "/events", "/tasks", "/agenda", "/message"}


def test_no_module_for_remote_config_sessions_or_heartbeat():
    assert not (SRC / "bot/system/remote_config.py").exists()
    assert not (SRC / "bot/system/session_upload.py").exists()


def test_source_has_no_forbidden_web_paths():
    forbidden = ("/heartbeat", "/sessions", "/device-login", '"/config"', "system.remote_config", "system.session_upload", "SESSION_UPLOAD", "session_upload")
    hits = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        hits += [f"{path.relative_to(SRC)}: {f}" for f in forbidden if f in text]
    assert not hits, hits


def test_server_client_paths_are_only_scheduling_paths():
    paths = set()
    for path in SRC.rglob("*.py"):
        for m in re.finditer(r'request\(\s*"(?:GET|POST|PATCH|DELETE|PUT)",\s*f?"(/[a-z-]+)', path.read_text(encoding="utf-8")):
            paths.add(m.group(1))
    assert paths <= ALLOWED, paths - ALLOWED


async def test_bot_never_calls_web_on_plain_message(make_bot, web):
    bot = make_bot()
    await bot.handle_payload(event("/bot xin chào"))
    await bot.drain()
    assert web.calls == []
