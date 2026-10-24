"""Chạy bot trên một tài khoản Zalo cá nhân (acc phụ) qua thư viện không chính thức zlapi.

Khác Zalo Bot Platform: không có token. Bot đăng nhập bằng phiên (IMEI + cookies) có được
khi quét mã QR (bot/zalo/qrlogin.py), nhận tin qua websocket (như Zalo Web) và trả lời dưới tên acc đó.
Cách này không được Zalo hỗ trợ chính thức: acc có thể bị khoá, thư viện có thể hỏng
khi Zalo đổi giao thức. Chỉ dùng acc phụ.

zlapi là thư viện đồng bộ (requests + websocket-client), nên:
- vòng nghe chạy trong một luồng riêng, đẩy tin về event loop bằng run_coroutine_threadsafe;
- gửi tin chạy qua asyncio.to_thread để không chặn event loop.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

from bot.config import ConfigError, Settings
from bot.core.mentions import build_mentions
from bot.storage import ActivityStore, MemoryDataStore, StateStore
from bot.core.timeutil import now_ms
from bot.zalo.client import ZaloError
from bot.zalo.models import TEXT_EVENT, IncomingMessage

log = logging.getLogger(__name__)

# Sự kiện cho tin không phải chữ (ảnh, sticker, file...): Bot chỉ cần biết nó không phải TEXT_EVENT.
OTHER_EVENT = "message.other.received"
HEARTBEAT_SECONDS = 60
MEMBERS_TTL_SECONDS = 3600  # làm mới danh sách thành viên nhóm mỗi giờ
RELOGIN_HINT = "Quét mã QR lại: `python -m bot zalo-login` hoặc giao diện quản lý → Cài đặt."


def load_session(path: Path, imei: str = "") -> tuple[dict[str, str], str, str]:
    """Đọc file phiên đăng nhập, trả về (cookies, imei, user_agent).

    Nhận các dạng:
    - file do `python -m bot zalo-login` / giao diện tạo: {"imei", "user_agent", "cookies": {...}};
    - cookies chép tay: {"tên": "giá trị"} hoặc danh sách [{"name", "value"}] (xuất từ extension).
    IMEI trong file (đi cùng cookies khi quét QR) được ưu tiên hơn ZALO_IMEI.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(
            f"Chưa đăng nhập acc Zalo cá nhân (không thấy {path}). "
            "Chạy `python -m bot zalo-login` hoặc vào giao diện quản lý → Cài đặt → Đăng nhập bằng mã QR."
        ) from None
    except ValueError as exc:
        raise ConfigError(f"File phiên Zalo {path} không phải JSON hợp lệ: {exc}") from None
    user_agent = ""
    if isinstance(raw, dict) and isinstance(raw.get("cookies"), (list, dict)):
        imei = str(raw.get("imei") or "") or imei
        user_agent = str(raw.get("user_agent") or "")
        raw = raw["cookies"]
    if isinstance(raw, list):
        raw = {str(c.get("name")): str(c.get("value", "")) for c in raw if isinstance(c, dict) and c.get("name")}
    if not isinstance(raw, dict) or not raw:
        raise ConfigError(f"File phiên Zalo {path} rỗng hoặc sai định dạng")
    if not imei:
        raise ConfigError("Thiếu IMEI: đăng nhập lại bằng mã QR, hoặc điền ZALO_IMEI trong userdata/config/.env.")
    return {str(k): str(v) for k, v in raw.items()}, imei, user_agent


def to_incoming(
    mid: Any, author_id: Any, content: Any, message_object: Any, thread_id: Any, is_group: bool, self_id: str
) -> IncomingMessage | None:
    """Đổi tham số onMessage của zlapi thành IncomingMessage dùng chung với Bot."""
    if author_id in (None, "") or thread_id in (None, ""):
        return None
    obj = message_object if message_object is not None else {}
    get = obj.get if hasattr(obj, "get") else (lambda _key, default=None: default)
    text = content if isinstance(content, str) else None
    author = str(author_id)
    try:
        date_ms = int(get("ts")) if get("ts") not in (None, "") else None
    except (TypeError, ValueError):
        date_ms = None
    return IncomingMessage(
        event_name=TEXT_EVENT if text is not None else OTHER_EVENT,
        chat_id=str(thread_id),
        chat_type="GROUP" if is_group else "PRIVATE",
        from_id=author,
        from_name=str(get("dName") or author),
        # Tin do chính acc này gửi (từ điện thoại hoặc do bot trả lời) phải bỏ qua, nếu không bot tự trả lời mình mãi.
        from_is_bot=bool(self_id) and author == self_id,
        text=text,
        message_id=str(mid) if mid not in (None, "") else None,
        date_ms=date_ms,
        raw={"personal": True},
        mentions=_mention_ids(get("mentions")),
    )


def _mention_list(value: Any) -> list[Any]:
    """Tin nhóm có @tag: message_object.mentions = [{"uid", "pos", "len", "type"}, ...]."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return []
    return [m for m in value if hasattr(m, "get") and m.get("uid") not in (None, "")] if isinstance(value, list) else []


def _mention_ids(value: Any) -> tuple[str, ...]:
    return tuple(str(m.get("uid")) for m in _mention_list(value))


def mention_names(text: str, value: Any) -> dict[str, str]:
    """{uid: tên} đọc từ các @tag trong tin người khác gửi (pos/len tính theo UTF-16)."""
    encoded = text.encode("utf-16-le")
    names = {}
    for m in _mention_list(value):
        try:
            pos, length = int(m.get("pos")), int(m.get("len"))
        except (TypeError, ValueError):
            continue
        if str(m.get("uid")) == "-1" or length <= 1:
            continue  # @All
        name = encoded[pos * 2:(pos + length) * 2].decode("utf-16-le", errors="ignore").lstrip("@").strip()
        if name:
            names[str(m.get("uid"))] = name
    return names


def _import_zlapi():
    try:
        import zlapi  # noqa: F401
        from zlapi.models import Message, ThreadType
    except ImportError:
        raise ConfigError(
            "RECEIVE_MODE=personal cần thư viện zlapi. Cài bằng: pip install -e \".[personal]\""
        ) from None
    return zlapi.ZaloAPI, Message, ThreadType


class PersonalZalo:
    """Gửi/nhận tin bằng acc Zalo cá nhân. Có cùng send_message/send_chat_action như ZaloClient."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._api: Any = None
        self._message_cls: Any = None
        self._thread_type_cls: Any = None
        # Zalo cá nhân gửi tin nhóm và tin riêng bằng hai API khác nhau, nên phải biết chat_id là loại nào.
        self._activity = ActivityStore(settings.data_dir / "activity.txt")
        self._connected = False
        self._handler: Callable[[IncomingMessage], Awaitable[None]] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._memory = MemoryDataStore(settings.data_dir / "memorydata")
        self._group_members: dict[str, tuple[float, dict[str, str]]] = {}  # chat_id -> (lúc lấy, {uid: tên})
        self._learned: dict[str, dict[str, str]] = {}  # chat_id -> {uid: tên} đọc từ các @tag người khác gửi
        self.self_id = ""
        self.self_name = ""

    def login(self) -> None:
        """Đăng nhập bằng cookies (chạy đồng bộ, gọi qua asyncio.to_thread)."""
        api_cls, self._message_cls, self._thread_type_cls = _import_zlapi()
        cookies, imei, user_agent = load_session(self.settings.zalo_session_file, self.settings.zalo_imei)
        owner = self

        class _Client(api_cls):
            def onListening(self) -> None:  # noqa: N802 - tên do zlapi đặt
                owner._connected = True
                log.info("Đã kết nối websocket Zalo cá nhân, đang nghe tin")

            def onMessage(self, mid=None, author_id=None, message=None, message_object=None,  # noqa: N802
                          thread_id=None, thread_type=None) -> None:
                owner._on_message(mid, author_id, message, message_object, thread_id, thread_type)

            def onErrorCallBack(self, error, ts=None) -> None:  # noqa: N802
                log.warning("zlapi lỗi: %s", error)

        try:
            self._api = _Client(imei=imei, cookies=cookies, user_agent=user_agent or None)
        except Exception as exc:  # noqa: BLE001 - zlapi ném nhiều loại lỗi khác nhau
            if _is_network_error(exc):
                raise ZaloError("Không kết nối được Zalo (lỗi mạng), sẽ thử lại", network=True) from None
            raise ZaloError(f"Đăng nhập Zalo cá nhân thất bại: {exc}. {RELOGIN_HINT}") from None
        self.self_id = str(self._api.uid() or "")
        if not self.self_id:
            raise ZaloError(f"Đăng nhập Zalo cá nhân thất bại: phiên đã hết hạn. {RELOGIN_HINT}")
        try:
            profile = self._api.fetchAccountInfo().profile
            self.self_name = str(profile.get("displayName") or profile.get("zaloName") or "")
        except Exception:  # noqa: BLE001 - chỉ để ghi log
            pass

    # ---------- nhận tin ----------

    def _on_message(self, mid, author_id, content, message_object, thread_id, thread_type) -> None:
        is_group = thread_type is not None and getattr(thread_type, "name", "") == "GROUP"
        msg = to_incoming(mid, author_id, content, message_object, thread_id, is_group, self.self_id)
        if msg is None:
            return
        if is_group and msg.text and msg.mentions:
            # Người khác tag ai đó: nhớ tên + uid người đó để bot tag lại được, kể cả khi không lấy được danh sách nhóm.
            get = message_object.get if hasattr(message_object, "get") else (lambda _k, _d=None: None)
            self._learned.setdefault(msg.chat_id, {}).update(mention_names(msg.text, get("mentions")))
        handler, loop = self._handler, self._loop
        if handler is None or loop is None:
            return
        future = asyncio.run_coroutine_threadsafe(handler(msg), loop)
        future.add_done_callback(_log_failure)

    async def run(
        self, handle: Callable[[IncomingMessage], Awaitable[None]], state: StateStore, stop: asyncio.Event
    ) -> None:
        """Nghe tin tới khi `stop` được đặt. Ghi last_poll_at định kỳ để `health`/giao diện biết bot còn sống."""
        self._handler, self._loop = handle, asyncio.get_running_loop()
        # Không dùng thread=True của zlapi: xử lý đã được đẩy sang event loop nên onMessage trả về ngay.
        listener = threading.Thread(target=self._listen_forever, args=(stop,), name="zalo-personal", daemon=True)
        listener.start()
        try:
            while not stop.is_set() and listener.is_alive():
                if self._connected:
                    state.update(last_poll_at=now_ms())
                try:
                    await asyncio.wait_for(stop.wait(), timeout=HEARTBEAT_SECONDS)
                except asyncio.TimeoutError:
                    pass
            if not listener.is_alive() and not stop.is_set():
                log.error("Luồng nghe tin Zalo cá nhân đã dừng")
        finally:
            self.close()

    def _listen_forever(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                # run_forever của websocket-client tự nối lại sau `reconnect` giây khi rớt mạng.
                self._api.listen(reconnect=5)
            except Exception:  # noqa: BLE001
                log.exception("Vòng nghe Zalo cá nhân lỗi, thử lại sau 10 giây")
            self._connected = False
            if stop.is_set():
                break
            threading.Event().wait(10)

    def close(self) -> None:
        ws = getattr(self._api, "ws", None)
        timer = getattr(self._api, "ping_interval", None)
        if timer is not None:
            timer.cancel()
        if ws is not None:
            try:
                ws.close()
            except Exception:  # noqa: BLE001
                pass

    # ---------- gửi tin ----------

    def _thread_type(self, chat_id: str) -> Any:
        # Bot ghi loại chat vào activity.txt mỗi khi nhận tin, nên vẫn biết sau khi khởi động lại.
        kind = str(self._activity.all().get(chat_id, {}).get("type", "")).upper()
        return self._thread_type_cls.GROUP if kind == "GROUP" else self._thread_type_cls.USER

    # ---------- thành viên nhóm (để tag) ----------

    def _fetch_group_members(self, chat_id: str) -> dict[str, str]:
        info = self._api.fetchGroupInfo(chat_id)
        grid = ((info.get("gridInfoMap") or {}) if hasattr(info, "get") else {}).get(str(chat_id)) or {}
        names: dict[str, str] = {}
        for member in grid.get("currentMems") or []:
            if hasattr(member, "get") and member.get("id"):
                names[str(member["id"])] = str(member.get("dName") or member.get("zaloName") or "")
        uids = [str(v).split("_")[0] for v in grid.get("memVerList") or []]
        missing = [uid for uid in uids if not names.get(uid)]
        for start in range(0, len(missing), 100):
            profiles = self._api.fetchUserInfo(missing[start:start + 100])
            changed = (profiles.get("changed_profiles") if hasattr(profiles, "get") else None) or {}
            for uid, profile in changed.items():
                if hasattr(profile, "get"):
                    names[str(uid)] = str(profile.get("displayName") or profile.get("zaloName") or "")
        return {uid: name for uid, name in names.items() if name}

    def members(self, chat_id: str) -> dict[str, str]:
        """{uid: tên} của người trong nhóm: danh sách thành viên từ Zalo (lưu 1 giờ) + người đã nhắn gần đây."""
        known: dict[str, str] = {}
        cached = self._group_members.get(chat_id)
        if self._api is not None and self._thread_type(chat_id) == self._thread_type_cls.GROUP:
            if cached is None or time.monotonic() - cached[0] > MEMBERS_TTL_SECONDS:
                try:
                    cached = (time.monotonic(), self._fetch_group_members(chat_id))
                    log.info("Đã lấy %d thành viên của nhóm %s", len(cached[1]), chat_id)
                except Exception as exc:  # noqa: BLE001 - không lấy được thì dùng người đã nhắn
                    log.info("Không lấy được thành viên nhóm %s: %s", chat_id, exc)
                    cached = (time.monotonic(), cached[1] if cached else {})
                self._group_members[chat_id] = cached
            known.update(cached[1])
        known.update(self._learned.get(chat_id, {}))
        for record in self._memory.recent(chat_id, 2000):
            if record.get("role") == "user" and record.get("uid") and record.get("name"):
                known[str(record["uid"])] = str(record["name"])  # tên mới nhất người đó dùng
        known.pop(self.self_id, None)
        return known

    async def send_message(self, chat_id: str, text: str) -> Any:
        def send() -> Any:
            thread_type = self._thread_type(chat_id)
            mention = None
            if thread_type == self._thread_type_cls.GROUP and "@" in text:
                found = build_mentions(text, self.members(chat_id))
                if found:
                    mention = json.dumps(found)
                    log.info("Tag %d người trong nhóm %s", len(found), chat_id)
                else:
                    log.info("Tin có '@' nhưng không khớp thành viên nào đã biết của nhóm %s", chat_id)
            return self._api.send(self._message_cls(text=text, mention=mention), chat_id, thread_type)

        try:
            result = await asyncio.to_thread(send)
        except Exception as exc:  # noqa: BLE001
            raise ZaloError(f"Gửi tin Zalo cá nhân lỗi: {exc}", network=True) from None
        if isinstance(result, dict) and result.get("error_code"):
            raise ZaloError(str(result.get("error_message") or result), result.get("error_code"))
        return result

    async def send_chat_action(self, chat_id: str, action: str = "typing") -> None:
        await asyncio.to_thread(self._api.setTyping, chat_id, self._thread_type(chat_id))

    async def aclose(self) -> None:
        self.close()


def _is_network_error(exc: BaseException) -> bool:
    """zlapi bọc lỗi mạng của requests thành ZaloLoginError, nên phải lần theo chuỗi nguyên nhân."""
    import requests

    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, (requests.RequestException, OSError)):
            return True
        current = current.__cause__ or current.__context__
    # Một số chỗ zlapi chỉ giữ lại thông điệp của lỗi gốc.
    return any(word in str(exc) for word in ("HTTPSConnectionPool", "ConnectionError", "Max retries exceeded"))


def _log_failure(future: Any) -> None:
    exc = future.exception()
    if exc is not None:
        log.error("Lỗi xử lý tin Zalo cá nhân: %s", exc)
