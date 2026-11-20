"""Kết quả và lỗi chung của các lệnh gọi model."""

from __future__ import annotations

from dataclasses import dataclass


class ModelCallError(Exception):
    """Gọi model lỗi; `str(exc)` đã là câu tiếng Việt đọc được và KHÔNG chứa key.

    `retryable`: lỗi của riêng model hoặc của lúc này (hết hạn mức, 5xx, hết giờ): thử model dự phòng được.
    `rephrase`: bộ lọc nội dung của nhà cung cấp từ chối lời nhắc (hay nhầm với từ vô hại): viết lại lời nhắc rồi gọi lại."""

    def __init__(self, message: str, *, retryable: bool = False, rephrase: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.rephrase = rephrase


@dataclass(frozen=True)
class ImageResult:
    data: bytes
    mime: str
    model: str

    @property
    def extension(self) -> str:
        return ".jpg" if self.mime == "image/jpeg" else ".png"


def sniff_image_mime(data: bytes) -> str:
    """Loại ảnh theo đầu file (Cloudflare không nói rõ PNG hay JPEG). Không phải ảnh thì ném ModelCallError."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    raise ModelCallError("Model trả về dữ liệu không phải ảnh PNG hoặc JPEG", retryable=True)
