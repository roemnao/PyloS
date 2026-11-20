"""Markdown (tập con) -> .docx: tiêu đề, đoạn, **đậm**, *nghiêng*, `mã`, danh sách (lồng 3 cấp), bảng, trích dẫn, khối mã, đường kẻ."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_NUMBER = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_INLINE = re.compile(r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|__.+?__|\*[^*\s][^*]*?\*|`[^`]+`)")
_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def _inline(par, text: str) -> None:
    for part in _INLINE.split(text):
        if not part:
            continue
        if part.startswith("***") and part.endswith("***") and len(part) > 6:
            run = par.add_run(part[3:-3])
            run.bold = run.italic = True
        elif (part.startswith("**") and part.endswith("**") and len(part) > 4) or \
             (part.startswith("__") and part.endswith("__") and len(part) > 4):
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            par.add_run(part[1:-1]).italic = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            run = par.add_run(part[1:-1])
            run.font.name = "Consolas"
        else:
            par.add_run(part)


def _rule(doc) -> None:
    par = doc.add_paragraph()
    pr = par._p.get_or_add_pPr()
    border = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "1"), ("w:color", "808080")):
        bottom.set(qn(k), v)
    border.append(bottom)
    pr.append(border)


def _cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def _table(doc, lines: list[str]) -> None:
    rows = [_cells(l) for l in lines if not _SEPARATOR.match(l)]
    if not rows:
        return
    width = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=width)
    try:
        table.style = "Table Grid"
    except KeyError:  # mẫu docx người dùng không có style này
        pass
    for i, row in enumerate(rows):
        for j in range(width):
            par = table.cell(i, j).paragraphs[0]
            _inline(par, row[j] if j < len(row) else "")
            if i == 0:
                for run in par.runs:
                    run.bold = True
    doc.add_paragraph()


def _style(doc, name: str, fallback: str) -> str:
    try:
        doc.styles[name]
        return name
    except KeyError:
        return fallback


def add_markdown(doc, md: str) -> None:
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    i = 0
    para: list[str] = []

    def flush() -> None:
        if para:
            _inline(doc.add_paragraph(), " ".join(s.strip() for s in para))
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                run = doc.add_paragraph().add_run(lines[i])
                run.font.name = "Consolas"
                run.font.size = Pt(9.5)
                i += 1
            i += 1
            continue
        if not line.strip():
            flush()
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < len(lines) and _SEPARATOR.match(lines[i + 1]):
            flush()
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            _table(doc, block)
            continue
        if _RULE.match(line):
            flush()
            _rule(doc)
            i += 1
            continue
        m = _HEADING.match(line)
        if m:
            flush()
            doc.add_heading(m.group(2), level=len(m.group(1)))
            i += 1
            continue
        m_b, m_n = _BULLET.match(line), _NUMBER.match(line)
        if m_b or m_n:
            flush()
            m = m_b or m_n
            level = min(len(m.group(1).replace("\t", "  ")) // 2, 2)
            base = "List Bullet" if m_b else "List Number"
            name = base if level == 0 else f"{base} {level + 1}"
            _inline(doc.add_paragraph(style=_style(doc, name, base)), m.group(2))
            i += 1
            continue
        if line.lstrip().startswith(">"):
            flush()
            _inline(doc.add_paragraph(style=_style(doc, "Quote", "Normal")), line.lstrip()[1:].strip())
            i += 1
            continue
        para.append(line)
        i += 1
    flush()


def markdown_to_docx(md: str, path: Path) -> None:
    doc = Document()
    add_markdown(doc, md)
    doc.save(str(path))
