"""Cấu hình log: ra console và file xoay vòng, luôn che bí mật."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class RedactFilter(logging.Filter):
    """Thay mọi bí mật (bot token nằm trong URL API, API key...) bằng ***."""

    def __init__(self, secrets: list[str]) -> None:
        super().__init__()
        self.secrets = [s for s in secrets if s]

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.secrets:
            return True
        message = record.getMessage()
        redacted = message
        for secret in self.secrets:
            redacted = redacted.replace(secret, "***")
        if redacted != message:
            record.msg, record.args = redacted, None
        if record.exc_info and not record.exc_text:
            record.exc_text = logging.Formatter().formatException(record.exc_info)
        if record.exc_text:
            for secret in self.secrets:
                record.exc_text = record.exc_text.replace(secret, "***")
        return True


def setup_logging(level: str, log_dir: Path | None, secrets: list[str], filename: str = "bot.log") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    redact = RedactFilter(secrets)

    handlers: list[logging.Handler] = []
    # Exe dạng cửa sổ (không console) có sys.stderr = None: chỉ ghi ra file.
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler(sys.stderr))
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(log_dir / filename, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
        )
    for handler in handlers:
        handler.setFormatter(fmt)
        handler.addFilter(redact)
        root.addHandler(handler)

    # httpx ghi URL đầy đủ (có bot token) ở mức INFO.
    for noisy in ("httpx", "httpcore", "google_genai", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
