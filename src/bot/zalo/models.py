"""Phân tích sự kiện Zalo Bot Platform.

Cấu trúc theo docs (bot.zapps.me/docs/webhook):
    {"ok": true, "result": {"event_name": "...", "message": {
        "from": {"id", "display_name", "is_bot"}, "chat": {"id", "chat_type"},
        "text", "message_id", "date"}}}

Docs không nói `getUpdates` trả một object hay một mảng, nên hàm ở đây
chấp nhận cả hai, cả khi có hoặc không có lớp bọc {"ok", "result"}.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

TEXT_EVENT = "message.text.received"


@dataclass(frozen=True)
class IncomingMessage:
    event_name: str
    chat_id: str
    chat_type: str
    from_id: str
    from_name: str
    from_is_bot: bool
    text: str | None
    message_id: str | None
    date_ms: int | None
    raw: dict[str, Any] = field(repr=False, compare=False, default_factory=dict)

    @property
    def is_group(self) -> bool:
        return self.chat_type.upper() == "GROUP"

    @property
    def is_text(self) -> bool:
        return self.event_name == TEXT_EVENT and bool(self.text and self.text.strip())

    @property
    def dedupe_key(self) -> str:
        if self.message_id:
            return f"{self.chat_id}:{self.message_id}"
        # Docs không liệt kê message_id trong bảng trường; dự phòng bằng hash nội dung.
        digest = hashlib.sha1(
            f"{self.chat_id}|{self.from_id}|{self.date_ms}|{self.text}".encode("utf-8")
        ).hexdigest()[:16]
        return f"{self.chat_id}:h{digest}"


def _to_ms(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    # Docs dùng mili giây; nếu trông như giây (trước năm ~5138 tính theo ms) thì đổi sang ms.
    return number * 1000 if number < 100_000_000_000 else number


def parse_event(event: dict[str, Any]) -> IncomingMessage | None:
    message = event.get("message")
    if not isinstance(message, dict):
        return None
    sender = message.get("from") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    from_id = sender.get("id")
    if chat_id is None or from_id is None:
        return None
    text = message.get("text")
    message_id = message.get("message_id")
    return IncomingMessage(
        event_name=str(event.get("event_name") or ""),
        chat_id=str(chat_id),
        chat_type=str(chat.get("chat_type") or "PRIVATE"),
        from_id=str(from_id),
        from_name=str(sender.get("display_name") or from_id),
        from_is_bot=bool(sender.get("is_bot", False)),
        text=text if isinstance(text, str) else None,
        message_id=str(message_id) if message_id not in (None, "") else None,
        date_ms=_to_ms(message.get("date")),
        raw=event,
    )


def parse_updates(payload: Any) -> list[IncomingMessage]:
    """Nhận payload webhook hoặc kết quả getUpdates, trả về danh sách tin hợp lệ."""
    if isinstance(payload, dict) and "result" in payload and "event_name" not in payload:
        payload = payload["result"]
    events = payload if isinstance(payload, list) else [payload]
    messages = []
    for event in events:
        if isinstance(event, dict):
            parsed = parse_event(event)
            if parsed is not None:
                messages.append(parsed)
    return messages
