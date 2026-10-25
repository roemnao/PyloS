"""Quản lý tiến trình chạy nền: bot (`python -m bot run`) và giao diện quản lý (`python -m bot admin`).

Tiến trình đang chạy được nhận biết bằng khóa data/<tên>.lock (đáng tin hơn đọc PID,
vì PID có thể bị Windows dùng lại). PID trong data/<tên>.pid chỉ dùng để dừng.

Các hàm trả về Result (mã, thông báo) thay vì in ra, để cả dòng lệnh lẫn giao diện web dùng chung.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bot.config import LOADED_FROM_DOTENV, PROJECT_ROOT, Settings, is_frozen
from bot.storage import FailedStore, GroupStore, StateStore, StatsStore, UsageStore
from bot.storage.process_lock import AlreadyRunning, InstanceLock
from bot.core.vietnam_time import now_ms
from bot.userdata_paths import (
    BOT_STATUS_FILE,
    DAILY_STATS_FILE,
    FAILED_REPLIES_FILE,
    GROUP_SETTINGS_FILE,
    GUI_LOCK_FILE,
    STANDBY_FILE,
    TOKEN_USAGE_FILE,
)

# Mã thoát của `bot run` khi máy đang ở chế độ chờ (bot đã chuyển sang máy khác). systemd không bật lại
# với mã này (RestartPreventExitStatus=5), scripts/run-forever.ps1 cũng không.
EXIT_STANDBY = 5
SYSTEMD_UNIT = "pylos-bot"


@dataclass(frozen=True)
class Service:
    name: str  # tên file khóa/pid trong data/
    label: str
    args: tuple[str, ...]
    task_name: str  # trùng với scripts/install-task.ps1
    log_file: str


BOT = Service("bot", "Bot", ("run",), "ZaloAssistantBot", "bot.log")
ADMIN = Service("admin", "Giao diện quản lý", ("admin",), "ZaloAssistantBotAdmin", "admin.log")


@dataclass(frozen=True)
class Result:
    code: int
    message: str

    @property
    def ok(self) -> bool:
        return self.code == 0


def pid_path(settings: Settings, service: Service = BOT) -> Path:
    return settings.system_dir / f"{service.name}.pid"


def write_pid(settings: Settings, service: Service = BOT) -> None:
    settings.system_dir.mkdir(parents=True, exist_ok=True)
    pid_path(settings, service).write_text(str(os.getpid()), encoding="utf-8")


def clear_pid(settings: Settings, service: Service = BOT) -> None:
    try:
        pid_path(settings, service).unlink()
    except FileNotFoundError:
        pass


def read_pid(settings: Settings, service: Service = BOT) -> int | None:
    try:
        return int(pid_path(settings, service).read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def lock_for(settings: Settings, service: Service = BOT) -> InstanceLock:
    return InstanceLock(settings.system_dir / f"{service.name}.lock")


def is_running(settings: Settings, service: Service = BOT) -> bool:
    """True nếu có tiến trình đang giữ khóa."""
    lock = lock_for(settings, service)
    try:
        lock.acquire()
    except AlreadyRunning:
        return True
    lock.release()
    return False


def gui_running(settings: Settings) -> bool:
    """True nếu ứng dụng quản lý (cửa sổ + khay) đang mở."""
    lock = InstanceLock(settings.system_dir / GUI_LOCK_FILE)
    try:
        lock.acquire()
    except AlreadyRunning:
        return True
    lock.release()
    return False


def run_hidden(cmd: list[str], timeout: float = 20, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Chạy một lệnh hệ thống mà không bật cửa sổ cmd.

    ZaloBot.exe là ứng dụng cửa sổ (không có console), nên mỗi lần gọi schtasks/taskkill kiểu thường
    sẽ làm Windows mở thoáng một cửa sổ cmd. Cờ CREATE_NO_WINDOW + SW_HIDE chặn việc đó.
    """
    kwargs: dict[str, Any] = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        kwargs["startupinfo"] = startup
    return subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, timeout=timeout, cwd=cwd, **kwargs)


def _kill(pid: int) -> None:
    if os.name == "nt":
        run_hidden(["taskkill", "/PID", str(pid), "/T", "/F"])
    else:
        import signal

        os.kill(pid, signal.SIGTERM)


_task_cache: dict[str, tuple[float, bool]] = {}


def task_installed(service: Service = BOT) -> bool:
    if os.name != "nt":
        return False
    cached = _task_cache.get(service.task_name)
    if cached and time.monotonic() - cached[0] < 30:
        return cached[1]
    try:
        installed = run_hidden(["schtasks", "/Query", "/TN", service.task_name]).returncode == 0
    except (OSError, subprocess.SubprocessError):
        installed = False
    _task_cache[service.task_name] = (time.monotonic(), installed)
    return installed


def _end_task(service: Service) -> None:
    # Dừng supervisor trước, nếu không nó sẽ bật lại tiến trình sau 10 giây.
    if task_installed(service):
        run_hidden(["schtasks", "/End", "/TN", service.task_name])


def _wait(predicate, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.25)
    return predicate()


def tail_log(settings: Settings, lines: int = 30, service: Service = BOT) -> str:
    path = settings.log_dir / service.log_file
    try:
        content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return "(chưa có log)"
    return "\n".join(content[-lines:])


def spawn_command(service: Service) -> list[str]:
    """Lệnh bật tiến trình: `ZaloBot.exe run` khi chạy từ exe, `python -m bot run` khi chạy từ mã nguồn."""
    if is_frozen():
        return [sys.executable, *service.args]
    return [sys.executable, "-m", "bot", *service.args]


def stop_flag(settings: Settings, service: Service = BOT) -> Path:
    """File cờ yêu cầu tiến trình tự dừng (dừng êm, để exe dọn được thư mục tạm của nó)."""
    return settings.system_dir / f"{service.name}.stop"


def _spawn(service: Service) -> subprocess.Popen:
    kwargs: dict[str, Any] = {}
    if os.name == "nt":
        # Không dùng DETACHED_PROCESS: Windows bỏ qua CREATE_NO_WINDOW khi có cờ đó, và tiến trình con
        # (python thật do launcher của venv sinh ra) sẽ tự mở một cửa sổ cmd; đóng cửa sổ đó là bot chết.
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    # Bỏ các biến lấy từ .env để tiến trình con đọc lại .env (có thể vừa được sửa trên giao diện).
    env = {k: v for k, v in os.environ.items() if k not in LOADED_FROM_DOTENV}
    if is_frozen():
        # Mặc định (PyInstaller >= 6.9) exe gọi lại chính nó sẽ DÙNG CHUNG thư mục giải nén của tiến trình cha;
        # thoát ứng dụng quản lý sẽ xóa thư mục đó và bot chết theo. Bắt tiến trình con tự giải nén riêng.
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return subprocess.Popen(
        spawn_command(service),
        cwd=PROJECT_ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **kwargs,
    )


# ---------- chế độ chờ: bot đã chuyển sang máy khác ----------

def standby_path(settings: Settings) -> Path:
    return settings.system_dir / STANDBY_FILE


def standby_info(settings: Settings) -> dict[str, Any] | None:
    """{reason, at} nếu máy này đang chờ (không được bật bot), ngược lại None."""
    path = standby_path(settings)
    try:
        text = path.read_text(encoding="utf-8").strip()
        at = int(path.stat().st_mtime * 1000)
    except OSError:
        return None
    return {"reason": text or "Bot đang chạy ở máy khác.", "at": at}


def set_standby(settings: Settings, reason: str) -> None:
    settings.system_dir.mkdir(parents=True, exist_ok=True)
    standby_path(settings).write_text(reason.strip()[:300] or "Bot đang chạy ở máy khác.", encoding="utf-8")


def clear_standby(settings: Settings) -> None:
    standby_path(settings).unlink(missing_ok=True)


# ---------- systemd (VPS: BOT_SUPERVISOR=systemd) ----------

def uses_systemd(settings: Settings, service: Service) -> bool:
    """Trên VPS bot là service pylos-bot của systemd; giao diện thì do systemd quản lý riêng (pylos-admin)."""
    return service is BOT and settings.bot_supervisor == "systemd" and os.name != "nt"


def systemctl(action: str, unit: str, *, timeout: float = 60) -> Result:
    """`sudo -n systemctl <action> <unit>`: user pylos chỉ được sudo đúng các lệnh này (xem docs/PLAN.md)."""
    try:
        done = run_hidden(["sudo", "-n", "systemctl", action, unit], timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return Result(1, f"Không chạy được systemctl {action} {unit}: {exc}")
    if done.returncode != 0:
        detail = (done.stderr or done.stdout).decode("utf-8", errors="replace").strip().splitlines()
        return Result(1, f"systemctl {action} {unit} lỗi: {detail[-1] if detail else done.returncode}")
    return Result(0, "")


def run_update_service() -> Result:
    """VPS: chạy ngay pylos-update (git pull + khởi động lại); --no-block để không chờ nó xong."""
    try:
        done = run_hidden(["sudo", "-n", "systemctl", "start", "--no-block", "pylos-update.service"], timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return Result(1, f"Không chạy được pylos-update: {exc}")
    if done.returncode != 0:
        detail = (done.stderr or done.stdout).decode("utf-8", errors="replace").strip().splitlines()
        return Result(1, f"Không nhờ được pylos-update: {detail[-1] if detail else done.returncode}")
    return Result(0, "")


def _start_systemd(settings: Settings) -> Result:
    started = now_ms()
    result = systemctl("start", SYSTEMD_UNIT)
    if not result.ok:
        return result

    def ready() -> bool:
        return int(StateStore(settings.system_dir / BOT_STATUS_FILE).data.get("ready_at") or 0) >= started

    if _wait(ready, 40):
        return Result(0, "Đã bật bot (service pylos-bot).")
    if not is_running(settings, BOT):
        return Result(1, f"Bot không khởi động được. Log gần nhất:\n{tail_log(settings, 10, BOT)}")
    return Result(0, "Bot đã chạy (service pylos-bot) nhưng chưa xác nhận được sẵn sàng. Xem log.")


def _stop_systemd(settings: Settings) -> Result:
    was_running = is_running(settings, BOT)
    result = systemctl("stop", SYSTEMD_UNIT)
    if not result.ok:
        return result
    if _wait(lambda: not is_running(settings, BOT), 15):
        clear_pid(settings, BOT)
        return Result(0, "Đã dừng bot." if was_running else "Bot không chạy.")
    return Result(1, "Đã gửi lệnh dừng service pylos-bot nhưng bot vẫn còn giữ khóa. Xem log.")


def start(settings: Settings, service: Service = BOT, *, force: bool = False) -> Result:
    if is_running(settings, service):
        return Result(0, f"{service.label} đã đang chạy.")
    if service is BOT:
        standby = standby_info(settings)
        if standby and not force:
            return Result(1, f"Máy này đang ở chế độ chờ: {standby['reason']} "
                             "Chuyển bot về máy này ở trang Máy chủ (hoặc bỏ chế độ chờ) rồi bật lại.")
        if force:
            clear_standby(settings)
        settings.require(zalo=True, gemini=True)
        if uses_systemd(settings, service):
            return _start_systemd(settings)
    started = now_ms()
    child = _spawn(service)

    if service is BOT:
        # Chờ bot báo sẵn sàng (ready_at, sau khi kiểm tra token) hoặc thoát sớm (token sai, thiếu cấu hình...).
        def ready() -> bool:
            return child.poll() is not None or int(
                StateStore(settings.system_dir / BOT_STATUS_FILE).data.get("ready_at") or 0
            ) >= started

        _wait(ready, 40)
    else:
        # Giao diện: chờ giữ được khóa, rồi chờ thêm chút để chắc không lỗi khi mở cổng.
        _wait(lambda: child.poll() is not None or is_running(settings, service), 15)
        _wait(lambda: child.poll() is not None, 1.5)
        ready = lambda: is_running(settings, service)  # noqa: E731

    if child.poll() is not None:
        return Result(1, f"{service.label} không khởi động được (mã thoát {child.poll()}). Log gần nhất:\n"
                         f"{tail_log(settings, 10, service)}")
    if not ready():
        return Result(0, f"{service.label} đã chạy (pid {child.pid}) nhưng chưa xác nhận được sẵn sàng. Xem log.")
    return Result(0, f"Đã bật {service.label.lower()} (pid {child.pid}).")


def stop(settings: Settings, service: Service = BOT) -> Result:
    if uses_systemd(settings, service):
        return _stop_systemd(settings)
    was_running = is_running(settings, service)
    _end_task(service)
    pid = read_pid(settings, service)
    if not was_running:
        clear_pid(settings, service)
        return Result(0, f"{service.label} không chạy.")
    if service is BOT:
        # Dừng êm trước: bot thấy file cờ thì tự thoát (tối đa ~2 giây). Exe một file thoát êm mới
        # dọn được thư mục giải nén trong %TEMP%; ép tắt sẽ để lại rác mỗi lần.
        flag = stop_flag(settings, service)
        flag.write_text(str(now_ms()), encoding="utf-8")
        stopped = _wait(lambda: not is_running(settings, service), 12)
        flag.unlink(missing_ok=True)
        if stopped:
            clear_pid(settings, service)
            return Result(0, f"Đã dừng {service.label.lower()}.")
    if pid is None:
        return Result(1, f"{service.label} đang chạy nhưng không có file PID (được bật bằng một cửa sổ riêng, "
                         "hoặc bằng phiên bản cũ). Hãy bấm Ctrl+C trong cửa sổ đó.")
    _kill(pid)
    if _wait(lambda: not is_running(settings, service), 10):
        clear_pid(settings, service)
        return Result(0, f"Đã dừng {service.label.lower()}.")
    return Result(1, f"Không dừng được {service.label.lower()} (khóa vẫn còn). Thử tắt python.exe trong Task Manager.")


def restart(settings: Settings, service: Service = BOT) -> Result:
    result = stop(settings, service)
    return result if not result.ok else start(settings, service)


def _registry_autostart() -> bool:
    """Mục "Khởi động cùng Windows" của ứng dụng quản lý (khay hệ thống)."""
    try:
        from bot.ui.desktop import windows_autostart

        return windows_autostart.is_enabled()
    except Exception:  # noqa: BLE001 - không phải Windows hoặc thiếu quyền đọc registry
        return False


def status_info(settings: Settings) -> dict[str, Any]:
    """Trạng thái bot dạng dữ liệu, dùng cho `gateway status` và trang Tổng quan."""
    running = is_running(settings, BOT)
    state = StateStore(settings.system_dir / BOT_STATUS_FILE).data
    groups = GroupStore(settings.data_dir / GROUP_SETTINGS_FILE).all()
    return {
        "running": running,
        "pid": read_pid(settings, BOT) if running else None,
        "receive_mode": settings.receive_mode,
        "model": settings.gemini_model,
        "started_at": state.get("started_at") if running else None,
        "last_poll_at": state.get("last_poll_at"),
        "last_message_at": state.get("last_message_at"),
        "tokens_today": UsageStore(settings.data_dir / TOKEN_USAGE_FILE).used_today(),
        "token_budget": settings.daily_token_budget,
        "today": StatsStore(settings.data_dir / DAILY_STATS_FILE).today(),
        "owner_set": bool(settings.owner_zalo_id),
        "allowed_groups": [{"chat_id": g.chat_id, "mode": g.mode, "label": g.label} for g in groups if g.allowed],
        "failed_pending": len(FailedStore(settings.data_dir / FAILED_REPLIES_FILE).pending()),
        "task_installed": task_installed(BOT),
        "autostart": _registry_autostart(),
        "zalo_token_set": bool(settings.zalo_bot_token),
        "gemini_key_set": bool(settings.gemini_api_key),
        "zalo_session_set": settings.zalo_session_file.is_file(),
        "personal": settings.personal,
        "standby": standby_info(settings),
        "supervisor": settings.bot_supervisor,
    }


def format_status(info: dict[str, Any]) -> str:
    def ago(value: Any) -> str:
        return f"{(now_ms() - int(value)) / 1000:.0f} giây trước" if value else "chưa có"

    lines = [
        f"Trạng thái : {'ĐANG CHẠY' if info['running'] else 'DỪNG'}" + (f" (pid {info['pid']})" if info["running"] else ""),
        f"Nhận tin   : {info['receive_mode']}  |  Model: {info['model']}",
    ]
    if info["running"]:
        lines += [f"Poll cuối  : {ago(info['last_poll_at'])}", f"Tin cuối   : {ago(info['last_message_at'])}"]
    budget = f"/{info['token_budget']}" if info["token_budget"] else " (không giới hạn)"
    lines.append(f"Token nay  : {info['tokens_today']}{budget}")
    lines.append(f"Chủ bot    : {'đã đặt' if info['owner_set'] else '(chưa đặt OWNER_ZALO_ID)'}")
    lines.append(f"Nhóm được phép: {len(info['allowed_groups'])}")
    lines += [f"  - {g['label'] or g['chat_id']}  chế độ {g['mode']}" for g in info["allowed_groups"]]
    if info["failed_pending"]:
        lines.append(f"Tin gửi lỗi chưa xử lý: {info['failed_pending']}")
    if os.name == "nt":
        autostart = "có (ứng dụng ZaloBot)" if info.get("autostart") else "có (Task Scheduler)" if info["task_installed"] else "chưa bật"
        lines.append(f"Tự chạy khi đăng nhập: {autostart}")
    return "\n".join(lines)


def follow_log(settings: Settings, lines: int, service: Service = BOT) -> int:
    print(tail_log(settings, lines, service))
    path = settings.log_dir / service.log_file
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            fh.seek(0, os.SEEK_END)
            while True:
                line = fh.readline()
                if line:
                    print(line, end="", flush=True)
                else:
                    time.sleep(0.5)
    except (KeyboardInterrupt, FileNotFoundError):
        return 0
