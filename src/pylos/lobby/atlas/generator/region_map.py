"""Bản đồ vùng: đồ thị graphify (mỗi hàm/lớp/file là một nút riêng, không gộp) xếp thành vùng theo 4 khu và 11 toà.

    python -m pylos.lobby.atlas.generator.region_map            # ghi graphify-out/pylos_map.html

Đọc graphify-out/graph.json (graphify) và atlas_map.toml (file nào thuộc toà nào), tính sẵn vị trí từng nút: nút của
một toà nằm trong vòng tròn của toà đó, các vòng của cùng một khu đứng gần nhau. Trang HTML chỉ vẽ lại, không phải
chạy mô phỏng nên mở nhanh trên điện thoại. Cần networkx (đi kèm graphify), nên đây là công cụ cho người phát triển.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "pyproject.toml").is_file())
TEMPLATE = HERE / "region_map.html"

# Vùng hiển thị: 11 toà + vài vùng ngoài Thành. (id, tên, khu, vị trí tương đối trên bản đồ)
REGIONS = [
    ("management/owner", "Toà Owner", "management", (-1.0, -2.3)),
    ("management/managers", "Toà quản lý", "management", (1.0, -2.3)),
    ("gate/main_gate", "Cổng chính", "gate", (-3.1, -0.9)),
    ("gate/side_gate", "Cổng phụ", "gate", (-3.5, 1.3)),
    ("gate/fence", "Hàng rào", "gate", (-2.2, 2.7)),
    ("gate/guest_house", "Toà khách", "gate", (-3.9, 3.0)),
    ("lobby/dispatch", "Điều phối", "lobby", (0.0, 0.0)),
    ("lobby/office", "Văn phòng", "lobby", (2.0, -1.2)),
    ("lobby/atlas", "Bản đồ", "lobby", (1.8, 2.0)),
    ("lobby/library", "Thư viện", "lobby", (-1.7, 2.1)),
    ("residential/residents", "Toà nhà dân", "residential", (3.8, 0.2)),
    ("outside/tests", "Test", "outside", (-1.6, 4.5)),
    ("outside/repo_root", "Gốc repo", "outside", (0.6, 4.5)),
    ("outside/tooling", "Công cụ", "outside", (2.2, 4.6)),
    ("outside/entry", "Lối vào bot", "outside", (3.8, 2.7)),
    ("outside/external", "Thư viện ngoài", "outside", (3.3, 4.6)),
]
ZONE_NAMES = {"management": "Khu quản lý", "gate": "Khu cổng", "lobby": "Khu đại sảnh", "residential": "Khu dân cư", "outside": "Ngoài Thành"}
ZONE_HUE = {"management": 265, "gate": 213, "lobby": 36, "residential": 150, "outside": 200}


def region_of(district: str, has_file: bool) -> str:
    """Toà (zone/building hoặc outside/<khu vực>) -> id vùng hiển thị."""
    if not has_file:
        return "outside/external"  # nút không thuộc file nào: thư viện ngoài (json, pytest, Path...)
    if district == "open":
        return "outside/entry"
    if district.startswith("outside/") and district not in {r[0] for r in REGIONS}:
        return "outside/tooling"
    if district in {r[0] for r in REGIONS}:
        return district
    zone = district.split("/")[0]  # nút của gói khu (src/pylos/<khu>/__init__.py): về toà đầu tiên của khu
    return next((r[0] for r in REGIONS if r[2] == zone), "outside/tooling")


def plan_regions(radius: dict[str, float], gap: float = 90.0) -> dict[str, tuple[float, float, float]]:
    """id vùng -> (x, y, bán kính). Đẩy các vòng ra cho tới khi không chồng nhau."""
    radius = {rid: radius.get(rid, 30.0) for rid, *_ in REGIONS}
    scale = max(radius.values()) * 1.05
    pos = {rid: [pt[0] * scale, pt[1] * scale] for rid, _, _, pt in REGIONS}
    ids = list(pos)
    for _ in range(600):
        moved = False
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
                dist = math.hypot(dx, dy) or 0.01
                need = radius[a] + radius[b] + gap
                if dist < need:
                    push = (need - dist) / 2 + 0.5
                    ux, uy = dx / dist, dy / dist
                    pos[a][0] -= ux * push; pos[a][1] -= uy * push
                    pos[b][0] += ux * push; pos[b][1] += uy * push
                    moved = True
        if not moved:
            break
    return {rid: (pos[rid][0], pos[rid][1], radius[rid]) for rid in ids}


GOLDEN = math.pi * (3 - math.sqrt(5))


def pack_region(files: list[list[int]], degree) -> tuple[dict[int, tuple[float, float]], float]:
    """Xếp các file của một toà (mỗi file là danh sách nút): file thành cụm tròn, cụm xếp xoắn ốc không chồng nhau.

    Trả về (vị trí tương đối của từng nút, bán kính cả vùng). Trong cụm, nút nối nhiều nhất nằm giữa."""
    files = sorted(files, key=len, reverse=True)
    blobs = [(9.0 * math.sqrt(len(f)) + 10.0) for f in files]
    centers: list[tuple[float, float]] = []
    for k, rf in enumerate(blobs):
        if k == 0:
            centers.append((0.0, 0.0)); continue
        step, ang = 6.0, 0.0
        r = blobs[0]
        while True:
            c = (r * math.cos(ang), r * math.sin(ang))
            if all(math.hypot(c[0] - o[0], c[1] - o[1]) >= rf + blobs[j] + 6.0 for j, o in enumerate(centers)):
                centers.append(c); break
            ang += 0.35
            r += step * 0.35 / (2 * math.pi) * 6.0
    pos: dict[int, tuple[float, float]] = {}
    for f, rf, (cx, cy) in zip(files, blobs, centers):
        members = sorted(f, key=lambda i: -degree(i))
        for k, i in enumerate(members):
            rr = rf * math.sqrt((k + 0.5) / len(members))
            pos[i] = (cx + rr * math.cos(k * GOLDEN), cy + rr * math.sin(k * GOLDEN))
    extent = max((math.hypot(cx, cy) + rf) for (cx, cy), rf in zip(centers, blobs))
    return pos, extent + 22.0


def build(graph_file: Path, out_file: Path) -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    from pylos.lobby.atlas.generator import atlas

    _, rules = atlas.load_map()
    atlas.assign(atlas.tracked_files(), rules)
    owner = atlas.file_targets(rules)
    g = json.loads(graph_file.read_text(encoding="utf-8"))
    nodes = g["nodes"]
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    edges = sorted({tuple(sorted((idx[e["source"]], idx[e["target"]]))) for e in g["links"]
                    if e["source"] in idx and e["target"] in idx and e["source"] != e["target"]})
    region = []
    for n in nodes:
        f = n.get("source_file") or ""
        rule = owner.get(f)
        region.append(region_of(atlas.district(rule.target) if rule else "", bool(f)))
    counts = Counter(region)
    deg = Counter(v for e in edges for v in e)
    rel, radius = {}, {}
    for rid, *_ in REGIONS:
        by_file: dict[str, list[int]] = {}
        for i, x in enumerate(region):
            if x == rid:
                by_file.setdefault(nodes[i].get("source_file") or "", []).append(i)
        if by_file:
            rel[rid], radius[rid] = pack_region(list(by_file.values()), lambda i: deg[i])
    plan = plan_regions(radius)
    pos = {}
    for rid, (cx, cy, _) in plan.items():
        for i, (x, y) in rel.get(rid, {}).items():
            pos[i] = (cx + x, cy + y)

    rids = [r[0] for r in REGIONS]
    files, fidx = [], {}
    out_nodes = []
    for i, n in enumerate(nodes):
        f = n.get("source_file") or ""
        if f not in fidx:
            fidx[f] = len(files); files.append(f)
        out_nodes.append([n["label"], round(pos[i][0]), round(pos[i][1]), rids.index(region[i]), fidx[f], deg[i]])
    regions = [{"id": rid, "name": name, "zone": zone, "zoneName": ZONE_NAMES[zone], "hue": ZONE_HUE[zone],
                "x": round(plan[rid][0]), "y": round(plan[rid][1]), "r": round(plan[rid][2]), "n": counts.get(rid, 0)}
               for rid, name, zone, _ in REGIONS]
    data = {"commit": (g.get("built_at_commit") or "")[:8], "regions": regions, "files": files, "nodes": out_nodes,
            "edges": [v for e in edges for v in e]}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    out_file.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", blob), encoding="utf-8")
    return data


def main() -> int:
    data = build(ROOT / "graphify-out" / "graph.json", ROOT / "graphify-out" / "pylos_map.html")
    print(f"{len(data['nodes'])} nút, {len(data['edges']) // 2} cạnh, {len(data['regions'])} vùng -> graphify-out/pylos_map.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
