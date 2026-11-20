"""Hạn mức tạo ảnh: số ảnh mỗi ngày (giờ Việt Nam, lưu file) và số ảnh mỗi người mỗi giờ (trong bộ nhớ).

Riêng với hạn mức token (DAILY_TOKEN_BUDGET): Cloudflare không trả số token, nên đếm theo số ảnh.
`check` chỉ xem, `record` ghi sau khi tạo THÀNH CÔNG, nên lần lỗi không bị trừ lượt. 0 = không giới hạn."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable

from pylos.lobby.dispatch.shared.data_stores import DailyCounter

HOUR = 3600


class ImageLimit:
    def __init__(self, counter: DailyCounter, per_day: int, per_user_hour: int,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.counter = counter
        self.per_day = per_day
        self.per_user_hour = per_user_hour
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _recent(self, user_id: str) -> deque[float]:
        hits = self._hits[user_id]
        now = self._clock()
        while hits and now - hits[0] >= HOUR:
            hits.popleft()
        return hits

    def check(self, user_id: str) -> str | None:
        """None = được tạo; ngược lại là câu từ chối để báo lại cho người dùng."""
        if self.per_day > 0 and self.counter.today() >= self.per_day:
            return f"Hôm nay bot đã tạo đủ {self.per_day} ảnh, mai thử lại nhé."
        if self.per_user_hour > 0 and len(self._recent(user_id)) >= self.per_user_hour:
            return f"Bạn đã nhờ tạo {self.per_user_hour} ảnh trong 1 giờ qua, lát nữa thử lại nhé."
        return None

    def record(self, user_id: str) -> None:
        self.counter.incr()
        self._recent(user_id).append(self._clock())
