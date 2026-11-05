"""Lọc đường dẫn của công cụ file (7.3): đóng toà Owner, điều phối, nhà bot khác, túp lều không phục vụ; không lách được."""

import os
import sys

import pytest

from pylos.lobby.dispatch.permissions.path_guard import AccessDenied, Actor, check_access

BOT, OWNER, MANAGER = Actor("bot", "pylos"), Actor("owner"), Actor("manager")


@pytest.fixture
def city(tmp_path):
    root, huts = tmp_path / "pylos", tmp_path / "userdata" / "data" / "huts"
    for rel in ("management/owner/private_plans", "lobby/dispatch/bus", "lobby/library/skills",
                "residential/residents/pylos/memory", "residential/residents/other/memory", "gate/guest_house"):
        (root / rel).mkdir(parents=True)
    for hut in ("u1", "u2", "g1"):
        (huts / hut).mkdir(parents=True)
    return root, huts


def ok(city, raw, actor=BOT, hut=None):
    return check_access(raw, actor, city_root=city[0], huts_root=city[1], served_hut=hut)


def test_open_places_and_own_apartment_are_allowed(city):
    assert ok(city, "lobby/library/skills").name == "skills"
    assert ok(city, "residential/residents/pylos/memory").name == "memory"


@pytest.mark.parametrize("raw", ["management/owner", "management/owner/private_plans", "lobby/dispatch/bus",
                                 "residential/residents/other/memory", "gate/guest_house/u1"])
def test_closed_places_are_refused_for_bots(city, raw):
    with pytest.raises(AccessDenied):
        ok(city, raw)


def test_traversal_absolute_paths_and_outside_are_refused(city, tmp_path):
    for raw in ("lobby/library/../../management/owner", str(city[0] / "management" / "owner"), "../userdata", str(tmp_path)):
        with pytest.raises(AccessDenied):
            ok(city, raw)


def test_symlink_into_closed_place_is_refused(city):
    link = city[0] / "lobby" / "library" / "skills" / "sneaky"
    try:
        os.symlink(city[0] / "management" / "owner", link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("không tạo được symlink trên máy này")
    with pytest.raises(AccessDenied):
        ok(city, link)


@pytest.mark.skipif(sys.platform != "win32", reason="chỉ Windows không phân biệt hoa thường")
def test_case_tricks_do_not_work_on_windows(city):
    with pytest.raises(AccessDenied):
        ok(city, "MANAGEMENT/Owner")


def test_hut_only_for_the_person_being_served(city):
    assert ok(city, city[1] / "u1", hut="u1").name == "u1"
    for hut in (None, "u2", "g1"):
        with pytest.raises(AccessDenied):
            ok(city, city[1] / "u1", hut=hut)
    with pytest.raises(AccessDenied):
        ok(city, city[1], hut="u1")  # không được liệt kê cả thư mục túp lều


def test_in_a_group_only_the_group_hut_is_open(city):
    assert ok(city, city[1] / "g1", hut="g1")
    with pytest.raises(AccessDenied):
        ok(city, city[1] / "u1", hut="g1")  # túp lều cá nhân của thành viên (A5)


def test_owner_and_manager_rules(city):
    assert ok(city, "management/owner", OWNER) and ok(city, "lobby/dispatch/bus", OWNER)
    assert ok(city, city[1] / "u1", MANAGER)  # quản lý vào được túp lều
    for raw in ("management/owner", "lobby/dispatch", "residential/residents/other/memory"):
        with pytest.raises(AccessDenied):
            ok(city, raw, MANAGER)  # nhưng không sửa trí nhớ bot khác, không vào toà Owner/điều phối
