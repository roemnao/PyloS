"""Thời gian. Việt Nam là UTC+7 cố định (không có giờ mùa hè), nên không cần tzdata."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7), name="Asia/Ho_Chi_Minh")


def now_ms() -> int:
    return int(time.time() * 1000)


def now_vn() -> datetime:
    return datetime.now(VN_TZ)


def today_vn() -> str:
    return now_vn().date().isoformat()
