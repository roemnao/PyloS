"""graphify-regions: vẽ graph.html của graphify thành bản đồ vùng (màu theo vùng, hình theo loại code, viền cộng đồng).

Điểm vào duy nhất: apply_regions(), được graphify.exporters.html.to_html gọi ngay trước khi ghi file.
Cấu hình trong <gốc dự án>/.graphifyrc:
    regions.mode=off          không vẽ vùng (graph.html gốc của graphify)
    regions.file=<đường dẫn>  file phân vùng (xem README)
    regions.depth=<n>         chia theo n cấp thư mục (mặc định 2)
    regions.center=a,b        vùng trung tâm (mặc định tự chọn theo đường nối giữa các vùng)
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from . import inject, layout, zoning
from .inject import RegionsSkip

__all__ = ["apply_regions", "build_layout", "RegionsSkip"]
NO_OUTLINE_MIN = 3  # nhóm ít hơn 3 nút trong một vùng không vẽ viền (vẫn sáng khi bấm)


def _project_root(output_path: str) -> Path:
    out = Path(output_path).resolve()
    for cand in (out.parent.parent, Path.cwd()):
        if (cand / ".graphifyrc").is_file() or (cand / "graphify-regions.json").is_file():
            return cand
    return out.parent.parent


def pick_zoning(root: Path, cfg: dict, nodes: dict[str, dict], edges: list[tuple[str, str]]) -> zoning.Zoning:
    rc_file = cfg.get("file")
    if rc_file:
        return zoning.from_file((root / rc_file) if not Path(rc_file).is_absolute() else Path(rc_file))
    default = root / "graphify-regions.json"
    if default.is_file():
        return zoning.from_file(default)
    try:
        depth = int(cfg.get("depth", 2))
    except ValueError:
        raise RegionsSkip(f"regions.depth không phải số: {cfg.get('depth')!r}")
    z = zoning.by_folder({a.get("source_file") for a in nodes.values()}, depth)
    return z or zoning.by_community(nodes, edges)


def build_layout(nodes: dict[str, dict], order: list[str], edges: list[tuple[str, str, str]], sizes: dict[str, float],
                 z: zoning.Zoning) -> tuple[dict, dict]:
    """nodes: id -> thuộc tính; order: thứ tự nút; edges: (từ, tới, quan hệ). Trả về (GREG_LAYOUT, dữ liệu cho bot)."""
    region = {nid: z.node_region(nid, nodes[nid]) for nid in order}
    counts = Counter(region.values())
    # đường nối giữa các vùng (bỏ đường cấu trúc, tới thư viện ngoài, test) để suy vị trí và vùng trung tâm
    flows: Counter = Counter()
    for u, v, rel in edges:
        if rel in zoning.STRUCT or u not in region or v not in region:
            continue
        a, b = region[u], region[v]
        if a != b and z.external not in (a, b) and z.tests not in (a, b):
            flows[(a, b)] += 1
    kept = [r for r in z.regions if counts.get(r["id"])]  # vùng không có nút nào thì bỏ
    if not kept:
        raise RegionsSkip("không nút nào rơi vào vùng nào")
    z.regions = kept
    w = zoning.symmetric(flows)
    outer = sorted((r for r in z.regions if zoning.is_outer(z, r)), key=lambda r: (r.get("pos") or (0, 0))[0])
    inner = [r["id"] for r in z.regions if not zoning.is_outer(z, r)]
    deg = Counter()
    for u, v, _ in edges:
        deg[u] += 1; deg[v] += 1
    stats = {i: {"flow": sum(w.get((i, j), 0.0) for j in inner if j != i), "nodes": counts[i],
                 "top": max((deg[n] for n in order if region[n] == i), default=0)} for i in inner}
    center = zoning.pick_center(inner, stats, z.centers) if inner else None
    rings = zoning.assign_rings(inner, center, w) if inner else []
    colors = zoning.auto_colors(z, [[center], *rings] if inner else [])
    ring_of = {center: 0, **{x: k + 1 for k, ring in enumerate(rings) for x in ring}}
    group = {r["id"]: r.get("group") or r["id"] for r in z.regions}
    comm = {nid: nodes[nid].get("community", -1) for nid in order}
    idx = {nid: i for i, nid in enumerate(order)}
    rel, radius = {}, {}
    for r in z.regions:
        by_file: dict[str, list[int]] = {}
        for nid in order:
            if region[nid] == r["id"]:
                by_file.setdefault(str(nodes[nid].get("source_file") or ""), []).append(idx[nid])
        rel[r["id"]], radius[r["id"]] = layout.pack_region(list(by_file.values()), lambda i: deg[order[i]],
                                                            lambda i: comm[order[i]], lambda i: sizes.get(order[i], 10.0))
    if center:
        plan = layout.plan_rings(radius, center, rings, group, w, [r["id"] for r in outer])
    else:  # không có vùng nội thành: chỉ một hàng
        plan = layout.plan_rings(radius, outer[0]["id"], [], group, w, [r["id"] for r in outer[1:]])
    pos, spots = {}, {}
    for rid, (cx, cy, _) in plan.items():
        for i, (x, y) in rel[rid].items():
            pos[order[i]] = [round(cx + x), round(cy + y)]
            spots.setdefault(rid, []).append((cx + x, cy + y, sizes.get(order[i], 10.0)))
    polys = layout.region_polygons(plan, spots)
    ridx = {r["id"]: k for k, r in enumerate(z.regions)}
    regions = []
    for r in z.regions:
        g = z.groups.get(r["group"], {})
        h, s, l = colors[r["id"]]
        regions.append({"id": r["id"], "name": r["name"], "zone": r["group"], "zoneName": g.get("name") or r["group"],
                        "h": h, "s": s, "l": l, "x": round(plan[r["id"]][0]), "y": round(plan[r["id"]][1]),
                        "r": round(plan[r["id"]][2]), "ring": ring_of.get(r["id"], -1), "n": counts[r["id"]], "poly": polys[r["id"]],
                        "ly": min(p[1] for p in polys[r["id"]])})
    kinds = {nid: layout.kind_of(nodes[nid]) for nid in order}
    node_map = {nid: [ridx[region[nid]], layout.KINDS.index(kinds[nid])] for nid in order}
    by_group: dict[tuple[str, int], list[str]] = {}
    for nid in order:
        if region[nid] != z.external:
            by_group.setdefault((region[nid], comm[nid]), []).append(nid)
    groups = []
    for (rid, cid), ids in sorted(by_group.items(), key=lambda kv: (ridx[kv[0][0]], kv[0][1])):
        if len(ids) < NO_OUTLINE_MIN:
            continue
        name = str(nodes[ids[0]].get("community_name") or "")
        if not name or name.startswith("Community "):
            name = str(nodes[max(ids, key=lambda i: (deg[i], i))].get("label") or f"#{cid}")
        groups.append({"region": ridx[rid], "cid": cid, "name": name, "nodes": ids})
    hub = center or z.regions[0]["id"]
    data = {"regions": regions, "pos": pos, "node": node_map, "kinds": layout.KINDS, "groups": groups,
            "external": z.external, "tests": z.tests, "hub": hub, "levels": z.levels}
    bot = {"how": z.how, "nodes": {nid: {"region": region[nid], "kind": kinds[nid], "community": comm[nid]} for nid in order}}
    return data, bot


def _fill_empty_legend(html: str, vis_nodes: list[dict]) -> str:
    """graphify dựng danh sách cộng đồng từ nhãn; thiếu nhãn (vd. `graphify export html`) thì danh sách rỗng. Dựng lại từ các nút."""
    if "const LEGEND = [];" not in html:
        return html
    info: dict = {}
    for n in vis_nodes:
        c = n["community"]
        e = info.setdefault(c, {"cid": c, "color": (n.get("color") or {}).get("background", "#888888"), "label": n.get("community_name") or f"Community {c}", "count": 0})
        e["count"] += 1
    legend = json.dumps([info[c] for c in sorted(info)], ensure_ascii=False).replace("<", "\u003c")
    return html.replace("const LEGEND = [];", "const LEGEND = " + legend + ";", 1)


def apply_regions(html: str, G, communities, community_labels, vis_nodes: list[dict], output_path: str) -> str:
    """Điểm vào: trả về HTML đã vẽ bản đồ vùng, hoặc HTML nguyên bản nếu tắt / không vẽ được (in một dòng lý do)."""
    root = _project_root(output_path)
    cfg = zoning.load_config(root)
    if cfg.get("mode", "").lower() == "off":
        return html
    try:
        order = [n["id"] for n in vis_nodes]
        nodes = {}
        for n in vis_nodes:
            attrs = dict(G.nodes[n["id"]]) if n["id"] in G else {}
            attrs.update({"label": n["label"], "community": n["community"], "community_name": n["community_name"],
                          "source_file": n["source_file"] or attrs.get("source_file", ""), "file_type": n["file_type"] or attrs.get("file_type", "")})
            nodes[n["id"]] = attrs
        sizes = {n["id"]: float(n["size"]) for n in vis_nodes}
        edges = [(d.get("_src", u), d.get("_tgt", v), d.get("relation", "")) for u, v, d in G.edges(data=True)]
        z = pick_zoning(root, cfg, nodes, [(a, b) for a, b, _ in edges])
        if cfg.get("center"):
            z.centers = [c.strip() for c in cfg["center"].split(",") if c.strip()]
        data, bot = build_layout(nodes, order, edges, sizes, z)
        html = inject.apply_patch(html, data)
        html = _fill_empty_legend(html, vis_nodes)
        try:
            (Path(output_path).parent / "graph_regions.json").write_text(
                json.dumps(bot, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        except OSError:
            pass
        _say(f"[graphify regions] bản đồ vùng ({z.how}): {len(data['regions'])} vùng, {len(data['groups'])} nhóm cộng đồng")
        return html
    except RegionsSkip as exc:
        _say(f"[graphify regions] bỏ qua: {exc}")
        return html


def _say(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode())
    except Exception:
        pass
