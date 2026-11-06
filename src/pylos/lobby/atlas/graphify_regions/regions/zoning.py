"""Chia nút thành vùng: theo file phân vùng, theo thư mục, hoặc theo cộng đồng graphify. Màu và vị trí tự tính khi thiếu."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .inject import RegionsSkip

STRUCT = {"contains", "method", "rationale_for"}
TEST_DIRS = {"tests", "test", "spec", "specs", "__tests__"}
MAX_REGIONS = 24
GREY = {"tests": 66, "root": 55, "other": 44, "external": 33}
UNPLACED_COLOR = (330, 50, 62)


@dataclass
class Zoning:
    regions: list[dict]  # {id, name, group, color?, pos?}
    groups: dict[str, dict]  # id -> {name, hue?}
    node_region: Callable[[str, dict], str]  # (id nút, thuộc tính) -> id vùng
    levels: dict = field(default_factory=lambda: {"group": "Nhóm", "region": "Vùng"})
    external: str = "(thư viện ngoài)"
    tests: str | None = None
    how: str = ""
    centers: list[str] = field(default_factory=list)  # ghi đè vùng trung tâm; rỗng = tự chọn theo đường nối


# ---------- cấu hình ----------

def load_config(root: Path) -> dict:
    """Đọc các khoá regions.* trong <root>/.graphifyrc (graphify bỏ qua khoá lạ nên không xung đột)."""
    cfg: dict = {}
    rc = Path(root) / ".graphifyrc"
    if not rc.is_file():
        return cfg
    for raw in rc.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = (x.strip() for x in line.split("=", 1))
        if key.startswith("regions."):
            cfg[key[len("regions."):]] = val
    return cfg


def norm(path: str) -> str:
    return str(path).replace("\\", "/").removeprefix("./") if path else ""


def is_test_path(path: str) -> bool:
    parts = path.split("/")
    name = parts[-1].lower()
    return any(p.lower() in TEST_DIRS for p in parts[:-1]) or name.startswith("test_") or ".spec." in name or ".test." in name \
        or name.rsplit(".", 1)[0].endswith("_test")


# ---------- 1. file phân vùng ----------

def from_file(path: Path) -> Zoning:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise RegionsSkip(f"không đọc được file phân vùng {path}: {exc}")
    if data.get("version") != 1 or "regions" not in data or not (data.get("files") or data.get("rules")):
        raise RegionsSkip(f"file phân vùng {path}: cần version=1, regions và files hoặc rules")
    regions = [dict(r) for r in data["regions"]]
    ids = {r["id"] for r in regions}
    rules = sorted(({"prefix": norm(r["prefix"]), "region": r["region"]} for r in data.get("rules", [])), key=lambda r: -len(r["prefix"]))
    bad = sorted({v for v in [*(data.get("files") or {}).values(), *(r["region"] for r in rules)] if v not in ids})
    if bad:
        raise RegionsSkip(f"file phân vùng {path}: vùng lạ {bad[:3]}")
    files = {norm(k): v for k, v in (data.get("files") or {}).items()}
    unplaced = data.get("unplaced_region") or "(chưa xếp)"
    external = data.get("external_region") or "(thư viện ngoài)"
    for rid, name in ((unplaced, "Chưa xếp"), (external, "Thư viện ngoài")):
        if rid not in ids:
            regions.append({"id": rid, "name": name, "group": "ngoài"})
            ids.add(rid)
    groups = {g["id"]: dict(g) for g in data.get("groups", [])}
    for r in regions:
        r.setdefault("group", r["id"].split("/")[0] if "/" in r["id"] else r["id"])
        r.setdefault("name", r["id"])

    def node_region(nid: str, attrs: dict) -> str:
        f = norm(attrs.get("source_file"))
        if not f:
            return external
        if f in files:
            return files[f]
        for r in rules:  # luật theo tiền tố đường dẫn: tiền tố dài nhất thắng
            if f.startswith(r["prefix"]):
                return r["region"]
        return unplaced

    return Zoning(regions, groups, node_region, data.get("levels") or {"group": "Nhóm", "region": "Vùng"},
                  external, data.get("tests_region"), "file phân vùng", list(data.get("center") or []))


# ---------- 2. theo thư mục ----------

def _common_dirs(paths: list[str]) -> list[str]:
    dirs = [p.split("/")[:-1] for p in paths]
    dirs = [d for d in dirs if d]
    if not dirs:
        return []
    out = dirs[0]
    for d in dirs[1:]:
        k = 0
        while k < len(out) and k < len(d) and out[k] == d[k]:
            k += 1
        out = out[:k]
    return out


def by_folder(files: set[str], depth: int = 2) -> Zoning | None:
    """Vùng = `depth` cấp thư mục đầu (sau khi bỏ tiền tố chung). None nếu dự án phẳng (chỉ ra một vùng)."""
    files = {norm(f) for f in files if f}
    code = [f for f in files if not is_test_path(f)]
    strip = len(_common_dirs(code))
    if strip and all(len(f.split("/")[:-1]) <= strip for f in code):
        strip = max(0, strip - 1)  # mọi file nằm cùng một thư mục: giữ lại cấp cuối làm tên

    def region(f: str, d: int) -> tuple[str, str]:
        if is_test_path(f):
            return "tests", "ngoài"
        parts = f.split("/")[:-1][strip:]
        if not parts:
            return "(gốc)", "ngoài"
        return "/".join(parts[:d]), parts[0]

    while depth >= 1:
        mapping = {f: region(f, depth) for f in files}
        ids = {r for r, _ in mapping.values()}
        if len(ids) <= MAX_REGIONS:
            break
        depth -= 1
    else:
        mapping = {f: region(f, 1) for f in files}
    real = {r for r, g in mapping.values() if g != "ngoài"}
    if len(real) < 2:
        return None
    groups: dict[str, dict] = {}
    regions: dict[str, dict] = {}
    for rid, grp in set(mapping.values()):
        groups.setdefault(grp, {"id": grp, "name": grp})
        regions[rid] = {"id": rid, "name": rid.split("/")[-1] if rid not in ("tests", "(gốc)") else {"tests": "Test", "(gốc)": "Gốc dự án"}[rid],
                        "group": grp}
    regions["(thư viện ngoài)"] = {"id": "(thư viện ngoài)", "name": "Thư viện ngoài", "group": "ngoài"}
    groups["ngoài"] = {"id": "ngoài", "name": "Ngoài dự án"}
    file_region = {f: r for f, (r, _) in mapping.items()}

    def node_region(nid: str, attrs: dict) -> str:
        f = norm(attrs.get("source_file"))
        return file_region.get(f, "(thư viện ngoài)") if f else "(thư viện ngoài)"

    return Zoning(list(regions.values()), groups, node_region, {"group": "Thư mục", "region": "Vùng"},
                  "(thư viện ngoài)", "tests", f"thư mục, depth {depth}")


# ---------- 3. theo cộng đồng ----------

def by_community(nodes: dict[str, dict], edges: list[tuple[str, str]], max_regions: int = 12) -> Zoning:
    """Dự án phẳng: gộp các cộng đồng graphify thành tối đa `max_regions` vùng (nhóm 1–2 nút vào "(lẻ)")."""
    comm = {nid: a.get("community") for nid, a in nodes.items() if a.get("source_file")}
    size = Counter(comm.values())
    clusters: dict[int, set] = {c: {c} for c, n in size.items() if n >= 3}
    cluster_of = {c: c for c in clusters}
    weight: Counter = Counter()
    for u, v in edges:
        cu, cv = comm.get(u), comm.get(v)
        if cu in clusters and cv in clusters and cu != cv:
            weight[tuple(sorted((cu, cv)))] += 1
    csize = {c: size[c] for c in clusters}
    while len(clusters) > max(1, max_regions - 1) and weight:
        (a, b), _ = max(weight.items(), key=lambda kv: (kv[1] / math.sqrt(csize[kv[0][0]] * csize[kv[0][1]]), -kv[0][0]))
        clusters[a] |= clusters.pop(b)
        csize[a] += csize.pop(b)
        for k in list(weight):
            if b in k:
                w = weight.pop(k)
                other = k[0] if k[1] == b else k[1]
                if other != a:
                    weight[tuple(sorted((a, other)))] += w
        weight.pop((a, b), None)
    while len(clusters) > max(1, max_regions - 1):  # còn dư mà không có đường nối: gộp nhỏ nhất vào lớn nhất
        small = min(clusters, key=lambda c: csize[c]); big = max((c for c in clusters if c != small), key=lambda c: csize[c])
        clusters[big] |= clusters.pop(small); csize[big] += csize.pop(small)
    for k, members in clusters.items():
        for c in members:
            cluster_of[c] = k
    deg: Counter = Counter()
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    regions = []
    for k, members in sorted(clusters.items(), key=lambda kv: -csize[kv[0]]):
        ids = [nid for nid, c in comm.items() if cluster_of.get(c) == k]
        top = max(ids, key=lambda i: (deg[i], i)) if ids else ""
        regions.append({"id": f"c{k}", "name": str(nodes.get(top, {}).get("label") or f"nhóm {k}"), "group": "cộng đồng"})
    regions.append({"id": "(lẻ)", "name": "Nhóm lẻ", "group": "cộng đồng"})
    regions.append({"id": "(thư viện ngoài)", "name": "Thư viện ngoài", "group": "ngoài"})
    groups = {"cộng đồng": {"id": "cộng đồng", "name": "Cộng đồng graphify"}, "ngoài": {"id": "ngoài", "name": "Ngoài dự án"}}

    def node_region(nid: str, attrs: dict) -> str:
        if not attrs.get("source_file"):
            return "(thư viện ngoài)"
        k = cluster_of.get(attrs.get("community"))
        return f"c{k}" if k is not None else "(lẻ)"

    return Zoning(regions, groups, node_region, {"group": "Nhóm", "region": "Vùng"}, "(thư viện ngoài)", None, "cộng đồng graphify")


# ---------- trung tâm, màu và vị trí tự động ----------

RING_SHARE = 0.15  # vùng vào vòng k+1 nếu nối vào vòng 0..k bằng ít nhất 15% của vùng nối nhiều nhất
# Luật tô màu (vòng vây):
#   1. Trung tâm và vòng 1 lấy màu NÓNG: trung tâm đỏ, vòng 1 lần lượt cam vàng, hồng, vàng nghệ, cam đỏ, hồng đậm...
#      (tách hai phía của đỏ để các toà vòng 1 khác hẳn nhau mà vẫn nóng).
#   2. Vòng 2 trở ra lấy màu LẠNH theo thứ tự vòng: xanh ngọc -> xanh lam -> chàm -> tím.
#   3. Bỏ dải vàng chanh / xanh lá (60-150°): bẩn trên nền tối, thành nâu ô liu trên nền sáng.
#   4. Màu đậm (bão hoà 85%); hai toà liên tiếp lệch độ sáng xen kẽ (+10); hai toà bất kỳ khác >=15° hoặc >=8% sáng.
#   5. Độ sáng lưu ở đây là cho nền tối; trang tự đưa về khoảng an toàn khi nền sáng (không thành nâu/đen).
WARM_SEQ = (2, 25, 340, 46, 14, 328, 36, 316, 8)
COOL_PATH = (170, 184, 198, 212, 226, 240, 254, 268, 282, 296)
SAT = 85
L_BASE, L_STEP = 56, 10


def is_outer(z: Zoning, r: dict) -> bool:
    """Vùng ngoại thành: thư viện ngoài, test, chưa xếp, nhóm 'ngoài', hoặc vùng được ghim vị trí tay (`pos`)."""
    return r["id"] in (z.external, z.tests) or r.get("group") == "ngoài" or bool(r.get("pos"))


def symmetric(flows: Counter) -> dict[tuple[str, str], float]:
    w: dict[tuple[str, str], float] = defaultdict(float)
    for (a, b), n in flows.items():
        w[(a, b)] += n; w[(b, a)] += n
    return w


def pick_center(ids: list[str], stats: dict[str, dict], override: list[str] | None = None) -> str:
    """Đúng một vùng trung tâm. Ghi đè thì lấy vùng đầu hợp lệ; không thì điểm = luồng + số nút + nút lớn nhất,
    mỗi thứ chia cho giá trị lớn nhất (bằng trọng số). Hoà thì luồng lớn hơn, rồi id."""
    for c in override or []:
        if c in ids:
            return c
    mx = {k: max((stats[i][k] for i in ids), default=0) or 1 for k in ("flow", "nodes", "top")}
    score = lambda i: sum(stats[i][k] / mx[k] for k in mx)
    return max(ids, key=lambda i: (round(score(i), 9), stats[i]["flow"], -ids.index(i)))


def assign_rings(ids: list[str], center: str, w: dict[tuple[str, str], float]) -> list[list[str]]:
    """Vòng 1, 2, ... (không gồm trung tâm). Vòng k+1 = vùng chưa xếp có đường nối vào vòng 0..k >= RING_SHARE * (nối nhiều nhất);
    vùng không có đường nối nào vào các vòng trước thì vào vòng cuối. Trong vòng: nối vào vòng ngay trước nhiều trước."""
    placed = {center}
    last = [center]
    left = [i for i in ids if i != center]
    rings: list[list[str]] = []
    while left:
        link = {x: sum(w.get((x, y), 0.0) for y in placed) for x in left}
        top = max(link.values())
        if top <= 0:
            ring = sorted(left)
        else:
            ring = [x for x in left if link[x] >= max(1.0, RING_SHARE * top)]
            ring.sort(key=lambda x: (-sum(w.get((x, y), 0.0) for y in last), -link[x], x))
        rings.append(ring)
        placed |= set(ring); last = ring
        left = [x for x in left if x not in placed]
    return rings


def sample(path: tuple[int, ...], n: int) -> list[int]:
    """n hue lấy đều trên `path` (giữ hai đầu); nhiều hơn số mốc thì nội suy giữa hai mốc kề nhau."""
    if n <= 0:
        return []
    if n == 1:
        return [path[0]]
    last = len(path) - 1
    out = []
    for i in range(n):
        t = i * last / (n - 1)
        k = min(int(t), last - 1)
        out.append(round(path[k] + (path[k + 1] - path[k]) * (t - k)))
    return out


def ring_hues(rings: list[list[str]]) -> list[int]:
    """Hue cho từng toà theo thứ tự vòng: vòng 0 và 1 lấy WARM_SEQ, các vòng sau lấy đều trên COOL_PATH."""
    warm_n = sum(len(r) for r in rings[:2])
    cool_n = sum(len(r) for r in rings[2:])
    warm = [WARM_SEQ[i % len(WARM_SEQ)] for i in range(warm_n)]
    return warm + sample(COOL_PATH, cool_n)


def auto_colors(z: Zoning, rings: list[list[str]] | None = None) -> dict[str, tuple[int, int, int]]:
    """Màu theo vòng (xem luật ở WARM_SEQ / COOL_PATH): `rings[0]` là trung tâm. Vùng có `color` giữ nguyên; ngoại thành xám."""
    colors: dict[str, tuple[int, int, int]] = {}
    for r in z.regions:
        if r.get("color"):
            colors[r["id"]] = tuple(r["color"])
    if rings is None:
        rings = [[r["id"]] for r in z.regions if not is_outer(z, r) and r["id"] not in colors]
    rings = [[i for i in ring if i not in colors] for ring in rings]
    todo = [i for ring in rings for i in ring]
    placed: list[tuple[int, int]] = []
    for j, (rid, hue) in enumerate(zip(todo, ring_hues(rings))):
        light = L_BASE + (L_STEP if j % 2 else 0)
        for _ in range(4):  # trùng một vùng đã tô (hue gần và sáng gần) thì đổi độ sáng
            if all(min(abs(hue - h), 360 - abs(hue - h)) >= 15 or abs(light - l) >= 8 for h, l in placed):
                break
            light = light - 8 if light > L_BASE else light + 18
        placed.append((hue, light))
        colors[rid] = (hue, SAT, light)
    n_out = 0
    for r in z.regions:
        rid = r["id"]
        if rid in colors:
            continue
        if rid == z.external:
            colors[rid] = (0, 0, GREY["external"])
        elif rid == z.tests:
            colors[rid] = (0, 0, GREY["tests"])
        else:
            colors[rid] = (0, 0, GREY["root"] if n_out % 2 == 0 else GREY["other"]); n_out += 1
    return colors
