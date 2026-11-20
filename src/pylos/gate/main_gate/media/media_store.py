"""Kho tệp người dùng gửi: huts/<chat_id>/media/<msg_id>.<đuôi> và media_index.jsonl.

Tệp tự xoá sau MEDIA_KEEP_HOURS. Chỉ lưu những tệp bộ lọc đã cho qua.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

from pylos.gate.main_gate.media.media_fetch import MediaFile
from pylos.lobby.dispatch.shared.data_stores import safe_name

MEDIA_DIR = "media"
INDEX_FILE = "media_index.jsonl"


def hut_media_dir(huts_dir: Path, chat_id: str) -> Path:
    """huts/<chat_id>/media: tệp người dùng gửi (ảnh, video, tin thoại)."""
    return huts_dir / safe_name(chat_id) / MEDIA_DIR


def _read_rows(index: Path) -> list[dict[str, Any]]:
    try:
        lines = index.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def _write_rows(index: Path, rows: list[dict[str, Any]]) -> None:
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


class MediaStore:
    def __init__(self, huts_dir: Path, keep_hours: float = 24, clock=time.time) -> None:
        self._huts = huts_dir
        self.keep_seconds = keep_hours * 3600
        self._clock = clock

    def dir_for(self, chat_id: str) -> Path:
        return hut_media_dir(self._huts, chat_id)

    def _index(self, chat_id: str) -> Path:
        return self.dir_for(chat_id) / INDEX_FILE

    def save(self, chat_id: str, msg_id: str, file: MediaFile, uid: str = "", caption: str = "") -> dict[str, Any]:
        rows = [r for r in _read_rows(self._index(chat_id)) if r.get("msg_id") != msg_id]
        row = {"msg_id": msg_id, "kind": file.kind, "path": file.path.name, "mime": file.mime, "size": file.size,
               "t": self._clock(), "uid": uid, "caption": caption, "file_uri": "", "file_uri_expires": 0}
        rows.append(row)
        _write_rows(self._index(chat_id), rows)
        self.prune(chat_id)
        return row

    def get(self, chat_id: str, msg_id: str, max_age: float | None = None) -> dict[str, Any] | None:
        """Bản ghi (kèm "full_path") nếu tệp còn trên đĩa và chưa quá max_age giây (mặc định: thời gian giữ)."""
        limit = self.keep_seconds if max_age is None else min(max_age, self.keep_seconds)
        for row in _read_rows(self._index(chat_id)):
            if row.get("msg_id") != msg_id:
                continue
            full = self.dir_for(chat_id) / str(row.get("path"))
            if self._clock() - float(row.get("t", 0)) <= limit and full.is_file():
                return {**row, "full_path": full}
        return None

    def recent(self, chat_id: str, msg_ids: list[str], max_age: float | None = None) -> list[dict[str, Any]]:
        """Các tệp còn hạn trong msg_ids, giữ thứ tự msg_ids."""
        found = (self.get(chat_id, m, max_age) for m in msg_ids)
        return [row for row in found if row]

    def set_file_uri(self, chat_id: str, msg_id: str, uri: str, expires: float) -> None:
        rows = _read_rows(self._index(chat_id))
        for row in rows:
            if row.get("msg_id") == msg_id:
                row["file_uri"], row["file_uri_expires"] = uri, expires
        _write_rows(self._index(chat_id), rows)

    def prune(self, chat_id: str | None = None) -> int:
        """Xoá tệp quá hạn. chat_id=None: quét mọi túp lều (lúc bot khởi động). Trả về số tệp đã xoá."""
        if chat_id is not None:
            return self._prune_dir(self.dir_for(chat_id))
        removed = 0
        if self._huts.is_dir():
            for hut in self._huts.iterdir():
                if (hut / MEDIA_DIR).is_dir():
                    removed += self._prune_dir(hut / MEDIA_DIR)
        return removed

    def _prune_dir(self, media_dir: Path) -> int:
        if not media_dir.is_dir():
            return 0
        index = media_dir / INDEX_FILE
        rows = _read_rows(index)
        keep, removed = [], 0
        for row in rows:
            if self._clock() - float(row.get("t", 0)) > self.keep_seconds:
                (media_dir / str(row.get("path"))).unlink(missing_ok=True)
                removed += 1
            else:
                keep.append(row)
        listed = {str(r.get("path")) for r in keep} | {INDEX_FILE}
        for stray in media_dir.iterdir():
            if stray.name not in listed and stray.is_file() and self._clock() - stray.stat().st_mtime > self.keep_seconds:
                stray.unlink(missing_ok=True)
        if len(keep) != len(rows):
            _write_rows(index, keep)
        if not keep and not any(p for p in media_dir.iterdir() if p.name != INDEX_FILE):
            shutil.rmtree(media_dir, ignore_errors=True)
        return removed
