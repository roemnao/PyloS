"""Client gọi Zalo Bot API: https://bot-api.zaloplatforms.com/bot<TOKEN>/<method>."""

from __future__ import annotations

import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)

BASE_URL = "https://bot-api.zaloplatforms.com"


class ZaloError(Exception):
    """Lỗi từ Zalo (ok=false) hoặc lỗi mạng. Thông điệp không bao giờ chứa token."""

    def __init__(self, description: str, error_code: int | None = None, network: bool = False) -> None:
        super().__init__(f"[{error_code}] {description}" if error_code is not None else description)
        self.description = description
        self.error_code = error_code
        self.network = network


class ZaloClient:
    def __init__(self, token: str, http: httpx.AsyncClient | None = None, base_url: str = BASE_URL) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._http = http or httpx.AsyncClient(timeout=httpx.Timeout(20.0))
        self._owns_http = http is None

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    def _redact(self, text: str) -> str:
        return text.replace(self._token, "***") if self._token else text

    async def call(self, method: str, params: dict[str, Any] | None = None, timeout: float | None = None) -> Any:
        url = f"{self._base_url}/bot{self._token}/{method}"
        try:
            response = await self._http.post(
                url, json=params or {}, timeout=timeout if timeout is not None else httpx.USE_CLIENT_DEFAULT
            )
        except httpx.HTTPError as exc:
            # str(exc) có thể chứa URL (có token) nên luôn che lại.
            raise ZaloError(self._redact(f"{type(exc).__name__}: {exc}"), network=True) from None
        try:
            data = response.json()
        except ValueError:
            raise ZaloError(f"Phản hồi không phải JSON (HTTP {response.status_code})", response.status_code) from None
        if not isinstance(data, dict) or not data.get("ok"):
            description = str(data.get("description") if isinstance(data, dict) else data)
            code = data.get("error_code") if isinstance(data, dict) else None
            raise ZaloError(self._redact(description or "unknown error"), code if code is not None else response.status_code)
        return data.get("result")

    async def get_me(self) -> dict[str, Any]:
        return await self.call("getMe")

    async def get_updates(self, timeout: int = 30) -> Any:
        # `timeout` của Zalo là thời gian giữ kết nối (giây); chờ HTTP dài hơn một chút.
        return await self.call("getUpdates", {"timeout": str(timeout)}, timeout=timeout + 15)

    async def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        return await self.call("sendMessage", {"chat_id": chat_id, "text": text})

    async def send_chat_action(self, chat_id: str, action: str = "typing") -> None:
        await self.call("sendChatAction", {"chat_id": chat_id, "action": action})

    async def set_webhook(self, url: str, secret_token: str) -> dict[str, Any]:
        return await self.call("setWebhook", {"url": url, "secret_token": secret_token})

    async def delete_webhook(self) -> Any:
        return await self.call("deleteWebhook")

    async def get_webhook_info(self) -> Any:
        return await self.call("getWebhookInfo")
