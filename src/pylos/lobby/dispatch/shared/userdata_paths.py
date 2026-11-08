"""Thư mục của ứng dụng. Dữ liệu của người dùng và của bot nằm ngay trong Thành (APP_HOME/src/pylos/...), không còn userdata/:

    management/owner/secrets/   khoá & thông số người dùng nhập: settings.env, zalo_login_session.json
    management/owner/runtime/   bot tự quản lý: logs/, *.lock, *.pid, bot_status.txt, standby, handover_backups/...
    gate/guest_house/data/      dữ liệu theo người / nhóm chat: memorydata/, session_history/, *.txt
    residential/residents/pylos/workspace/   tài liệu riêng của bot (SOUL.md...), bot đọc hết; MEMORY.md (ghi nhớ). Git theo dõi (trừ .backup/)
    gate/fence/SYSTEM.md                     quy tắc chung của bot (nằm ở hàng rào, bot không tự sửa), git theo dõi
    lobby/office/agent_tools/custom/         tool người dùng tự viết (.py)

Git bỏ qua nội dung secrets, runtime, guest_house/data, custom (.gitignore); workspace và fence/SYSTEM.md thì git theo dõi. Tên từng file và ý nghĩa: xem các hằng số bên dưới.

Chuyển máy chỉ cần chép các thư mục đó (hoặc dùng gói chuyển máy). Hai lần chuyển bố cục, đều tự chạy ở lần khởi động đầu:
  migrate_legacy():   bản cũ nhất (.env, data/, logs/, workspace/, tools/ ngay ở APP_HOME) -> userdata/
  migrate_to_city():  userdata/ -> trong Thành (sao lưu zip trước; workspace cũ bị xoá, bot tạo lại từ file mẫu)
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
import time
from pathlib import Path

log = logging.getLogger(__name__)

APP_NAME = "ZaloAssistantBot"

# Đường dẫn tương đối tính từ APP_HOME (biến DATA_DIR, LOG_DIR... trong settings.env vẫn ghi đè được).
CITY = "src/pylos"
SECRETS_REL = f"{CITY}/management/owner/secrets"
CONFIG_REL = SECRETS_REL
ENV_REL = f"{SECRETS_REL}/settings.env"                      # khoá API và mọi cài đặt (trang Cài đặt ghi vào đây)
SESSION_REL = f"{SECRETS_REL}/zalo_login_session.json"       # phiên đăng nhập acc Zalo cá nhân (quét QR)
DATA_REL = f"{CITY}/gate/guest_house/data"
WORKSPACE_REL = f"{CITY}/residential/residents/pylos/workspace"   # tài liệu riêng của bot (SOUL.md...), MEMORY.md (ghi nhớ)
SYSTEM_FILE_REL = f"{CITY}/gate/fence/SYSTEM.md"             # quy tắc chung của bot, ở hàng rào
TOOLS_REL = f"{CITY}/lobby/office/agent_tools/custom"        # tool người dùng tự viết (.py)
SYSTEM_REL = f"{CITY}/management/owner/runtime"
LOGS_REL = f"{SYSTEM_REL}/logs"
# Thư mục dữ liệu nằm trong cây mã nguồn (không phải gói Python; git bỏ qua trừ workspace): test khung Thành bỏ qua chúng.
RUNTIME_DIRS = (SECRETS_REL, DATA_REL, WORKSPACE_REL, TOOLS_REL, SYSTEM_REL)

# Bố cục trung gian (userdata/), chỉ còn dùng để chuyển sang Thành.
USERDATA = "userdata"
OLD_CONFIG_REL = "userdata/config"
OLD_ENV_REL = "userdata/config/settings.env"
OLD_SESSION_REL = "userdata/config/zalo_login_session.json"
OLD_DATA_REL = "userdata/data"
OLD_WORKSPACE_REL = "userdata/data/workspace"
OLD_TOOLS_REL = "userdata/data/custom_tools"
OLD_SYSTEM_REL = "userdata/system"
OLD_LOGS_REL = "userdata/system/logs"

# ---------- tên file/thư mục bên trong gate/guest_house/data (Settings.data_dir) ----------
GROUP_SETTINGS_FILE = "group_settings.txt"    # nhóm nào được phép, chế độ all/default, nhãn tự đặt
CHAT_ACTIVITY_FILE = "chat_activity.txt"      # lần nhắn cuối của từng cuộc trò chuyện (để nhận ra nhóm)
DAILY_STATS_FILE = "daily_stats.txt"          # số tin nhận/trả lời/lỗi/token theo ngày (trang Tổng quan)
TOKEN_USAGE_FILE = "token_usage.txt"          # token Gemini đã dùng mỗi ngày (hạn mức ngày)
FAILED_REPLIES_FILE = "failed_replies.txt"    # câu trả lời gửi lên Zalo thất bại (trang Tin lỗi)
ASSIGNED_EVENTS_FILE = "assigned_events.txt"  # lịch bot đã giao cho người khác (để sửa / huỷ "việc lúc nãy")
MEMORYDATA_DIR = "memorydata"                 # mọi tin của từng cuộc trò chuyện, kèm kết quả bộ lọc
SESSION_HISTORY_DIR = "session_history"       # session: tin qua bộ lọc + câu trả lời (gửi cho Gemini)
CONSOLE_TEST_DIR = "console_test"             # dữ liệu riêng của chế độ chat thử `python -m bot console`

# ---------- tên file/thư mục bên trong management/owner/runtime (Settings.system_dir) ----------
BOT_STATUS_FILE = "bot_status.txt"                 # lúc khởi động, lần nhận tin cuối (để biết bot còn sống)
PROCESSED_IDS_FILE = "processed_message_ids.txt"   # id tin đã xử lý, chống trả lời trùng
PENDING_UPDATES_FILE = "pending_updates.txt"       # số thay đổi mới trên GitHub chưa cập nhật
APP_WINDOW_PROFILE_DIR = "app_window_profile"      # hồ sơ của cửa sổ ứng dụng (giữ đăng nhập giao diện)
ZALO_LOGIN_QR_FILE = "zalo_login_qr.png"           # ảnh mã QR tạm khi đăng nhập Zalo bằng dòng lệnh
GUI_LOCK_FILE = "gui.lock"                         # chỉ một ứng dụng quản lý chạy cùng lúc
SHOW_WINDOW_REQUEST = "show_window.request"        # nhờ ứng dụng đang chạy hiện cửa sổ
UPDATE_REQUEST = "update.request"                  # nhờ ứng dụng đang chạy tự cập nhật (nút trên Tổng quan)
ADMIN_DEVICES_FILE = "admin_devices.json"         # khoá thiết bị (băm) của ứng dụng ở máy khác, cấp khi đăng nhập Gmail
STANDBY_FILE = "standby.txt"                       # bot đã chuyển sang máy khác: máy này không được bật bot
HANDOVER_BACKUP_DIR = "handover_backups"           # dữ liệu cũ trước mỗi lần nhận bot từ máy khác


def is_frozen() -> bool:
    """True khi đang chạy từ ZaloBot.exe (đóng gói bằng PyInstaller)."""
    return bool(getattr(sys, "frozen", False))


def _writable(directory: Path) -> bool:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / f".write-test-{os.getpid()}"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def app_home() -> Path:
    """Thư mục chứa userdata/ (và code khi chạy từ mã nguồn).

    - Biến môi trường ZALOBOT_HOME nếu có.
    - Chạy từ exe: thư mục chứa exe; nếu không ghi được (ví dụ C:\\Program Files) thì %LOCALAPPDATA%\\ZaloAssistantBot.
    - Chạy từ mã nguồn: thư mục dự án (đi ngược từ file này tới thư mục có pyproject.toml).
    """
    override = os.environ.get("ZALOBOT_HOME", "").strip()
    if override:
        return Path(override).resolve()
    if is_frozen():
        beside_exe = Path(sys.executable).resolve().parent
        if _writable(beside_exe):
            return beside_exe
        return Path(os.environ.get("LOCALAPPDATA") or Path.home()) / APP_NAME
    here = Path(__file__).resolve()
    return next((p for p in here.parents if (p / "pyproject.toml").is_file()), here.parents[5])


APP_HOME = app_home()
ENV_FILE = APP_HOME / ENV_REL


def done_file(name: str) -> str:
    """failed_replies.txt -> failed_replies_done.txt (các tin lỗi đã gửi lại/bỏ qua)."""
    stem, dot, ext = name.rpartition(".")
    return f"{stem}_done.{ext}" if dot else f"{name}_done"


# ---------- chuyển từ bố cục cũ ----------

# (đường dẫn cũ so với APP_HOME, đường dẫn mới, chép thay vì chuyển)
_LEGACY_MOVES: tuple[tuple[str, str, bool], ...] = (
    (".env", OLD_ENV_REL, False),
    (".env.bak", OLD_ENV_REL + ".bak", False),
    ("data/zalo_session.json", OLD_SESSION_REL, False),
    ("data/zalo_cookies.json", OLD_SESSION_REL, False),
    ("data/memorydata", f"{OLD_DATA_REL}/{MEMORYDATA_DIR}", False),
    ("data/history", f"{OLD_DATA_REL}/{SESSION_HISTORY_DIR}", False),
    ("data/console", f"{OLD_DATA_REL}/{CONSOLE_TEST_DIR}", False),
    ("data/groups.txt", f"{OLD_DATA_REL}/{GROUP_SETTINGS_FILE}", False),
    ("data/stats.txt", f"{OLD_DATA_REL}/{DAILY_STATS_FILE}", False),
    ("data/usage.txt", f"{OLD_DATA_REL}/{TOKEN_USAGE_FILE}", False),
    ("data/failed.txt", f"{OLD_DATA_REL}/{FAILED_REPLIES_FILE}", False),
    ("data/failed_done.txt", f"{OLD_DATA_REL}/{done_file(FAILED_REPLIES_FILE)}", False),
    ("data/activity.txt", f"{OLD_DATA_REL}/{CHAT_ACTIVITY_FILE}", False),
    ("data/state.txt", f"{OLD_SYSTEM_REL}/{BOT_STATUS_FILE}", False),
    ("data/seen.txt", f"{OLD_SYSTEM_REL}/{PROCESSED_IDS_FILE}", False),
    ("data/webview", f"{OLD_SYSTEM_REL}/{APP_WINDOW_PROFILE_DIR}", False),
    ("data/update.txt", f"{OLD_SYSTEM_REL}/{PENDING_UPDATES_FILE}", False),
    ("logs", OLD_LOGS_REL, False),
    ("workspace/MEMORY.md", OLD_WORKSPACE_REL + "/MEMORY.md", False),
    ("workspace/notes", OLD_WORKSPACE_REL + "/notes", False),
    ("workspace/.backup", OLD_WORKSPACE_REL + "/.backup", False),
    # SYSTEM.md và tools/_example.py có trong git: chép (giữ bản người dùng đã sửa) rồi trả file gốc về cho git.
    ("workspace/SYSTEM.md", OLD_WORKSPACE_REL + "/SYSTEM.md", True),
)
# Biến trong .env cũ trỏ vào chỗ cũ (giá trị mặc định của bản cũ): bỏ đi để dùng chỗ mới.
_LEGACY_ENV_DEFAULTS = {"DATA_DIR": "data", "WORKSPACE_DIR": "workspace", "LOG_DIR": "logs",
                        "ZALO_SESSION_FILE": "data/zalo_session.json"}
_LEGACY_LOCKS = ("data/bot.lock", "data/admin.lock", "data/gui.lock")
_GIT_TRACKED_DEFAULTS = ("workspace/SYSTEM.md", "tools/_example.py")


def needs_migration(home: Path = APP_HOME) -> bool:
    """Chưa có userdata/ mà còn dữ liệu kiểu cũ (.env hoặc data/ ngay ở APP_HOME)."""
    return not (home / USERDATA).exists() and not (home / ENV_REL).exists() and ((home / ".env").is_file() or (home / "data").is_dir())


def _old_version_running(home: Path) -> bool:
    from pylos.lobby.dispatch.lifecycle.process_lock import AlreadyRunning, InstanceLock

    for rel in _LEGACY_LOCKS:
        if not (home / rel).exists():
            continue
        lock = InstanceLock(home / rel)
        try:
            lock.acquire()
        except AlreadyRunning:
            return True
        lock.release()
    return False


def _move(src: Path, dst: Path, copy: bool) -> bool:
    if not src.exists() or dst.exists():
        return False  # không có gì để chuyển, hoặc chỗ mới đã có (giữ bản ở chỗ mới)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        shutil.copy2(src, dst)
    else:
        shutil.move(str(src), str(dst))
    return True


def _clean_env(env_file: Path) -> None:
    from dotenv import dotenv_values

    values = dotenv_values(env_file)
    stale = [k for k, v in _LEGACY_ENV_DEFAULTS.items() if (values.get(k) or "").strip() == v]
    if not stale:
        return
    lines = env_file.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if line.split("=", 1)[0].strip() not in stale]
    env_file.write_text("\n".join(kept) + "\n", encoding="utf-8")
    log.info("Bỏ khỏi .env các đường dẫn cũ: %s", ", ".join(stale))


def _restore_git_defaults(home: Path) -> None:
    """Trả file mẫu có trong git về bản gốc (đã chép bản người dùng sang userdata), để lần
    "Cập nhật" sau gỡ được workspace/, tools/ mà git không từ chối vì có thay đổi ở máy."""
    if not (home / ".git").exists():
        return
    from pylos.gate.side_gate.vps.bot_process import run_hidden

    tracked = [rel for rel in _GIT_TRACKED_DEFAULTS if (home / rel).exists()]
    if not tracked:
        return
    try:
        result = run_hidden(["git", "checkout", "--", *tracked], cwd=home)
        if result.returncode != 0:
            log.info("Không trả được file mẫu về bản gốc: %s", result.stderr.decode("utf-8", "replace").strip())
    except (OSError, ValueError) as exc:
        log.info("Không chạy được git để trả file mẫu về bản gốc: %s", exc)


# Các mục đã chuyển ở lần chạy này (ứng dụng quản lý dùng để biết vừa chuyển xong, ví dụ để bật lại bot).
LAST_MIGRATED: list[str] = []


def migrate_legacy(home: Path = APP_HOME, wait_old: float = 0.0) -> list[str]:
    """Chuyển .env, data/, logs/, workspace/, tools/ của bản cũ vào userdata/. Trả về các mục đã chuyển.

    `wait_old`: số giây chờ bản cũ (đang tắt sau khi bấm Cập nhật) nhả khoá trước khi bỏ cuộc.
    """
    if not needs_migration(home):
        return []
    from pylos.lobby.dispatch.lifecycle.process_lock import AlreadyRunning, InstanceLock

    guard = InstanceLock(home / ".migrate.lock")
    try:
        guard.acquire(wait=30.0)  # bot và ứng dụng quản lý có thể khởi động cùng lúc
    except AlreadyRunning:
        return []
    try:
        if not needs_migration(home):
            return []  # tiến trình kia vừa chuyển xong
        deadline = time.monotonic() + wait_old
        while _old_version_running(home):
            if time.monotonic() >= deadline:
                log.warning("Bản cũ của bot/ứng dụng vẫn đang chạy: tạm chưa chuyển dữ liệu sang userdata/.")
                return []
            time.sleep(0.5)
        moved = []
        for old, new, copy in _LEGACY_MOVES:
            try:
                if _move(home / old, home / new, copy):
                    moved.append(f"{old} -> {new}")
            except OSError as exc:
                log.warning("Không chuyển được %s: %s", old, exc)
        tools = home / "tools"
        if tools.is_dir():
            for path in tools.glob("*.py"):
                if path.name != "_example.py":
                    try:
                        if _move(path, home / OLD_TOOLS_REL / path.name, False):
                            moved.append(f"tools/{path.name} -> {OLD_TOOLS_REL}/{path.name}")
                    except OSError as exc:
                        log.warning("Không chuyển được %s: %s", path, exc)
        (home / OLD_CONFIG_REL).mkdir(parents=True, exist_ok=True)  # đánh dấu đã chuyển (userdata/ tồn tại)
        if (home / OLD_ENV_REL).is_file():
            _clean_env(home / OLD_ENV_REL)
        _restore_git_defaults(home)
        # data/ cũ chỉ còn lock/pid (tự tạo lại ở chỗ mới): dọn nếu được, không thì để đó.
        for leftover in (home / "data",):
            if leftover.is_dir() and not any(p for p in leftover.iterdir() if p.suffix not in (".lock", ".pid", ".stop")):
                shutil.rmtree(leftover, ignore_errors=True)
        if moved:
            log.info("Đã chuyển dữ liệu sang %s/: %s", USERDATA, "; ".join(moved))
        LAST_MIGRATED[:] = moved
        return moved
    finally:
        guard.release()
        (home / ".migrate.lock").unlink(missing_ok=True)


# ---------- chuyển từ userdata/ vào Thành ----------

_CITY_LOCKS = ("bot.lock", "admin.lock", "gui.lock")


def needs_city_migration(home: Path = APP_HOME) -> bool:
    return (home / USERDATA).is_dir()


def _city_old_running(home: Path) -> bool:
    from pylos.lobby.dispatch.lifecycle.process_lock import AlreadyRunning, InstanceLock

    for name in _CITY_LOCKS:
        path = home / OLD_SYSTEM_REL / name
        if not path.exists():
            continue
        lock = InstanceLock(path)
        try:
            lock.acquire()
        except AlreadyRunning:
            return True
        lock.release()
    return False


def _backup_userdata(home: Path) -> Path | None:
    """Nén userdata/ (trừ bộ nhớ đệm cửa sổ và file khoá) trước khi chuyển. Lỗi thì ném ra để không chuyển gì cả."""
    import zipfile

    old = home / USERDATA
    files = [p for p in sorted(old.rglob("*"))
             if p.is_file() and p.relative_to(old).parts[:2] != ("system", "app_window_profile") and p.suffix not in (".lock", ".pid")]
    if not files:
        return None
    target = home / f"userdata_backup_{time.strftime('%Y%m%d-%H%M%S')}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(old).as_posix())
    return target


def _move_children(src: Path, dst: Path, skip: tuple[str, ...] = ()) -> list[str]:
    moved: list[str] = []
    if not src.is_dir():
        return moved
    for child in sorted(src.iterdir()):
        if child.name in skip or child.suffix in (".lock", ".pid"):
            continue
        if _move(child, dst / child.name, False):
            moved.append(f"{src.name}/{child.name}")
    return moved


def migrate_to_city(home: Path = APP_HOME, wait_old: float = 0.0) -> list[str]:
    """userdata/ -> trong Thành. Sao lưu zip trước; workspace cũ bị xoá (bot tạo lại SYSTEM.md, MEMORY.md từ file mẫu);
    chạy lại bao nhiêu lần cũng được (chỗ mới đã có thì giữ bản ở chỗ mới)."""
    if not needs_city_migration(home):
        return []
    from pylos.lobby.dispatch.lifecycle.process_lock import AlreadyRunning, InstanceLock

    guard = InstanceLock(home / ".migrate.lock")
    try:
        guard.acquire(wait=30.0)
    except AlreadyRunning:
        return []
    try:
        if not needs_city_migration(home):
            return []
        deadline = time.monotonic() + wait_old
        while _city_old_running(home):
            if time.monotonic() >= deadline:
                log.warning("Bản cũ của bot/ứng dụng vẫn đang chạy: tạm chưa chuyển userdata/ vào Thành.")
                return []
            time.sleep(0.5)
        backup = _backup_userdata(home)
        old = home / USERDATA
        moved: list[str] = []
        pairs = (
            (old / "config", home / CONFIG_REL, ()),
            (old / "data" / "custom_tools", home / TOOLS_REL, ()),
            (old / "data", home / DATA_REL, ("workspace", "custom_tools")),
            (old / "system", home / SYSTEM_REL, ()),
        )
        for src, dst, skip in pairs:
            try:
                moved += _move_children(src, dst, skip)
            except OSError as exc:
                log.warning("Không chuyển được %s: %s", src, exc)
        shutil.rmtree(old / "data" / "workspace", ignore_errors=True)  # chủ dự án chọn xoá; bản sao lưu nằm trong zip
        for stale in list(old.rglob("*.lock")) + list(old.rglob("*.pid")):  # bản cũ đã tắt (kiểm ở trên): khoá và pid thừa
            try:
                stale.unlink()
            except OSError:
                pass
        for path in sorted(old.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        try:
            old.rmdir()
        except OSError:
            log.warning("userdata/ còn file chưa chuyển (chỗ mới đã có bản khác): giữ lại, xem %s", backup.name if backup else "(không có)")
        log.info("Đã chuyển userdata/ vào Thành (sao lưu: %s): %d mục", backup.name if backup else "không cần", len(moved))
        LAST_MIGRATED.extend(moved)
        return moved
    finally:
        guard.release()
        (home / ".migrate.lock").unlink(missing_ok=True)


def migrate_all(wait_old: float = 0.0) -> None:
    """Hai lần chuyển nối nhau: bố cục cũ nhất -> userdata/ -> Thành."""
    migrate_legacy(wait_old=wait_old)
    migrate_to_city(wait_old=wait_old)


def pending_migration(home: Path = APP_HOME) -> bool:
    return needs_migration(home) or needs_city_migration(home)
