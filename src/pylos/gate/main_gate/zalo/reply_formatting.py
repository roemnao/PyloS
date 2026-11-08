"""Xử lý văn bản gửi lên Zalo."""

from __future__ import annotations

import re

# sendMessage nhận 1–2000 ký tự. Đếm theo UTF-16 (emoji = 2) cho chắc, vì
# text_styles của Zalo cũng đo bằng UTF-16 code unit.
ZALO_TEXT_LIMIT = 2000


def utf16_len(text: str) -> int:
    return sum(2 if ord(ch) > 0xFFFF else 1 for ch in text)


def _max_prefix(text: str, limit: int) -> int:
    size = 0
    for index, ch in enumerate(text):
        size += 2 if ord(ch) > 0xFFFF else 1
        if size > limit:
            return index
    return len(text)


def split_message(text: str, limit: int = ZALO_TEXT_LIMIT) -> list[str]:
    """Chia văn bản thành các đoạn <= limit, ưu tiên cắt ở đoạn văn, dòng, câu, rồi khoảng trắng."""
    text = text.strip()
    chunks = []
    while utf16_len(text) > limit:
        cut = _max_prefix(text, limit)
        window = text[:cut]
        for separator in ("\n\n", "\n", ". ", " "):
            position = window.rfind(separator)
            if position > cut // 2:
                cut = position + len(separator)
                break
        chunk = text[:cut].rstrip()
        if chunk:
            chunks.append(chunk)
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


SPLIT_OFF = "off"
SPLIT_LINE = "line"
SPLIT_PARAGRAPH = "paragraph"
SPLIT_MODES = (SPLIT_OFF, SPLIT_LINE, SPLIT_PARAGRAPH)

_LIST_ITEM = re.compile(r"^\s*(?:[•\-*]|\d+[.)])\s+")


def _blocks(text: str) -> list[list[str]]:
    """Chia văn bản thành các đoạn (ngăn bởi dòng trống); mỗi đoạn là danh sách "khối không được cắt":
    khối code giữa hai dòng ```, một danh sách liền nhau (kèm dòng tiêu đề kết thúc bằng ':' ngay trước), hoặc một dòng."""
    paragraphs: list[list[str]] = [[]]
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            if paragraphs[-1]:
                paragraphs.append([])
            i += 1
        elif line.lstrip().startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            end = min(j + 1, len(lines))  # thiếu dấu đóng thì gom tới hết
            paragraphs[-1].append("\n".join(lines[i:end]))
            i = end
        elif _LIST_ITEM.match(line) or (
            line.rstrip().endswith(":") and i + 1 < len(lines) and _LIST_ITEM.match(lines[i + 1])
        ):
            j = i if _LIST_ITEM.match(line) else i + 1
            while j < len(lines) and _LIST_ITEM.match(lines[j]):
                j += 1
            paragraphs[-1].append("\n".join(lines[i:j]))
            i = j
        else:
            paragraphs[-1].append(line.rstrip())
            i += 1
    return [p for p in paragraphs if p]


def _merge(units: list[str], parts: int, joiner: str) -> list[str]:
    """Gộp các đơn vị liền nhau thành đúng `parts` nhóm, cân theo độ dài (không bỏ chữ nào)."""
    target = sum(utf16_len(u) for u in units) / parts
    groups: list[list[str]] = [[]]
    size = 0.0
    for index, unit in enumerate(units):
        remaining_units = len(units) - index
        remaining_groups = parts - len(groups)
        if groups[-1] and remaining_groups > 0 and (size >= target or remaining_units <= remaining_groups):
            groups.append([])
            size = 0.0
        groups[-1].append(unit)
        size += utf16_len(unit)
    return [joiner.join(g) for g in groups]


def split_reply(text: str, mode: str = SPLIT_LINE, max_parts: int = 6, limit: int = ZALO_TEXT_LIMIT) -> list[str]:
    """Chia câu trả lời thành các tin Zalo: mỗi dòng (line) hoặc mỗi đoạn (paragraph) một tin, tối đa
    max_parts tin (nhiều hơn thì gộp các phần liền nhau), mỗi tin vẫn <= limit. off: như split_message."""
    text = text.strip()
    if mode == SPLIT_OFF or max_parts <= 1 or not text:
        return split_message(text, limit)
    paragraphs = _blocks(text)
    if mode == SPLIT_PARAGRAPH:
        units, joiner = ["\n".join(p) for p in paragraphs], "\n\n"
    else:
        units, joiner = [b for p in paragraphs for b in p], "\n"
    if len(units) > max_parts:
        units = _merge(units, max_parts, joiner)
    return [chunk for unit in units for chunk in split_message(unit, limit)]


_BOLD = re.compile(r"\*\*(.+?)\*\*|__(.+?)__", re.S)
_HEADING = re.compile(r"^#{1,6}\s+", re.M)
_BULLET = re.compile(r"^(\s*)[*-]\s+", re.M)


def to_plain_text(text: str) -> str:
    """Bỏ các dấu markdown phổ biến mà Zalo hiển thị nguyên ký tự."""
    text = _BOLD.sub(lambda m: m.group(1) or m.group(2), text)
    text = _HEADING.sub("", text)
    text = _BULLET.sub(lambda m: f"{m.group(1)}• ", text)
    return text.strip()
