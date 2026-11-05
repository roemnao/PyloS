"""Cập nhật khi chạy từ mã nguồn (ZaloBot.cmd / python -m bot gui): git pull, cài thư viện nếu đổi, khởi động lại.

Không dùng được cho ZaloBot.exe (exe là bản đóng gói, muốn mới phải build lại).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from pylos.lobby.dispatch.shared.config import PROJECT_ROOT, is_frozen

log = logging.getLogger(__name__)

LAST_GOOD_FILE = "last_good_commit.txt"   # commit mà giao diện đã chạy ổn định (trong userdata/system)
ROLLBACK_FILE = "rollback_state.json"     # có file này = đang giữ ở bản tốt, không tự cập nhật nữa
HOLD_BRANCH = "rollback-hold"
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
    from pylos.gate.side_gate.vps.bot_process import run_hidden

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
    held = _git("branch", "--show-current") == HOLD_BRANCH
    if held:
        raise UpdateError("Đang giữ ở bản tốt sau khi quay về. Chạy `python -m bot rollback --resume` để nhận code mới.")
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


# ---------- mốc bản tốt và quay về ----------
# Khi một commit làm giao diện/bot không lên, không có ai ở VPS để sửa tay (script pylos-update do root cài, ngoài repo).
# Quay về = chuyển sang nhánh `rollback-hold` đặt ở bản tốt gần nhất. Nhánh này không có bản tương ứng trên origin nên
# `git merge --ff-only origin/<nhánh>` của pylos-update không áp dụng được: VPS đứng yên ở bản tốt, không kéo lại commit hỏng
# cho tới khi người vận hành chạy `rollback --resume`.


def mark_good(system_dir: Path) -> str:
    """Ghi commit hiện tại là bản tốt. Trả về commit đã ghi ("" nếu không phải thư mục git)."""
    if unavailable_reason():
        return ""
    head = _git("rev-parse", "HEAD")
    path = system_dir / LAST_GOOD_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.read_text(encoding="utf-8").strip() != head:
        path.write_text(head, encoding="utf-8")
    return head


def last_good(system_dir: Path) -> str:
    path = system_dir / LAST_GOOD_FILE
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def hold_state(system_dir: Path) -> dict | None:
    path = system_dir / ROLLBACK_FILE
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (OSError, ValueError):
        return None


def rollback(system_dir: Path) -> UpdateResult:
    """Quay về commit tốt gần nhất. Người gọi phải khởi động lại bot và giao diện."""
    reason = unavailable_reason()
    if reason:
        raise UpdateError(reason)
    good = last_good(system_dir)
    if not good:
        raise UpdateError("Chưa có mốc bản tốt (giao diện chưa chạy ổn định lần nào ở máy này).")
    try:
        _git("cat-file", "-e", f"{good}^{{commit}}")
    except UpdateError:
        raise UpdateError(f"Commit tốt {good[:7]} không còn trong kho git của máy này.") from None
    old = _git("rev-parse", "HEAD")
    if old == good:
        return UpdateResult(False, f"Đã ở bản tốt {good[:7]}.", old, good)
    branch = _git("branch", "--show-current")
    _git("checkout", "-q", "-B", HOLD_BRANCH, good)
    if "pyproject.toml" in _git("diff", "--name-only", old, good).splitlines():
        try:
            _run(python_for_pip(), "-m", "pip", "install", "--quiet", "-e", f".[{EXTRAS}]", timeout=900)
        except UpdateError as exc:  # VPS dùng uv, venv có thể không có pip: giữ code đã quay về, báo để người dùng biết
            log.warning("Quay về xong nhưng cài lại thư viện lỗi: %s", exc)
    state = {"from": old, "to": good, "branch": branch if branch != HOLD_BRANCH else (hold_state(system_dir) or {}).get("branch", "main"),
             "at": int(time.time())}
    (system_dir / ROLLBACK_FILE).write_text(json.dumps(state), encoding="utf-8")
    log.warning("Đã quay về bản tốt %s (bản hỏng %s)", good[:7], old[:7])
    return UpdateResult(True, f"Đã quay về bản tốt {good[:7]}. Bản vừa rồi ({old[:7]}) bị bỏ qua. "
                              "VPS giữ ở bản này, không tự cập nhật tới khi chạy `python -m bot rollback --resume`.", old, good)


def resume(system_dir: Path) -> UpdateResult:
    """Thôi giữ ở bản tốt: về nhánh cũ và nhận code mới nhất."""
    reason = unavailable_reason()
    if reason:
        raise UpdateError(reason)
    state = hold_state(system_dir)
    if not state:
        return UpdateResult(False, "Không ở trạng thái giữ bản tốt.")
    old = _git("rev-parse", "HEAD")
    _git("checkout", "-q", state.get("branch") or "main")
    (system_dir / ROLLBACK_FILE).unlink(missing_ok=True)
    result = update()
    return UpdateResult(True, "Đã nhận code mới nhất. " + result.message, old, result.new)
