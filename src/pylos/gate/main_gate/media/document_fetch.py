"""Tải tệp tài liệu (.docx, .md, .txt) người dùng gửi về huts/<chat>/docs/. Chỉ tải khi bộ lọc đã cho tin đi qua."""

from __future__ import annotations

from pathlib import Path

import httpx

from pylos.gate.main_gate.media.media_fetch import CHUNK, TIMEOUT, MediaError
from pylos.gate.main_gate.zalo.incoming_message import Attachment
from pylos.lobby.office.documents.files import DocError, unique_path

# Test gắn httpx.MockTransport vào đây (giống media_fetch.transport).
transport: httpx.AsyncBaseTransport | None = None


async def fetch_document(att: Attachment, folder: Path, max_bytes: int) -> Path | MediaError:
    """Tải att.url vào folder/<tên gốc> (trùng tên thì thêm -2, -3...). Trả đường dẫn hoặc MediaError."""
    if not att.url.startswith(("http://", "https://")):
        return MediaError("download_failed", "không có URL")
    if att.size and att.size > max_bytes:
        return MediaError("too_large", str(att.size))
    try:
        target = unique_path(folder, att.name or att.title)
    except DocError as exc:
        return MediaError("unsupported", str(exc))
    folder.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    try:
        async with httpx.AsyncClient(transport=transport, timeout=TIMEOUT, follow_redirects=True) as client:
            async with client.stream("GET", att.url) as response:
                if response.status_code != 200:
                    return MediaError("download_failed", f"HTTP {response.status_code}")
                if int(response.headers.get("content-length") or 0) > max_bytes:
                    return MediaError("too_large", response.headers.get("content-length", ""))
                total = 0
                with part.open("wb") as out:
                    async for chunk in response.aiter_bytes(CHUNK):
                        total += len(chunk)
                        if total > max_bytes:
                            return MediaError("too_large", str(total))
                        out.write(chunk)
        if total == 0:
            return MediaError("download_failed", "tệp rỗng")
        part.replace(target)
        return target
    except (httpx.HTTPError, ValueError, OSError) as exc:
        return MediaError("download_failed", str(exc)[:200])
    finally:
        part.unlink(missing_ok=True)
