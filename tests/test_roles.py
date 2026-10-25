from __future__ import annotations

import pytest

from bot.core.roles import BASIC, LEADER, OWNER, allows, required_role, role_of
from bot.storage import GroupStore


@pytest.fixture
def groups(tmp_path):
    return GroupStore(tmp_path / "groups.txt")


def role(groups, user, *, owner=False, chat="g", is_group=True, assign_allowed="owner"):
    return role_of(is_owner=owner, groups=groups, chat_id=chat, user_id=user, is_group=is_group, assign_allowed=assign_allowed)


def test_role_of(groups):
    assert role(groups, "o", owner=True) == OWNER
    assert role(groups, "a") == BASIC
    groups.set_leaders("g", add=["a"])
    assert role(groups, "a") == LEADER
    assert role(groups, "a", chat="g2") == BASIC  # leader chỉ trong nhóm đã đặt
    assert role(groups, "a", chat="a", is_group=False) == BASIC  # chat riêng không có leader
    assert role(groups, "b", assign_allowed="all") == LEADER  # ASSIGN_ALLOWED=all giữ nghĩa cũ
    groups.set_leaders("g2", all_=True)
    assert role(groups, "anyone", chat="g2") == LEADER
    assert role(groups, "a", owner=True) == OWNER


@pytest.mark.parametrize("name, arg, needed", [
    ("help", "", BASIC), ("id", "", BASIC), ("vaitro", "", BASIC), ("role", "", BASIC),
    ("leader", "", BASIC), ("leader", "@a", LEADER), ("leader", "all", OWNER), ("leader", "off", OWNER),
    ("leader", "bo @a", OWNER), ("add", "leader @a", LEADER), ("remove", "leader @a", OWNER),
    ("team", "", BASIC), ("team", "thietke", BASIC), ("team", "thietke @a", LEADER),
    ("team", "thietke bo @a", LEADER), ("team", "xoa thietke", LEADER),
    ("mode", "", OWNER), ("mode", "all", OWNER), ("allow", "", OWNER), ("deny", "", OWNER),
    ("status", "", OWNER), ("reset", "", OWNER),
])
def test_required_role(name, arg, needed):
    assert required_role(name, arg) == needed


def test_allows():
    assert allows(OWNER, LEADER) and allows(LEADER, LEADER) and allows(LEADER, BASIC)
    assert not allows(BASIC, LEADER) and not allows(LEADER, OWNER)
