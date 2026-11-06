import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file()) / "src" / "pylos" / "lobby" / "atlas" / "graphify_regions"))
import json
from collections import Counter

import pytest

from regions import zoning
from regions.inject import RegionsSkip


def test_folder_zoning_strips_the_common_prefix_and_splits_tests():
    files = {"src/app/api/a.py", "src/app/api/b.py", "src/app/db/c.py", "src/app/ui/d.py", "src/app/ui/x/e.py", "tests/test_a.py"}
    z = zoning.by_folder(files, 2)
    ids = {r["id"] for r in z.regions}
    assert {"api", "db", "ui", "ui/x", "tests"} <= ids
    assert z.node_region("n", {"source_file": "src/app/db/c.py"}) == "db"
    assert z.node_region("n", {"source_file": "tests/test_a.py"}) == "tests"
    assert z.node_region("n", {}) == z.external


def test_folder_zoning_returns_none_for_a_flat_project():
    assert zoning.by_folder({"app/a.py", "app/b.py", "app/c.py"}, 2) is None


def test_folder_zoning_lowers_the_depth_when_there_are_too_many_regions():
    files = {f"p/g{i}/h{j}/f.py" for i in range(8) for j in range(5)}
    z = zoning.by_folder(files, 3)
    assert len([r for r in z.regions if r["group"] != "ngoài"]) <= zoning.MAX_REGIONS


def test_community_zoning_has_at_most_twelve_regions_and_named_regions():
    nodes, edges = {}, []
    for c in range(30):
        for k in range(4):
            nodes[f"{c}_{k}"] = {"community": c, "source_file": f"f{c}.py", "label": f"fn{c}_{k}"}
            if k:
                edges.append((f"{c}_0", f"{c}_{k}"))
        if c:
            edges.append((f"{c}_0", f"{c - 1}_0"))
    nodes["lone"] = {"community": 99, "source_file": "z.py", "label": "lone"}
    nodes["ext"] = {"community": 98, "label": "os"}
    z = zoning.by_community(nodes, edges, 12)
    real = [r for r in z.regions if r["group"] == "cộng đồng"]
    assert len(real) <= 12 + 1 and all(r["name"] for r in z.regions)
    assert z.node_region("lone", nodes["lone"]) == "(lẻ)"
    assert z.node_region("ext", nodes["ext"]) == z.external


def _file(tmp_path, **over):
    data = {"version": 1, "regions": [{"id": "a/x", "name": "X"}, {"id": "a/y"}], "files": {"src/one.py": "a/x", "src\\two.py": "a/y"}}
    data.update(over)
    p = tmp_path / "r.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_zoning_file_maps_files_and_adds_unplaced_and_external(tmp_path):
    z = zoning.from_file(_file(tmp_path))
    assert z.node_region("n", {"source_file": "src/one.py"}) == "a/x"
    assert z.node_region("n", {"source_file": "src/two.py"}) == "a/y"
    assert z.node_region("n", {"source_file": "src/new.py"}) == "(chưa xếp)"
    assert z.node_region("n", {}) == z.external
    assert z.node_region("n", {"source_file": ".github/w.yml"}) == "(chưa xếp)"


def test_zoning_file_rejects_unknown_region_and_bad_version(tmp_path):
    with pytest.raises(RegionsSkip):
        zoning.from_file(_file(tmp_path, files={"a.py": "nope"}))
    with pytest.raises(RegionsSkip):
        zoning.from_file(_file(tmp_path, version=2))


def test_config_reads_only_regions_keys(tmp_path):
    (tmp_path / ".graphifyrc").write_text("viz_node_limit=100\nregions.depth = 3\n# regions.mode=off\n", encoding="utf-8")
    assert zoning.load_config(tmp_path) == {"depth": "3"}


STATS = {"dispatch": {"flow": 355, "nodes": 296, "top": 103}, "side": {"flow": 244, "nodes": 197, "top": 58},
         "owner": {"flow": 154, "nodes": 195, "top": 90}, "guest": {"flow": 0, "nodes": 6, "top": 3}}


def test_pick_center_is_exactly_one_region_and_override_wins():
    ids = list(STATS)
    assert zoning.pick_center(ids, STATS) == "dispatch"
    assert zoning.pick_center(ids, STATS, ["nope", "guest"]) == "guest"


def _w(pairs):
    w = {}
    for (a, b), n in pairs.items():
        w[(a, b)] = w[(b, a)] = float(n)
    return w


def test_rings_follow_the_links_to_the_inner_rings():
    w = _w({("c", "a"): 100, ("c", "b"): 50, ("c", "n"): 5, ("a", "d"): 30, ("b", "e"): 1})
    rings = zoning.assign_rings(["c", "a", "b", "n", "d", "e", "iso"], "c", w)
    assert rings[0] == ["a", "b"]  # n chỉ 5 < 15% của 100
    assert set(rings[1]) == {"n", "d", "e"} or "d" in rings[1]
    assert rings[-1][-1] == "iso" or "iso" in rings[-1]  # không có đường nối: vòng cuối
    assert sorted(x for r in rings for x in r) == sorted(["a", "b", "n", "d", "e", "iso"])


def test_auto_colors_warm_center_and_first_ring_cool_further_out_and_distinct():
    rings = [["c"], ["a1", "a2", "a3", "a4", "a5"], ["b1", "b2", "b3"], ["d1", "d2"]]
    ids = [x for r in rings for x in r]
    regions = [{"id": i, "name": i, "group": "g"} for i in ids] + [{"id": "(ext)", "name": "e", "group": "ngoài"}]
    z = zoning.Zoning(regions, {}, lambda *_: "", external="(ext)")
    colors = zoning.auto_colors(z, rings)
    warm = lambda h: h <= 50 or h >= 310
    assert colors["c"][0] < 10  # trung tâm đỏ
    assert all(warm(colors[i][0]) for i in rings[1])  # vòng 1 nóng
    cool = [colors[i][0] for r in rings[2:] for i in r]
    assert all(160 <= h <= 300 for h in cool) and cool == sorted(cool)  # vòng 2 trở ra lạnh dần
    assert all(not 60 <= colors[i][0] <= 150 for i in ids)  # không vàng chanh / xanh lá
    assert colors["(ext)"][1] == 0
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            (ha, _, la), (hb, _, lb) = colors[a], colors[b]
            assert min(abs(ha - hb), 360 - abs(ha - hb)) >= 15 or abs(la - lb) >= 8, (a, b)


def test_pinned_regions_are_outer_and_keep_their_own_color():
    regions = [{"id": "a", "name": "a", "group": "g"}, {"id": "b", "name": "b", "group": "g", "pos": [1, 2], "color": [10, 20, 30]}]
    z = zoning.Zoning(regions, {}, lambda *_: "")
    assert [zoning.is_outer(z, r) for r in regions] == [False, True]
    assert zoning.auto_colors(z)["b"] == (10, 20, 30)


def test_zoning_rules_use_the_longest_prefix_and_files_win(tmp_path):
    z = zoning.from_file(_file(tmp_path, files={"src/a/special.py": "a/y"},
                               rules=[{"prefix": "src/a/", "region": "a/x"}, {"prefix": "src/a/deep/", "region": "a/y"}]))
    assert z.node_region("n", {"source_file": "src/a/one.py"}) == "a/x"
    assert z.node_region("n", {"source_file": "src/a/deep/two.py"}) == "a/y"
    assert z.node_region("n", {"source_file": "src/a/special.py"}) == "a/y"
    assert z.node_region("n", {"source_file": "other/x.py"}) == "(chưa xếp)"
    with pytest.raises(RegionsSkip):
        zoning.from_file(_file(tmp_path, files={}, rules=[{"prefix": "x/", "region": "nope"}]))
