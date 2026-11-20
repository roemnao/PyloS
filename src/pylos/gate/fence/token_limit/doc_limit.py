"""Hạn mức tạo / sửa tài liệu: cùng cách đếm với ImageLimit (ngày lưu file, giờ theo người trong bộ nhớ), chỉ khác câu từ chối.
Đọc tài liệu không tính. 0 = không giới hạn."""

from __future__ import annotations

from pylos.gate.fence.token_limit.image_limit import HOUR, ImageLimit  # noqa: F401


class DocLimit(ImageLimit):
    def check(self, user_id: str) -> str | None:
        if self.per_day > 0 and self.counter.today() >= self.per_day:
            return f"Hôm nay bot đã tạo / sửa đủ {self.per_day} tài liệu, mai thử lại nhé."
        if self.per_user_hour > 0 and len(self._recent(user_id)) >= self.per_user_hour:
            return f"Bạn đã nhờ tạo / sửa {self.per_user_hour} tài liệu trong 1 giờ qua, lát nữa thử lại nhé."
        return None
