"""Lọc đường dẫn cho công cụ file của bot (city.md, mục 4 "Access rules").

Áp cho **bot** (file mà LLM xin qua một công cụ), không áp cho code hệ thống của PyloS. Công cụ file phải gọi
`check_access` trước mọi lần đọc/ghi và chỉ dùng đường dẫn nó trả về (đã chuẩn hoá). Chưa có công cụ file nào của bot
dùng nó; đây là hàng rào sẵn để gắn vào khi công cụ đầu tiên ra đời.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class AccessDenied(PermissionError):
    pass


@dataclass(frozen=True)
class Actor:
    kind: str  # "bot" | "manager" | "owner"
    name: str = ""  # tên căn hộ của bot (residents/<name>)


def _inside(path: Path, base: Path) -> bool:
    return path == base or base in path.parents


def check_access(raw: str | Path, actor: Actor, *, city_root: Path, huts_root: Path,
                 served_hut: str | None = None) -> Path:
    """Trả về đường dẫn đã chuẩn hoá nếu `actor` được vào, ngược lại ném AccessDenied.

    `city_root`: thư mục pylos/ (4 khu). `huts_root`: nơi lưu túp lều (userdata/data/huts). `served_hut`: túp lều của
    người (hoặc nhóm) mà bot đang phục vụ; None nghĩa là không phục vụ ai nên không vào túp lều nào.
    Chuẩn hoá bằng resolve() nên `..`, symlink và đường dẫn tuyệt đối không lách được; so sánh không phân biệt hoa/thường
    ở Windows nhờ chuẩn hoá của hệ điều hành.
    """
    city, huts = city_root.resolve(), huts_root.resolve()
    path = (Path(raw) if Path(raw).is_absolute() else city / raw).resolve()
    if actor.kind == "owner":
        return path

    if _inside(path, huts):
        hut = path.relative_to(huts).parts[:1]
        if not hut:
            raise AccessDenied("không được liệt kê các túp lều")
        if actor.kind == "manager" or hut[0] == served_hut:
            return path
        raise AccessDenied("túp lều này không phải của người đang được phục vụ")

    if not _inside(path, city):
        raise AccessDenied("ngoài nội thành")
    parts = path.relative_to(city).parts
    if parts[:2] == ("management", "owner"):
        raise AccessDenied("toà Owner chỉ dành cho owner")
    if parts[:2] == ("lobby", "dispatch"):
        raise AccessDenied("toà điều phối chỉ dành cho owner")
    if parts[:2] == ("residential", "residents") and len(parts) >= 3 and parts[2] != actor.name:
        raise AccessDenied("căn hộ của bot khác")
    if parts[:2] == ("gate", "guest_house") and len(parts) >= 3:
        raise AccessDenied("túp lều nằm trong userdata, không nằm trong mã nguồn")
    return path
