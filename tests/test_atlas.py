"""Bản đồ Thành chính (src/pylos/lobby/atlas/maps/atlas.md) phải khớp repo: mọi file đã track đều có chỗ."""

from __future__ import annotations

from pylos.lobby.atlas.generator import atlas


def test_every_tracked_file_has_a_place_and_atlas_is_fresh():
    assert atlas.main(["--check"]) == 0


def test_most_specific_pattern_wins():
    rules = [atlas.Rule("docs/*", "outside/a", "agreed"), atlas.Rule("docs/architecture/*", "outside/b", "agreed"),
             atlas.Rule("docs/architecture/city.md", "outside/c", "agreed")]
    unplaced = atlas.assign(["docs/x.md", "docs/architecture/atlas.md", "docs/architecture/city.md", "other.txt"], rules)
    assert unplaced == ["other.txt"]
    assert [r.files for r in rules] == [["docs/x.md"], ["docs/architecture/atlas.md"], ["docs/architecture/city.md"]]


def _city():
    rules = [atlas.Rule("src/gate.py", "gate/fence/ethics", "agreed", files=["src/gate.py"]),
             atlas.Rule("src/bus.py", "lobby/dispatch/bus", "proposed", note="ghi chú", files=["src/bus.py"]),
             atlas.Rule("tests/t.py", "outside/tests", "agreed", files=["tests/t.py"])]
    node = lambda i, f: {"id": i, "label": i.title(), "norm_label": i, "source_file": f, "source_location": "L1"}
    graph = atlas.Graph(
        {"gate": node("gate", "src/gate.py"), "check": node("check", "src/gate.py"),
         "bus": node("bus", "src/bus.py"), "test": node("test", "tests/t.py")},
        [{"source": "gate", "target": "bus", "relation": "calls"},
         {"source": "gate", "target": "check", "relation": "contains"},
         {"source": "bus", "target": "check", "relation": "imports"},
         {"source": "test", "target": "gate", "relation": "calls"}])
    return rules, graph


def test_region_shows_links_crossing_the_border_and_hides_tests_by_default():
    rules, graph = _city()
    out, inn, per_file = atlas.crossings(graph, atlas.file_targets(rules), "gate/fence", with_tests=False)
    assert [(s["id"], d["id"], other) for s, _, d, other in out] == [("gate", "bus", "lobby/dispatch")]
    assert [(s["id"], d["id"]) for s, _, d, _ in inn] == [("bus", "check")]
    assert per_file["src/gate.py"] == {"lobby/dispatch": 2}
    _, inn, _ = atlas.crossings(graph, atlas.file_targets(rules), "gate/fence", with_tests=True)
    assert {other for *_, other in inn} == {"lobby/dispatch", "outside/tests"}

    report = atlas.region_report("gate", rules, graph)
    assert "src/gate.py -> gate/fence/ethics" in report and "links across the border: lobby/dispatch 2" in report
    assert "src/bus.py" not in report.split("## Links")[0]
    assert "graph.json" in atlas.region_report("gate", rules, None)


def test_where_finds_files_and_symbols():
    rules, graph = _city()
    assert atlas.where_report("src/bus.py", rules, graph) == "src/bus.py -> lobby/dispatch/bus [proposed]\n  note: ghi chú"
    assert atlas.where_report("check", rules, graph) == "Check  src/gate.py:L1 -> gate/fence/ethics [agreed]"
    assert "no tracked file or graph symbol" in atlas.where_report("nothing", rules, graph)


def test_problems_catch_bad_target_status_and_dead_pattern():
    zones = [{"name": "lobby", "building": [{"name": "atlas", "apartments": [{"name": "maps"}]}]}]
    rules = [atlas.Rule("a", "lobby/atlas/maps", "agreed", files=["a"]),
             atlas.Rule("b", "lobby/nowhere", "agreed", files=["b"]),
             atlas.Rule("c", "open", "maybe", files=["c"]),
             atlas.Rule("d", "outside/x", "agreed"),
             atlas.Rule("e", "outside/x", "agreed", optional=True)]
    found = atlas.problems(zones, rules, ["lost.py"])
    assert found == [
        "no place in the atlas: lost.py",
        "target 'lobby/nowhere' of b is not a place in the city",
        "unknown status 'maybe' for c",
        "pattern matches no tracked file (remove it or set optional = true): d",
    ]
