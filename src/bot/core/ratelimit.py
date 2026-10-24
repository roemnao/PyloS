"""Giới hạn số tin mỗi phút theo cửa sổ trượt, trong bộ nhớ."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable


class RateLimiter:
    def __init__(self, per_minute: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.per_minute = per_minute
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        """0 = không giới hạn."""
        if self.per_minute <= 0:
            return True
        now = self._clock()
        hits = self._hits[key]
        while hits and now - hits[0] >= 60:
            hits.popleft()
        if len(hits) >= self.per_minute:
            return False
        hits.append(now)
        return True
