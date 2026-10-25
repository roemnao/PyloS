"""Lõi bot: quyết định có trả lời tin hay không, xếp hàng theo từng chat và gửi trả lời."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any, Protocol

from bot.agent import Agent, PromptBuilder, ToolContext, Turn
from bot.core.owner_commands import CommandHandler, parse_command
from bot.config import Settings
from bot.core.message_filter import Decision, MessageFilter
from bot.core.mention_tags import add_tags
from bot.core.rate_limiter import RateLimiter
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
from bot.core.reply_formatting import split_message, to_plain_text
from bot.core.vietnam_time import now_ms
from bot.zalo import IncomingMessage, ZaloError, parse_updates
from bot.userdata_paths import (
    BOT_STATUS_FILE,
    CHAT_ACTIVITY_FILE,
    DAILY_STATS_FILE,
    FAILED_REPLIES_FILE,
    GROUP_SETTINGS_FILE,
    MEMORYDATA_DIR,
    PROCESSED_IDS_FILE,
    SESSION_HISTORY_DIR,
    TOKEN_USAGE_FILE,
)

log = logging.getLogger(__name__)

ERROR_REPLY = "Xin lỗi, mình đang gặp lỗi, bạn thử lại sau nhé."
NON_TEXT_REPLY = "Hiện mình chỉ đọc được tin nhắn chữ."
EMPTY_PROMPT_REPLY = "Bạn cần mình giúp gì?"
NO_OWNER_HINT = (
    "Bot chưa có chủ. Nếu bạn là người cài bot, hãy điền OWNER_ZALO_ID={user_id} "
    "vào userdata/config/settings.env (hoặc trang Cài đặt) rồi khởi động lại bot."
)
BUDGET_NOTICE = (
    "Đã dùng hết hạn mức token hôm nay. Đến hết ngày, mình chỉ trả lời "
    "những tin gọi mình (chế độ default)."
)
# Tin riêng chỉ gồm mã 6 số (hoặc "/lienket 123456"): liên kết Zalo với tài khoản trên web app.
LINK_CODE = re.compile(r"^\s*(?:/?li[eê]n\s*k[eế]t\s*:?\s*)?(\d{6})\s*$", re.IGNORECASE)
LINK_OFFLINE = "Chưa liên kết được vì không kết nối được máy chủ. Bạn thử gửi lại mã sau ít phút nhé."
# Tool gửi lệnh cho bot lịch trên web: ghi thêm bước "bot lịch" vào session.
CALBOT_TOOLS = {"giao_lich": "create", "sua_lich": "update", "huy_lich": "delete"}


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
        self.groups = GroupStore(data / GROUP_SETTINGS_FILE, settings.allowed_chat_ids)
        self.seen = SeenStore(settings.system_dir / PROCESSED_IDS_FILE)
        self.history = HistoryStore(data / SESSION_HISTORY_DIR, keep=max(200, settings.history_turns * 4))
        self.state = StateStore(settings.system_dir / BOT_STATUS_FILE)
        self.usage = UsageStore(data / TOKEN_USAGE_FILE)
        self.failed = FailedStore(data / FAILED_REPLIES_FILE)
        self.stats = StatsStore(data / DAILY_STATS_FILE)
        self.activity = ActivityStore(data / CHAT_ACTIVITY_FILE)
        self.memory = MemoryDataStore(data / MEMORYDATA_DIR, keep=settings.memorydata_keep)
        self.filter = MessageFilter(settings, agent, self._self_identity)
        self.commands = CommandHandler(
            self.groups, self.history, self.usage, settings.bot_triggers, settings.daily_token_budget,
            allow_all=settings.allow_all_chats,
        )
        self.user_limiter = RateLimiter(settings.user_rate_per_min)
        self.chat_limiter = RateLimiter(settings.chat_rate_per_min)

        self.started_at_ms = now_ms()
        self.state.update(started_at=self.started_at_ms)
        self.sessions = None  # SessionUploader khi có kết nối web (bot/system/session_upload.py)
        self._queues: dict[str, asyncio.Queue[Job]] = {}
        self._workers: dict[str, asyncio.Task[None]] = {}
        self._warned_no_owner: set[str] = set()
        self._hinted: set[str] = set()

    def apply_settings(self, settings: Settings) -> None:
        """Áp cấu hình mới khi đang chạy (thông số chủ hệ thống đổi trên web), không cần khởi động lại."""
        self.settings = settings
        self.filter.settings = settings
        self.memory.keep = settings.memorydata_keep
        self.history.keep = max(200, settings.history_turns * 4)
        self.commands.triggers = settings.bot_triggers
        self.commands.daily_budget = settings.daily_token_budget
        self.commands.allow_all = settings.allow_all_chats
        self.user_limiter.per_minute = settings.user_rate_per_min
        self.chat_limiter.per_minute = settings.chat_rate_per_min
        if settings.allowed_chat_ids:
            self.groups.allow_seed(settings.allowed_chat_ids)
        configure = getattr(self.agent, "configure", None)
        if configure is not None:
            configure(model=settings.gemini_model, max_tool_rounds=settings.max_tool_rounds,
                      max_output_tokens=settings.max_output_tokens, timeout_seconds=settings.llm_timeout_seconds)

    def _trace(self, chat_id: str, kind: str, **fields: Any) -> None:
        """Ghi một bước vào session gửi lên web (nếu bật). Không bao giờ làm hỏng việc trả lời."""
        if self.sessions is not None and self.settings.session_upload:
            self.sessions.record(chat_id, kind, **fields)

    def _chat_name(self, msg: IncomingMessage) -> str:
        label = self.groups.get(msg.chat_id).label
        if label:
            return label
        lookup = getattr(self.zalo, "chat_name", None)
        name = lookup(msg.chat_id) if lookup is not None else ""
        return name or ("" if msg.is_group else msg.from_name)

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
                "Nếu đây là bạn, điền from_id vào OWNER_ZALO_ID trong userdata/config/settings.env rồi khởi động lại.",
                msg.from_id, msg.from_name, msg.chat_id, msg.chat_type,
            )

        if not msg.is_group and msg.is_text and await self._maybe_link(msg):
            return

        cmd = parse_command(msg.text)
        if cmd is not None:
            # Chưa đặt chủ bot thì chỉ cho /id để lấy ID; người khác gõ lệnh thì bỏ qua.
            if is_owner or (cmd.name == "id" and not self.settings.owner_zalo_id):
                members = await self._members(msg.chat_id) if cmd.name == "leader" and msg.is_group else {}
                await self._send(msg.chat_id, self.commands.handle(cmd, msg, members, self._self_identity()[0]))
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

    async def _maybe_link(self, msg: IncomingMessage) -> bool:
        """Người dùng nhắn mã lấy trong web app: báo web liên kết Zalo này với Gmail của họ. Không tốn token."""
        from bot.system import server_client

        match = LINK_CODE.match(msg.text or "")
        if not match or not server_client.configured():
            return False
        result = await server_client.request("POST", "/zalo-link", timeout=20, json={
            "code": match.group(1), "zaloUid": msg.from_id, "zaloName": msg.from_name,
        })
        if isinstance(result, dict) and "error" in result:
            # Web trả lỗi kèm lời giải thích (mã sai, hết hạn, gửi sai quá nhiều lần); mất mạng thì báo thử lại sau.
            text = (result.get("message") or LINK_OFFLINE) if result.get("status") else LINK_OFFLINE
            log.info("Liên kết Zalo thất bại cho %s: %s", msg.from_id, result["error"])
        else:
            member = result.get("member") or {}
            who = " ".join(x for x in (member.get("name"), f"({member['email']})" if member.get("email") else "") if x)
            text = (f"✅ Đã liên kết Zalo này với tài khoản {who or 'của bạn'}. Từ giờ lịch được giao cho bạn trong nhóm "
                    "sẽ tự vào Google Lịch qua app iforgotmywayhome (nhớ mở app để lịch được cập nhật).")
            log.info("Đã liên kết Zalo %s với tài khoản trên web", msg.from_id)
        self._trace(msg.chat_id, "calbot", op="link", title="Liên kết Zalo", summary=text[:200], chatName=msg.from_name)
        await self._send(msg.chat_id, text)
        return True

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
        self._trace(msg.chat_id, "message", chatName=self._chat_name(msg), isGroup=msg.is_group, senderId=msg.from_id,
                    senderName=msg.from_name, text=msg.text if msg.is_text else "(không phải tin chữ)", messageId=msg.message_id)
        self._trace(msg.chat_id, "filter", decision="reply" if decision.passed else "skip", tier=decision.stage,
                    reason=decision.reason, tokens=decision.tokens or None,
                    model=(self.settings.filter_model or self.settings.gemini_model) if decision.stage == "ai" else None)

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
        members = await self._members(msg.chat_id) if msg.is_group else {}
        is_owner = self._is_owner(msg.from_id)
        self_id, _ = self._self_identity()
        ctx = ToolContext(
            msg.chat_id, msg.from_id, msg.from_name, is_owner, self.settings.data_dir,
            is_group=msg.is_group, chat_name=self._chat_name(msg), message_id=msg.message_id,
            mentions=tuple(m for m in msg.mentions if m != self_id), members=members, self_id=self_id,
            can_assign=is_owner or self.settings.assign_allowed == "all"
            or (msg.is_group and self.groups.can_assign(msg.chat_id, msg.from_id)),
        )
        system = self.prompts.build(is_group=msg.is_group, tool_names=self.tool_names, members=list(members.values()))

        was_over = self._over_budget()
        try:
            reply = await self.agent.reply(system, turns, ctx)
        except Exception as exc:
            log.exception("Agent lỗi ở chat %s", msg.chat_id)
            self.stats.incr("errors")
            self._trace(msg.chat_id, "error", message=f"Agent lỗi: {type(exc).__name__}: {exc}"[:300])
            await self._say(msg.chat_id, ERROR_REPLY)
            return
        self.usage.add(reply.tokens)
        self.stats.incr("tokens", reply.tokens)
        self.stats.incr("replied")
        names = {msg.from_name, *(t.name for t in turns), *self.filter.names()}
        text = strip_name_prefix(to_plain_text(reply.text), names)
        if members:
            text = add_tags(text, prompt, members)  # model hay quên "@" trước tên người cần tag
        self._trace_reply(msg, system, turns, reply, text)
        self.history.append(msg.chat_id, "model", text)
        await self._say(msg.chat_id, text)

        if msg.is_group and not was_over and self._over_budget():
            log.warning("Đã vượt hạn mức token ngày: %d", self.usage.used_today())
            if self.groups.get(msg.chat_id).mode == MODE_ALL and self.usage.mark_notified(msg.chat_id):
                await self._say(msg.chat_id, BUDGET_NOTICE)

    def _trace_reply(self, msg: IncomingMessage, system: str, turns: list[Turn], reply: Any, text: str) -> None:
        if self.sessions is None or not self.settings.session_upload:
            return
        last = "\n".join(f"{t.name or t.role}: {t.text}" for t in turns[-3:])
        self._trace(msg.chat_id, "agent", model=getattr(reply, "model", "") or self.settings.gemini_model,
                    tokens=reply.tokens, ms=getattr(reply, "ms", None), reply=text,
                    prompt=f"{system[:1500]}\n\n--- 3 lượt cuối ---\n{last[:1500]}")
        for step in getattr(reply, "steps", ()):
            self._trace(msg.chat_id, "tool", name=step.name, args=step.args, result=step.result, ms=step.ms)
            op = CALBOT_TOOLS.get(step.name)
            if op and isinstance(step.result, dict) and "error" not in step.result:
                assigned = [a.get("name") or a.get("zaloUid") for a in step.result.get("assigned", [])]
                unlinked = [a.get("name") or a.get("zaloUid") for a in step.result.get("unlinked", [])]
                summary = f"{len(assigned)} người nhận" + (f", {len(unlinked)} chưa liên kết" if unlinked else "")
                self._trace(msg.chat_id, "calbot", op=op, title=(step.result.get("event") or {}).get("title"), summary=summary)
        self._trace(msg.chat_id, "reply", text=text)

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
