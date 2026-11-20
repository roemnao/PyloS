"""Thư mục tài liệu của từng chat: huts/<chat_id>/docs/. Mọi đường dẫn đi qua `resolve` để không thoát khỏi thư mục này."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

from pylos.lobby.dispatch.shared.data_stores import safe_name

ALLOWED = (".docx", ".md", ".txt")
MAX_NAME = 80
_BAD_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


class DocError(Exception):
    """Lỗi người dùng hiểu được (tên sai, không thấy file...), tool trả nguyên văn về cho model."""


@dataclass(frozen=True)
class DocInfo:
    name: str
    size: int
    modified: float


def docs_dir(huts_dir: Path, chat_id: str) -> Path:
    return huts_dir / safe_name(chat_id) / "docs"


def clean_name(name: str) -> str:
    """Bỏ thư mục, ký tự cấm; kiểm tra đuôi. Giữ chữ tiếng Việt có dấu."""
    base = Path(str(name or "").replace("\\", "/")).name.strip()
    stem, dot, ext = base.rpartition(".")
    ext = ("." + ext.lower()) if dot else ""
    if ext not in ALLOWED:
        raise DocError(f"Chỉ làm việc với tệp {', '.join(ALLOWED)} (tên bạn đưa: {base or '(trống)'}).")
    stem = _BAD_CHARS.sub("_", stem).strip(" .")[:MAX_NAME]
    if not stem:
        raise DocError("Tên tệp trống.")
    return stem + ext


def resolve(folder: Path, name: str) -> Path:
    path = (folder / clean_name(name)).resolve()
    try:
        path.relative_to(folder.resolve())
    except ValueError:
        raise DocError("Tên tệp không hợp lệ.") from None
    return path


def existing(folder: Path, name: str) -> Path:
    path = resolve(folder, name)
    if not path.is_file():
        raise DocError(f"Không thấy tệp {path.name}. Gọi ds_tai_lieu để xem danh sách.")
    return path


def unique_path(folder: Path, name: str) -> Path:
    """Đường dẫn chưa dùng: trùng tên thì thêm -2, -3..."""
    path = resolve(folder, name)
    n = 2
    while path.exists():
        path = resolve(folder, f"{path.stem}-{n}{path.suffix}")
        n += 1
    return path


def list_docs(folder: Path) -> list[DocInfo]:
    if not folder.is_dir():
        return []
    out = [DocInfo(p.name, p.stat().st_size, p.stat().st_mtime) for p in folder.iterdir()
           if p.is_file() and p.suffix.lower() in ALLOWED]
    return sorted(out, key=lambda d: d.modified, reverse=True)


def folder_size(folder: Path) -> int:
    return sum(p.stat().st_size for p in folder.iterdir() if p.is_file()) if folder.is_dir() else 0


def prune(folder: Path, keep_days: int, now: float | None = None) -> int:
    """Xoá tệp (cả .bak) quá keep_days ngày không đụng tới. keep_days 0 = giữ mãi. Trả số tệp đã xoá."""
    if keep_days <= 0 or not folder.is_dir():
        return 0
    cutoff = (now if now is not None else time.time()) - keep_days * 86400
    removed = 0
    for p in folder.iterdir():
        if p.is_file() and p.stat().st_mtime < cutoff:
            p.unlink(missing_ok=True)
            removed += 1
    return removed
