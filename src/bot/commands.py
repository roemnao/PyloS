"""Lệnh điều khiển bot, chỉ chủ bot (OWNER_ZALO_ID) được dùng."""

from __future__ import annotations

from dataclasses import dataclass

from bot.storage import MODE_ALL, MODE_DEFAULT, GroupStore, HistoryStore, UsageStore
from bot.zalo import IncomingMessage

COMMANDS = ("help", "mode", "allow", "deny", "status", "reset", "id")

HELP = (
    "Lệnh của chủ bot:\n"
    "/mode - xem chế độ của nhóm này\n"
    "/mode all - trả lời mọi tin nhắn\n"
    "/mode default - chỉ trả lời tin gọi bot\n"
    "/allow - cho phép nhóm này dùng bot\n"
    "/deny - chặn nhóm này\n"
    "/status - xem trạng thái\n"
    "/reset - xóa lịch sử hội thoại của nhóm này\n"
    "/id - xem chat id và user id"
)


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
        return "all (trả lời mọi tin nhắn)"
    return f"default (chỉ trả lời tin bắt đầu bằng {', '.join(triggers)})"


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

    def handle(self, cmd: ParsedCommand, msg: IncomingMessage) -> str:
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
