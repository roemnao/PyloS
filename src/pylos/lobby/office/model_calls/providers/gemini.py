"""Nhà cung cấp Gemini: một client google-genai cho mỗi key."""

from __future__ import annotations

from typing import Any, Callable

from pylos.lobby.office.model_calls.catalog import KeyEntry


def _genai_client(secret: str) -> Any:
    from google import genai

    return genai.Client(api_key=secret)


class GeminiProvider:
    name = "gemini"

    def __init__(self, factory: Callable[[str], Any] = _genai_client) -> None:
        self._factory = factory
        self._clients: dict[tuple[str, str], Any] = {}

    def client_for(self, entry: KeyEntry) -> Any:
        """Client của key này, giữ lại để dùng tiếp; giá trị key đổi (sửa ở trang Cài đặt) thì tạo client mới."""
        cache_key = (entry.name, entry.secret)
        client = self._clients.get(cache_key)
        if client is None:
            for old in [k for k in self._clients if k[0] == entry.name]:
                del self._clients[old]
            client = self._clients[cache_key] = self._factory(entry.secret)
        return client
