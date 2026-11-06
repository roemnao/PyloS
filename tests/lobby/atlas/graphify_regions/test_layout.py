import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file()) / "src" / "pylos" / "lobby" / "atlas" / "graphify_regions"))
import math

import pytest

from regions import layout as rm


def _city():
    """c là trung tâm; ba khu: A (a1 vòng 1, a2 vòng 2), B (b1 vòng 1, b2 vòng 2), C (c1 vòng 1)."""
    group = {"c": "G0", "a1": "A", "a2": "A", "b1": "B", "b2": "B", "c1": "C"}
    rings = [["a1", "b1", "c1"], ["a2", "b2"]]
    edges = {("c", "a1"): 30, ("c", "b1"): 20, ("c", "c1"): 10, ("a1", "a2"): 8, ("b1", "b2"): 6, ("a1", "b1"): 3}
    w = {}
    for (x, y), n in edges.items():
        w[(x, y)] = w[(y, x)] = float(n)
    radius = {k: 150.0 for k in group}
    return radius, group, rings, w


def _dist(plan, i):
    return math.hypot(plan[i][0], plan[i][1])


def test_plan_rings_puts_the_center_at_the_origin_without_overlap():
    radius, group, rings, w = _city()
    plan = rm.plan_rings(radius, "c", rings, group, w, [])
    assert plan["c"][:2] == (0.0, 0.0)
    ids = list(plan)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            (ax, ay, ar), (bx, by, br) = plan[a], plan[b]
            assert math.hypot(ax - bx, ay - by) >= ar + br


def test_plan_rings_keeps_the_ring_order_inside_each_zone_and_zone_in_one_sector():
    radius, group, rings, w = _city()
    plan = rm.plan_rings(radius, "c", rings, group, w, [])
    assert _dist(plan, "a2") > _dist(plan, "a1") and _dist(plan, "b2") > _dist(plan, "b1")
    ang = lambda i: math.atan2(plan[i][1], plan[i][0])
    gap = lambda a, b: abs((ang(a) - ang(b) + math.pi) % (2 * math.pi) - math.pi)
    assert gap("a1", "a2") < gap("a1", "b2") and gap("b1", "b2") <= gap("b1", "a2") + 1e-9  # cùng khu thì cùng hướng


def test_plan_rings_is_compact_connected_regions_touch():
    radius, group, rings, w = _city()
    plan = rm.plan_rings(radius, "c", rings, group, w, [])
    assert _dist(plan, "a1") <= 150.0 * 2 + 2 * rm.CITY_GAP + 1  # vòng 1 chạm trung tâm


def test_plan_rings_puts_outer_regions_in_rows_below_the_inner_ones():
    radius, group, rings, w = _city()
    radius.update({"o1": 100.0, "o2": 100.0})
    plan = rm.plan_rings(radius, "c", rings, group, w, ["o1", "o2"])
    low = max(plan[i][1] + plan[i][2] for i in group)
    assert all(plan[o][1] - plan[o][2] >= low for o in ("o1", "o2"))


@pytest.mark.parametrize("node,kind", [
    ({"source_file": "a.py", "_callable": True, "_callable_class": True, "file_type": "code"}, "class"),
    ({"source_file": "a.py", "_callable": True, "file_type": "code"}, "function"),
    ({"source_file": "a.py", "label": "a.py", "file_type": "code"}, "module"),
    ({"source_file": "a.py", "label": "Path", "file_type": "code"}, "symbol"),
    ({"source_file": "a.md", "file_type": "document"}, "document"),
    ({"source_file": "a.py", "file_type": "rationale"}, "rationale"),
    ({"source_file": "a.md", "file_type": "concept"}, "concept"),
    ({"source_file": "a.py", "type": "external", "file_type": "concept"}, "external"),
    ({"file_type": "code"}, "external"),
])
def test_kind_of(node, kind):
    assert rm.kind_of(node) == kind
    assert kind in rm.KINDS


def test_pack_region_gives_every_node_its_own_spot_inside_the_radius():
    files = [[0, 1, 2, 3, 4], [5, 6], [7]]
    pos, radius = rm.pack_region(files, lambda i: 10 - i)
    assert set(pos) == set(range(8)) and len(set(pos.values())) == 8
    assert all(math.hypot(x, y) <= radius for x, y in pos.values())


def _center(pos, ids):
    return (sum(pos[i][0] for i in ids) / len(ids), sum(pos[i][1] for i in ids) / len(ids))


def test_files_sharing_a_community_sit_next_to_each_other():
    A, B, C, D = list(range(0, 8)), list(range(8, 14)), list(range(14, 24)), list(range(24, 28))
    comm = lambda i: 1 if i < 14 else (2 if i < 24 else 3)
    pos, _ = rm.pack_region([A, B, C, D], lambda i: 1, comm)
    dist = lambda x, y: math.dist(_center(pos, x), _center(pos, y))
    assert dist(A, B) < dist(A, D) and dist(A, B) < dist(B, D)


def test_pack_region_is_deterministic():
    files = [list(range(0, 5)), list(range(5, 9)), list(range(9, 12))]
    comm = lambda i: i % 3
    assert rm.pack_region(files, lambda i: i % 4, comm) == rm.pack_region(files, lambda i: i % 4, comm)


def test_packed_nodes_do_not_overlap_at_their_real_size():
    files = [list(range(0, 30)), list(range(30, 50))]
    size = lambda i: 10.0 + (i % 7) * 4
    pos, _ = rm.pack_region(files, lambda i: i % 5, lambda i: i % 3, size)
    ids = list(pos)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            assert math.dist(pos[ids[a]], pos[ids[b]]) >= size(ids[a]) + size(ids[b]), (ids[a], ids[b])


def test_territory_hugs_the_outermost_nodes():
    ids = [f"r{i}" for i in range(4)]
    plan = rm.plan_rings({k: 300.0 for k in ids}, "r0", [ids[1:]], {}, {}, [])
    cx, cy = plan["r1"][0], plan["r1"][1]
    spots = {"r1": [(cx + dx, cy, 12.0) for dx in (-200, -100, 0, 100, 200)]}
    poly = rm.region_polygons(plan, spots)["r1"]
    xs = [p[0] for p in poly]
    assert max(xs) - cx >= 200 + 12 and max(xs) - cx <= 200 + 12 + rm.BORDER_MARGIN + 2


def test_territories_share_borders_when_regions_are_close():
    plan = rm.plan_rings({"a": 150.0, "b": 150.0}, "a", [["b"]], {}, {("a", "b"): 5.0, ("b", "a"): 5.0}, [])
    polys = rm.region_polygons(plan)
    assert len(polys["a"]) < 72 and len(polys["b"]) < 72  # mỗi bên bị cắt thẳng bởi bên kia
