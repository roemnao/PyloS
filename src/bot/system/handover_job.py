"""Chuyển bot giữa máy này và VPS: kiểm tra, dừng bên cũ, chép dữ liệu, bật bên mới, hoàn tác nếu lỗi.

Chạy trong một luồng nền (mỗi lần một việc); giao diện hỏi tiến trình qua GET /api/handover/job.
Chỉ chạy ở máy local vì chỉ máy local có mã truy cập VPS (REMOTE_ADMIN_TOKEN).
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from bot.config import ConfigError, Settings
from bot.system import bot_process, handover, remote_server
from bot.system.handover import HandoverError
from bot.system.remote_server import RemoteError

log = logging.getLogger(__name__)

LOCAL, VPS = "local", "vps"
WHERE = {LOCAL: "máy này", VPS: "VPS"}


class JobError(Exception):
    """Lỗi đã có câu giải thích cho người dùng."""


@dataclass
class Job:
    to: str
    state: str = "running"  # running | done | error
    message: str = ""
    steps: list[dict[str, str]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)

    def step(self, label: str) -> dict[str, str]:
        entry = {"label": label, "status": "running", "detail": ""}
        self.steps.append(entry)
        return entry

    def public(self) -> dict[str, Any]:
        return {"to": self.to, "state": self.state, "message": self.message, "steps": [dict(s) for s in self.steps]}


_lock = threading.Lock()
_current: Job | None = None


def current() -> Job | None:
    return _current


def start(settings_provider: Callable[[], Settings], to: str, *, run_in_thread: bool = True) -> Job:
    """Bắt đầu chuyển bot tới `to` ("vps" hoặc "local"). Ném JobError nếu đang có việc khác hoặc `to` sai."""
    global _current
    if to not in (LOCAL, VPS):
        raise JobError("Chỉ chuyển được sang 'vps' hoặc 'local'.")
    with _lock:
        if _current is not None and _current.state == "running":
            raise JobError("Đang có một lần chuyển bot chưa xong.")
        job = _current = Job(to)
    if run_in_thread:
        threading.Thread(target=_run, args=(job, settings_provider), name="handover", daemon=True).start()
    else:
        _run(job, settings_provider)
    return job


def _run(job: Job, settings_provider: Callable[[], Settings]) -> None:
    try:
        settings = settings_provider()
        (_to_vps if job.to == VPS else _to_local)(job, settings)
        job.state = "done"
        job.message = f"Bot đang chạy ở {WHERE[job.to]}."
    except (JobError, HandoverError, RemoteError, ConfigError) as exc:
        job.state = "error"
        job.message = str(exc)
    except Exception as exc:  # noqa: BLE001 - lỗi bất ngờ vẫn phải báo lên giao diện
        log.exception("Chuyển bot lỗi")
        job.state = "error"
        job.message = f"Lỗi bất ngờ: {type(exc).__name__}: {exc}"


def _step(job: Job, label: str, work: Callable[[], str | None]) -> None:
    entry = job.step(label)
    try:
        entry["detail"] = work() or ""
    except Exception as exc:
        entry.update(status="error", detail=str(exc))
        raise
    entry["status"] = "ok"


# ---------- kiểm tra trước ----------

def precheck(to: str, local: dict[str, Any], remote: dict[str, Any]) -> list[str]:
    """Trả về danh sách cảnh báo (không chặn). Ném JobError nếu không thể chuyển."""
    src, dst = (local, remote) if to == VPS else (remote, local)
    if "webhook" in (local.get("receive_mode"), remote.get("receive_mode")):
        raise JobError("Chế độ nhận tin webhook gắn với một địa chỉ cố định, không chuyển qua lại được. "
                       "Dùng polling hoặc personal.")
    if local.get("receive_mode") != remote.get("receive_mode"):
        raise JobError(f"Hai bên đang ở chế độ nhận tin khác nhau (máy này: {local.get('receive_mode')}, "
                       f"VPS: {remote.get('receive_mode')}). Đặt giống nhau ở trang Cài đặt rồi thử lại.")
    if dst.get("running"):
        raise JobError(f"Bot đang chạy ở {WHERE[to]} rồi.")
    if not dst.get("gemini_key_set"):
        raise JobError(f"{WHERE[to].capitalize()} chưa đặt GEMINI_API_KEY (trang Cài đặt).")
    if dst.get("personal"):
        if not (dst.get("zalo_session_set") or src.get("zalo_session_set")):
            raise JobError("Chưa có phiên đăng nhập Zalo cá nhân ở cả hai bên: đăng nhập bằng mã QR trước.")
    elif not dst.get("zalo_token_set"):
        raise JobError(f"{WHERE[to].capitalize()} chưa đặt ZALO_BOT_TOKEN (trang Cài đặt).")
    warnings = []
    if dst.get("personal"):
        warnings.append("Acc Zalo cá nhân đổi sang địa chỉ IP khác có thể bị Zalo đòi đăng nhập lại (quét QR).")
    return warnings


def _statuses(settings: Settings) -> tuple[dict[str, Any], dict[str, Any]]:
    local = bot_process.status_info(settings)
    remote = remote_server.call_sync(settings, "GET", "status", timeout=20)
    return local, remote


def _bundle_path() -> Path:
    return Path(tempfile.mkdtemp(prefix="handover-")) / "bundle.zip"


# ---------- local -> VPS ----------

def _to_vps(job: Job, settings: Settings) -> None:
    if not remote_server.configured(settings):
        raise JobError("Chưa cấu hình VPS (REMOTE_URL, REMOTE_ADMIN_TOKEN).")

    def check() -> str:
        local, remote = _statuses(settings)
        return "; ".join(precheck(VPS, local, remote))

    _step(job, "Kiểm tra hai bên", check)
    stopped = False
    bundle = _bundle_path()
    try:
        def stop_local() -> None:
            nonlocal stopped
            stopped = True
            bot_process.set_standby(settings, "Bot đang chạy ở VPS.")  # đặt cờ trước để không ai bật lại bot khi đang chép
            result = bot_process.stop(settings, bot_process.BOT)
            if not result.ok:
                raise JobError(result.message)

        _step(job, "Tắt bot ở máy này", stop_local)
        _step(job, "Đóng gói dữ liệu",
              lambda: f"{handover.export_bundle(settings, bundle, origin='may-local')['files']} file")
        _step(job, "Gửi dữ liệu lên VPS", lambda: remote_server.upload_sync(settings, "handover/import", bundle) and None)

        def start_remote() -> None:
            data = remote_server.call_sync(settings, "POST", "bot/start", timeout=120)
            if not data.get("ok"):
                raise JobError(f"VPS không bật được bot: {data.get('message')}")

        _step(job, "Bật bot trên VPS", start_remote)
    except Exception:
        if stopped:
            _rollback_local(job, settings)
        raise
    finally:
        shutil.rmtree(bundle.parent, ignore_errors=True)


def _rollback_local(job: Job, settings: Settings) -> None:
    """Chuyển lỗi: bật lại bot ở máy này để không bị gián đoạn."""
    def work() -> str:
        try:
            remote_server.call_sync(settings, "POST", "bot/stop", timeout=60)  # VPS không được chạy cùng lúc
        except RemoteError:
            pass
        bot_process.clear_standby(settings)
        return bot_process.start(settings, bot_process.BOT).message

    try:
        _step(job, "Hoàn tác: bật lại bot ở máy này", work)
    except Exception:  # noqa: BLE001 - đã báo lỗi gốc; lỗi hoàn tác chỉ ghi vào bước
        log.exception("Hoàn tác chuyển bot lỗi")


# ---------- VPS -> local ----------

def _to_local(job: Job, settings: Settings) -> None:
    if not remote_server.configured(settings):
        raise JobError("Chưa cấu hình VPS (REMOTE_URL, REMOTE_ADMIN_TOKEN).")

    def check() -> str:
        local, remote = _statuses(settings)
        return "; ".join(precheck(LOCAL, local, remote))

    _step(job, "Kiểm tra hai bên", check)
    stopped = False
    bundle = _bundle_path()
    try:
        def stop_remote() -> None:
            nonlocal stopped
            stopped = True
            data = remote_server.call_sync(settings, "POST", "handover/standby",
                                           json={"reason": "Bot đang chạy ở máy tính."}, timeout=120)
            if data.get("running"):
                raise JobError("VPS chưa tắt được bot.")

        _step(job, "Tắt bot trên VPS", stop_remote)
        _step(job, "Tải dữ liệu từ VPS", lambda: remote_server.download_sync(settings, "handover/export", bundle))
        _step(job, "Nhận dữ liệu vào máy này", lambda: f"{handover.import_bundle(settings, bundle)['files']} file")

        def start_local() -> None:
            result = bot_process.start(settings, bot_process.BOT, force=True)
            if not result.ok:
                raise JobError(f"Máy này không bật được bot: {result.message}")

        _step(job, "Bật bot ở máy này", start_local)
    except Exception:
        if stopped:
            _rollback_remote(job, settings)
        raise
    finally:
        shutil.rmtree(bundle.parent, ignore_errors=True)


def _rollback_remote(job: Job, settings: Settings) -> None:
    def work() -> str:
        bot_process.set_standby(settings, "Bot đang chạy ở VPS.")
        remote_server.call_sync(settings, "DELETE", "handover/standby", timeout=60)
        data = remote_server.call_sync(settings, "POST", "bot/start", timeout=120)
        return str(data.get("message") or "")

    try:
        _step(job, "Hoàn tác: bật lại bot trên VPS", work)
    except Exception:  # noqa: BLE001
        log.exception("Hoàn tác chuyển bot lỗi")
