"""Phong bì: thứ duy nhất Đại sảnh được đọc. Nội dung (payload) đi kèm nhưng không bao giờ được ghi log."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from pylos.lobby.dispatch.clock.vietnam_time import now_ms


@dataclass(frozen=True)
class Envelope:
    sender: str  # vd "gate.main_gate.zalo", "residential.residents.<bot>"
    recipient: str  # tên đăng ký trên bus
    kind: str  # loại tin: "chat.incoming", "chat.reply", "command"...
    payload: Any = None  # nội dung: chỉ người nhận được đọc
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_ms: int = field(default_factory=now_ms)

    def meta(self) -> dict:
        """Phần được phép ghi log: mọi thứ trừ nội dung."""
        return {"id": self.id, "sender": self.sender, "recipient": self.recipient, "kind": self.kind,
                "created_ms": self.created_ms}
