"""Kết nối từ ứng dụng ở máy này tới trang quản lý của bot trên VPS (REMOTE_URL + REMOTE_ADMIN_TOKEN).

Trình duyệt chỉ nói chuyện với server giao diện ở máy này (/api/remote/...), server này mới gọi VPS kèm mã truy cập,
nên mã của VPS không bao giờ xuống trang web. Lỗi mạng/HTTP không ném ra mà trả về RemoteError để route đổi thành 502.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator

import httpx

from bot.config import Settings

TIMEOUT = 30.0
# Phần đầu đường dẫn không được chuyển tiếp: chính proxy này, đăng nhập, và việc đặt khoá bí mật (khoá của VPS
# chỉ nên đặt khi đứng trên VPS).
BLOCKED_PREFIXES = ("remote", "auth", "secrets")
FORWARD_HEADERS = ("content-type", "accept")

# Test thay bằng httpx.MockTransport.
transport: httpx.AsyncBaseTransport | None = None


class RemoteError(Exception):
    """Thông báo đã sẵn sàng để hiện cho người dùng."""


@dataclass(frozen=True)
class Reply:
    status: int
    body: bytes
    content_type: str


def configured(settings: Settings) -> bool:
    return bool(settings.remote_url and settings.remote_url != "off" and settings.remote_admin_token)


def blocked(path: str) -> bool:
    first = path.strip("/").split("/", 1)[0].lower()
    return first in BLOCKED_PREFIXES


def _url(settings: Settings, path: str, *, auth: bool = True) -> str:
    if not settings.remote_url or settings.remote_url == "off":
        raise RemoteError("Chưa đặt địa chỉ VPS (REMOTE_URL).")
    if auth and not configured(settings):
        raise RemoteError("Chưa kết nối VPS: vào trang Máy chủ, bấm Kết nối VPS bằng Gmail.")
    if not settings.remote_url.startswith(("https://", "http://127.0.0.1", "http://localhost")):
        raise RemoteError("REMOTE_URL phải bắt đầu bằng https:// (mã truy cập không được gửi qua http).")
    return f"{settings.remote_url}/api/{path.lstrip('/')}"


def _client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout, transport=transport)


def _explain(exc: httpx.HTTPError) -> RemoteError:
    if isinstance(exc, httpx.TimeoutException):
        return RemoteError("VPS không trả lời kịp. Kiểm tra mạng hoặc thử lại.")
    return RemoteError(f"Không kết nối được VPS ({type(exc).__name__}).")


def _check_status(status: int) -> None:
    # 401 của VPS không được trả nguyên cho trang: trang sẽ tưởng phiên của máy này hết hạn và đăng xuất.
    if status == 401:
        raise RemoteError("VPS từ chối mã truy cập (REMOTE_ADMIN_TOKEN sai hoặc đã đổi).")


async def request(settings: Settings, method: str, path: str, *, params: dict[str, str] | None = None,
                  content: bytes | None = None, headers: dict[str, str] | None = None,
                  timeout: float = TIMEOUT, auth: bool = True) -> Reply:
    url = _url(settings, path, auth=auth)
    send = {k: v for k, v in (headers or {}).items() if k.lower() in FORWARD_HEADERS}
    if auth:
        send["Authorization"] = f"Bearer {settings.remote_admin_token}"
    async with _client(timeout) as client:
        try:
            response = await client.request(method, url, params=params, content=content, headers=send)
        except httpx.HTTPError as exc:
            raise _explain(exc) from None
    _check_status(response.status_code)
    return Reply(response.status_code, response.content, response.headers.get("content-type", "application/json"))


async def json_request(settings: Settings, method: str, path: str, *, json: Any = None, timeout: float = TIMEOUT,
                       auth: bool = True) -> Any:
    """Gọi và đọc JSON; lỗi HTTP >= 400 thành RemoteError kèm câu báo lỗi của VPS."""
    import json as jsonlib

    content = jsonlib.dumps(json).encode() if json is not None else None
    reply = await request(settings, method, path, content=content, timeout=timeout, auth=auth,
                          headers={"content-type": "application/json"} if content else None)
    try:
        data = jsonlib.loads(reply.body or b"null")
    except ValueError:
        raise RemoteError(f"VPS trả về dữ liệu không phải JSON (HTTP {reply.status}).") from None
    if reply.status >= 400:
        message = data.get("error") or data.get("detail") if isinstance(data, dict) else None
        raise RemoteError(f"VPS báo lỗi HTTP {reply.status}: {message or data}")
    return data


async def stream(settings: Settings, path: str, params: dict[str, str] | None = None) -> AsyncIterator[bytes]:
    """Luồng byte (log trực tiếp). Ném RemoteError trước khi trả byte đầu tiên nếu không kết nối được."""
    url = _url(settings, path)
    headers = {"Authorization": f"Bearer {settings.remote_admin_token}"}
    client = _client(timeout=None)  # type: ignore[arg-type]  # log trực tiếp chờ vô hạn
    try:
        response = await client.send(client.build_request("GET", url, params=params, headers=headers), stream=True)
    except httpx.HTTPError as exc:
        await client.aclose()
        raise _explain(exc) from None
    try:
        _check_status(response.status_code)
    except RemoteError:
        await response.aclose()
        await client.aclose()
        raise

    async def body() -> AsyncIterator[bytes]:
        try:
            async for chunk in response.aiter_raw():
                yield chunk
        except httpx.HTTPError:
            return
        finally:
            await response.aclose()
            await client.aclose()

    return body()


# Test thay bằng httpx.MockTransport.
sync_transport: httpx.BaseTransport | None = None


def _sync_client(timeout: float | None) -> httpx.Client:
    return httpx.Client(timeout=timeout, transport=sync_transport)


# ---------- bản đồng bộ cho ứng dụng khay (chạy trong luồng nền, không có vòng lặp asyncio) ----------

def call_sync(settings: Settings, method: str, path: str, *, json: Any = None, timeout: float = 15.0) -> Any:
    """Gọi VPS và trả JSON; ném RemoteError (thông báo tiếng Việt) khi lỗi."""
    url = _url(settings, path)
    headers = {"Authorization": f"Bearer {settings.remote_admin_token}"}
    try:
        with _sync_client(timeout) as client:
            response = client.request(method, url, headers=headers, json=json)
    except httpx.HTTPError as exc:
        raise _explain(exc) from None
    _check_status(response.status_code)
    try:
        data = response.json()
    except ValueError:
        raise RemoteError(f"VPS trả về dữ liệu không phải JSON (HTTP {response.status_code}).") from None
    if response.status_code >= 400:
        message = data.get("error") or data.get("detail") if isinstance(data, dict) else None
        raise RemoteError(f"VPS báo lỗi HTTP {response.status_code}: {message or data}")
    return data


def status_sync(settings: Settings) -> dict[str, Any]:
    """{configured, ok, running, standby, error} cho menu khay."""
    out: dict[str, Any] = {"configured": configured(settings), "ok": False, "running": False, "standby": None, "error": None}
    if not out["configured"]:
        return out
    try:
        data = call_sync(settings, "GET", "status", timeout=10)
    except RemoteError as exc:
        out["error"] = str(exc)
        return out
    out.update(ok=True, running=bool(data.get("running")), standby=data.get("standby"))
    return out


def download_sync(settings: Settings, path: str, dest: Any, *, timeout: float = 600.0) -> None:
    """Tải một file (gói chuyển bot) từ VPS về dest."""
    url = _url(settings, path)
    headers = {"Authorization": f"Bearer {settings.remote_admin_token}"}
    try:
        with _sync_client(timeout) as client, client.stream("GET", url, headers=headers) as response:
            _check_status(response.status_code)
            if response.status_code >= 400:
                raise RemoteError(f"VPS báo lỗi HTTP {response.status_code} khi tải dữ liệu.")
            with open(dest, "wb") as out:
                for chunk in response.iter_bytes():
                    out.write(chunk)
    except httpx.HTTPError as exc:
        raise _explain(exc) from None


def upload_sync(settings: Settings, path: str, source: Any, *, timeout: float = 600.0) -> Any:
    """Gửi một file (gói chuyển bot) lên VPS; trả JSON phản hồi."""
    url = _url(settings, path)
    headers = {"Authorization": f"Bearer {settings.remote_admin_token}", "Content-Type": "application/zip"}
    try:
        with _sync_client(timeout) as client, open(source, "rb") as fh:
            response = client.post(url, headers=headers, content=fh)
    except httpx.HTTPError as exc:
        raise _explain(exc) from None
    _check_status(response.status_code)
    try:
        data = response.json()
    except ValueError:
        data = {}
    if response.status_code >= 400:
        message = data.get("error") or data.get("detail") if isinstance(data, dict) else None
        raise RemoteError(f"VPS không nhận được dữ liệu (HTTP {response.status_code}): {message or ''}".strip())
    return data
