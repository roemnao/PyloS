"""Lõi bot: quyết định có trả lời tin hay không, xếp hàng theo từng chat và gửi trả lời."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Protocol

from bot.agent import Agent, PromptBuilder, ToolContext, Turn
from bot.commands import CommandHandler, parse_command
from bot.config import Settings
from bot.ratelimit import RateLimiter
from bot.storage import (
    MODE_ALL,
    ActivityStore,
    FailedStore,
    GroupStore,
    HistoryStore,
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
    prompt: str


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

        if not msg.is_text:
            if not msg.is_group:
                await self._send(msg.chat_id, NON_TEXT_REPLY)
            return

        prompt = self._addressed_prompt(msg)
        if prompt is None:
            return
        if not prompt:
            await self._send(msg.chat_id, EMPTY_PROMPT_REPLY)
            return

        if not self.user_limiter.allow(f"{msg.chat_id}:{msg.from_id}") or not self.chat_limiter.allow(msg.chat_id):
            log.warning("Vượt giới hạn tần suất: chat=%s user=%s", msg.chat_id, msg.from_id)
            return

        self._enqueue(Job(msg, prompt))

    def _is_owner(self, user_id: str) -> bool:
        return bool(self.settings.owner_zalo_id) and user_id == self.settings.owner_zalo_id

    def _chat_allowed(self, msg: IncomingMessage, is_owner: bool) -> bool:
        if not msg.is_group and is_owner:
            return True  # chat riêng với chủ bot luôn được phép
        return self.groups.is_allowed(msg.chat_id, self.settings.allow_all_chats)

    def _over_budget(self) -> bool:
        budget = self.settings.daily_token_budget
        return budget > 0 and self.usage.used_today() >= budget

    def _addressed_prompt(self, msg: IncomingMessage) -> str | None:
        """Nội dung cần trả lời, hoặc None nếu theo chế độ hiện tại thì không trả lời."""
        text = (msg.text or "").strip()
        if not msg.is_group:
            return text
        mode = self.groups.get(msg.chat_id).mode
        if mode == MODE_ALL and not self._over_budget():
            stripped = self._strip_trigger(text)
            return stripped if stripped is not None else text
        return self._strip_trigger(text)

    def _strip_trigger(self, text: str) -> str | None:
        lowered = text.lower()
        for trigger in self.settings.bot_triggers:
            t = trigger.lower()
            if lowered == t:
                return ""
            if lowered.startswith(t) and not lowered[len(t)].isalnum():
                return text[len(t):].lstrip(" ,:;-\t\n")
        return None

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
        try:
            await self.zalo.send_chat_action(msg.chat_id, "typing")
        except Exception as exc:  # noqa: BLE001 - chỉ là hiệu ứng "đang gõ"
            log.debug("sendChatAction lỗi: %s", exc)

        self.history.append(msg.chat_id, "user", job.prompt, uid=msg.from_id, name=msg.from_name)
        records = self.history.recent(msg.chat_id, self.settings.history_turns)
        turns = [Turn(r.get("role", "user"), str(r.get("text", "")), str(r.get("name", ""))) for r in records]
        ctx = ToolContext(msg.chat_id, msg.from_id, msg.from_name, self._is_owner(msg.from_id))
        system = self.prompts.build(is_group=msg.is_group, tool_names=self.tool_names)

        was_over = self._over_budget()
        try:
            reply = await self.agent.reply(system, turns, ctx)
        except Exception:
            log.exception("Agent lỗi ở chat %s", msg.chat_id)
            self.stats.incr("errors")
            await self._send(msg.chat_id, ERROR_REPLY)
            return
        self.usage.add(reply.tokens)
        self.stats.incr("tokens", reply.tokens)
        self.stats.incr("replied")
        text = to_plain_text(reply.text)
        self.history.append(msg.chat_id, "model", text)
        await self._send(msg.chat_id, text)

        if msg.is_group and not was_over and self._over_budget():
            log.warning("Đã vượt hạn mức token ngày: %d", self.usage.used_today())
            if self.groups.get(msg.chat_id).mode == MODE_ALL and self.usage.mark_notified(msg.chat_id):
                await self._send(msg.chat_id, BUDGET_NOTICE)

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
