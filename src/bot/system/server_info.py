"""Thông tin máy đang chạy bot (máy Windows hoặc VPS Linux), để trang Máy chủ so sánh hai bên.

Chỉ đọc: không ghi gì vào .git hay hệ thống. Mọi phần lỗi được bỏ qua (trả None) thay vì làm hỏng cả trang.
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import time
from typing import Any

from bot.config import PROJECT_ROOT, Settings
from bot.system import auto_update, bot_process

UNITS = ("pylos-bot", "pylos-admin", "pylos-update.timer")


def _uptime_seconds() -> int | None:
    try:
        with open("/proc/uptime", encoding="utf-8") as fh:
            return int(float(fh.read().split()[0]))
    except (OSError, ValueError, IndexError):
        pass
    if os.name == "nt":
        try:
            import ctypes

            return int(ctypes.windll.kernel32.GetTickCount64() / 1000)
        except (AttributeError, OSError):
            return None
    return None


def _memory() -> dict[str, int] | None:
    """{total, available} tính bằng byte."""
    try:
        values: dict[str, int] = {}
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                key, _, rest = line.partition(":")
                if key in ("MemTotal", "MemAvailable"):
                    values[key] = int(rest.split()[0]) * 1024
        return {"total": values["MemTotal"], "available": values["MemAvailable"]}
    except (OSError, ValueError, KeyError):
        pass
    if os.name == "nt":
        try:
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                            ("avail", ctypes.c_ulonglong), ("tpage", ctypes.c_ulonglong), ("apage", ctypes.c_ulonglong),
                            ("tvirt", ctypes.c_ulonglong), ("avirt", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]

            status = Status()
            status.length = ctypes.sizeof(Status)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return {"total": int(status.total), "available": int(status.avail)}
        except (AttributeError, OSError):
            return None
    return None


def _git(*args: str, timeout: float = 20) -> str | None:
    try:
        return auto_update._git(*args, timeout=timeout)
    except auto_update.UpdateError:
        return None


def code_version() -> dict[str, Any]:
    """Commit đang chạy và commit mới nhất trên nhánh theo dõi (git ls-remote: không ghi gì vào .git)."""
    if auto_update.unavailable_reason():
        return {"git": False}
    head = _git("rev-parse", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    subject = _git("log", "-1", "--format=%s")
    latest = None
    if branch and branch != "HEAD":
        out = _git("ls-remote", "origin", f"refs/heads/{branch}")
        latest = out.split()[0] if out else None
    return {"git": True, "head": head, "branch": branch, "subject": subject, "latest": latest,
            "behind": bool(head and latest and head != latest)}


def _systemd_state(unit: str) -> str | None:
    try:
        done = bot_process.run_hidden(["systemctl", "is-active", unit], timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.decode("utf-8", errors="replace").strip() or None


def last_update_run() -> dict[str, str] | None:
    try:
        done = bot_process.run_hidden(
            ["systemctl", "show", "pylos-update.service", "-p", "ExecMainExitTimestamp", "-p", "Result"], timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    pairs = dict(line.split("=", 1) for line in done.stdout.decode("utf-8", errors="replace").splitlines() if "=" in line)
    return {"at": pairs.get("ExecMainExitTimestamp", ""), "result": pairs.get("Result", "")} if pairs else None


def collect(settings: Settings) -> dict[str, Any]:
    disk = None
    try:
        usage = shutil.disk_usage(settings.system_dir if settings.system_dir.exists() else PROJECT_ROOT)
        disk = {"total": usage.total, "free": usage.free}
    except OSError:
        pass
    load = None
    if hasattr(os, "getloadavg"):
        try:
            load = [round(x, 2) for x in os.getloadavg()]
        except OSError:
            pass
    systemd = settings.bot_supervisor == "systemd" and os.name != "nt"
    return {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "uptime_seconds": _uptime_seconds(),
        "load": load,
        "memory": _memory(),
        "disk": disk,
        "version": code_version(),
        "supervisor": settings.bot_supervisor,
        "units": {unit: _systemd_state(unit) for unit in UNITS} if systemd else None,
        "last_update": last_update_run() if systemd else None,
        "standby": bot_process.standby_info(settings),
        "now": int(time.time() * 1000),
    }
