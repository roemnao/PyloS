"""Kết nối tới web iforgotmywayhome (repo quanlythoigian) qua API dành cho agent: /api/agent/*.

Dùng cho tool lịch, bot lịch (giao lịch cho người khác), liên kết Zalo, cấu hình từ xa, nhịp tim và session.
Cấu hình trong userdata/config/settings.env:
  SCHEDULE_API_URL  địa chỉ web (hoặc .../api/agent); để trống = web mặc định
  SCHEDULE_API_KEY  khoá agent tạo ở web: Cài đặt → Kết nối AI agent
Khoá chỉ nằm trên máy này, web không bao giờ gửi khoá bí mật xuống bot.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import dotenv_values

DEFAULT_URL = "https://quanlythoigian-azure.vercel.app/api/agent"
TIMEOUT = 30.0


def env_values() -> dict[str, str]:
    """settings.env + biến môi trường (giao diện quản lý không nạp settings.env vào os.environ như bot)."""
    from bot.config import APP_HOME
    from bot.userdata_paths import ENV_REL

    values = {k: v for k, v in dotenv_values(APP_HOME / ENV_REL).items() if v is not None}
    return {**values, **os.environ}


def base_url(raw: str) -> str:
    """Nhận cả địa chỉ web lẫn địa chỉ API: https://x.vercel.app, .../api/agent, .../api/agent/."""
    url = (raw or "").strip().rstrip("/") or DEFAULT_URL
    if not url.endswith("/api/agent"):
        url += "/api/agent"
    return url


def server_config() -> tuple[str, str]:
    env = env_values()
    return base_url(env.get("SCHEDULE_API_URL", "")), env.get("SCHEDULE_API_KEY", "").strip()


def configured() -> bool:
    return bool(server_config()[1])


async def request(method: str, path: str, *, json: Any = None, params: dict[str, str] | None = None,
                  timeout: float = TIMEOUT) -> Any:
    """Gọi API của web. Lỗi không ném ra mà trả {"error", "status", "message"} để tool đưa lại cho model."""
    url, key = server_config()
    if not key:
        return {"error": "Chưa cấu hình SCHEDULE_API_KEY (khoá agent của web iforgotmywayhome).", "status": 0, "message": ""}
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(method, url + path, json=json, params=params,
                                            headers={"Authorization": f"Bearer {key}"})
        except httpx.HTTPError as exc:
            return {"error": f"Không gọi được web: {type(exc).__name__}", "status": 0, "message": ""}
    try:
        data = response.json()
    except ValueError:
        data = {"error": f"Phản hồi không phải JSON (HTTP {response.status_code})"}
    if response.status_code >= 400:
        message = data.get("error") if isinstance(data, dict) else None
        return {"error": f"Web báo lỗi HTTP {response.status_code}: {message or data}", "status": response.status_code,
                "message": str(message or "")}
    return data
