"""regions.json: phân vùng cho graphify-regions (máy admin vẽ bản đồ). Sinh từ atlas_map.toml, phải khớp định dạng chung."""

import json

from pylos.lobby.atlas.generator import atlas, region_map as rm


def test_region_of_maps_buildings_zone_packages_and_outside_things():
    assert rm.region_of("lobby/dispatch", True) == "lobby/dispatch"
    assert rm.region_of("open", True) == "outside/entry"
    assert rm.region_of("", False) == "outside/external"  # json, pytest, Path...: không thuộc file nào
    assert rm.region_of("gate", True).startswith("gate/")  # __init__ của gói khu về một toà trong khu
    assert rm.region_of("outside/unknown", True) == "outside/tooling"


def test_regions_table_is_complete_inner_is_placed_by_graphify_and_only_grey_outside_is_pinned():
    assert len(rm.REGIONS) == 16 and set(rm.ZONE_NAMES) >= {r[2] for r in rm.REGIONS}
    pinned = {rid for rid, _, _, pos, color in rm.REGIONS if pos or color}
    assert pinned == {"outside/tests", "outside/repo_root", "outside/tooling", "outside/external"}
    for rid, _, _, pos, color in rm.REGIONS:
        assert bool(pos) == bool(color) and (not color or color[1] == 0), rid  # ghim thì xám


def test_regions_json_follows_the_shared_format_and_places_every_atlas_file():
    data = json.loads(rm.regions_text())
    assert data["version"] == 1 and data["levels"] == {"group": "Khu", "region": "Toà"}
    ids = {r["id"] for r in data["regions"]}
    assert len(ids) == 16 and all(len(r.get("color", [0, 0, 0])) == 3 and len(r.get("pos", [0, 0])) == 2 for r in data["regions"])
    assert {data["unplaced_region"], data["external_region"], data["tests_region"]} <= ids
    assert set(data["files"].values()) <= ids
    _, rules = atlas.load_map()
    atlas.assign(atlas.tracked_files(), rules)
    assert set(data["files"]) == set(atlas.file_targets(rules))  # mọi file được theo dõi đều có vùng


def test_regions_json_on_disk_is_up_to_date():
    assert rm.REGIONS_FILE.read_text(encoding="utf-8").replace("\r\n", "\n") == rm.regions_text()
