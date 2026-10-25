"""Vai trò trong bot: basic (mặc định) < leader (theo từng nhóm) < owner (OWNER_ZALO_ID).

- basic: nhận việc, dùng lệnh xem, tự thêm lịch cho chính mình; không giao việc cho người khác.
- leader: giao việc cho người khác (@tag hoặc đội), tạo đội, cho người khác lên leader.
- owner: mọi quyền của leader, cộng lệnh về bộ lọc / chỉnh bot và gỡ leader.
"""

from __future__ import annotations

from bot.storage import GroupStore

BASIC = "basic"
LEADER = "leader"
OWNER = "owner"
RANK = {BASIC: 0, LEADER: 1, OWNER: 2}
LABEL = {BASIC: "basic-user", LEADER: "leader", OWNER: "owner"}

# Lệnh chỉ owner dùng được, bất kể tham số.
OWNER_COMMANDS = ("allow", "deny", "mode", "status", "reset", "remove")
LEADER_REMOVE = ("bo", "bỏ", "remove", "xoa", "xoá", "xóa")
LEADER_OFF = ("off", "clear", "none")


def role_of(*, is_owner: bool, groups: GroupStore, chat_id: str, user_id: str, is_group: bool,
            assign_allowed: str = "owner") -> str:
    if is_owner:
        return OWNER
    if assign_allowed == "all" or (is_group and groups.can_assign(chat_id, user_id)):
        return LEADER
    return BASIC


def required_role(name: str, arg: str = "") -> str:
    """Vai trò tối thiểu để dùng lệnh `/name arg` (arg đã hạ chữ thường)."""
    head, _, rest = arg.partition(" ")
    if name in OWNER_COMMANDS:
        return OWNER
    if name == "add":
        return LEADER
    if name == "leader":
        if not arg:
            return BASIC
        if head == "all" or head in LEADER_OFF or head in LEADER_REMOVE:
            return OWNER
        return LEADER
    if name == "team":
        # /team và /team <tên> chỉ xem; còn lại (thêm người, bỏ, xoá) cần leader.
        return BASIC if len(arg.split()) <= 1 else LEADER
    return BASIC  # help, id, vaitro, role


def allows(role: str, needed: str) -> bool:
    return RANK[role] >= RANK[needed]
