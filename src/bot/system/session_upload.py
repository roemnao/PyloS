"""Gửi session bộ lọc ↔ agent lên web (iforgotmywayhome → Hệ thống → Session) để chủ hệ thống xem lại.

Không làm chậm việc trả lời: mỗi bước (tin, quyết định của bộ lọc, lượt agent, tool, câu trả lời) chỉ được
thêm vào hàng đợi trong bộ nhớ; một tác vụ nền gửi theo lô mỗi 10 giây. Mất mạng thì giữ lại (tối đa 1000 bước)
và gửi sau. Tắt bằng SESSION_UPLOAD=false trong settings.env hoặc trên web.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any, Callable

from bot.system import server_client

log = logging.getLogger(__name__)


class SessionUploader:
    def __init__(self, enabled: Callable[[], bool], *, interval: float = 10.0, batch: int = 100,
                 buffer: int = 1000) -> None:
        self.enabled = enabled
        self.interval = interval
        self.batch = batch
        self._queue: deque[dict[str, Any]] = deque(maxlen=buffer)  # đầy thì bỏ bước cũ nhất
        self._warned = False

    def __len__(self) -> int:
        return len(self._queue)

    def record(self, chat_id: str, kind: str, **fields: Any) -> None:
        """Thêm một bước. Không bao giờ ném lỗi ra ngoài."""
        try:
            if not self.enabled():
                return
            event = {"at": datetime.now(timezone.utc).isoformat(), "chatId": str(chat_id), "kind": kind}
            event.update({k: v for k, v in fields.items() if v is not None})
            self._queue.append(event)
        except Exception:  # noqa: BLE001 - ghi session lỗi không được ảnh hưởng tới bot
            log.debug("Không ghi được bước session", exc_info=True)

    async def flush(self) -> bool:
        """Gửi một lô. Trả về False nếu gửi lỗi (các bước được giữ lại để gửi lần sau)."""
        if not self._queue:
            return True
        if not self.enabled():
            self._queue.clear()
            return True
        events = [self._queue.popleft() for _ in range(min(self.batch, len(self._queue)))]
        result = await server_client.request("POST", "/sessions", json={"events": events}, timeout=20)
        if isinstance(result, dict) and "error" in result:
            if not self._warned:
                log.warning("Chưa gửi được session lên web (%s), sẽ thử lại", result["error"])
                self._warned = True
            # Trả lại đầu hàng đợi, giữ đúng thứ tự (hàng đầy thì các bước cũ nhất bị bỏ).
            for event in reversed(events):
                if len(self._queue) < (self._queue.maxlen or 0):
                    self._queue.appendleft(event)
            return False
        self._warned = False
        return True

    async def run(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
            try:
                while self._queue and await self.flush():
                    if len(self._queue) < self.batch:
                        break
            except Exception:  # noqa: BLE001 - lỗi gửi không được làm sập bot
                log.exception("Gửi session lỗi")
