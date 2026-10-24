"""Vẽ biểu tượng bằng Pillow (không cần file ảnh trong repo)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BRAND = (0, 104, 255)  # xanh Zalo
STATE_COLORS = {
    "running": (26, 170, 70),
    "warning": (230, 160, 0),
    "stopped": (140, 140, 140),
}


def make_icon(state: str | None = None, size: int = 64) -> Image.Image:
    """Ô vuông bo góc màu xanh có chữ Z; `state` thêm chấm trạng thái ở góc dưới phải."""
    scale = 4  # vẽ to rồi thu nhỏ cho mịn
    big = size * scale
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, big - 1, big - 1), radius=big // 5, fill=BRAND + (255,))
    font = ImageFont.load_default(size=int(big * 0.68))
    draw.text((big / 2, big / 2), "Z", fill=(255, 255, 255, 255), font=font, anchor="mm")
    if state in STATE_COLORS:
        r = big // 4
        cx = cy = big - r - big // 24
        draw.ellipse((cx - r - scale * 3, cy - r - scale * 3, cx + r + scale * 3, cy + r + scale * 3), fill=(255, 255, 255, 255))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=STATE_COLORS[state] + (255,))
    return image.resize((size, size), Image.LANCZOS)


def write_ico(path: Path) -> Path:
    """File .ico nhiều kích thước cho ZaloBot.exe (dùng khi build)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    make_icon(size=256).save(path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return path
