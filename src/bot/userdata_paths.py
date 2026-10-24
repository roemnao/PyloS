"""Thư mục của ứng dụng. Mọi thứ của riêng người dùng nằm trong APP_HOME/userdata/:

    userdata/config/   (1) khoá & thông số người dùng nhập: settings.env, zalo_login_session.json
    userdata/data/     (2) dữ liệu bot: memorydata/, session_history/, workspace/, custom_tools/, *.txt
    userdata/system/   (3) bot tự quản lý: logs/, *.lock, *.pid, bot_status.txt, processed_message_ids.txt...

Tên từng file và ý nghĩa: xem các hằng số bên dưới (GROUP_SETTINGS_FILE, ...).

Chuyển máy chỉ cần chép userdata/. Bản cũ để .env, data/, logs/, workspace/, tools/ ngay ở APP_HOME:
migrate_legacy() chuyển sang bố cục này ở lần chạy đầu.
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
USERDATA = "userdata"
CONFIG_REL = "userdata/config"
ENV_REL = "userdata/config/settings.env"            # khoá API và mọi cài đặt (trang Cài đặt ghi vào đây)
SESSION_REL = "userdata/config/zalo_login_session.json"  # phiên đăng nhập acc Zalo cá nhân (quét QR)
DATA_REL = "userdata/data"
WORKSPACE_REL = "userdata/data/workspace"           # SYSTEM.md (tính cách), MEMORY.md (ghi nhớ)
TOOLS_REL = "userdata/data/custom_tools"            # tool người dùng tự viết (.py)
SYSTEM_REL = "userdata/system"
LOGS_REL = "userdata/system/logs"

# ---------- tên file/thư mục bên trong userdata/data (Settings.data_dir) ----------
GROUP_SETTINGS_FILE = "group_settings.txt"    # nhóm nào được phép, chế độ all/default, nhãn tự đặt
CHAT_ACTIVITY_FILE = "chat_activity.txt"      # lần nhắn cuối của từng cuộc trò chuyện (để nhận ra nhóm)
DAILY_STATS_FILE = "daily_stats.txt"          # số tin nhận/trả lời/lỗi/token theo ngày (trang Tổng quan)
TOKEN_USAGE_FILE = "token_usage.txt"          # token Gemini đã dùng mỗi ngày (hạn mức ngày)
FAILED_REPLIES_FILE = "failed_replies.txt"    # câu trả lời gửi lên Zalo thất bại (trang Tin lỗi)
ASSIGNED_EVENTS_FILE = "assigned_events.txt"  # lịch bot đã giao cho người khác (để sửa / huỷ "việc lúc nãy")
MEMORYDATA_DIR = "memorydata"                 # mọi tin của từng cuộc trò chuyện, kèm kết quả bộ lọc
SESSION_HISTORY_DIR = "session_history"       # session: tin qua bộ lọc + câu trả lời (gửi cho Gemini)
CONSOLE_TEST_DIR = "console_test"             # dữ liệu riêng của chế độ chat thử `python -m bot console`

# ---------- tên file/thư mục bên trong userdata/system (Settings.system_dir) ----------
BOT_STATUS_FILE = "bot_status.txt"                 # lúc khởi động, lần nhận tin cuối (để biết bot còn sống)
PROCESSED_IDS_FILE = "processed_message_ids.txt"   # id tin đã xử lý, chống trả lời trùng
PENDING_UPDATES_FILE = "pending_updates.txt"       # số thay đổi mới trên GitHub chưa cập nhật
REMOTE_CONFIG_FILE = "remote_config.json"         # thông số lấy từ web (bản gần nhất, dùng khi mất mạng)
APP_WINDOW_PROFILE_DIR = "app_window_profile"      # hồ sơ của cửa sổ ứng dụng (giữ đăng nhập giao diện)
ZALO_LOGIN_QR_FILE = "zalo_login_qr.png"           # ảnh mã QR tạm khi đăng nhập Zalo bằng dòng lệnh
GUI_LOCK_FILE = "gui.lock"                         # chỉ một ứng dụng quản lý chạy cùng lúc
SHOW_WINDOW_REQUEST = "show_window.request"        # nhờ ứng dụng đang chạy hiện cửa sổ
UPDATE_REQUEST = "update.request"                  # nhờ ứng dụng đang chạy tự cập nhật (nút trên Tổng quan)


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
    - Chạy từ mã nguồn: thư mục dự án (src/bot/userdata_paths.py -> lên 2 cấp).
    """
    override = os.environ.get("ZALOBOT_HOME", "").strip()
    if override:
        return Path(override).resolve()
    if is_frozen():
        beside_exe = Path(sys.executable).resolve().parent
        if _writable(beside_exe):
            return beside_exe
        return Path(os.environ.get("LOCALAPPDATA") or Path.home()) / APP_NAME
    return Path(__file__).resolve().parents[2]


APP_HOME = app_home()
ENV_FILE = APP_HOME / ENV_REL


def done_file(name: str) -> str:
    """failed_replies.txt -> failed_replies_done.txt (các tin lỗi đã gửi lại/bỏ qua)."""
    stem, dot, ext = name.rpartition(".")
    return f"{stem}_done.{ext}" if dot else f"{name}_done"


# ---------- chuyển từ bố cục cũ ----------

# (đường dẫn cũ so với APP_HOME, đường dẫn mới, chép thay vì chuyển)
_LEGACY_MOVES: tuple[tuple[str, str, bool], ...] = (
    (".env", ENV_REL, False),
    (".env.bak", ENV_REL + ".bak", False),
    ("data/zalo_session.json", SESSION_REL, False),
    ("data/zalo_cookies.json", SESSION_REL, False),
    ("data/memorydata", f"{DATA_REL}/{MEMORYDATA_DIR}", False),
    ("data/history", f"{DATA_REL}/{SESSION_HISTORY_DIR}", False),
    ("data/console", f"{DATA_REL}/{CONSOLE_TEST_DIR}", False),
    ("data/groups.txt", f"{DATA_REL}/{GROUP_SETTINGS_FILE}", False),
    ("data/stats.txt", f"{DATA_REL}/{DAILY_STATS_FILE}", False),
    ("data/usage.txt", f"{DATA_REL}/{TOKEN_USAGE_FILE}", False),
    ("data/failed.txt", f"{DATA_REL}/{FAILED_REPLIES_FILE}", False),
    ("data/failed_done.txt", f"{DATA_REL}/{done_file(FAILED_REPLIES_FILE)}", False),
    ("data/activity.txt", f"{DATA_REL}/{CHAT_ACTIVITY_FILE}", False),
    ("data/state.txt", f"{SYSTEM_REL}/{BOT_STATUS_FILE}", False),
    ("data/seen.txt", f"{SYSTEM_REL}/{PROCESSED_IDS_FILE}", False),
    ("data/webview", f"{SYSTEM_REL}/{APP_WINDOW_PROFILE_DIR}", False),
    ("data/update.txt", f"{SYSTEM_REL}/{PENDING_UPDATES_FILE}", False),
    ("logs", LOGS_REL, False),
    ("workspace/MEMORY.md", WORKSPACE_REL + "/MEMORY.md", False),
    ("workspace/notes", WORKSPACE_REL + "/notes", False),
    ("workspace/.backup", WORKSPACE_REL + "/.backup", False),
    # SYSTEM.md và tools/_example.py có trong git: chép (giữ bản người dùng đã sửa) rồi trả file gốc về cho git.
    ("workspace/SYSTEM.md", WORKSPACE_REL + "/SYSTEM.md", True),
)
# Biến trong .env cũ trỏ vào chỗ cũ (giá trị mặc định của bản cũ): bỏ đi để dùng chỗ mới.
_LEGACY_ENV_DEFAULTS = {"DATA_DIR": "data", "WORKSPACE_DIR": "workspace", "LOG_DIR": "logs",
                        "ZALO_SESSION_FILE": "data/zalo_session.json"}
_LEGACY_LOCKS = ("data/bot.lock", "data/admin.lock", "data/gui.lock")
_GIT_TRACKED_DEFAULTS = ("workspace/SYSTEM.md", "tools/_example.py")


def needs_migration(home: Path = APP_HOME) -> bool:
    """Chưa có userdata/ mà còn dữ liệu kiểu cũ (.env hoặc data/ ngay ở APP_HOME)."""
    return not (home / USERDATA).exists() and ((home / ".env").is_file() or (home / "data").is_dir())


def _old_version_running(home: Path) -> bool:
    from bot.storage.process_lock import AlreadyRunning, InstanceLock

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
    from bot.system.bot_process import run_hidden

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
    from bot.storage.process_lock import AlreadyRunning, InstanceLock

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
                        if _move(path, home / TOOLS_REL / path.name, False):
                            moved.append(f"tools/{path.name} -> {TOOLS_REL}/{path.name}")
                    except OSError as exc:
                        log.warning("Không chuyển được %s: %s", path, exc)
        (home / CONFIG_REL).mkdir(parents=True, exist_ok=True)  # đánh dấu đã chuyển (userdata/ tồn tại)
        if (home / ENV_REL).is_file():
            _clean_env(home / ENV_REL)
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
