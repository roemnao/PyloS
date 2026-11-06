"""Chuẩn hoá chữ để so tên: không phân biệt hoa thường và dấu tiếng Việt."""

from __future__ import annotations

import unicodedata


def fold(text: str) -> str:
    """Chữ thường, bỏ dấu tiếng Việt: "Trợ Lý" -> "tro ly"."""
    text = text.lower().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
