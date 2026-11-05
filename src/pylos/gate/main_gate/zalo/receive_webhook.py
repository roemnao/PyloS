"""Nhận tin bằng webhook (cần URL HTTPS công khai, ví dụ qua Cloudflare Tunnel).

Zalo gửi header X-Bot-Api-Secret-Token = secret_token đã đặt qua setWebhook.
Trả lời ngay sau khi xếp hàng, không chờ Gemini.
"""

from __future__ import annotations

import hmac
import logging
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from bot.storage import StateStore

log = logging.getLogger(__name__)

SECRET_HEADER = "X-Bot-Api-Secret-Token"
WEBHOOK_PATH = "/webhook/zalo"


def create_app(secret: str, handle: Callable[[Any], Awaitable[None]], state: StateStore | None = None) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.post(WEBHOOK_PATH)
    async def webhook(request: Request) -> JSONResponse:
        received = request.headers.get(SECRET_HEADER, "")
        if not secret or not hmac.compare_digest(received.encode(), secret.encode()):
            log.warning("Webhook sai secret từ %s", request.client.host if request.client else "?")
            return JSONResponse({"message": "Unauthorized"}, status_code=403)
        try:
            payload = await request.json()
        except ValueError:
            return JSONResponse({"message": "Bad Request"}, status_code=400)
        await handle(payload)
        return JSONResponse({"message": "Success"})

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"ok": True, "state": state.data if state else {}}

    return app
