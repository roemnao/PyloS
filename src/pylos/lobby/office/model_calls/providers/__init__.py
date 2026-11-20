"""Các nhà cung cấp model. Thêm nhà cung cấp mới: một file trong thư mục này và một dòng trong PROVIDERS."""

from __future__ import annotations

from pylos.lobby.office.model_calls.providers.cloudflare import CloudflareProvider
from pylos.lobby.office.model_calls.providers.gemini import GeminiProvider

PROVIDERS = {
    GeminiProvider.name: GeminiProvider,
    CloudflareProvider.name: CloudflareProvider,
}
