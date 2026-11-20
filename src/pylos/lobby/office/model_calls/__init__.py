"""Cửa chung gọi model: danh sách key -> model (model_keys.md) và các nhà cung cấp (providers/).

Code khác trong bot không giữ key hay client riêng mà hỏi ModelCalls: model này dùng key nào, của nhà cung cấp nào."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pylos.lobby.office.model_calls.catalog import KEYS_FILE, KeyEntry, Lookup, ModelCatalog, env_lookup
from pylos.lobby.office.model_calls.providers import PROVIDERS

log = logging.getLogger(__name__)

__all__ = ["ModelCalls", "KeyEntry", "settings_lookup"]


def settings_lookup(settings: Any) -> Lookup:
    """Giá trị biến: ưu tiên cài đặt đang chạy (đổi ở trang quản lý có hiệu lực ngay), còn lại lấy từ môi trường."""
    known = {
        "GEMINI_API_KEY": settings.gemini_api_key,
        "CLOUDFLARE_API_TOKEN": settings.cloudflare_api_token,
        "CLOUDFLARE_ACCOUNT_ID": settings.cloudflare_account_id,
    }

    def lookup(name: str) -> str:
        return known[name].strip() if name in known else env_lookup(name)

    return lookup


class ModelCalls:
    def __init__(self, lookup: Lookup = env_lookup, path: Path = KEYS_FILE) -> None:
        self.catalog = ModelCatalog(path, lookup, known_providers=set(PROVIDERS))
        self._providers = {name: factory() for name, factory in PROVIDERS.items()}

    def update(self, settings: Any) -> None:
        """Cài đặt đổi khi bot đang chạy: dùng giá trị key mới."""
        self.catalog.lookup = settings_lookup(settings)

    def resolve(self, model: str) -> KeyEntry | None:
        return self.catalog.resolve(model)

    def provider_of(self, model: str) -> str | None:
        """Nhà cung cấp của model, hoặc None nếu model không có trong danh sách (bên gọi dùng key mặc định)."""
        entry = self.resolve(model)
        return entry.provider if entry else None

    def gemini_client(self, model: str) -> Any | None:
        """Client Gemini của key dành cho `model`; None nếu model không có trong danh sách hoặc không thuộc Gemini."""
        entry = self.resolve(model)
        if entry is None or entry.provider != "gemini":
            return None
        return self._providers["gemini"].client_for(entry)
