"""File .txt dạng JSON Lines: mỗi dòng một bản ghi JSON, UTF-8.

- Ghi đè dùng file tạm + os.replace để mất điện giữa chừng không để lại file cụt.
- Dòng hỏng (ví dụ dòng cuối bị cắt) bị bỏ qua khi đọc, có ghi log.
- Mọi thao tác là đồng bộ và ngắn; bot chạy một tiến trình, một event loop,
  nên không có hai thao tác ghi xen kẽ nhau trên cùng một file.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    # errors="replace": ký tự lỗi (ví dụ surrogate lẻ) thành "?" thay vì làm hỏng cả lượt xử lý.
    with open(tmp, "w", encoding="utf-8", errors="replace", newline="\n") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    # Trên Windows, antivirus/editor đôi khi giữ file trong chốc lát.
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1 * (attempt + 1))


class JsonLinesFile:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read_all(self) -> list[dict[str, Any]]:
        try:
            with open(self.path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except FileNotFoundError:
            return []
        records = []
        for number, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                log.warning("Bỏ qua dòng hỏng %s:%d", self.path, number)
                continue
            if isinstance(record, dict):
                records.append(record)
            else:
                log.warning("Bỏ qua dòng không phải object %s:%d", self.path, number)
        return records

    def append(self, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8", errors="replace", newline="\n") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def rewrite(self, records: list[dict[str, Any]]) -> None:
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
        atomic_write_text(self.path, text)

    def tail(self, n: int) -> list[dict[str, Any]]:
        return self.read_all()[-n:] if n > 0 else []

    def count_lines(self) -> int:
        try:
            with open(self.path, encoding="utf-8") as fh:
                return sum(1 for line in fh if line.strip())
        except FileNotFoundError:
            return 0

    def trim(self, keep: int) -> None:
        records = self.read_all()
        if len(records) > keep:
            self.rewrite(records[-keep:])


class JsonObjectFile:
    """File .txt chứa đúng một object JSON (trạng thái nhỏ, ghi đè nguyên tử)."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> dict[str, Any]:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        try:
            data = json.loads(text) if text.strip() else {}
        except json.JSONDecodeError:
            log.warning("File trạng thái hỏng, bắt đầu lại từ rỗng: %s", self.path)
            return {}
        return data if isinstance(data, dict) else {}

    def write(self, data: dict[str, Any]) -> None:
        atomic_write_text(self.path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
