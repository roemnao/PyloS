"""Log phong bì: mỗi dòng JSON một phong bì, chỉ có siêu dữ liệu — không có nội dung tin."""

from __future__ import annotations

import json
from pathlib import Path

from pylos.lobby.dispatch.bus.envelope import Envelope


class EnvelopeLog:
    def __init__(self, path: Path | None) -> None:
        self.path = path  # None = không ghi (test, hoặc chưa cấu hình)

    def record(self, envelope: Envelope, outcome: str = "delivered") -> None:
        if self.path is None:
            return
        line = json.dumps({**envelope.meta(), "outcome": outcome}, ensure_ascii=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
