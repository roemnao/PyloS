"""Lệnh điều khiển bot, chỉ chủ bot (OWNER_ZALO_ID) được dùng."""

from __future__ import annotations

from dataclasses import dataclass

import re

from bot.agent.tools.assign_events import match_member
from bot.storage import MODE_ALL, MODE_DEFAULT, GroupStore, HistoryStore, UsageStore
from bot.zalo import IncomingMessage

COMMANDS = ("help", "mode", "allow", "deny", "status", "reset", "id", "leader")

HELP = (
    "Lệnh của chủ bot:\n"
    "/mode - xem chế độ của nhóm này\n"
    "/mode all - bộ lọc AI: trả lời khi được gọi hoặc khi AI thấy tin đang nhờ bot\n"
    "/mode default - chỉ trả lời khi được gọi (/bot, @tag, tên bot)\n"
    "/allow - cho phép nhóm này dùng bot\n"
    "/deny - chặn nhóm này\n"
    "/status - xem trạng thái\n"
    "/reset - xóa lịch sử hội thoại của nhóm này\n"
    "/id - xem chat id và user id\n"
    "/leader - xem ai được nhờ bot giao lịch trong nhóm này\n"
    "/leader @a @b - cho a, b giao lịch trong nhóm này\n"
    "/leader all - ai trong nhóm cũng giao lịch được\n"
    "/leader bo @a - bỏ a khỏi danh sách\n"
    "/leader off - xoá hết, chỉ chủ bot giao lịch"
)
LEADER_REMOVE = ("bo", "bỏ", "remove", "xoa", "xoá", "xóa")
LEADER_OFF = ("off", "clear", "none")


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

    def handle(self, cmd: ParsedCommand, msg: IncomingMessage, members: dict[str, str] | None = None,
               self_id: str = "") -> str:
        chat_id = msg.chat_id
        if cmd.name == "help":
            return HELP
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
        if cmd.name == "leader":
            return self._leader(cmd.arg, msg, members or {}, self_id)
        if cmd.name == "status":
            state = self.groups.get(chat_id)
            budget = f"/{self.daily_budget}" if self.daily_budget else " (không giới hạn)"
            return (
                f"Cho phép: {'có' if self.groups.is_allowed(chat_id, self.allow_all) else 'không'}"
                f"{' (mọi chat đều được phép, trừ chat bị /deny)' if self.allow_all else ''}\n"
                f"Chế độ: {describe_mode(state.mode, self.triggers)}\n"
                f"Token hôm nay: {self.usage.used_today()}{budget}"
            )
        return HELP

    def _leader(self, arg: str, msg: IncomingMessage, members: dict[str, str], self_id: str) -> str:
        if not msg.is_group:
            return "Dùng /leader trong nhóm: mỗi nhóm có danh sách người được giao lịch riêng."
        chat_id = msg.chat_id
        head, _, rest = arg.partition(" ")
        if head in LEADER_OFF:
            self.groups.set_leaders(chat_id, clear=True)
            return "Đã xoá danh sách leader. Trong nhóm này chỉ chủ bot được nhờ bot giao lịch."
        if head == "all":
            self.groups.set_leaders(chat_id, all_=True)
            return "Đã cho phép mọi người trong nhóm này nhờ bot giao lịch."
        if not arg:
            return self._describe_leaders(chat_id, members)
        removing = head in LEADER_REMOVE
        people, missing = _pick_people(rest if removing else arg, msg.mentions, members, self_id)
        if not people:
            hint = f" Không tìm thấy: {', '.join(missing)}." if missing else ""
            return f"Chưa chọn được ai.{hint} Tag người đó: /leader @tên (hoặc gõ Zalo ID)."
        names = ", ".join(members.get(uid) or uid for uid in people)
        if removing:
            self.groups.set_leaders(chat_id, remove=people)
            text = f"Đã bỏ quyền giao lịch của: {names}."
        else:
            self.groups.set_leaders(chat_id, add=people)
            text = f"Đã cho phép giao lịch trong nhóm này: {names}."
        if missing:
            text += f" Không tìm thấy: {', '.join(missing)}."
        return text

    def _describe_leaders(self, chat_id: str, members: dict[str, str]) -> str:
        state = self.groups.get(chat_id)
        if state.leaders_all:
            return "Trong nhóm này ai cũng được nhờ bot giao lịch (/leader off để tắt)."
        if not state.leaders:
            return "Nhóm này chưa có leader: chỉ chủ bot được nhờ bot giao lịch. Thêm bằng /leader @tên."
        names = ", ".join(members.get(uid) or uid for uid in state.leaders)
        return f"Leader của nhóm này (được nhờ bot giao lịch): {names}."


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
