from __future__ import annotations

import subprocess

import pytest
from fastapi.testclient import TestClient

from bot.config import Settings
from bot.system import bot_process, server_info
from bot.ui.admin.admin_web_server import AdminContext, create_app

TOKEN = "admin-token-123456"
BASE = "http://127.0.0.1:8081"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def make_settings(tmp_path, **env):
    values = {"ZALO_BOT_TOKEN": "1:abc", "GEMINI_API_KEY": "key", "ADMIN_TOKEN": TOKEN, **env}
    return Settings.from_env(values, base_dir=tmp_path)


def test_supervisor_value_is_validated(tmp_path):
    with pytest.raises(Exception, match="BOT_SUPERVISOR"):
        make_settings(tmp_path, BOT_SUPERVISOR="docker")
    assert make_settings(tmp_path).bot_supervisor == "process"


def test_standby_blocks_start_until_forced(tmp_path):
    settings = make_settings(tmp_path)
    assert bot_process.standby_info(settings) is None
    bot_process.set_standby(settings, "Bot đang chạy ở VPS.")
    info = bot_process.standby_info(settings)
    assert info and "VPS" in info["reason"]
    result = bot_process.start(settings)
    assert result.code == 1 and "chế độ chờ" in result.message
    bot_process.clear_standby(settings)
    assert bot_process.standby_info(settings) is None


def test_systemd_start_and_stop_call_sudo_systemctl(tmp_path, monkeypatch):
    settings = make_settings(tmp_path, BOT_SUPERVISOR="systemd")
    monkeypatch.setattr(bot_process, "uses_systemd", lambda settings, service: service is bot_process.BOT)
    calls = []

    def fake_run(cmd, timeout=20, cwd=None):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(bot_process, "run_hidden", fake_run)
    monkeypatch.setattr(bot_process, "_wait", lambda predicate, seconds: True)
    assert bot_process.start(settings).ok
    assert calls[-1] == ["sudo", "-n", "systemctl", "start", "pylos-bot"]
    assert bot_process.stop(settings).ok
    assert calls[-1] == ["sudo", "-n", "systemctl", "stop", "pylos-bot"]


def test_systemd_failure_is_reported(tmp_path, monkeypatch):
    settings = make_settings(tmp_path, BOT_SUPERVISOR="systemd")
    monkeypatch.setattr(bot_process, "uses_systemd", lambda settings, service: service is bot_process.BOT)
    monkeypatch.setattr(bot_process, "run_hidden",
                        lambda cmd, timeout=20, cwd=None: subprocess.CompletedProcess(cmd, 1, b"", b"sudo: a password is required"))
    result = bot_process.start(settings)
    assert not result.ok and "password" in result.message


def test_run_command_exits_in_standby(tmp_path, monkeypatch):
    from bot import command_line

    settings = make_settings(tmp_path)
    bot_process.set_standby(settings, "Bot đang chạy ở VPS.")
    monkeypatch.setattr(command_line, "setup_logging", lambda *a, **k: None)
    monkeypatch.setattr(Settings, "from_env", classmethod(lambda cls, *a, **k: settings))
    assert command_line.main(["run"]) == bot_process.EXIT_STANDBY


def test_api_server_returns_info_without_secrets(tmp_path):
    (tmp_path / "userdata" / "config").mkdir(parents=True)
    env = tmp_path / ".env"
    env.write_text(f"ADMIN_TOKEN={TOKEN}\nZALO_BOT_TOKEN=999:secret\nDATA_DIR=data\nWORKSPACE_DIR=ws\nLOG_DIR=logs\n", encoding="utf-8")
    client = TestClient(create_app(AdminContext(env, tmp_path), 8081), base_url=BASE)
    res = client.get("/api/server", headers=AUTH)
    assert res.status_code == 200
    body = res.json()
    assert body["hostname"] and "version" in body and body["bot"]["running"] is False
    assert "999:secret" not in res.text


def test_collect_skips_systemd_on_non_systemd(tmp_path):
    info = server_info.collect(make_settings(tmp_path))
    assert info["units"] is None and info["supervisor"] == "process"
