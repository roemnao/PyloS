"""Sửa tài liệu có sẵn: thay chữ, thêm cuối, ghi đè. Mỗi lần sửa giữ bản cũ ở <tên>.bak để hoàn tác."""

from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document

from pylos.lobby.office.documents.files import DocError
from pylos.lobby.office.documents.writer import add_markdown


def backup(path: Path) -> Path:
    bak = path.with_name(path.name + ".bak")
    shutil.copy2(path, bak)
    return bak


def restore(path: Path) -> None:
    bak = path.with_name(path.name + ".bak")
    if not bak.is_file():
        raise DocError(f"Chưa có bản cũ nào của {path.name} để hoàn tác.")
    shutil.copy2(bak, path)


def _open(path: Path):
    try:
        return Document(str(path))
    except Exception as exc:
        raise DocError(f"Không mở được {path.name}: {exc}") from None


def _paragraphs(container):
    yield from container.paragraphs
    for table in container.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from _paragraphs(cell)


def _replace_in_paragraph(par, find: str, repl: str) -> int:
    """Thay trong đoạn kể cả khi chữ bị chia qua nhiều run; phần thay mang định dạng của run đầu tiên."""
    runs = par.runs
    full = "".join(r.text for r in runs)
    starts, i = [], full.find(find)
    while i != -1:
        starts.append(i)
        i = full.find(find, i + len(find))
    for s in reversed(starts):  # từ cuối lên để các vị trí phía trước không lệch
        e, off, first = s + len(find), 0, True
        for r in runs:
            text = r.text
            rs, re_ = off, off + len(text)
            off = re_
            if re_ <= s or rs >= e:
                continue
            a, b = max(s, rs) - rs, min(e, re_) - rs
            r.text = text[:a] + (repl if first else "") + text[b:]
            first = False
    return len(starts)


def replace_text(path: Path, find: str, repl: str) -> int:
    if not find:
        raise DocError("Thiếu chuỗi cần tìm.")
    if path.suffix.lower() != ".docx":
        text = path.read_text(encoding="utf-8")
        count = text.count(find)
        if count:
            backup(path)
            path.write_text(text.replace(find, repl), encoding="utf-8")
        return count
    doc = _open(path)
    containers = [doc] + [part for s in doc.sections for part in (s.header, s.footer)]
    count = sum(_replace_in_paragraph(p, find, repl) for c in containers for p in _paragraphs(c))
    if count:
        backup(path)
        doc.save(str(path))
    return count


def append_markdown(path: Path, md: str) -> None:
    backup(path)
    if path.suffix.lower() != ".docx":
        old = path.read_text(encoding="utf-8")
        path.write_text(old.rstrip("\n") + "\n\n" + md.strip("\n") + "\n", encoding="utf-8")
        return
    doc = _open(path)
    add_markdown(doc, md)
    doc.save(str(path))


def overwrite_markdown(path: Path, md: str) -> None:
    """Viết lại toàn bộ nội dung; với .docx giữ nguyên style/khổ giấy của file cũ."""
    backup(path)
    if path.suffix.lower() != ".docx":
        path.write_text(md, encoding="utf-8")
        return
    doc = _open(path)
    body = doc.element.body
    for child in list(body.iterchildren()):
        if not child.tag.endswith("}sectPr"):
            body.remove(child)
    add_markdown(doc, md)
    doc.save(str(path))
