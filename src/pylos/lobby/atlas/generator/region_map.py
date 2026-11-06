"""Phân vùng cho bản đồ graphify: xuất `maps/regions.json` (file nào thuộc khu/toà nào, tên, màu, vị trí).

    python -m pylos.lobby.atlas.generator.atlas        # ghi atlas.md và regions.json (--check: chỉ kiểm)

Phần VẼ bản đồ (màu theo toà, hình theo loại code, viền cộng đồng, nút `?`) nằm trong graphify trên máy admin
(graphify-regions, xem management/owner/private_plans/graphify_regions_plan.md). `.graphifyrc` trỏ tới file này
bằng `regions.file`. Máy không cài graphify-regions vẫn dựng graph.html bình thường (bản gốc của graphify).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "pyproject.toml").is_file())
REGIONS_FILE = ROOT / "src" / "pylos" / "lobby" / "atlas" / "maps" / "regions.json"

# Vùng hiển thị: 11 toà + vài vùng ngoài Thành.
# (id, tên, khu, vị trí, màu). Vị trí/màu None: graphify-regions tự chọn MỘT toà trung tâm (luồng + số nút + nút lớn nhất),
# chia vòng vây theo đường nối, mỗi khu một quạt, màu nóng (gần trung tâm) sang lạnh (xa). Lối vào bot (outside/entry)
# tính là nội thành. Chỉ 4 vùng xám của ngoại thành ghim vị trí: nằm thành hàng dưới cùng.
REGIONS = [
    ("management/owner", "Toà Owner", "management", None, None),
    ("management/managers", "Toà quản lý", "management", None, None),
    ("gate/main_gate", "Cổng chính", "gate", None, None),
    ("gate/fence", "Hàng rào", "gate", None, None),
    ("gate/side_gate", "Cổng phụ", "gate", None, None),
    ("gate/guest_house", "Toà khách", "gate", None, None),
    ("lobby/dispatch", "Điều phối", "lobby", None, None),
    ("lobby/office", "Văn phòng", "lobby", None, None),
    ("lobby/atlas", "Bản đồ", "lobby", None, None),
    ("lobby/library", "Thư viện", "lobby", None, None),
    ("residential/residents", "Toà nhà dân", "residential", None, None),
    ("outside/entry", "Lối vào bot", "outside", None, None),
    ("outside/tests", "Test", "outside", (-1.6, 4.2), (0, 0, 66)),
    ("outside/repo_root", "Gốc repo", "outside", (0.6, 4.2), (0, 0, 55)),
    ("outside/tooling", "Công cụ", "outside", (2.2, 4.2), (0, 0, 44)),
    ("outside/external", "Thư viện ngoài", "outside", (4.6, 3.8), (0, 0, 33)),
]
ZONE_NAMES = {"management": "Khu quản lý", "gate": "Khu cổng", "lobby": "Khu đại sảnh", "residential": "Khu dân cư", "outside": "Ngoài Thành"}


def region_of(district: str, has_file: bool) -> str:
    """Toà (zone/building hoặc outside/<khu vực>) -> id vùng hiển thị."""
    if not has_file:
        return "outside/external"  # nút không thuộc file nào: thư viện ngoài (json, pytest, Path...)
    if district == "open":
        return "outside/entry"
    ids = {r[0] for r in REGIONS}
    if district.startswith("outside/") and district not in ids:
        return "outside/tooling"
    if district in ids:
        return district
    zone = district.split("/")[0]  # nút của gói khu (src/pylos/<khu>/__init__.py): về toà đầu tiên của khu
    return next((r[0] for r in REGIONS if r[2] == zone), "outside/tooling")


def _region(rid: str, name: str, zone: str, pt, hsl) -> dict:
    out = {"id": rid, "name": name, "group": zone}
    if hsl:
        out["color"] = list(hsl)
    if pt:
        out["pos"] = list(pt)  # có pos = ngoại thành, xếp thành hàng dưới cụm nội thành theo thứ tự x
    return out


def regions_text() -> str:
    """Nội dung regions.json (định dạng chung của graphify-regions, version 1), tính từ atlas_map.toml."""
    sys.path.insert(0, str(ROOT / "src"))
    from pylos.lobby.atlas.generator import atlas

    _, rules = atlas.load_map()
    atlas.assign(atlas.tracked_files(), rules)
    files = {path: region_of(atlas.district(rule.target), True) for path, rule in sorted(atlas.file_targets(rules).items())}
    data = {
        "version": 1,
        "levels": {"group": "Khu", "region": "Toà"},
        "groups": [{"id": z, "name": n} for z, n in ZONE_NAMES.items()],
        "regions": [_region(*r) for r in REGIONS],
        "unplaced_region": "outside/tooling",
        "external_region": "outside/external",
        "tests_region": "outside/tests",
        "files": files,
    }
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def main() -> int:
    REGIONS_FILE.write_text(regions_text(), encoding="utf-8", newline="\n")
    print(f"wrote {REGIONS_FILE.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
