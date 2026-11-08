"""Căn hộ của bot lọc: chỉ dẫn lấy từ mọi tài liệu .md/.txt trong workspace/ (SOUL.md...), tự nạp lại khi file đổi."""

from __future__ import annotations

import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

# Ghi chú <!-- ... --> trong file là cho người đọc, không đưa vào chỉ dẫn.
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
DOC_SUFFIXES = {".md", ".txt"}
MAX_CHARS = 20_000  # tổng chỉ dẫn; quá thì bỏ phần sau và ghi cảnh báo


class FilterInstructions:
    """`text(names)`: chỉ dẫn của bot lọc, `{names}` được thay bằng tên gọi của bot chính. Rỗng nếu workspace trống."""

    def __init__(self, workspace_dir: Path) -> None:
        self._workspace = workspace_dir
        self._cache: dict[Path, tuple[float, str]] = {}

    def _read(self, path: Path) -> str:
        mtime = path.stat().st_mtime
        cached = self._cache.get(path)
        if cached is None or cached[0] != mtime:
            cached = (mtime, _HTML_COMMENT.sub("", path.read_text(encoding="utf-8")).strip())
            self._cache[path] = cached
            log.info("Đã nạp %s của bot lọc", path.name)
        return cached[1]

    def docs(self) -> list[tuple[str, str]]:
        if not self._workspace.is_dir():
            return []
        found, used = [], 0
        for path in sorted(self._workspace.rglob("*"), key=lambda p: p.relative_to(self._workspace).as_posix().lower()):
            rel = path.relative_to(self._workspace)
            if not path.is_file() or path.suffix.lower() not in DOC_SUFFIXES or any(part.startswith(".") for part in rel.parts):
                continue
            try:
                text = self._read(path)
            except OSError as exc:
                log.warning("Không đọc được %s của bot lọc: %s", rel, exc)
                continue
            if not text:
                continue
            if used + len(text) > MAX_CHARS:
                log.warning("Chỉ dẫn của bot lọc quá dài: bỏ %s và các file sau (tối đa %d ký tự)", rel, MAX_CHARS)
                break
            used += len(text)
            found.append((rel.as_posix(), text))
        return found

    def text(self, names: str) -> str:
        docs = self.docs()
        body = docs[0][1] if len(docs) == 1 else "\n\n".join(f"## {name}\n{text}" for name, text in docs)
        return body.replace("{names}", names)
