"""Đọc tài liệu thành văn bản markdown cho model: .md/.txt đọc thẳng, .docx đổi sang markdown."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from pylos.lobby.office.documents.files import DocError

_HEADING = re.compile(r"^Heading (\d)$")


def _runs_md(par: Paragraph) -> str:
    out = []
    for run in par.runs:
        text = run.text
        if not text.strip():
            out.append(text)
            continue
        lead, core, tail = text[:len(text) - len(text.lstrip())], text.strip(), text[len(text.rstrip()):]
        if run.bold and run.italic:
            core = f"***{core}***"
        elif run.bold:
            core = f"**{core}**"
        elif run.italic:
            core = f"*{core}*"
        out.append(lead + core + tail)
    return "".join(out).replace("****", "")  # hai run đậm liền nhau


def _paragraph_md(par: Paragraph) -> str:
    text = _runs_md(par).strip()
    if not text:
        return ""
    style = par.style.name if par.style is not None else ""
    if style == "Title":
        return f"# {text}"
    m = _HEADING.match(style)
    if m:
        return f"{'#' * min(int(m.group(1)), 6)} {text}"
    level = 0
    if style.startswith("List") and style[-1].isdigit():
        level = int(style[-1]) - 1
    if style.startswith("List Bullet"):
        return f"{'  ' * level}- {text}"
    if style.startswith("List Number"):
        return f"{'  ' * level}1. {text}"
    if style in ("Quote", "Intense Quote"):
        return f"> {text}"
    return text


def _cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def _table_md(table: Table) -> str:
    rows = [[_cell(c.text) for c in row.cells] for row in table.rows]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def docx_to_markdown(path: Path) -> str:
    try:
        doc = Document(str(path))
    except Exception as exc:  # file hỏng / không phải docx
        raise DocError(f"Không mở được {path.name} (file hỏng hoặc không phải .docx): {exc}") from None
    blocks: list[str] = []
    for child in doc.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            md = _paragraph_md(Paragraph(child, doc))
        elif tag == "tbl":
            md = _table_md(Table(child, doc))
        else:
            continue
        if md:
            blocks.append(md)
    # Dòng liền kề cùng loại danh sách thì không chèn dòng trống giữa.
    out: list[str] = []
    for i, b in enumerate(blocks):
        if i and not (_is_item(b) and _is_item(blocks[i - 1])):
            out.append("")
        out.append(b)
    return "\n".join(out)


def _is_item(block: str) -> bool:
    return bool(re.match(r"^\s*(- |\d+\. )", block))


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return docx_to_markdown(path)
    return path.read_text(encoding="utf-8", errors="replace")


def read_slice(path: Path, start: int = 0, max_chars: int = 12000) -> dict:
    """Đọc từ ký tự `start`, tối đa max_chars; báo còn bao nhiêu để model đọc tiếp."""
    text = read_text(path)
    start = max(0, int(start))
    chunk = text[start:start + max_chars]
    end = start + len(chunk)
    result = {"ten": path.name, "noi_dung": chunk, "tong_ky_tu": len(text)}
    if end < len(text):
        result["con_lai"] = len(text) - end
        result["doc_tiep_tu_vi_tri"] = end
    return result
