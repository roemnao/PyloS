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


_BOLD = re.compile(r"\*\*(.+?)\*\*|__(.+?)__", re.S)
_HEADING = re.compile(r"^#{1,6}\s+", re.M)
_BULLET = re.compile(r"^(\s*)[*-]\s+", re.M)


def to_plain_text(text: str) -> str:
    """Bỏ các dấu markdown phổ biến mà Zalo hiển thị nguyên ký tự."""
    text = _BOLD.sub(lambda m: m.group(1) or m.group(2), text)
    text = _HEADING.sub("", text)
    text = _BULLET.sub(lambda m: f"{m.group(1)}• ", text)
    return text.strip()
