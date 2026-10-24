from __future__ import annotations

import json
import subprocess

from bot import paths
from bot.storage.lock import InstanceLock


def legacy_home(tmp_path):
    """Bố cục của bản cũ: .env, data/, logs/, workspace/, tools/ ngay ở thư mục gốc."""
    home = tmp_path / "home"
    (home / "data" / "memorydata").mkdir(parents=True)
    (home / "data" / "history").mkdir()
    (home / "data" / "webview").mkdir()
    (home / "logs").mkdir()
    (home / "workspace" / ".backup").mkdir(parents=True)
    (home / "tools").mkdir()
    (home / ".env").write_text("# cài đặt\nGEMINI_API_KEY=k\nDATA_DIR=data\nWORKSPACE_DIR=workspace\nLOG_DIR=logs\n"
                               "BOT_NAMES=roemnao\n", encoding="utf-8")
    (home / ".env.bak").write_text("cũ", encoding="utf-8")
    (home / "data" / "zalo_session.json").write_text(json.dumps({"imei": "i", "cookies": {"a": "b"}}), encoding="utf-8")
    (home / "data" / "memorydata" / "g1.txt").write_text("{}\n", encoding="utf-8")
    (home / "data" / "history" / "g1.txt").write_text("{}\n", encoding="utf-8")
    for name in ("groups.txt", "stats.txt", "state.txt", "seen.txt"):
        (home / "data" / name).write_text("{}", encoding="utf-8")
    (home / "data" / "bot.lock").write_text("", encoding="utf-8")
    (home / "logs" / "bot.log").write_text("log", encoding="utf-8")
    (home / "workspace" / "SYSTEM.md").write_text("tính cách tôi đã sửa", encoding="utf-8")
    (home / "workspace" / "MEMORY.md").write_text("ghi nhớ", encoding="utf-8")
    (home / "tools" / "_example.py").write_text("# mẫu", encoding="utf-8")
    (home / "tools" / "thoi_tiet.py").write_text("TOOLS = []", encoding="utf-8")
    return home


def test_migrates_everything_to_userdata(tmp_path):
    home = legacy_home(tmp_path)
    assert paths.needs_migration(home)
    moved = paths.migrate_legacy(home)
    assert moved and not paths.needs_migration(home)

    u = home / "userdata"
    assert (u / "config" / ".env").is_file() and (u / "config" / ".env.bak").is_file()
    assert json.loads((u / "config" / "zalo_session.json").read_text(encoding="utf-8"))["imei"] == "i"
    for rel in ("data/memorydata/g1.txt", "data/history/g1.txt", "data/groups.txt", "data/stats.txt",
                "data/workspace/SYSTEM.md", "data/workspace/MEMORY.md", "data/workspace/.backup",
                "data/tools/thoi_tiet.py", "system/state.txt", "system/seen.txt", "system/webview",
                "system/logs/bot.log"):
        assert (u / rel).exists(), rel
    assert (u / "data" / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "tính cách tôi đã sửa"
    # chỗ cũ: data/ chỉ còn lock nên được dọn; file mẫu có trong git ở lại; lock không bị chuyển
    assert not (home / "data").exists() and not (home / ".env").exists()
    assert (home / "workspace" / "SYSTEM.md").exists() and (home / "tools" / "_example.py").exists()
    assert not (u / "data" / "tools" / "_example.py").exists() and not (u / "system" / "bot.lock").exists()

    env = (u / "config" / ".env").read_text(encoding="utf-8")
    assert "DATA_DIR" not in env and "LOG_DIR" not in env and "WORKSPACE_DIR" not in env
    assert "GEMINI_API_KEY=k" in env and "BOT_NAMES=roemnao" in env and env.startswith("# cài đặt")

    assert paths.migrate_legacy(home) == []  # lần hai không làm gì


def test_settings_read_migrated_env(tmp_path, monkeypatch):
    from bot.config import Settings

    home = legacy_home(tmp_path)
    paths.migrate_legacy(home)
    env = dict(line.split("=", 1) for line in (home / "userdata" / "config" / ".env").read_text(
        encoding="utf-8").splitlines() if "=" in line and not line.startswith("#"))
    s = Settings.from_env(env, base_dir=home)
    assert s.data_dir == home / "userdata" / "data" and s.workspace_dir == home / "userdata" / "data" / "workspace"
    assert (s.workspace_dir / "SYSTEM.md").is_file() and s.zalo_session_file.is_file()


def test_skips_while_old_version_still_running(tmp_path):
    home = legacy_home(tmp_path)
    held = InstanceLock(home / "data" / "bot.lock")
    held.acquire()
    try:
        assert paths.migrate_legacy(home, wait_old=0.2) == []
        assert paths.needs_migration(home) and (home / ".env").exists()
    finally:
        held.release()
    assert paths.migrate_legacy(home)  # bản cũ tắt rồi thì chuyển được


def test_fresh_install_needs_nothing(tmp_path):
    assert not paths.needs_migration(tmp_path)
    assert paths.migrate_legacy(tmp_path) == []


def test_restores_git_tracked_defaults(tmp_path):
    home = legacy_home(tmp_path)

    def git(*args):
        subprocess.run(["git", *args], cwd=home, check=True, capture_output=True)

    (home / "workspace" / "SYSTEM.md").write_text("bản gốc trong git", encoding="utf-8")
    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("add", "workspace/SYSTEM.md", "tools/_example.py")
    git("commit", "-q", "-m", "mẫu")
    (home / "workspace" / "SYSTEM.md").write_text("tính cách tôi đã sửa", encoding="utf-8")

    paths.migrate_legacy(home)
    assert (home / "userdata" / "data" / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "tính cách tôi đã sửa"
    assert (home / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "bản gốc trong git"
