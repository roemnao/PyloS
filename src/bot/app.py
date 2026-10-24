"""Lõi bot: quyết định có trả lời tin hay không, xếp hàng theo từng chat và gửi trả lời."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any, Protocol

from bot.agent import Agent, PromptBuilder, ToolContext, Turn
from bot.commands import CommandHandler, parse_command
from bot.config import Settings
from bot.filter import Decision, MessageFilter
from bot.mentions import add_tags
from bot.ratelimit import RateLimiter
from bot.storage import (
    MODE_ALL,
    ActivityStore,
    FailedStore,
    GroupStore,
    HistoryStore,
    MemoryDataStore,
    SeenStore,
    StateStore,
    StatsStore,
    UsageStore,
)
from bot.text import split_message, to_plain_text
from bot.timeutil import now_ms
from bot.zalo import IncomingMessage, ZaloError, parse_updates

log = logging.getLogger(__name__)

ERROR_REPLY = "Xin lỗi, mình đang gặp lỗi, bạn thử lại sau nhé."
NON_TEXT_REPLY = "Hiện mình chỉ đọc được tin nhắn chữ."
EMPTY_PROMPT_REPLY = "Bạn cần mình giúp gì?"
NO_OWNER_HINT = (
    "Bot chưa có chủ. Nếu bạn là người cài bot, hãy điền OWNER_ZALO_ID={user_id} "
    "vào file .env rồi khởi động lại bot."
)
BUDGET_NOTICE = (
    "Đã dùng hết hạn mức token hôm nay. Đến hết ngày, mình chỉ trả lời "
    "những tin gọi mình (chế độ default)."
)


class ZaloSender(Protocol):
    async def send_message(self, chat_id: str, text: str) -> Any: ...
    async def send_chat_action(self, chat_id: str, action: str = "typing") -> Any: ...


@dataclass(frozen=True)
class Job:
    msg: IncomingMessage


class Bot:
    def __init__(
        self,
        settings: Settings,
        zalo: ZaloSender,
        agent: Agent,
        prompts: PromptBuilder,
        tool_names: list[str] | None = None,
        *,
        send_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.settings = settings
        self.zalo = zalo
        self.agent = agent
        self.prompts = prompts
        self.tool_names = tool_names or []
        self.send_retries = send_retries
        self.retry_delay = retry_delay

        data = settings.data_dir
        self.groups = GroupStore(data / "groups.txt", settings.allowed_chat_ids)
        self.seen = SeenStore(data / "seen.txt")
        self.history = HistoryStore(data / "history", keep=max(200, settings.history_turns * 4))
        self.state = StateStore(data / "state.txt")
        self.usage = UsageStore(data / "usage.txt")
        self.failed = FailedStore(data / "failed.txt")
        self.stats = StatsStore(data / "stats.txt")
        self.activity = ActivityStore(data / "activity.txt")
        self.memory = MemoryDataStore(data / "memorydata", keep=settings.memorydata_keep)
        self.filter = MessageFilter(settings, agent, self._self_identity)
        self.commands = CommandHandler(
            self.groups, self.history, self.usage, settings.bot_triggers, settings.daily_token_budget,
            allow_all=settings.allow_all_chats,
        )
        self.user_limiter = RateLimiter(settings.user_rate_per_min)
        self.chat_limiter = RateLimiter(settings.chat_rate_per_min)

        self.started_at_ms = now_ms()
        self.state.update(started_at=self.started_at_ms)
        self._queues: dict[str, asyncio.Queue[Job]] = {}
        self._workers: dict[str, asyncio.Task[None]] = {}
        self._warned_no_owner: set[str] = set()
        self._hinted: set[str] = set()

    # ---------- nhận tin ----------

    async def handle_payload(self, payload: Any) -> None:
        """Điểm vào chung cho polling và webhook. Chỉ lọc và xếp hàng, không chờ Gemini."""
        for msg in parse_updates(payload):
            try:
                await self.handle_message(msg)
            except Exception:
                log.exception("Lỗi khi xử lý tin %s", msg.dedupe_key)

    async def handle_message(self, msg: IncomingMessage) -> None:
        if msg.from_is_bot:
            return
        key = msg.dedupe_key
        if key in self.seen:
            log.debug("Bỏ qua tin trùng %s", key)
            return
        self.seen.add(key)
        # Tin gửi lúc bot đang tắt thì bỏ qua (đã chốt trong PLAN.md).
        if msg.date_ms is not None and msg.date_ms < self.started_at_ms:
            log.info("Bỏ qua tin cũ từ lúc bot tắt: chat=%s", msg.chat_id)
            return
        self.state.update(last_message_at=now_ms())
        self.stats.incr("received")
        self.activity.touch(msg.chat_id, msg.chat_type, msg.from_name)

        is_owner = self._is_owner(msg.from_id)
        if not self.settings.owner_zalo_id and msg.from_id not in self._warned_no_owner:
            self._warned_no_owner.add(msg.from_id)
            log.warning(
                "OWNER_ZALO_ID chưa đặt. Tin từ from_id=%s (%s), chat_id=%s (%s). "
                "Nếu đây là bạn, điền from_id vào OWNER_ZALO_ID trong .env rồi khởi động lại.",
                msg.from_id, msg.from_name, msg.chat_id, msg.chat_type,
            )

        cmd = parse_command(msg.text)
        if cmd is not None:
            # Chưa đặt chủ bot thì chỉ cho /id để lấy ID; người khác gõ lệnh thì bỏ qua.
            if is_owner or (cmd.name == "id" and not self.settings.owner_zalo_id):
                await self._send(msg.chat_id, self.commands.handle(cmd, msg))
            else:
                log.info("Bỏ qua lệnh /%s từ người không phải chủ bot (%s)", cmd.name, msg.from_id)
            return

        if not self._chat_allowed(msg, is_owner):
            log.debug("Chat %s chưa được cho phép", msg.chat_id)
            if not self.settings.owner_zalo_id and not msg.is_group and msg.from_id not in self._hinted:
                # Chưa có chủ bot nên không ai được phép; nhắn hướng dẫn một lần thay vì im lặng.
                self._hinted.add(msg.from_id)
                await self._send(msg.chat_id, NO_OWNER_HINT.format(user_id=msg.from_id))
            return

        # Bộ lọc (có thể gọi AI) chạy trong hàng đợi của từng chat: không làm chậm chat khác, giữ đúng thứ tự tin.
        self._enqueue(Job(msg))

    def _is_owner(self, user_id: str) -> bool:
        return bool(self.settings.owner_zalo_id) and user_id == self.settings.owner_zalo_id

    def _chat_allowed(self, msg: IncomingMessage, is_owner: bool) -> bool:
        if not msg.is_group and is_owner:
            return True  # chat riêng với chủ bot luôn được phép
        return self.groups.is_allowed(msg.chat_id, self.settings.allow_all_chats)

    def _over_budget(self) -> bool:
        budget = self.settings.daily_token_budget
        return budget > 0 and self.usage.used_today() >= budget

    def _self_identity(self) -> tuple[str, str]:
        """(id, tên) của acc bot; chỉ có khi chạy trên acc Zalo cá nhân."""
        return str(getattr(self.zalo, "self_id", "") or ""), str(getattr(self.zalo, "self_name", "") or "")

    # ---------- hàng đợi theo chat ----------

    def _enqueue(self, job: Job) -> None:
        chat_id = job.msg.chat_id
        queue = self._queues.get(chat_id)
        if queue is None:
            queue = self._queues[chat_id] = asyncio.Queue()
        worker = self._workers.get(chat_id)
        if worker is None or worker.done():
            self._workers[chat_id] = asyncio.create_task(self._worker(chat_id, queue), name=f"chat-{chat_id}")
        queue.put_nowait(job)

    async def _worker(self, chat_id: str, queue: asyncio.Queue[Job]) -> None:
        """Xử lý tuần tự các tin của một chat để câu trả lời không lẫn nhau."""
        while True:
            job = await queue.get()
            try:
                await self._process(job)
            except Exception:
                log.exception("Lỗi xử lý tin ở chat %s", chat_id)
            finally:
                queue.task_done()

    async def drain(self) -> None:
        """Chờ mọi hàng đợi xử lý xong (dùng trong test và khi tắt)."""
        for queue in list(self._queues.values()):
            await queue.join()

    async def stop(self) -> None:
        for task in self._workers.values():
            task.cancel()
        await asyncio.gather(*self._workers.values(), return_exceptions=True)
        self._workers.clear()

    async def _process(self, job: Job) -> None:
        msg = job.msg
        decision = await self._decide(msg)
        self.memory.add_user(msg.chat_id, msg_id=msg.message_id, uid=msg.from_id, name=msg.from_name,
                             text=msg.text, is_text=msg.is_text, decision=decision.as_record())
        if msg.is_group:
            self.stats.incr("filter_pass" if decision.passed else "filter_block")
        log.debug("Lọc tin chat=%s: %s (%s) %s", msg.chat_id, decision.passed, decision.stage, decision.reason)

        if not decision.passed:
            if not msg.is_text and not msg.is_group:
                await self._say(msg.chat_id, NON_TEXT_REPLY)
            return
        prompt = decision.prompt or ""
        if not prompt:
            await self._say(msg.chat_id, EMPTY_PROMPT_REPLY)
            return
        if not self.user_limiter.allow(f"{msg.chat_id}:{msg.from_id}") or not self.chat_limiter.allow(msg.chat_id):
            log.warning("Vượt giới hạn tần suất: chat=%s user=%s", msg.chat_id, msg.from_id)
            return
        await self._reply(msg, prompt)

    async def _decide(self, msg: IncomingMessage) -> Decision:
        try:
            decision = await self.filter.decide(
                msg,
                mode=self.groups.get(msg.chat_id).mode if msg.is_group else "",
                over_budget=self._over_budget(),
                # Đọc trước khi ghi tin mới: ngữ cảnh là các tin TRƯỚC tin đang xét.
                recent=self.memory.recent(msg.chat_id, self.settings.filter_context_lines),
            )
        except Exception as exc:  # noqa: BLE001 - lỗi bộ lọc: ghi lại, coi như không gọi bot
            log.exception("Bộ lọc lỗi ở chat %s", msg.chat_id)
            return Decision(False, "error", f"bộ lọc lỗi: {type(exc).__name__}")
        if decision.tokens:
            self.usage.add(decision.tokens)
            self.stats.incr("tokens", decision.tokens)
        return decision

    async def _members(self, chat_id: str) -> dict[str, str]:
        """{uid: tên} thành viên nhóm để bot tag được (chỉ acc Zalo cá nhân có danh sách này)."""
        lookup = getattr(self.zalo, "members", None)
        if lookup is None:
            return {}
        try:
            return await asyncio.to_thread(lookup, chat_id)
        except Exception:  # noqa: BLE001 - thiếu danh sách thì bot vẫn trả lời, chỉ không tag được
            log.exception("Không lấy được thành viên nhóm %s", chat_id)
            return {}

    async def _say(self, chat_id: str, text: str) -> None:
        """Gửi và ghi vào memorydata (không vào session)."""
        self.memory.add_model(chat_id, text)
        await self._send(chat_id, text)

    async def _reply(self, msg: IncomingMessage, prompt: str) -> None:
        try:
            await self.zalo.send_chat_action(msg.chat_id, "typing")
        except Exception as exc:  # noqa: BLE001 - chỉ là hiệu ứng "đang gõ"
            log.debug("sendChatAction lỗi: %s", exc)

        self.history.append(msg.chat_id, "user", prompt, uid=msg.from_id, name=msg.from_name)
        records = self.history.recent(msg.chat_id, self.settings.history_turns)
        turns = [Turn(r.get("role", "user"), str(r.get("text", "")), str(r.get("name", ""))) for r in records]
        ctx = ToolContext(msg.chat_id, msg.from_id, msg.from_name, self._is_owner(msg.from_id), self.settings.data_dir)
        members = await self._members(msg.chat_id) if msg.is_group else {}
        system = self.prompts.build(is_group=msg.is_group, tool_names=self.tool_names, members=list(members.values()))

        was_over = self._over_budget()
        try:
            reply = await self.agent.reply(system, turns, ctx)
        except Exception:
            log.exception("Agent lỗi ở chat %s", msg.chat_id)
            self.stats.incr("errors")
            await self._say(msg.chat_id, ERROR_REPLY)
            return
        self.usage.add(reply.tokens)
        self.stats.incr("tokens", reply.tokens)
        self.stats.incr("replied")
        names = {msg.from_name, *(t.name for t in turns), *self.filter.names()}
        text = strip_name_prefix(to_plain_text(reply.text), names)
        if members:
            text = add_tags(text, prompt, members)  # model hay quên "@" trước tên người cần tag
        self.history.append(msg.chat_id, "model", text)
        await self._say(msg.chat_id, text)

        if msg.is_group and not was_over and self._over_budget():
            log.warning("Đã vượt hạn mức token ngày: %d", self.usage.used_today())
            if self.groups.get(msg.chat_id).mode == MODE_ALL and self.usage.mark_notified(msg.chat_id):
                await self._say(msg.chat_id, BUDGET_NOTICE)

    # ---------- gửi tin ----------

    async def _send(self, chat_id: str, text: str) -> None:
        for chunk in split_message(text):
            await self._send_chunk(chat_id, chunk)

    async def _send_chunk(self, chat_id: str, text: str) -> None:
        delay = self.retry_delay
        last_error = ""
        for attempt in range(1, self.send_retries + 1):
            try:
                await self.zalo.send_message(chat_id, text)
                return
            except ZaloError as exc:
                last_error = str(exc)
                log.warning("Gửi tin lỗi (lần %d/%d) chat=%s: %s", attempt, self.send_retries, chat_id, exc)
            if attempt < self.send_retries:
                await asyncio.sleep(delay)
                delay *= 2
        self.failed.add(chat_id, text, last_error)
        self.stats.incr("errors")
        log.error("Bỏ cuộc gửi tin tới chat %s, đã lưu vào failed.txt", chat_id)


def strip_name_prefix(text: str, names: set[str]) -> str:
    """Model hay bắt chước dạng "Tên: nội dung" của lịch sử và trả "An: ...": bỏ phần "Tên:" ở đầu."""
    for name in sorted((n.strip() for n in names if n and n.strip()), key=len, reverse=True):
        match = re.match(rf"\s*{re.escape(name)}\s*:\s*", text, re.IGNORECASE)
        if match and text[match.end():].strip():
            return text[match.end():]
    return text
