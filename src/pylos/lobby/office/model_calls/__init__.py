"""Cửa chung gọi model: danh sách key -> model (model_keys.md) và các nhà cung cấp (providers/).

Code khác trong bot không giữ key hay client riêng mà hỏi ModelCalls: model này dùng key nào, của nhà cung cấp nào."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from pylos.lobby.office.model_calls.catalog import KEYS_FILE, KeyEntry, Lookup, ModelCatalog, env_lookup
from pylos.lobby.office.model_calls.providers import PROVIDERS
from pylos.lobby.office.model_calls.results import ImageResult, ModelCallError

log = logging.getLogger(__name__)

__all__ = ["ModelCalls", "KeyEntry", "ImageResult", "ModelCallError", "settings_lookup"]


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

    async def generate_image(self, prompt: str, model: str, *, fallbacks: tuple[str, ...] = (), steps: int = 4,
                             timeout: float = 60) -> ImageResult:
        """Tạo ảnh bằng `model`; lỗi của riêng model (hết hạn mức, 5xx, hết giờ) thì thử lần lượt `fallbacks`.

        Lỗi cuối cùng ném lên dạng ModelCallError (câu tiếng Việt, không chứa key)."""
        names: list[str] = []
        for name in (model, *fallbacks):
            if name and name not in names:
                names.append(name)
        for index, name in enumerate(names):
            entry = self.resolve(name)
            provider = self._providers.get(entry.provider) if entry else None
            started = time.monotonic()
            try:
                if entry is None:
                    raise ModelCallError(f"Model {name} chưa có key dùng được trong model_keys.md")
                if not hasattr(provider, "generate_image"):
                    raise ModelCallError(f"Model {name} (nhà cung cấp {entry.provider}) chưa tạo ảnh được")
                result = await provider.generate_image(entry, name, prompt, steps=steps, timeout=timeout)
            except ModelCallError as exc:
                if exc.retryable and index < len(names) - 1:
                    log.warning("Tạo ảnh bằng %s lỗi (%s), thử model dự phòng %s", name, exc, names[index + 1])
                    continue
                raise
            log.info("Đã tạo ảnh bằng %s: %d byte trong %.1f giây (lời nhắc: %.80s)", name, len(result.data),
                     time.monotonic() - started, prompt)
            return result
        raise ModelCallError("Chưa có model tạo ảnh")

    def gemini_client(self, model: str) -> Any | None:
        """Client Gemini của key dành cho `model`; None nếu model không có trong danh sách hoặc không thuộc Gemini."""
        entry = self.resolve(model)
        if entry is None or entry.provider != "gemini":
            return None
        return self._providers["gemini"].client_for(entry)
