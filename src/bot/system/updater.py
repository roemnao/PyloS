"""Cập nhật khi chạy từ mã nguồn (ZaloBot.cmd / python -m bot gui): git pull, cài thư viện nếu đổi, khởi động lại.

Không dùng được cho ZaloBot.exe (exe là bản đóng gói, muốn mới phải build lại).
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from dataclasses import dataclass

from bot.config import PROJECT_ROOT, is_frozen

log = logging.getLogger(__name__)

# Thư viện của ứng dụng quản lý + chế độ acc Zalo cá nhân (xem pyproject.toml)
EXTRAS = "desktop,personal"


class UpdateError(Exception):
    pass


@dataclass(frozen=True)
class UpdateResult:
    changed: bool
    message: str
    old: str = ""
    new: str = ""


def unavailable_reason() -> str | None:
    """None nếu cập nhật được; ngược lại là lý do để hiện cho người dùng."""
    if is_frozen():
        return "Đang chạy ZaloBot.exe: bản exe không tự cập nhật. Dùng ZaloBot.cmd để luôn chạy code mới nhất."
    if not (PROJECT_ROOT / ".git").exists():
        return f"{PROJECT_ROOT} không phải thư mục git (cần tải code bằng git clone)."
    return None


def _run(*args: str, timeout: float = 120) -> str:
    from bot.system.gateway import run_hidden  # ẩn cửa sổ cmd khi chạy từ pythonw / exe

    try:
        done = run_hidden(list(args), timeout=timeout, cwd=PROJECT_ROOT)
    except FileNotFoundError:
        raise UpdateError(f"Không tìm thấy lệnh {args[0]} (đã cài Git chưa?)") from None
    except subprocess.TimeoutExpired:
        raise UpdateError(f"Lệnh {' '.join(args[:3])} chạy quá lâu") from None
    stdout = done.stdout.decode("utf-8", errors="replace").strip()
    if done.returncode != 0:
        detail = (done.stderr.decode("utf-8", errors="replace") or stdout).strip().splitlines()
        raise UpdateError(f"{' '.join(args[:3])} lỗi: {detail[-1] if detail else done.returncode}")
    return stdout


def _git(*args: str, timeout: float = 120) -> str:
    return _run("git", *args, timeout=timeout)


def pending_commits() -> int:
    """Số commit mới trên GitHub chưa có ở máy (git fetch rồi so với nhánh đang theo dõi)."""
    if unavailable_reason():
        return 0
    _git("fetch", "--quiet", timeout=60)
    return int(_git("rev-list", "--count", "HEAD..@{u}") or 0)


def python_for_pip() -> str:
    # pythonw.exe không có console; pip chạy được nhưng dùng python.exe cùng thư mục cho chắc.
    exe = sys.executable
    if exe.lower().endswith("pythonw.exe"):
        candidate = exe[: -len("pythonw.exe")] + "python.exe"
        if os.path.exists(candidate):
            return candidate
    return exe


def update() -> UpdateResult:
    reason = unavailable_reason()
    if reason:
        raise UpdateError(reason)
    old = _git("rev-parse", "HEAD")
    _git("pull", "--ff-only", timeout=180)
    new = _git("rev-parse", "HEAD")
    if old == new:
        return UpdateResult(False, "Đã là bản mới nhất.", old, new)
    changed_files = _git("diff", "--name-only", old, new).splitlines()
    if "pyproject.toml" in changed_files:
        log.info("pyproject.toml thay đổi: cài lại thư viện")
        _run(python_for_pip(), "-m", "pip", "install", "--quiet", "-e", f".[{EXTRAS}]", timeout=900)
    summary = _git("log", "--format=• %s", f"{old}..{new}").splitlines()
    log.info("Đã cập nhật %s -> %s (%d commit)", old[:7], new[:7], len(summary))
    head = "\n".join(summary[:5]) + (f"\n… và {len(summary) - 5} thay đổi khác" if len(summary) > 5 else "")
    return UpdateResult(True, f"Đã cập nhật {len(summary)} thay đổi:\n{head}", old, new)
