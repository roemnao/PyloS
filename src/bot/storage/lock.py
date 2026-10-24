"""Khóa một phiên bản: không cho hai bot cùng chạy trên một thư mục data/."""

from __future__ import annotations

import os
from pathlib import Path
from typing import IO


class AlreadyRunning(Exception):
    pass


class InstanceLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh: IO[str] | None = None

    def acquire(self, wait: float = 0.0) -> None:
        """Lấy khóa; `wait` > 0 thì thử lại trong khoảng đó (ví dụ khi giao diện vừa kiểm tra khóa trong chốc lát)."""
        import time

        deadline = time.monotonic() + wait
        while True:
            try:
                self._acquire_once()
                return
            except AlreadyRunning:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.1)

    def _acquire_once(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.path, "a+", encoding="utf-8")
        try:
            if os.name == "nt":
                import msvcrt

                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            raise AlreadyRunning(f"Đã có một bot khác đang chạy (khóa {self.path}).") from None
        self._fh = fh

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        self._fh.close()
        self._fh = None

    def __enter__(self) -> InstanceLock:
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()
