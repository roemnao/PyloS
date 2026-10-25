"""Lệnh trong chat theo vai trò (xem core/roles.py): basic, leader, owner (OWNER_ZALO_ID)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from bot.agent.tools.assign_events import match_member
from bot.core.roles import (
    BASIC, LABEL, LEADER, LEADER_OFF, LEADER_REMOVE, OWNER, allows, required_role,
)
from bot.core.text_fold import fold
from bot.storage import MODE_ALL, MODE_DEFAULT, GroupStore, HistoryStore, UsageStore
from bot.zalo import IncomingMessage

COMMANDS = ("help", "mode", "allow", "deny", "status", "reset", "id", "leader", "add", "remove", "team", "vaitro", "role")

HELP_LINES: tuple[tuple[str, str, str], ...] = (
    (BASIC, "/help", "danh sách lệnh bạn dùng được"),
    (BASIC, "/id", "xem chat id và user id"),
    (BASIC, "/vaitro", "xem vai trò của bạn trong nhóm này"),
    (BASIC, "/leader", "xem ai là leader của nhóm này"),
    (BASIC, "/team", "xem các đội của nhóm; /team tên: xem thành viên đội"),
    (LEADER, "/add leader @a @b", "cho a, b làm leader (giao việc được) trong nhóm này"),
    (LEADER, "/team tên @a @b", "tạo đội hoặc thêm người vào đội"),
    (LEADER, "/team tên bo @a", "bỏ người khỏi đội"),
    (LEADER, "/team xoa tên", "xoá đội"),
    (OWNER, "/remove leader @a", "gỡ leader"),
    (OWNER, "/leader all | /leader off", "cả nhóm là leader | xoá hết leader"),
    (OWNER, "/mode all | /mode default", "bộ lọc AI | chỉ trả lời khi được gọi (/bot, @tag, tên bot)"),
    (OWNER, "/allow, /deny", "cho phép hoặc chặn nhóm này dùng bot"),
    (OWNER, "/status", "xem trạng thái"),
    (OWNER, "/reset", "xóa lịch sử hội thoại của nhóm này"),
)
NEED_ROLE = "Lệnh này cần quyền {needed} (bạn đang là {role})."


def help_text(role: str) -> str:
    lines = [f"- {cmd}: {desc}" for need, cmd, desc in HELP_LINES if allows(role, need)]
    return f"Lệnh bạn dùng được (vai trò: {LABEL[role]}):\n" + "\n".join(lines)


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    arg: str


def parse_command(text: str | None) -> ParsedCommand | None:
    if not text:
        return None
    stripped = text.strip()
    if not stripped.startswith("/"):
        return None
    head, _, rest = stripped[1:].partition(" ")
    name = head.split("@", 1)[0].lower()
    if name not in COMMANDS:
        return None
    return ParsedCommand(name, rest.strip().lower())


def describe_mode(mode: str, triggers: tuple[str, ...]) -> str:
    if mode == MODE_ALL:
        return "all (bộ lọc AI: trả lời khi được gọi hoặc khi AI thấy tin đang nhờ bot)"
    return f"default (chỉ trả lời khi được gọi: {', '.join(triggers)}, @tag hoặc tên bot)"


class CommandHandler:
    def __init__(
        self,
        groups: GroupStore,
        history: HistoryStore,
        usage: UsageStore,
        triggers: tuple[str, ...],
        daily_budget: int,
        allow_all: bool = False,
    ) -> None:
        self.groups = groups
        self.history = history
        self.usage = usage
        self.triggers = triggers
        self.daily_budget = daily_budget
        self.allow_all = allow_all

    def handle(self, cmd: ParsedCommand, msg: IncomingMessage, role: str = OWNER,
               members: dict[str, str] | None = None, self_id: str = "") -> str:
        """Trả lời cho lệnh; chuỗi rỗng = không đáp (lệnh không dành cho bot, ví dụ `/add` không kèm `leader`)."""
        chat_id = msg.chat_id
        members = members or {}
        if cmd.name in ("add", "remove") and not cmd.arg.startswith("leader"):
            return ""
        needed = required_role(cmd.name, cmd.arg)
        if not allows(role, needed):
            return NEED_ROLE.format(needed=LABEL[needed], role=LABEL[role])
        if cmd.name == "help":
            return help_text(role)
        if cmd.name in ("vaitro", "role"):
            return f"Vai trò của bạn trong cuộc trò chuyện này: {LABEL[role]}."
        if cmd.name == "id":
            return f"chat_id: {chat_id}\nuser_id của bạn: {msg.from_id}\nloại: {msg.chat_type}"
        if cmd.name == "allow":
            self.groups.set_allowed(chat_id, True)
            mode = self.groups.get(chat_id).mode
            return f"Đã cho phép cuộc trò chuyện này dùng bot. Chế độ: {describe_mode(mode, self.triggers)}."
        if cmd.name == "deny":
            self.groups.set_allowed(chat_id, False)
            return "Đã chặn cuộc trò chuyện này. Bot sẽ không trả lời ở đây nữa (kể cả khi bật cho phép mọi chat)."
        if cmd.name == "reset":
            self.history.clear(chat_id)
            return "Đã xóa lịch sử hội thoại của cuộc trò chuyện này."
        if cmd.name == "mode":
            if cmd.arg in (MODE_ALL, MODE_DEFAULT):
                self.groups.set_mode(chat_id, cmd.arg)
                return f"Đã chuyển sang chế độ {describe_mode(cmd.arg, self.triggers)}."
            if cmd.arg:
                return "Chế độ không hợp lệ. Dùng /mode all hoặc /mode default."
            return f"Chế độ hiện tại: {describe_mode(self.groups.get(chat_id).mode, self.triggers)}."
        if cmd.name in ("leader", "add", "remove"):
            return self._leader(cmd, msg, members, self_id)
        if cmd.name == "team":
            return self._team(cmd.arg, msg, members, self_id)
        if cmd.name == "status":
            state = self.groups.get(chat_id)
            budget = f"/{self.daily_budget}" if self.daily_budget else " (không giới hạn)"
            return (
                f"Cho phép: {'có' if self.groups.is_allowed(chat_id, self.allow_all) else 'không'}"
                f"{' (mọi chat đều được phép, trừ chat bị /deny)' if self.allow_all else ''}\n"
                f"Chế độ: {describe_mode(state.mode, self.triggers)}\n"
                f"Token hôm nay: {self.usage.used_today()}{budget}"
            )
        return help_text(role)

    # ---------- leader ----------

    def _leader(self, cmd: ParsedCommand, msg: IncomingMessage, members: dict[str, str], self_id: str) -> str:
        if not msg.is_group:
            return "Dùng lệnh này trong nhóm: mỗi nhóm có danh sách leader riêng."
        chat_id = msg.chat_id
        arg = cmd.arg
        # /add leader @a và /remove leader @a: bỏ chữ "leader" để dùng chung với dạng cũ /leader @a, /leader bo @a.
        if cmd.name in ("add", "remove"):
            arg = arg.removeprefix("leader").strip()
            if cmd.name == "remove":
                arg = f"bo {arg}"
            if not arg or arg == "bo ":
                return f"Thiếu người: /{cmd.name} leader @tên."
        head, _, rest = arg.partition(" ")
        if head in LEADER_OFF:
            self.groups.set_leaders(chat_id, clear=True)
            return "Đã xoá danh sách leader. Trong nhóm này chỉ owner được nhờ bot giao lịch."
        if head == "all":
            self.groups.set_leaders(chat_id, all_=True)
            return "Đã cho phép mọi người trong nhóm này nhờ bot giao lịch."
        if not arg:
            return self._describe_leaders(chat_id, members)
        removing = head in LEADER_REMOVE
        people, missing = _pick_people(rest if removing else arg, msg.mentions, members, self_id)
        if not people:
            hint = f" Không tìm thấy: {', '.join(missing)}." if missing else ""
            return f"Chưa chọn được ai.{hint} Tag người đó: /add leader @tên (hoặc gõ Zalo ID)."
        names = ", ".join(members.get(uid) or uid for uid in people)
        if removing:
            self.groups.set_leaders(chat_id, remove=people)
            text = f"Đã gỡ quyền leader của: {names}."
        else:
            self.groups.set_leaders(chat_id, add=people, by=msg.from_id)
            text = f"Đã cho làm leader trong nhóm này: {names}."
        if missing:
            text += f" Không tìm thấy: {', '.join(missing)}."
        return text

    def _describe_leaders(self, chat_id: str, members: dict[str, str]) -> str:
        state = self.groups.get(chat_id)
        if state.leaders_all:
            return "Trong nhóm này ai cũng được nhờ bot giao lịch (owner dùng /leader off để tắt)."
        if not state.leaders:
            return "Nhóm này chưa có leader: chỉ owner được nhờ bot giao lịch. Thêm bằng /add leader @tên."
        names = ", ".join(members.get(uid) or uid for uid in state.leaders)
        return f"Leader của nhóm này: {names}."

    # ---------- đội ----------

    def _team(self, arg: str, msg: IncomingMessage, members: dict[str, str], self_id: str) -> str:
        if not msg.is_group:
            return "Dùng /team trong nhóm: mỗi nhóm có các đội riêng."
        chat_id = msg.chat_id
        state = self.groups.get(chat_id)
        if not arg:
            if not state.teams:
                return "Nhóm này chưa có đội. Leader tạo bằng /team tên @a @b."
            return "Các đội: " + "; ".join(
                f"{t['name']} ({len(t['members'])})" for t in state.teams.values()) + "."
        name, _, rest = arg.partition(" ")
        rest = rest.strip()
        label = lambda uids: ", ".join(members.get(u) or u for u in uids) or "chưa có ai"  # noqa: E731
        if name in ("xoa", "xoá", "xóa", "delete"):
            if not rest:
                return "Thiếu tên đội: /team xoa tên."
            return f"Đã xoá đội {rest}." if self.groups.delete_team(chat_id, rest) else f"Không có đội {rest}."
        if not rest:
            found = self.groups.team_members(chat_id, name)
            if found is None:
                return f"Không có đội {name}. Xem danh sách bằng /team."
            return f"Đội {state.teams[fold(name).strip()]['name']}: {label(found)}."
        head, _, who = rest.partition(" ")
        removing = head in LEADER_REMOVE
        people, missing = _pick_people(who if removing else rest, msg.mentions, members, self_id)
        if not people:
            hint = f" Không tìm thấy: {', '.join(missing)}." if missing else ""
            return f"Chưa chọn được ai.{hint} Dùng /team {name} @a @b."
        if removing:
            if self.groups.team_members(chat_id, name) is None:
                return f"Không có đội {name}."
            team = self.groups.set_team(chat_id, name, remove=people)
            text = f"Đã bỏ khỏi đội {name}: {label(people)}."
        else:
            team = self.groups.set_team(chat_id, name, add=people)
            text = f"Đội {name} hiện có: {label(team.teams[fold(name).strip()]['members'])}."
        if missing:
            text += f" Không tìm thấy: {', '.join(missing)}."
        return text


def _pick_people(text: str, mentions: tuple[str, ...], members: dict[str, str],
                 self_id: str) -> tuple[list[str], list[str]]:
    """(Zalo ID được chọn, tên không tìm thấy). Ưu tiên @tag thật; không có thì khớp tên thành viên hoặc ID gõ thẳng."""
    tagged = [uid for uid in dict.fromkeys(mentions) if uid and uid != self_id]
    if tagged:
        return tagged, []
    names = [n.strip(" ,") for n in (text.split("@") if "@" in text else re.split(r"[,\s]+", text))]
    people: list[str] = []
    missing: list[str] = []
    for name in filter(None, names):
        found = match_member(name, members)
        if len(found) == 1:
            people.append(found[0])
        elif not found and name.isdigit() and len(name) >= 6:
            people.append(name)  # Zalo ID gõ thẳng
        else:
            missing.append(name if not found else f"{name} (trùng nhiều người)")
    return list(dict.fromkeys(people)), missing
