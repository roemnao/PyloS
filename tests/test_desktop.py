from __future__ import annotations

import logging
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import make_settings

from bot.system import bootstrap, gateway

from bot import config, paths
from bot.agent.tools import discover

ROOT = Path(__file__).resolve().parents[1]


# ---------- thư mục ứng dụng ----------

def test_app_home_from_source_is_project_root(monkeypatch):
    monkeypatch.delenv("ZALOBOT_HOME", raising=False)
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert paths.app_home() == ROOT


def test_app_home_when_frozen_is_exe_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("ZALOBOT_HOME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "app" / "ZaloBot.exe"))
    assert paths.app_home() == (tmp_path / "app").resolve()


def test_app_home_falls_back_to_localappdata_when_not_writable(monkeypatch, tmp_path):
    monkeypatch.delenv("ZALOBOT_HOME", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "ProgramFiles" / "ZaloBot.exe"))
    monkeypatch.setattr(paths, "_writable", lambda _: False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert paths.app_home() == tmp_path / "local" / "ZaloAssistantBot"


def test_app_home_override(monkeypatch, tmp_path):
    monkeypatch.setenv("ZALOBOT_HOME", str(tmp_path))
    assert paths.app_home() == tmp_path.resolve()


@pytest.mark.skipif(sys.platform != "win32", reason="chỉ Windows mở cửa sổ console")
def test_system_commands_never_open_a_console_window(monkeypatch):
    seen = []
    real_run = subprocess.run

    def spy(cmd, **kwargs):
        seen.append((cmd[0], kwargs.get("creationflags", 0), kwargs.get("startupinfo")))
        return real_run([sys.executable, "-c", "pass"], capture_output=True)

    monkeypatch.setattr(gateway.subprocess, "run", spy)
    monkeypatch.setattr(gateway, "_task_cache", {})
    gateway.task_installed(gateway.BOT)
    gateway._kill(0)
    monkeypatch.setattr(gateway, "task_installed", lambda service: True)
    gateway._end_task(gateway.BOT)
    assert [name for name, *_ in seen] == ["schtasks", "taskkill", "schtasks"]
    for name, flags, startup in seen:
        assert flags & subprocess.CREATE_NO_WINDOW, name
        assert startup is not None and startup.wShowWindow == subprocess.SW_HIDE, name


def test_no_visible_subprocess_calls_left_in_source():
    """Mọi lời gọi tiến trình con trong src phải đi qua run_hidden/_spawn (hai chỗ đã ẩn cửa sổ)."""
    import re

    offenders = []
    for path in (ROOT / "src").rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"subprocess\.(run|call|check_output|check_call)\(", line):
                offenders.append(path.relative_to(ROOT).as_posix())
    # đúng một chỗ được phép: bên trong run_hidden
    assert offenders == ["src/bot/system/gateway.py"]


def test_frozen_child_gets_its_own_unpack_dir(monkeypatch):
    captured = {}

    def fake_popen(cmd, **kwargs):
        captured.update(kwargs)
        return None

    monkeypatch.setattr(gateway.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    gateway._spawn(gateway.BOT)
    assert captured["env"]["PYINSTALLER_RESET_ENVIRONMENT"] == "1"
    monkeypatch.delattr(sys, "frozen")
    gateway._spawn(gateway.BOT)
    assert "PYINSTALLER_RESET_ENVIRONMENT" not in captured["env"]


def test_spawn_command_source_and_frozen(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert gateway.spawn_command(gateway.BOT) == [sys.executable, "-m", "bot", "run"]
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert gateway.spawn_command(gateway.BOT) == [sys.executable, "run"]
    assert gateway.spawn_command(gateway.ADMIN) == [sys.executable, "admin"]


# ---------- lần chạy đầu ----------

def test_ensure_home_creates_userdata_without_overwriting(tmp_path):
    env = tmp_path / "userdata" / "config" / ".env"
    env.parent.mkdir(parents=True)
    env.write_text("ZALO_BOT_TOKEN=keep-me\n", encoding="utf-8")
    created = bootstrap.ensure_home(tmp_path)
    assert set(created) == {"userdata/data/workspace/SYSTEM.md", "userdata/data/workspace/MEMORY.md",
                            "userdata/data/tools/_example.py"}
    assert env.read_text(encoding="utf-8") == "ZALO_BOT_TOKEN=keep-me\n"
    for directory in ("config", "data", "data/workspace", "data/tools", "system", "system/logs"):
        assert (tmp_path / "userdata" / directory).is_dir()
    assert bootstrap.ensure_home(tmp_path) == []

    fresh = tmp_path / "fresh"
    assert "userdata/config/.env" in bootstrap.ensure_home(fresh)


def test_env_template_keeps_data_inside_userdata(tmp_path):
    """Mẫu .env (app chép vào userdata/config/.env) không được trỏ dữ liệu về chỗ cũ data/, logs/..."""
    from dotenv import dotenv_values

    template = ROOT / "src" / "bot" / "templates" / "env.example"
    env = {k: v or "" for k, v in dotenv_values(template).items()}
    s = config.Settings.from_env(env, base_dir=tmp_path)
    for path in (s.data_dir, s.workspace_dir, s.log_dir, s.system_dir, s.zalo_session_file):
        assert (tmp_path / "userdata") in path.parents, path


def test_ensure_admin_token_writes_once(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# x\nADMIN_TOKEN=\n", encoding="utf-8")
    settings = make_settings(tmp_path, ADMIN_TOKEN="")
    updated, created = bootstrap.ensure_admin_token(settings, env)
    assert created and len(updated.admin_token) > 30
    assert f"ADMIN_TOKEN={updated.admin_token}" in env.read_text(encoding="utf-8")
    assert bootstrap.ensure_admin_token(updated, env) == (updated, False)


# ---------- tool ngoài exe ----------

def test_external_tools_are_loaded_and_broken_ones_skipped(tmp_path, caplog):
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "hello.py").write_text(
        "from bot.agent.tools import Tool\n"
        "TOOLS = [Tool('hello', 'chào', lambda a, c: 'hi')]\n", encoding="utf-8")
    (tools / "broken.py").write_text("raise RuntimeError('hỏng')\n", encoding="utf-8")
    (tools / "_example.py").write_text("raise RuntimeError('không được nạp')\n", encoding="utf-8")
    with caplog.at_level(logging.ERROR):
        registry = discover(tools)
    assert registry.names() == ["doc_memorydata", "hello"]  # tool có sẵn + tool ngoài
    assert "broken.py" in caplog.text


# ---------- dừng bot êm qua file cờ ----------

HELPER = """
import sys, time
from pathlib import Path
from bot.storage.lock import InstanceLock
data = Path(sys.argv[1])
with InstanceLock(data / "bot.lock"):
    (data / "bot.pid").write_text("999999", encoding="utf-8")  # pid giả: nếu bị ép tắt thì test sẽ lộ
    (data / "ready").write_text("1", encoding="utf-8")
    while not (data / "bot.stop").exists():
        time.sleep(0.1)
"""


def test_gateway_stops_bot_gracefully_with_flag(tmp_path):
    settings = make_settings(tmp_path)
    settings.system_dir.mkdir(parents=True)  # khoá, pid, cờ dừng nằm ở userdata/system
    proc = subprocess.Popen([sys.executable, "-c", HELPER, str(settings.system_dir)])
    try:
        assert gateway._wait(lambda: (settings.system_dir / "ready").exists(), 20)
        assert gateway.is_running(settings, gateway.BOT)
        result = gateway.stop(settings, gateway.BOT)
        assert result.ok, result.message
        assert proc.wait(timeout=10) == 0  # tự thoát, không bị taskkill
        assert not gateway.stop_flag(settings).exists()
        assert not gateway.pid_path(settings).exists()
    finally:
        if proc.poll() is None:
            proc.kill()


# ---------- linh tinh ----------

def test_logging_without_console(monkeypatch, tmp_path):
    from bot.system.logging_setup import setup_logging

    monkeypatch.setattr(sys, "stderr", None)
    setup_logging("INFO", tmp_path, ["secret-value"], filename="gui.log")
    logging.getLogger("x").info("hello secret-value")
    for handler in logging.getLogger().handlers:
        handler.flush()
    text = (tmp_path / "gui.log").read_text(encoding="utf-8")
    assert "hello ***" in text
    logging.getLogger().handlers.clear()


def test_free_port_skips_busy_port():
    from bot.ui.desktop.app import _free_port

    with socket.socket() as busy:
        busy.bind(("127.0.0.1", 0))
        port = busy.getsockname()[1]
        assert _free_port(port) != port


def test_autostart_command(monkeypatch):
    from bot.ui.desktop import autostart

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"D:\app\ZaloBot.exe")
    assert autostart.command() == r'"D:\app\ZaloBot.exe" gui --tray --start-bot'
    monkeypatch.delattr(sys, "frozen")
    assert autostart.command().endswith('-m bot gui --tray --start-bot')


@pytest.mark.skipif(sys.platform != "win32", reason="registry chỉ có trên Windows")
def test_autostart_registry_roundtrip(monkeypatch):
    from bot.ui.desktop import autostart

    monkeypatch.setattr(autostart, "VALUE_NAME", "ZaloAssistantBot-pytest")  # không đụng mục thật
    try:
        autostart.set_enabled(True)
        assert autostart.is_enabled()
        autostart.set_enabled(False)
        assert not autostart.is_enabled()
    finally:
        autostart.set_enabled(False)


def test_desktop_bot_actions_report_to_tray(monkeypatch, tmp_path):
    from bot.ui.desktop.app import Desktop

    settings = make_settings(tmp_path)
    desktop = Desktop(settings, tray_only=True, start_bot=False)
    notes = []
    desktop.tray = type("T", (), {"notify": lambda self, m: notes.append(m), "refresh": lambda self: None})()
    monkeypatch.setattr(desktop, "settings_now", lambda: settings)
    monkeypatch.setattr(gateway, "start", lambda s, svc: gateway.Result(0, "Đã bật bot (pid 1).\nchi tiết"))
    desktop._run_bot_action("start")
    assert notes == ["Đã bật bot (pid 1)."] and not desktop.busy

    def broken(s, svc):
        raise config.ConfigError("Thiếu biến môi trường: ZALO_BOT_TOKEN")

    shown = []
    monkeypatch.setattr(gateway, "stop", broken)
    monkeypatch.setattr(desktop, "show_window", lambda *_: shown.append(True))
    desktop._run_bot_action("stop")
    assert "ZALO_BOT_TOKEN" in notes[-1] and shown == [True]


def test_icons(tmp_path):
    from bot.ui.desktop.icons import make_icon, write_ico

    assert make_icon("running").size == (64, 64)
    assert make_icon().getpixel((32, 4))[3] == 255
    ico = write_ico(tmp_path / "x.ico")
    assert ico.read_bytes()[:4] == b"\x00\x00\x01\x00"


def test_check_secrets_finds_leaks(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "packaging"))
    try:
        import check_secrets
    finally:
        sys.path.pop(0)
    env = tmp_path / ".env"
    env.write_text("ZALO_BOT_TOKEN=very-secret-token\nGEMINI_API_KEY=\n", encoding="utf-8")
    secrets = check_secrets.secrets_from_env(env)
    assert b"very-secret-token" in secrets
    build = tmp_path / "build"
    build.mkdir()
    (build / "clean.txt").write_text("nothing here", encoding="utf-8")
    assert check_secrets.check_dir(build, secrets) == []
    (build / "leak.txt").write_text("x very-secret-token y", encoding="utf-8")
    assert len(check_secrets.check_dir(build, secrets)) == 1
