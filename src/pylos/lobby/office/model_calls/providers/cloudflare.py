"""Nhà cung cấp Cloudflare Workers AI: tạo ảnh qua REST (POST /accounts/<id>/ai/run/<model>).

Theo tài liệu model flux-1-schnell của Cloudflare: body {"prompt", "steps" (1-8, mặc định 4)}, phản hồi JSON
{"result": {"image": "<base64>"}, "success": true}. Cloudflare không nói rõ PNG hay JPEG nên loại ảnh nhận từ đầu file."""

from __future__ import annotations

import base64
import binascii
from typing import Any, Callable

import httpx

from pylos.lobby.office.model_calls.catalog import KeyEntry
from pylos.lobby.office.model_calls.results import ImageResult, ModelCallError, sniff_image_mime

API_BASE = "https://api.cloudflare.com/client/v4"


def _describe(response: httpx.Response) -> str:
    """Lý do Cloudflare nêu trong phản hồi lỗi (không chứa key)."""
    try:
        errors = response.json().get("errors") or []
    except ValueError:
        return ""
    return "; ".join(str(e.get("message") or e) for e in errors if e)[:200]


class CloudflareProvider:
    name = "cloudflare"

    def __init__(self, client_factory: Callable[..., Any] = httpx.AsyncClient) -> None:
        self._client_factory = client_factory

    async def generate_image(self, entry: KeyEntry, model: str, prompt: str, *, steps: int = 4,
                             timeout: float = 60) -> ImageResult:
        account = entry.extras.get("account", "")
        url = f"{API_BASE}/accounts/{account}/ai/run/{model}"
        try:
            async with self._client_factory(timeout=timeout) as client:
                response = await client.post(url, headers={"Authorization": f"Bearer {entry.secret}"},
                                             json={"prompt": prompt, "steps": max(1, min(8, steps))})
        except httpx.TimeoutException:
            raise ModelCallError(f"Cloudflare ({model}) không trả lời sau {timeout:.0f} giây", retryable=True) from None
        except httpx.HTTPError as exc:  # str(exc) chỉ có tên lỗi mạng, không có header chứa token
            raise ModelCallError(f"Không kết nối được Cloudflare: {type(exc).__name__}", retryable=True) from None
        status = response.status_code
        if status in (401, 403):
            raise ModelCallError("Cloudflare từ chối token: kiểm tra CLOUDFLARE_API_TOKEN có quyền Workers AI "
                                 "và đúng CLOUDFLARE_ACCOUNT_ID")
        if status == 429:
            raise ModelCallError("Cloudflare báo hết hạn mức (429): có thể đã dùng hết Neurons miễn phí hôm nay",
                                 retryable=True)
        if status >= 500:
            raise ModelCallError(f"Cloudflare lỗi phía máy chủ ({status})", retryable=True)
        if status >= 400:
            detail = _describe(response)
            raise ModelCallError(f"Cloudflare từ chối yêu cầu ({status}){': ' + detail if detail else ''}")
        if response.headers.get("content-type", "").startswith("image/"):
            data = response.content
        else:
            try:
                body = response.json()
                if body.get("success") is False:
                    raise ModelCallError(f"Cloudflare báo lỗi: {_describe(response) or 'không rõ lý do'}")
                data = base64.b64decode(body["result"]["image"], validate=False)
            except (ValueError, KeyError, TypeError, binascii.Error):
                raise ModelCallError("Phản hồi của Cloudflare không có ảnh", retryable=True) from None
        return ImageResult(data, sniff_image_mime(data), model)
