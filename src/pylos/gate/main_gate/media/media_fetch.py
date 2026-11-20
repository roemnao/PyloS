"""Tải tệp đính kèm (ảnh, video, tin thoại) từ CDN của Zalo về thư mục túp lều.

Chỉ tải khi bộ lọc đã cho tin đi qua. Dừng ngay khi vượt giới hạn dung lượng.
"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path

import httpx

from pylos.gate.main_gate.zalo.incoming_message import Attachment

# Test gắn httpx.MockTransport vào đây (giống gate/side_gate/vps/remote_server.py).
transport: httpx.AsyncBaseTransport | None = None

TIMEOUT = 30.0
CHUNK = 64 * 1024

ALLOWED = {
    "photo": {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"},
    "voice": {"audio/aac", "audio/mp4", "audio/mpeg", "audio/ogg", "audio/wav", "audio/flac"},
    "video": {"video/mp4", "video/quicktime", "video/webm", "video/3gpp"},
}
# Zalo hay gửi tin thoại không có Content-Type rõ: đoán theo loại tin.
DEFAULT_MIME = {"photo": "image/jpeg", "voice": "audio/aac", "video": "video/mp4"}
ALIASES = {
    "audio/x-aac": "audio/aac", "audio/m4a": "audio/mp4", "audio/x-m4a": "audio/mp4", "audio/mp3": "audio/mpeg",
    "audio/x-wav": "audio/wav", "image/jpg": "image/jpeg", "video/x-m4v": "video/mp4",
}
EXTENSIONS = {
    "audio/aac": ".aac", "audio/mp4": ".m4a", "audio/mpeg": ".mp3", "audio/ogg": ".ogg", "audio/wav": ".wav",
    "audio/flac": ".flac", "video/quicktime": ".mov", "video/3gpp": ".3gp", "video/mp4": ".mp4",
    "video/webm": ".webm", "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
    "image/heic": ".heic", "image/heif": ".heif",
}


@dataclass(frozen=True)
class Limits:
    photo_mb: float = 10
    voice_mb: float = 15
    video_mb: float = 50

    def max_bytes(self, kind: str) -> int:
        mb = {"photo": self.photo_mb, "voice": self.voice_mb, "video": self.video_mb}.get(kind, 0)
        return int(mb * 1024 * 1024)


@dataclass(frozen=True)
class MediaFile:
    path: Path
    mime: str
    kind: str
    size: int


@dataclass(frozen=True)
class MediaError:
    reason: str  # too_large | unsupported | download_failed
    detail: str = ""


def sniff_mime(head: bytes) -> str:
    """Đoán MIME từ vài byte đầu (magic bytes). Rỗng nếu không nhận ra."""
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav"
    if head.startswith(b"OggS"):
        return "audio/ogg"
    if head.startswith(b"fLaC"):
        return "audio/flac"
    if head.startswith(b"ID3") or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "audio/mpeg"
    if head[:2] in (b"\xff\xf1", b"\xff\xf9"):
        return "audio/aac"
    if head[4:8] == b"ftyp":
        brand = head[8:12]
        if brand in (b"heic", b"heix", b"mif1", b"heif"):
            return "image/heic"
        if brand in (b"M4A ", b"M4B "):
            return "audio/mp4"
        if brand == b"qt  ":
            return "video/quicktime"
        if brand.startswith(b"3gp"):
            return "video/3gpp"
        return "video/mp4"
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        return "video/webm"
    return ""


def pick_mime(kind: str, content_type: str, head: bytes, url: str) -> str:
    """Content-Type, rồi magic bytes, rồi đuôi file, rồi mặc định theo loại tin. Phải nằm trong ALLOWED."""
    allowed = ALLOWED.get(kind, set())
    declared = content_type.split(";")[0].strip().lower()
    declared = ALIASES.get(declared, declared)
    if declared in allowed:
        return declared
    sniffed = sniff_mime(head)
    if sniffed in allowed:
        return sniffed
    # Content-Type chung chung (octet-stream, rỗng): thử đuôi file, rồi mặc định theo loại tin.
    if declared in ("", "application/octet-stream", "binary/octet-stream"):
        guessed = (mimetypes.guess_type(url.split("?")[0])[0] or "").lower()
        guessed = ALIASES.get(guessed, guessed)
        if guessed in allowed:
            return guessed
        if not sniffed:
            return DEFAULT_MIME.get(kind, "")
    return ""


async def fetch_attachment(att: Attachment, dest_dir: Path, name: str, limits: Limits) -> MediaFile | MediaError:
    """Tải att.url vào dest_dir/<name><đuôi>. Trả MediaFile hoặc MediaError."""
    if att.kind not in ALLOWED:
        return MediaError("unsupported", att.kind)
    if not att.url.startswith(("http://", "https://")):
        return MediaError("download_failed", "không có URL")
    limit = limits.max_bytes(att.kind)
    if att.size and att.size > limit:
        return MediaError("too_large", str(att.size))
    dest_dir.mkdir(parents=True, exist_ok=True)
    part = dest_dir / f"{name}.part"
    try:
        async with httpx.AsyncClient(transport=transport, timeout=TIMEOUT, follow_redirects=True) as client:
            async with client.stream("GET", att.url) as response:
                if response.status_code != 200:
                    return MediaError("download_failed", f"HTTP {response.status_code}")
                declared = int(response.headers.get("content-length") or 0)
                if declared > limit:
                    return MediaError("too_large", str(declared))
                total, head = 0, b""
                with part.open("wb") as out:
                    async for chunk in response.aiter_bytes(CHUNK):
                        total += len(chunk)
                        if total > limit:
                            return MediaError("too_large", str(total))
                        if len(head) < 32:
                            head += chunk[: 32 - len(head)]
                        out.write(chunk)
                content_type = response.headers.get("content-type", "")
        if total == 0:
            return MediaError("download_failed", "tệp rỗng")
        mime = pick_mime(att.kind, content_type, head, att.url)
        if not mime:
            return MediaError("unsupported", content_type or "?")
        final = dest_dir / f"{name}{EXTENSIONS.get(mime, '.bin')}"
        part.replace(final)
        return MediaFile(final, mime, att.kind, total)
    except (httpx.HTTPError, ValueError, OSError) as exc:
        return MediaError("download_failed", str(exc)[:200])
    finally:
        part.unlink(missing_ok=True)
