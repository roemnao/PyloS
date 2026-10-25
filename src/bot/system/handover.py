"""Gói dữ liệu để chuyển bot giữa máy local và VPS (xem docs/PLAN.md, mục Điều khiển VPS từ xa).

Gói là một file zip gồm:
  data/...                   toàn bộ Settings.data_dir (nhóm, lịch sử, memorydata, tool tự viết...)
  workspace/...              Settings.workspace_dir, chỉ khi nó nằm ngoài data_dir
  system/processed_message_ids.txt   id tin đã xử lý, để bên nhận không trả lời lại tin cũ
  session/zalo_login_session.json    phiên acc Zalo cá nhân (nếu có)
  manifest.json              nơi gửi, giờ gửi, commit, chế độ nhận tin

Không bao giờ có settings.env (khoá của mỗi máy khác nhau), log, file khoá/pid, hồ sơ cửa sổ.
Nhập gói thay thế dữ liệu hiện tại (sao lưu trước), nên chỉ làm khi bot ở máy nhận đang tắt.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from bot.config import Settings
from bot.core.vietnam_time import now_ms, now_vn
from bot.system import bot_process
from bot.userdata_paths import CONSOLE_TEST_DIR, HANDOVER_BACKUP_DIR, PROCESSED_IDS_FILE

MAX_FILES = 100_000
MAX_FILE_BYTES = 200 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
KEEP_BACKUPS = 3

SKIP_DIRS = {".backup", CONSOLE_TEST_DIR, "__pycache__"}
SKIP_SUFFIXES = (".lock", ".pid", ".tmp")
MANIFEST = "manifest.json"
SESSION_ARC = "session/zalo_login_session.json"
IDS_ARC = f"system/{PROCESSED_IDS_FILE}"


class HandoverError(Exception):
    """Thông báo đã sẵn sàng để hiện cho người dùng."""


def _skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    return any(part in SKIP_DIRS for part in rel.parts[:-1]) or path.name.endswith(SKIP_SUFFIXES)


def _tree(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and not _skip(p, root))


def _workspace_outside_data(settings: Settings) -> bool:
    try:
        settings.workspace_dir.resolve().relative_to(settings.data_dir.resolve())
    except ValueError:
        return True
    return False


def _sources(settings: Settings) -> list[tuple[str, Path]]:
    """[(tên trong zip, file thật)]"""
    items = [(f"data/{p.relative_to(settings.data_dir).as_posix()}", p) for p in _tree(settings.data_dir)]
    if _workspace_outside_data(settings):
        items += [(f"workspace/{p.relative_to(settings.workspace_dir).as_posix()}", p) for p in _tree(settings.workspace_dir)]
    ids = settings.system_dir / PROCESSED_IDS_FILE
    if ids.is_file():
        items.append((IDS_ARC, ids))
    if settings.zalo_session_file.is_file():
        items.append((SESSION_ARC, settings.zalo_session_file))
    return items


def export_bundle(settings: Settings, dest: Path, *, origin: str = "") -> dict[str, Any]:
    """Ghi gói zip ra dest và trả về manifest."""
    from bot import __version__

    sources = _sources(settings)
    manifest = {
        "origin": origin or socket.gethostname(), "created_at": now_ms(), "version": __version__,
        "receive_mode": settings.receive_mode, "files": len(sources),
        "bytes": sum(p.stat().st_size for _, p in sources),
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc, path in sources:
            zf.write(path, arc)
        zf.writestr(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def _target(settings: Settings, arc: str) -> Path | None:
    """Đường dẫn thật cho một tên trong zip, hoặc None nếu tên không được phép."""
    if not arc or arc.startswith(("/", "\\")) or "\\" in arc or ":" in arc or "\x00" in arc:
        return None
    parts = PurePosixPath(arc).parts
    if any(p in ("", ".", "..") for p in parts):
        return None
    if arc == IDS_ARC:
        return settings.system_dir / PROCESSED_IDS_FILE
    if arc == SESSION_ARC:
        return settings.zalo_session_file
    if len(parts) >= 2 and parts[0] == "data":
        root = settings.data_dir
    elif len(parts) >= 2 and parts[0] == "workspace" and _workspace_outside_data(settings):
        root = settings.workspace_dir
    else:
        return None
    if any(p in SKIP_DIRS for p in parts[1:-1]) or parts[-1].endswith(SKIP_SUFFIXES):
        return None
    target = root.joinpath(*parts[1:])
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return target


def read_manifest(zip_path: Path) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(zip_path) as zf:
            return json.loads(zf.read(MANIFEST).decode("utf-8"))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile):
        raise HandoverError("Đây không phải gói chuyển bot hợp lệ.") from None


def validate_bundle(settings: Settings, zip_path: Path) -> list[tuple[zipfile.ZipInfo, Path]]:
    """Kiểm tra kỹ từng tên và kích thước trước khi ghi bất cứ thứ gì."""
    try:
        zf = zipfile.ZipFile(zip_path)
    except (OSError, zipfile.BadZipFile):
        raise HandoverError("Gói chuyển bot bị hỏng hoặc không phải file zip.") from None
    with zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > MAX_FILES:
            raise HandoverError("Gói có quá nhiều file.")
        plan: list[tuple[zipfile.ZipInfo, Path]] = []
        total = 0
        for info in infos:
            if info.filename == MANIFEST:
                continue
            target = _target(settings, info.filename)
            if target is None:
                raise HandoverError(f"Gói chứa đường dẫn không được phép: {info.filename!r}")
            if info.file_size > MAX_FILE_BYTES:
                raise HandoverError(f"File quá lớn trong gói: {info.filename}")
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise HandoverError("Gói quá lớn.")
            plan.append((info, target))
    return plan


def backup_dir(settings: Settings) -> Path:
    return settings.system_dir / HANDOVER_BACKUP_DIR


def _prune_backups(settings: Settings) -> None:
    for old in sorted(backup_dir(settings).glob("*.zip"))[:-KEEP_BACKUPS]:
        old.unlink(missing_ok=True)


def import_bundle(settings: Settings, zip_path: Path) -> dict[str, Any]:
    """Thay dữ liệu của máy này bằng gói. Từ chối khi bot đang chạy. Trả về manifest của gói."""
    if bot_process.is_running(settings, bot_process.BOT):
        raise HandoverError("Bot đang chạy ở máy nhận. Hãy tắt bot trước khi nhận dữ liệu.")
    manifest = read_manifest(zip_path)
    plan = validate_bundle(settings, zip_path)

    backup = backup_dir(settings) / f"{now_vn():%Y%m%d-%H%M%S}.zip"
    export_bundle(settings, backup, origin="sao-luu-truoc-khi-nhan")
    _prune_backups(settings)

    wanted = {target.resolve() for _, target in plan}
    with zipfile.ZipFile(zip_path) as zf:
        # Ghi file mới sang tên tạm trước; chỉ khi tất cả đã ghi xong mới đổi tên và xoá file thừa.
        staged: list[tuple[Path, Path]] = []
        try:
            for info, target in plan:
                target.parent.mkdir(parents=True, exist_ok=True)
                tmp = target.with_name(target.name + ".handover.tmp")
                with zf.open(info) as src, open(tmp, "wb") as out:
                    shutil.copyfileobj(src, out)
                staged.append((tmp, target))
        except Exception:
            for tmp, _ in staged:
                tmp.unlink(missing_ok=True)
            raise
    for tmp, target in staged:
        for attempt in range(5):
            try:
                os.replace(tmp, target)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.1 * (attempt + 1))
    # Bản sao phải giống hệt nơi gửi: bỏ file chỉ có ở máy này (đã có bản sao lưu).
    roots = [(settings.data_dir, "data")]
    if _workspace_outside_data(settings):
        roots.append((settings.workspace_dir, "workspace"))
    for root, _ in roots:
        for path in _tree(root):
            if path.resolve() not in wanted:
                path.unlink(missing_ok=True)
    ids = settings.system_dir / PROCESSED_IDS_FILE
    if ids.resolve() not in wanted:
        ids.unlink(missing_ok=True)
    bot_process.clear_standby(settings)
    return manifest
