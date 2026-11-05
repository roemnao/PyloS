"""Bản đồ vùng: mỗi toà một vòng tròn, các vòng không chồng nhau, mọi file đều rơi vào một vùng."""

import math

from pylos.lobby.atlas.generator import region_map as rm


def test_every_building_has_a_region_and_regions_do_not_overlap():
    plan = rm.plan_regions({rid: 150.0 for rid, *_ in rm.REGIONS})
    ids = list(plan)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            (ax, ay, ar), (bx, by, br) = plan[a], plan[b]
            assert math.hypot(ax - bx, ay - by) >= ar + br, (a, b)
    assert {"lobby/dispatch", "gate/fence", "management/owner", "residential/residents"} <= set(plan)


def test_region_of_maps_buildings_zone_packages_and_outside_things():
    assert rm.region_of("lobby/dispatch", True) == "lobby/dispatch"
    assert rm.region_of("open", True) == "outside/entry"
    assert rm.region_of("", False) == "outside/external"  # json, pytest, Path...: không thuộc file nào
    assert rm.region_of("gate", True).startswith("gate/")  # __init__ của gói khu về một toà trong khu


def test_pack_region_gives_every_node_its_own_spot_inside_the_radius():
    files = [[0, 1, 2, 3, 4], [5, 6], [7]]
    pos, radius = rm.pack_region(files, lambda i: 10 - i)
    assert set(pos) == set(range(8)) and len(set(pos.values())) == 8
    assert all(math.hypot(x, y) <= radius for x, y in pos.values())
