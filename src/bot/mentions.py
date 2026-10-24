"""Tag (@mention) người trong nhóm Zalo.

- add_tags: model hay viết "Phúc Xo ơi…" mà quên "@". Khi người nhờ có ý tag/nhắc/gọi ai đó
  (có tên người đó trong yêu cầu), thêm "@" trước tên đó trong câu trả lời.
- build_mentions: tìm "@Tên" khớp một thành viên, đổi thành mention Zalo [{"pos","len","uid","type"}].

So khớp tên không phân biệt hoa thường và dấu ("@phuc xo" khớp "Phúc Xo"), theo ranh giới từ,
tên dài khớp trước ("Thái Toàn" trước "Thái").
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

# Từ cho thấy người nhờ muốn bot gọi/nhắc người khác (đã bỏ dấu): tag, nhắc, gọi, kêu, ping, @
_TAG_INTENT = re.compile(r"@|(?<!\w)(tag|nhac|goi|keu|ping)(?!\w)")


def _fold_char(c: str) -> str:
    if c in "đĐ":
        return "d"
    base = unicodedata.normalize("NFD", c)[:1] or c
    return base.lower()[:1] or c


def fold_same_length(text: str) -> str:
    """Bỏ dấu + chữ thường, GIỮ NGUYÊN độ dài (mỗi ký tự thành đúng một ký tự) để dùng lại vị trí."""
    return "".join(_fold_char(c) for c in text)


def utf16_len(text: str) -> int:
    # Zalo (JavaScript) tính vị trí theo đơn vị UTF-16: emoji ngoài BMP chiếm 2.
    return len(text.encode("utf-16-le")) // 2


def _names(members: dict[str, str]) -> list[tuple[str, str]]:
    """[(tên đã bỏ dấu, uid)], tên dài trước; bỏ tên quá ngắn dễ khớp nhầm."""
    items = {(fold_same_length(name.strip()), uid) for uid, name in members.items() if name and len(name.strip()) >= 2}
    return sorted(items, key=lambda item: len(item[0]), reverse=True)


def _is_boundary(folded: str, index: int) -> bool:
    return index <= 0 or index >= len(folded) or not folded[index].isalnum()


def _find(folded: str, name: str, start: int = 0) -> int:
    i = folded.find(name, start)
    while i != -1:
        if _is_boundary(folded, i - 1) and _is_boundary(folded, i + len(name)):
            return i
        i = folded.find(name, i + 1)
    return -1


def build_mentions(text: str, members: dict[str, str]) -> list[dict[str, Any]]:
    names = _names(members)
    folded = fold_same_length(text)
    mentions = []
    i = text.find("@")
    while i != -1:
        for name, uid in names:
            end = i + 1 + len(name)
            if folded.startswith(name, i + 1) and _is_boundary(folded, end):
                mentions.append({"pos": utf16_len(text[:i]), "len": utf16_len(text[i:end]), "uid": uid, "type": 0})
                i = end - 1
                break
        i = text.find("@", i + 1)
    return mentions


def add_tags(reply: str, request: str, members: dict[str, str]) -> str:
    """Thêm "@" trước tên thành viên mà người nhờ yêu cầu tag/nhắc/gọi, nếu câu trả lời có tên đó mà thiếu "@"."""
    folded_request = fold_same_length(request)
    if not _TAG_INTENT.search(folded_request):
        return reply
    folded_reply = fold_same_length(reply)
    inserts: list[int] = []
    taken: list[tuple[int, int]] = []
    for name, _uid in _names(members):
        if _find(folded_request, name) == -1:
            continue  # người nhờ không nhắc tới người này
        i = _find(folded_reply, name)
        while i != -1 and any(a <= i < b for a, b in taken):
            i = _find(folded_reply, name, i + 1)  # nằm trong tên dài hơn đã xử lý
        if i == -1:
            continue
        taken.append((i, i + len(name)))
        if i == 0 or reply[i - 1] != "@":
            inserts.append(i)
    for i in sorted(inserts, reverse=True):
        reply = reply[:i] + "@" + reply[i:]
    return reply
