from __future__ import annotations

import json
import subprocess

from pylos.lobby.dispatch.shared import userdata_paths
from pylos.lobby.dispatch.lifecycle.process_lock import InstanceLock


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
    assert userdata_paths.needs_migration(home)
    moved = userdata_paths.migrate_legacy(home)
    assert moved and not userdata_paths.needs_migration(home)

    u = home / "userdata"
    assert (u / "config" / "settings.env").is_file() and (u / "config" / "settings.env.bak").is_file()
    assert json.loads((u / "config" / "zalo_login_session.json").read_text(encoding="utf-8"))["imei"] == "i"
    # đổi luôn sang tên dễ hiểu: groups.txt -> group_settings.txt, history/ -> session_history/, ...
    for rel in ("data/memorydata/g1.txt", "data/session_history/g1.txt", "data/group_settings.txt",
                "data/daily_stats.txt", "data/workspace/SYSTEM.md", "data/workspace/MEMORY.md",
                "data/workspace/.backup", "data/custom_tools/thoi_tiet.py", "system/bot_status.txt",
                "system/processed_message_ids.txt", "system/app_window_profile", "system/logs/bot.log"):
        assert (u / rel).exists(), rel
    assert (u / "data" / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "tính cách tôi đã sửa"
    # chỗ cũ: data/ chỉ còn lock nên được dọn; file mẫu có trong git ở lại; lock không bị chuyển
    assert not (home / "data").exists() and not (home / ".env").exists()
    assert (home / "workspace" / "SYSTEM.md").exists() and (home / "tools" / "_example.py").exists()
    assert not (u / "data" / "custom_tools" / "_example.py").exists() and not (u / "system" / "bot.lock").exists()

    env = (u / "config" / "settings.env").read_text(encoding="utf-8")
    assert "DATA_DIR" not in env and "LOG_DIR" not in env and "WORKSPACE_DIR" not in env
    assert "GEMINI_API_KEY=k" in env and "BOT_NAMES=roemnao" in env and env.startswith("# cài đặt")

    assert userdata_paths.migrate_legacy(home) == []  # lần hai không làm gì


def test_settings_read_migrated_env(tmp_path, monkeypatch):
    from pylos.lobby.dispatch.shared.config import Settings

    home = legacy_home(tmp_path)
    userdata_paths.migrate_legacy(home)
    env = dict(line.split("=", 1) for line in (home / "userdata" / "config" / "settings.env").read_text(
        encoding="utf-8").splitlines() if "=" in line and not line.startswith("#"))
    s = Settings.from_env(env, base_dir=home)
    city = home / "src" / "pylos"
    assert s.data_dir == city / "gate" / "guest_house" / "data" and s.workspace_dir == city / "residential" / "residents" / "pylos" / "workspace"
    assert s.zalo_session_file == city / "management" / "owner" / "secrets" / "zalo_login_session.json"


def test_skips_while_old_version_still_running(tmp_path):
    home = legacy_home(tmp_path)
    held = InstanceLock(home / "data" / "bot.lock")
    held.acquire()
    try:
        assert userdata_paths.migrate_legacy(home, wait_old=0.2) == []
        assert userdata_paths.needs_migration(home) and (home / ".env").exists()
    finally:
        held.release()
    assert userdata_paths.migrate_legacy(home)  # bản cũ tắt rồi thì chuyển được


def test_fresh_install_needs_nothing(tmp_path):
    assert not userdata_paths.needs_migration(tmp_path)
    assert userdata_paths.migrate_legacy(tmp_path) == []


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

    userdata_paths.migrate_legacy(home)
    assert (home / "userdata" / "data" / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "tính cách tôi đã sửa"
    assert (home / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "bản gốc trong git"


# ---------- userdata/ -> trong Thành ----------

def userdata_home(tmp_path):
    home = tmp_path / "home"
    u = home / "userdata"
    (u / "config").mkdir(parents=True)
    (u / "data" / "memorydata").mkdir(parents=True)
    (u / "data" / "workspace").mkdir()
    (u / "data" / "custom_tools").mkdir()
    (u / "system" / "logs").mkdir(parents=True)
    (u / "system" / "app_window_profile").mkdir()
    (u / "config" / "settings.env").write_text("GEMINI_API_KEY=k\n", encoding="utf-8")
    (u / "config" / "zalo_login_session.json").write_text("{}", encoding="utf-8")
    (u / "data" / "memorydata" / "g1.txt").write_text("{}\n", encoding="utf-8")
    (u / "data" / "group_settings.txt").write_text("{}", encoding="utf-8")
    (u / "data" / "workspace" / "SYSTEM.md").write_text("tính cách cũ", encoding="utf-8")
    (u / "data" / "workspace" / "MEMORY.md").write_text("ghi nhớ cũ", encoding="utf-8")
    (u / "data" / "custom_tools" / "thoi_tiet.py").write_text("TOOLS = []", encoding="utf-8")
    (u / "system" / "bot_status.txt").write_text("{}", encoding="utf-8")
    (u / "system" / "logs" / "bot.log").write_text("log", encoding="utf-8")
    (u / "system" / "app_window_profile" / "cache").write_text("x" * 10, encoding="utf-8")
    (u / "system" / "bot.lock").write_text("", encoding="utf-8")
    (u / "system" / "bot.pid").write_text("1", encoding="utf-8")
    return home


def test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(tmp_path):
    import zipfile

    home = userdata_home(tmp_path)
    assert userdata_paths.needs_city_migration(home) and userdata_paths.pending_migration(home)
    moved = userdata_paths.migrate_to_city(home)
    assert moved and not userdata_paths.needs_city_migration(home)

    city = home / "src" / "pylos"
    for rel in ("management/owner/secrets/settings.env", "management/owner/secrets/zalo_login_session.json",
                "gate/guest_house/data/memorydata/g1.txt", "gate/guest_house/data/group_settings.txt",  # chưa vào túp lều: bước riêng
                "lobby/office/agent_tools/custom/thoi_tiet.py", "management/owner/runtime/bot_status.txt",
                "management/owner/runtime/logs/bot.log", "management/owner/runtime/app_window_profile/cache"):
        assert (city / rel).exists(), rel
    assert not (home / "userdata").exists()  # kể cả khoá và pid thừa đã dọn
    assert not (city / "residential" / "residents" / "pylos" / "workspace").exists()  # workspace cũ bị xoá, bot tạo lại từ file mẫu
    assert not (city / "gate" / "guest_house" / "data" / "workspace").exists()

    zips = list(home.glob("userdata_backup_*.zip"))
    assert len(zips) == 1
    names = zipfile.ZipFile(zips[0]).namelist()
    assert "data/workspace/SYSTEM.md" in names and "config/settings.env" in names
    assert not any("app_window_profile" in n or n.endswith((".lock", ".pid")) for n in names)

    assert userdata_paths.migrate_to_city(home) == []  # lần hai không làm gì, không thêm bản sao lưu
    assert len(list(home.glob("userdata_backup_*.zip"))) == 1


def test_city_migration_keeps_what_is_already_in_the_new_place(tmp_path):
    home = userdata_home(tmp_path)
    existing = home / "src" / "pylos" / "management" / "owner" / "secrets" / "settings.env"
    existing.parent.mkdir(parents=True)
    existing.write_text("GEMINI_API_KEY=moi\n", encoding="utf-8")
    userdata_paths.migrate_to_city(home)
    assert existing.read_text(encoding="utf-8") == "GEMINI_API_KEY=moi\n"
    assert (home / "userdata" / "config" / "settings.env").is_file()  # bản cũ còn lại, không mất


def test_city_migration_waits_for_the_old_version(tmp_path):
    home = userdata_home(tmp_path)
    held = InstanceLock(home / "userdata" / "system" / "bot.lock")
    held.acquire()
    try:
        assert userdata_paths.migrate_to_city(home) == []
        assert userdata_paths.needs_city_migration(home) and not list(home.glob("userdata_backup_*.zip"))
    finally:
        held.release()


# ---------- memorydata/ và session_history/ -> túp lều ----------

def old_chat_data(tmp_path):
    home = tmp_path / "home"
    data = home / "src" / "pylos" / "gate" / "guest_house" / "data"
    (data / "memorydata").mkdir(parents=True)
    (data / "session_history").mkdir()
    (data / "memorydata" / "g1.txt").write_text('{"text": "tin 1"}\n', encoding="utf-8")
    (data / "memorydata" / "u2.txt").write_text('{"text": "tin 2"}\n', encoding="utf-8")
    (data / "session_history" / "g1.txt").write_text('{"text": "session 1"}\n', encoding="utf-8")
    (data / "group_settings.txt").write_text("{}", encoding="utf-8")
    return home


def test_chat_data_moves_into_one_hut_per_person_or_group(tmp_path):
    import zipfile

    home = old_chat_data(tmp_path)
    assert userdata_paths.needs_huts_migration(home) and userdata_paths.pending_migration(home)
    moved = userdata_paths.migrate_to_huts(home)
    assert len(moved) == 3 and not userdata_paths.pending_migration(home)

    huts = home / "src" / "pylos" / "gate" / "guest_house" / "huts"
    assert (huts / "g1" / "memorydata.txt").read_text(encoding="utf-8") == '{"text": "tin 1"}\n'
    assert (huts / "g1" / "session_history.txt").is_file() and (huts / "u2" / "memorydata.txt").is_file()
    assert not (huts / "u2" / "session_history.txt").exists()
    data = home / "src" / "pylos" / "gate" / "guest_house" / "data"
    assert not (data / "memorydata").exists() and not (data / "session_history").exists()
    assert (data / "group_settings.txt").is_file()  # cài đặt chung ở lại data/

    zips = list(home.glob("data_backup_*.zip"))
    assert len(zips) == 1 and "memorydata/g1.txt" in zipfile.ZipFile(zips[0]).namelist()
    assert userdata_paths.migrate_to_huts(home) == [] and len(list(home.glob("data_backup_*.zip"))) == 1  # lần hai không làm gì


def test_hut_migration_keeps_a_hut_file_that_already_exists(tmp_path):
    home = old_chat_data(tmp_path)
    huts = home / "src" / "pylos" / "gate" / "guest_house" / "huts"
    (huts / "g1").mkdir(parents=True)
    (huts / "g1" / "memorydata.txt").write_text("mới hơn\n", encoding="utf-8")
    userdata_paths.migrate_to_huts(home)
    assert (huts / "g1" / "memorydata.txt").read_text(encoding="utf-8") == "mới hơn\n"
    old = home / "src" / "pylos" / "gate" / "guest_house" / "data" / "memorydata" / "g1.txt"
    assert old.is_file()  # bản cũ không bị mất, chờ người xem


def test_hut_migration_waits_for_the_running_bot(tmp_path):
    home = old_chat_data(tmp_path)
    system = home / "src" / "pylos" / "management" / "owner" / "runtime"
    system.mkdir(parents=True)
    held = InstanceLock(system / "bot.lock")
    held.acquire()
    try:
        assert userdata_paths.migrate_to_huts(home) == [] and userdata_paths.needs_huts_migration(home)
    finally:
        held.release()
