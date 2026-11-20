"""Gửi tệp (.docx, .md, .txt...) vào chat Zalo bằng acc cá nhân. zlapi 1.0.3 không có gửi tệp cục bộ nên làm theo
giao thức Zalo Web (đối chiếu zca-js, src/apis/uploadAttachment.ts và sendMessage.ts):

1. POST tệp lên .../asyncfile/upload (multipart, một chunk) -> Zalo trả fileId và clientFileId;
2. Zalo xử lý rồi báo qua websocket lệnh 601, act_type "file_done", kèm đường dẫn tệp;
3. POST .../asyncfile/msg với đường dẫn đó thì tệp xuất hiện trong chat.

zlapi bỏ qua sự kiện file_done nên bọc _util.zws_decode (hàm giải mã mọi gói websocket) để đọc nó (xem FileDoneWatcher).
Không đụng tới zlapi trên đĩa. Chưa kiểm chứng với Zalo thật: mọi lỗi giao thức đều dẫn tới ZaloUnsupported / ZaloError."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from pathlib import Path
from typing import Any

from pylos.gate.main_gate.zalo.bot_platform_api import ZaloError, ZaloUnsupported

log = logging.getLogger(__name__)

FILE_HOST = "https://tt-files-wpa.chat.zalo.me"
MAX_FILE_BYTES = 2 * 1024 * 1024  # một chunk; tệp lớn hơn do bên gọi báo ZaloUnsupported để gửi dạng chữ
FILE_DONE_TIMEOUT = 45.0  # chờ Zalo báo file_done
KEEP_URLS = 64


class FileDoneWatcher:
    """Nhớ đường dẫn của các tệp Zalo đã xử lý xong ({fileId: url}); wait() chờ tới khi có."""

    def __init__(self) -> None:
        self._cond = threading.Condition()
        self._urls: dict[str, str] = {}

    def feed(self, decoded: Any) -> None:
        """Gói websocket đã giải mã; lấy các control file_done (gọi từ luồng nghe của zlapi, không được ném lỗi)."""
        data = decoded.get("data") if isinstance(decoded, dict) else None
        controls = data.get("controls") if isinstance(data, dict) else None
        if not isinstance(controls, list):
            return
        for control in controls:
            content = control.get("content") if isinstance(control, dict) else None
            if not isinstance(content, dict) or content.get("act_type") != "file_done":
                continue
            inner = content.get("data")
            if isinstance(inner, str):
                try:
                    inner = json.loads(inner)
                except ValueError:
                    inner = {}
            url = str((inner or {}).get("url") or "")
            if url and content.get("fileId") not in (None, ""):
                with self._cond:
                    self._urls[str(content["fileId"])] = url
                    while len(self._urls) > KEEP_URLS:
                        self._urls.pop(next(iter(self._urls)))
                    self._cond.notify_all()

    def wait(self, file_id: str, timeout: float) -> str | None:
        with self._cond:
            self._cond.wait_for(lambda: file_id in self._urls, timeout)
            return self._urls.pop(file_id, None)


WATCHER = FileDoneWatcher()
_installed = False


def install_hook() -> None:
    """Bọc zlapi._util.zws_decode một lần để WATCHER thấy mọi gói websocket. Gọi sau khi import zlapi."""
    global _installed
    if _installed:
        return
    from zlapi import _util

    original = _util.zws_decode

    def wrapped(parsed, key):
        result = original(parsed, key)
        try:
            WATCHER.feed(result)
        except Exception:  # noqa: BLE001 - không được làm hỏng vòng nghe của zlapi
            log.debug("Không đọc được gói websocket file_done", exc_info=True)
        return result

    _util.zws_decode = wrapped
    _installed = True


def _decoded(api: Any, response: Any) -> dict:
    """Giải mã phản hồi của Zalo (cùng cách với zlapi._uploadImage / sendRemoteFile); ném ZaloError nếu Zalo từ chối."""
    body = response.json()
    if body.get("error_code") != 0 or not body.get("data"):
        raise ZaloError(str(body.get("error_message") or body.get("data") or body), body.get("error_code"))
    result = api._decode(body["data"])
    if isinstance(result, dict) and "data" in result and result.get("error_code", 0) == 0:
        result = result["data"]
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except ValueError:
            raise ZaloError(f"Zalo trả dữ liệu lạ: {result[:200]}") from None
    if not isinstance(result, dict):
        raise ZaloError("Zalo trả dữ liệu rỗng")
    if result.get("error_code") not in (None, 0):
        raise ZaloError(str(result.get("error_message") or result), result.get("error_code"))
    return result


def send_file(api: Any, chat_id: str, is_group: bool, path: Path, *, timeout: float | None = None) -> None:
    """Upload và gửi `path` vào chat (đồng bộ; gọi qua asyncio.to_thread). `api` là zlapi.ZaloAPI đã đăng nhập."""
    data = path.read_bytes()
    if not data:
        raise ZaloError("Tệp rỗng")
    if len(data) > MAX_FILE_BYTES:
        raise ZaloUnsupported(f"Tệp quá lớn để gửi qua Zalo ({len(data) // 1024} KB)")
    from zlapi._util import now  # cùng đồng hồ mili giây zlapi dùng cho clientId

    side = "group" if is_group else "message"
    owner_key = "grid" if is_group else "toid"
    params = {"totalChunk": 1, "fileName": path.name, "clientId": now(), "totalSize": len(data),
              "imei": api._imei, "isE2EE": 0, "jxl": 0, "chunkId": 1, owner_key: str(chat_id)}
    upload = {"params": api._encode(params), "zpw_ver": 647, "zpw_type": 30, "type": 11 if is_group else 2}
    response = api._post(f"{FILE_HOST}/api/{side}/asyncfile/upload", params=upload,
                         files=[("chunkContent", (path.name, data, "application/octet-stream"))])
    uploaded = _decoded(api, response)
    file_id = str(uploaded.get("fileId") if uploaded.get("fileId") is not None else "-1")
    if file_id in ("-1", "", "None"):
        raise ZaloError(f"Zalo không nhận tệp: {uploaded}")

    url = WATCHER.wait(file_id, FILE_DONE_TIMEOUT if timeout is None else timeout)
    if not url:
        raise ZaloUnsupported("Zalo không báo tải tệp xong (có thể chưa nghe websocket hoặc giao thức đã đổi)")

    message = {"fileId": file_id, "checksum": hashlib.md5(data).hexdigest(), "checksumSha": "",
               "extention": path.suffix.lstrip(".").lower(), "totalSize": len(data), "fileName": path.name,
               "clientId": uploaded.get("clientFileId") or params["clientId"], "fType": 1, "fileCount": 0,
               "fdata": "{}", owner_key: str(chat_id), "fileUrl": url, "zsource": -1, "ttl": 0}
    sent = api._post(f"{FILE_HOST}/api/{side}/asyncfile/msg",
                     params={"zpw_ver": 647, "zpw_type": 30, "nretry": 0}, data={"params": api._encode(message)})
    _decoded(api, sent)
