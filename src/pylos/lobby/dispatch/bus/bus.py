"""Bus: giao diện + bản chạy trong cùng process (B1). Khi có ≥2 process thì thêm bản SQLite, giao diện giữ nguyên.

Luật: mọi luồng liên khu đi qua bus. Bus chỉ đọc phong bì; lỗi ở một người nhận không làm mất tin của người khác.
"""

from __future__ import annotations

import inspect
import logging
from collections import defaultdict
from typing import Awaitable, Callable, Protocol

from pylos.lobby.dispatch.bus.envelope import Envelope
from pylos.lobby.dispatch.envelope_log.envelope_log import EnvelopeLog

log = logging.getLogger(__name__)
Handler = Callable[[Envelope], "Awaitable[None] | None"]


class Bus(Protocol):
    def subscribe(self, recipient: str, handler: Handler) -> None: ...

    async def publish(self, envelope: Envelope) -> int:
        """Gửi phong bì; trả về số người nhận đã xử lý xong không lỗi."""
        ...


class InProcessBus:
    def __init__(self, envelope_log: EnvelopeLog | None = None) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._log = envelope_log or EnvelopeLog(None)

    def subscribe(self, recipient: str, handler: Handler) -> None:
        self._handlers[recipient].append(handler)

    async def publish(self, envelope: Envelope) -> int:
        handlers = list(self._handlers.get(envelope.recipient, ()))
        if not handlers:
            self._log.record(envelope, "no_recipient")
            log.warning("Bus: không ai nhận %s (%s)", envelope.recipient, envelope.kind)
            return 0
        done = 0
        for handler in handlers:
            try:
                result = handler(envelope)
                if inspect.isawaitable(result):
                    await result
                done += 1
            except Exception:
                log.exception("Bus: người nhận %s lỗi với phong bì %s", envelope.recipient, envelope.id)
        self._log.record(envelope, "delivered" if done == len(handlers) else "failed")
        return done
