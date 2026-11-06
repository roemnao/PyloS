"""Bố cục bản đồ vùng: loại nút, xếp nút không đè, lãnh thổ có biên, vị trí vùng (chuyển từ PyloS region_map.py)."""

from __future__ import annotations

import math
from collections import Counter

KINDS = ["function", "class", "module", "symbol", "external", "document", "rationale", "concept"]


def kind_of(node: dict) -> str:
    """Loại code của một nút graphify (đọc từ graph.json). Không đổi giữa các lần dựng lại, khác với cộng đồng."""
    ftype = node.get("file_type")
    if node.get("type") == "external" or not node.get("source_file"):
        return "external"
    if node.get("_callable_class"):  # lớp cũng có _callable: xét lớp trước
        return "class"
    if node.get("_callable"):
        return "function"
    if ftype == "code":
        label = str(node.get("label") or "")
        return "module" if node.get("type") == "package" or label.endswith((".py", ".js")) else "symbol"
    if ftype == "document":
        return "document"
    if ftype == "rationale":
        return "rationale"
    if ftype == "concept":
        return "concept"
    return "symbol"


CITY_GAP = 24.0
SCAN_STEP = 8.0


def _outer_rows(out: dict, r: dict, outer: list[str], gap: float) -> None:
    """Ngoại thành: hàng ngang ngay dưới cụm nội thành, xuống dòng khi dài hơn cụm. Ghi thêm vào `out`."""
    x0 = min(p[0] - p[2] for p in out.values()); x1 = max(p[0] + p[2] for p in out.values())
    y = max(p[1] + p[2] for p in out.values()) + gap
    limit = max(x1 - x0, 2 * max(r[i] for i in outer)) * 1.25
    rows, cur, cw = [], [], 0.0
    for i in outer:
        wd = 2 * r[i] + gap
        if cur and cw + wd > limit:
            rows.append(cur); cur, cw = [], 0.0
        cur.append(i); cw += wd
    rows.append(cur)
    mid = (x0 + x1) / 2
    for row in rows:
        rh = max(r[i] for i in row)
        wd = sum(2 * r[i] + gap for i in row) - gap
        x = mid - wd / 2
        for i in row:
            out[i] = (x + r[i], y + rh, r[i]); x += 2 * r[i] + gap
        y += 2 * rh + gap


def sector_order(groups: list[str], aff: dict[tuple[str, str], float], to_center: dict[str, float]) -> list[str]:
    """Thứ tự các khu quanh vòng: bắt đầu từ khu nối trung tâm nhiều nhất, rồi lần lượt khu nối nhiều nhất với khu vừa xếp."""
    left = sorted(groups)
    order = [max(left, key=lambda g: (to_center.get(g, 0.0), g))]
    left.remove(order[0])
    while left:
        nxt = max(left, key=lambda g: (aff.get((order[-1], g), 0.0), -left.index(g)))
        order.append(nxt); left.remove(nxt)
    return order


def plan_rings(radius: dict[str, float], center: str, rings: list[list[str]], group: dict[str, str],
               w: dict[tuple[str, str], float], outer: list[str], gap: float = CITY_GAP) -> dict[str, tuple[float, float, float]]:
    """Xếp vùng theo vòng vây: `center` ở (0, 0); `rings[k-1]` là các vùng vòng k. Mỗi khu có một quạt góc,
    vùng nào ở vòng nào cũng nằm trong quạt của khu mình; sau đó ép từng vùng tiến về tâm theo bán kính tới khi chạm
    vùng khác nhưng không vào trong vòng trước. `outer` xếp hàng ngang dưới cụm. Trả về id -> (x, y, bán kính)."""
    r = {i: radius.get(i, 30.0) for i in [center, *[x for ring in rings for x in ring], *outer]}
    ring_of = {x: k + 1 for k, ring in enumerate(rings) for x in ring}
    members = [x for ring in rings for x in ring]
    out: dict[str, tuple[float, float, float]] = {center: (0.0, 0.0, r[center])}
    if members:
        by_group: dict[str, list[str]] = {}
        for x in members:
            by_group.setdefault(group.get(x, x), []).append(x)
        aff: dict[tuple[str, str], float] = {}
        for (a, b), wt in w.items():
            ga, gb = group.get(a, a), group.get(b, b)
            if ga != gb and a in ring_of and b in ring_of:
                aff[(ga, gb)] = aff.get((ga, gb), 0.0) + wt
        to_center = {g: sum(w.get((center, x), 0.0) for x in xs) for g, xs in by_group.items()}
        gorder = sector_order(list(by_group), aff, to_center)
        width = {g: sum(2 * r[x] + gap for x in by_group[g]) for g in gorder}
        total = sum(width.values())
        # bán kính xuất phát của từng vòng: ngoài vòng trước + hở + vùng lớn nhất của vòng này
        start, reach = {}, r[center]
        for k, ring in enumerate(rings, 1):
            start[k] = max(reach + gap + max(r[x] for x in ring), 0.0)
            reach = start[k] + max(r[x] for x in ring)
        # góc: khu đầu tiên có góc giữa ở hướng trên (-90 độ), các khu sau theo chiều kim đồng hồ
        ang = -math.pi / 2 - width[gorder[0]] / total * math.pi
        angle: dict[str, float] = {}
        for g in gorder:
            share = width[g] / total * 2 * math.pi
            slots = sorted(by_group[g], key=lambda x: (ring_of[x], -w.get((center, x), 0.0), x))
            # vòng thấp ở giữa quạt, vòng cao ra hai mép: xen kẽ phải/trái
            seq = slots[0::2][::-1] + slots[1::2]
            tw = sum(2 * r[x] + gap for x in seq)
            a0 = ang
            for x in seq:
                span = (2 * r[x] + gap) / tw * share
                angle[x] = a0 + span / 2; a0 += span
            ang += share
        # ép theo bán kính, từ vòng 1 ra ngoài
        dist: dict[str, float] = {}
        for k, ring in enumerate(rings, 1):
            for x in sorted(ring, key=lambda x: (start[k], x)):
                lb = r[center] + r[x] + gap
                prev = [dist[y] for y in rings[k - 2] if group.get(y, y) == group.get(x, x)] if k > 1 else []
                if prev:
                    lb = max(lb, max(prev) + 1.0)
                ux, uy = math.cos(angle[x]), math.sin(angle[x])
                d = lb
                while d < start[k]:
                    px, py = d * ux, d * uy
                    if all(math.hypot(px - o[0], py - o[1]) >= r[x] + o[2] + gap for o in out.values()):
                        break
                    d += SCAN_STEP
                d = min(d, start[k])
                dist[x] = d
                out[x] = (d * ux, d * uy, r[x])
        # còn đè (do quạt hẹp): đẩy vùng xa tâm hơn ra theo bán kính
        ids = [x for x in out if x != center]
        for _ in range(300):
            moved = False
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    (ax, ay, ar), (bx, by, br) = out[a], out[b]
                    if math.hypot(ax - bx, ay - by) >= ar + br + gap - 0.5:
                        continue
                    far = b if math.hypot(bx, by) >= math.hypot(ax, ay) else a
                    fx, fy, fr = out[far]
                    n = math.hypot(fx, fy) or 1.0
                    out[far] = (fx + fx / n * 6.0, fy + fy / n * 6.0, fr)
                    moved = True
            if not moved:
                break
    if outer:
        _outer_rows(out, r, outer, gap)
    return out


GOLDEN = math.pi * (3 - math.sqrt(5))
BLOB_GAP = 6.0
PACK_DENSITY = 0.45
NODE_GAP = 5.0  # khoảng trống tối thiểu giữa hai nút




def _affinity(a: Counter, b: Counter) -> int:
    """Số nút "chung cộng đồng" của hai file."""
    if len(b) < len(a):
        a, b = b, a
    return sum(min(n, b[c]) for c, n in a.items() if c in b)


def order_files(files: list[list[int]], community) -> list[list[int]]:
    """Thứ tự đặt file: bắt đầu từ file nhiều nút nhất, rồi lần lượt file chung cộng đồng nhiều nhất với hai file vừa đặt.

    Hoà thì file nhiều nút hơn, rồi nút nhỏ nhất (id ổn định) để chạy hai lần ra cùng bố cục."""
    counts = [Counter(community(i) for i in f) for f in files]
    size_key = lambda k: (-len(files[k]), min(files[k]))
    left = sorted(range(len(files)), key=size_key)
    order = [left.pop(0)] if left else []
    while left:
        recent = order[-2:]
        best = max(left, key=lambda k: (sum(_affinity(counts[k], counts[j]) for j in recent), len(files[k]), -min(files[k])))
        left.remove(best)
        order.append(best)
    return [files[k] for k in order]


def _pack_file(f: list[int], degree, community, size) -> tuple[dict[int, tuple[float, float]], float]:
    """Xếp các nút của một file quanh gốc (0, 0): mỗi cộng đồng một múi, nút lớn/nối nhiều vào trước,
    nút nào đè lên nút đã đặt thì đẩy ra xa tâm cho tới khi hết đè. Trả về (vị trí, bán kính thật của cụm)."""
    by_comm: dict[int, list[int]] = {}
    for i in f:
        by_comm.setdefault(community(i), []).append(i)
    est = math.sqrt(sum((size(i) + NODE_GAP) ** 2 for i in f) / PACK_DENSITY)  # bán kính ước tính, chỉ để chia múi
    grid: dict[tuple[int, int], list[tuple[float, float, float]]] = {}
    cell = 100.0

    def free(x: float, y: float, s: float) -> bool:
        cx, cy = int(x // cell), int(y // cell)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for ox, oy, os_ in grid.get((cx + dx, cy + dy), ()):
                    if math.hypot(x - ox, y - oy) < s + os_ + NODE_GAP:
                        return False
        return True

    pos: dict[int, tuple[float, float]] = {}
    extent = 0.0
    angle = 0.0
    for cid in sorted(by_comm, key=lambda c: (-len(by_comm[c]), c)):  # múi lớn trước
        members = sorted(by_comm[cid], key=lambda i: (-degree(i), i))
        single = len(by_comm) == 1
        width = 2 * math.pi * len(members) / len(f)
        for k, i in enumerate(members):
            s = size(i)
            r = est * math.sqrt((k + 0.5) / len(members))
            a = k * GOLDEN if single else angle + width * ((k * 0.6180339887) % 1.0 * 0.84 + 0.08)
            for _ in range(600):
                x, y = r * math.cos(a), r * math.sin(a)
                if free(x, y, s):
                    break
                r += 3.0
            grid.setdefault((int(x // cell), int(y // cell)), []).append((x, y, s))
            pos[i] = (x, y)
            extent = max(extent, math.hypot(x, y) + s)
        angle += width
    return pos, extent + 2.0


def pack_region(files: list[list[int]], degree, community=None, size=None) -> tuple[dict[int, tuple[float, float]], float]:
    """Xếp các file của một toà (mỗi file là danh sách nút): file thành cụm tròn, file chung cộng đồng đứng cạnh nhau.

    Trả về (vị trí tương đối của từng nút, bán kính cả vùng). Nút giữ kích thước thật của graphify nên không đè nhau."""
    community = community or (lambda i: 0)
    size = size or (lambda i: 10.0)
    files = order_files(files, community)
    counts = [Counter(community(i) for i in f) for f in files]
    local = [_pack_file(f, degree, community, size) for f in files]
    blobs = [rad for _, rad in local]
    centers: list[tuple[float, float]] = []
    for k, rf in enumerate(blobs):
        if k == 0:
            centers.append((0.0, 0.0)); continue
        free = lambda c: all(math.hypot(c[0] - o[0], c[1] - o[1]) >= rf + blobs[j] + BLOB_GAP for j, o in enumerate(centers))
        # điểm mong muốn: trung bình (theo độ chung cộng đồng) vị trí các file đã đặt; không chung gì thì về tâm
        aff = [_affinity(counts[k], counts[j]) for j in range(k)]
        total = sum(aff)
        tx = sum(a * centers[j][0] for j, a in enumerate(aff)) / total if total else 0.0
        ty = sum(a * centers[j][1] for j, a in enumerate(aff)) / total if total else 0.0
        near = sorted(range(k), key=lambda j: (-aff[j], j))[:3] + [k - 1]
        best, best_d = None, 0.0
        for j in dict.fromkeys(near):
            ring = rf + blobs[j] + BLOB_GAP + 0.5
            for s in range(28):
                ang = s * 2 * math.pi / 28
                c = (centers[j][0] + ring * math.cos(ang), centers[j][1] + ring * math.sin(ang))
                d = math.hypot(c[0] - tx, c[1] - ty)
                if (best is None or d < best_d) and free(c):
                    best, best_d = c, d
        if best is None:  # không có chỗ quanh các file gần: xoắn ốc từ tâm ra
            ang, r = 0.0, blobs[0]
            while True:
                c = (r * math.cos(ang), r * math.sin(ang))
                if free(c):
                    best = c; break
                ang += 0.35
                r += 0.35 * 6.0 / (2 * math.pi) * 6.0
        centers.append(best)
    pos: dict[int, tuple[float, float]] = {}
    for (lp, _), (cx, cy) in zip(local, centers):
        for i, (x, y) in lp.items():
            pos[i] = (cx + x, cy + y)
    extent = max((math.hypot(cx, cy) + rf) for (cx, cy), rf in zip(centers, blobs))
    return pos, extent + 22.0


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    def half(seq):
        out: list[tuple[float, float]] = []
        for q in seq:
            while len(out) >= 2 and cross(out[-2], out[-1], q) <= 0:
                out.pop()
            out.append(q)
        return out[:-1]
    return half(pts) + half(pts[::-1])


BORDER_MARGIN = 22.0  # biên cách nút ngoài cùng một khoảng nhỏ


def region_polygons(plan: dict[str, tuple[float, float, float]], nodes: dict[str, list[tuple[float, float, float]]] | None = None,
                    pad: float = 80.0, sides: int = 72) -> dict[str, list[list[int]]]:
    """Lãnh thổ từng toà: bao lồi của các nút (cộng một khoảng nhỏ BORDER_MARGIN) cắt bởi biểu đồ Voronoi có trọng số.

    Biên ôm sát nút ngoài cùng; hai toà gần nhau chung một đường biên thẳng như hai nước. Toà không có nút: vòng tròn."""
    out = {}
    for rid, (cx, cy, r) in plan.items():
        spots = (nodes or {}).get(rid) or []
        if spots:
            ring = [(x + (s + BORDER_MARGIN) * math.cos(k * math.pi / 6), y + (s + BORDER_MARGIN) * math.sin(k * math.pi / 6))
                    for x, y, s in spots for k in range(12)]
            poly = convex_hull(ring)
        else:
            poly = [(cx + (r + pad) * math.cos(2 * math.pi * k / sides), cy + (r + pad) * math.sin(2 * math.pi * k / sides)) for k in range(sides)]
        for oid, (ox, oy, orr) in plan.items():
            if oid == rid:
                continue
            # giữ phía gần toà này hơn: 2 p.(o - c) <= |o|^2 - |c|^2 - orr^2 + r^2
            nx, ny, lim = 2 * (ox - cx), 2 * (oy - cy), ox * ox + oy * oy - cx * cx - cy * cy - orr * orr + r * r
            clipped = []
            for a, b in zip(poly, poly[1:] + poly[:1]):
                da, db = nx * a[0] + ny * a[1] - lim, nx * b[0] + ny * b[1] - lim
                if da <= 0:
                    clipped.append(a)
                if (da <= 0) != (db <= 0):
                    t = da / (da - db)
                    clipped.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            poly = clipped
        out[rid] = [[round(x), round(y)] for x, y in poly]
    return out
