"""Kích thước (rộng, cao) của ảnh PNG hoặc JPEG đọc từ đầu file, không cần thư viện ảnh."""

from __future__ import annotations

import struct

# Các marker JPEG "bắt đầu khung" (SOF) có chứa kích thước; trừ DHT (C4), JPG (C8) và DAC (CC).
_SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def image_size(data: bytes) -> tuple[int, int] | None:
    """(rộng, cao) nếu đọc được; None nếu không phải PNG/JPEG hợp lệ."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return (width, height) if width and height else None
    if data.startswith(b"\xff\xd8"):
        pos = 2
        while pos + 9 < len(data):
            if data[pos] != 0xFF:
                pos += 1
                continue
            marker = data[pos + 1]
            if marker == 0xFF:  # byte đệm
                pos += 1
                continue
            if marker in _SOF:
                height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
                return (width, height) if width and height else None
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:  # marker không có độ dài
                pos += 2
                continue
            pos += 2 + struct.unpack(">H", data[pos + 2:pos + 4])[0]
    return None
