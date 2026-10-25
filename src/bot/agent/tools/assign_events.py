"""Bot lịch: giao / sửa / huỷ lịch cho những người được nhắc trong nhóm Zalo.

Mỗi người nhận lịch trong Google Lịch của chính họ qua web app iforgotmywayhome (đăng nhập Gmail, liên kết Zalo
bằng mã 6 số nhắn riêng cho bot). Bot chỉ báo cho web (bot lịch) ai nhận lịch gì; web ghi lệnh vào hàng của từng
người và ghi log. Bật khi có SCHEDULE_API_KEY. Ai được giao lịch: ASSIGN_ALLOWED (owner = chỉ chủ bot, all = mọi
người), chỉnh được trên web.

Người nhận lấy từ @tag thật trong tin, rồi tới tên khớp (không phân biệt dấu) với danh sách thành viên nhóm.
Bot nhớ các lịch đã giao trong userdata/data/assigned_events.txt để sửa / huỷ "lịch lúc nãy".

API của web (src/calbot.js của quanlythoigian):
  POST   /assign        {title, start, end?, allDay?, note?, assignees: [{zaloUid, name}], source}
  PATCH  /assign/{id}   {title?, start?, end?, allDay?, note?, add?: [...], remove?: [...]}
  DELETE /assign/{id}
  GET    /assign/{id}   tình trạng: ai đã liên kết, app của ai đã lấy lệnh
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from bot.agent.tools import Tool, ToolContext
from bot.core.text_fold import fold
from bot.core.vietnam_time import VN_TZ, now_ms
from bot.storage.text_files import JsonLinesFile
from bot.system import server_client
from bot.userdata_paths import ASSIGNED_EVENTS_FILE

KEEP = 500
ONLY_SELF = ("Bạn là basic-user: chỉ thêm được lịch cho chính mình (không @tag hay giao cho người khác, không giao cho đội). "
             "Nhờ leader giao việc, hoặc owner dùng /add leader @tên để cho phép.")
NO_PERMISSION = ONLY_SELF  # tên cũ, giữ cho test và tool tự viết
NOT_YOURS = "Bạn chỉ sửa / huỷ được lịch do chính bạn tạo cho chính bạn. Nhờ leader xử lý lịch này."
SELF_WORDS = {"toi", "minh", "tui", "me", "ban than", "chinh toi", "chinh minh"}
_TIME_HINT = ("ISO 8601 kèm múi giờ Việt Nam, ví dụ 2026-10-30T14:00:00+07:00 (tính từ ngày giờ trong phần Bối cảnh). "
              "Lịch cả ngày: YYYY-MM-DD và ca_ngay=true.")


# ---------- người nhận ----------

def match_member(name: str, members: dict[str, str]) -> list[str]:
    """ID thành viên khớp tên (không phân biệt hoa thường, dấu): trùng hẳn, rồi trùng một từ, rồi đầu tên."""
    target = fold(name).strip()
    if not target:
        return []
    folded = {uid: fold(n).strip() for uid, n in members.items() if n}
    for test in (lambda n: n == target, lambda n: target in n.split(), lambda n: n.startswith(target)):
        found = [uid for uid, n in folded.items() if test(n)]
        if found:
            return found
    return []


def resolve_people(ctx: ToolContext, names: list[str] | None, *, use_mentions: bool = True,
                   include_sender: bool = False, teams: list[str] | None = None) -> tuple[list[dict[str, str]], list[str]]:
    """([{zaloUid, name}], tên không tìm được). @tag thật trong tin được ưu tiên, sau đó tới tên khớp thành viên.

    `teams`: tên các đội của nhóm (/team); thành viên mỗi đội được cộng vào, tên đội không có thì vào danh sách không tìm thấy.
    """
    people: dict[str, str] = {}
    team_missing: list[str] = []
    for raw in teams or []:
        key = fold(str(raw or "")).strip()
        key = key.removeprefix("nhom ").strip()
        uids = ctx.teams.get(key)
        if uids is None:
            team_missing.append(f"đội {raw}")
            continue
        for uid in uids:
            people[uid] = ctx.members.get(uid) or uid
    if use_mentions:
        for uid in ctx.mentions:
            if uid and uid != ctx.self_id:
                people[uid] = ctx.members.get(uid) or uid
    tagged = [fold(n) for n in people.values()]
    missing: list[str] = []
    for raw in names or []:
        name = str(raw or "").strip().lstrip("@").strip()
        if not name:
            continue
        found = match_member(name, ctx.members)
        if len(found) == 1:
            people.setdefault(found[0], ctx.members[found[0]])
        elif not any(fold(name) in t for t in tagged):  # đã có trong số người được @tag thì thôi
            missing.append(name if not found else f"{name} (trùng tên nhiều người, hãy @tag)")
    if include_sender and ctx.user_id:
        people.setdefault(ctx.user_id, ctx.user_name)
    people.pop(ctx.self_id, None)
    return [{"zaloUid": uid, "name": name} for uid, name in people.items()], missing + team_missing


# ---------- lịch đã giao (nhớ để sửa / huỷ) ----------

def _store(ctx: ToolContext) -> JsonLinesFile | None:
    return JsonLinesFile(Path(ctx.data_dir) / ASSIGNED_EVENTS_FILE) if ctx.data_dir else None


def _remember(ctx: ToolContext, event_id: str, event: dict[str, Any], assignees: list[dict[str, str]]) -> None:
    store = _store(ctx)
    if store is None:
        return
    records = [r for r in store.read_all() if r.get("eventId") != event_id]
    old = next((r for r in store.read_all() if r.get("eventId") == event_id), {})
    records.append({
        **old, "eventId": event_id, "chatId": ctx.chat_id, "title": event.get("title"), "start": event.get("start"),
        "end": event.get("end"), "allDay": bool(event.get("allDay")), "assignees": assignees,
        "by": old.get("by") or ctx.user_id, "createdAt": old.get("createdAt") or now_ms(), "updatedAt": now_ms(),
        "cancelled": False,
    })
    store.rewrite(records[-KEEP:])


def _forget(ctx: ToolContext, event_id: str) -> None:
    store = _store(ctx)
    if store is None:
        return
    records = store.read_all()
    for r in records:
        if r.get("eventId") == event_id:
            r["cancelled"] = True
            r["updatedAt"] = now_ms()
    store.rewrite(records)


def recent_in_chat(ctx: ToolContext, n: int = 5) -> list[dict[str, Any]]:
    store = _store(ctx)
    if store is None:
        return []
    records = [r for r in store.read_all() if r.get("chatId") == ctx.chat_id and not r.get("cancelled")]
    return records[-n:][::-1]


def _is_own(ctx: ToolContext, record: dict[str, Any]) -> bool:
    """Lịch do chính người này tạo và chỉ giao cho chính họ (basic chỉ sửa / huỷ được loại này)."""
    uids = {a.get("zaloUid") for a in record.get("assignees", [])}
    return record.get("by") == ctx.user_id and uids <= {ctx.user_id}


def _event_id(ctx: ToolContext, args: dict[str, Any]) -> tuple[str | None, str | None]:
    """(mã lịch, lỗi). Basic chỉ được chọn lịch của chính mình."""
    given = str(args.get("ma_lich") or "").strip()
    if ctx.can_assign:
        if given:
            return given, None
        latest = recent_in_chat(ctx, 1)
        return (latest[0]["eventId"] if latest else None), None
    own = [r for r in recent_in_chat(ctx, KEEP) if _is_own(ctx, r)]
    if given:
        return (given, None) if any(r["eventId"] == given for r in own) else (None, NOT_YOURS)
    return (own[0]["eventId"] if own else None), None


def _event_fields(args: dict[str, Any]) -> dict[str, Any]:
    body: dict[str, Any] = {}
    for src, dst in (("tieu_de", "title"), ("bat_dau", "start"), ("ket_thuc", "end"), ("ghi_chu", "note")):
        if args.get(src) not in (None, ""):
            body[dst] = args[src]
    if args.get("ca_ngay") is not None:
        body["allDay"] = bool(args["ca_ngay"])
    return body


def _names(people: list[dict[str, Any]]) -> list[str]:
    return [p.get("name") or p.get("zaloUid") for p in people]


OPS = {"create": "thêm vào lịch", "update": "cập nhật lịch", "delete": "xoá khỏi lịch"}


def _summary(result: dict[str, Any], missing: list[str], *, show_op: bool = False) -> dict[str, Any]:
    unlinked = _names(result.get("unlinked", []))
    out = {
        "ok": True,
        "ma_lich": result.get("eventId"),
        "lich": result.get("event"),
        "da_giao": [f"{a.get('name') or a.get('zaloUid')}" + (f" ({OPS.get(a.get('op'), a.get('op'))})" if show_op else "")
                    for a in result.get("assigned", [])],
        "chua_lien_ket": unlinked,
    }
    if unlinked:
        out["huong_dan_chua_lien_ket"] = (
            f"Người chưa liên kết mở {result.get('appUrl') or 'web app iforgotmywayhome'}, đăng nhập Gmail, "
            "lấy mã 6 số rồi nhắn riêng mã đó cho bot. Sau đó sửa lịch (sua_lich) để giao lại cho họ."
        )
    if missing:
        out["khong_tim_thay"] = missing
    return out


# ---------- tool ----------

async def _assign(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    teams = [str(t) for t in (args.get("nhom") or [])]
    if ctx.can_assign:
        assignees, missing = resolve_people(ctx, args.get("nguoi_nhan"), include_sender=bool(args.get("gom_nguoi_gui")),
                                            teams=teams)
    else:
        # Basic: chỉ lịch cho chính mình. Người nêu tên / @tag / đội khác người gửi thì từ chối, không đoán ý.
        named = [n for n in (args.get("nguoi_nhan") or []) if fold(str(n or "")).strip().lstrip("@") not in SELF_WORDS
                 and str(n or "").strip()]
        others, missing = resolve_people(ctx, named, teams=teams)
        if teams or missing or any(p["zaloUid"] != ctx.user_id for p in others):
            return {"error": ONLY_SELF}
        assignees = [{"zaloUid": ctx.user_id, "name": ctx.user_name}]
    if not assignees:
        hint = f" Không tìm thấy: {', '.join(missing)}." if missing else ""
        return {"error": "Không rõ giao cho ai: hãy @tag người nhận trong tin." + hint}
    body = {
        **_event_fields(args), "assignees": assignees,
        "source": {"chatId": ctx.chat_id, "chatName": ctx.chat_name or None, "senderId": ctx.user_id,
                   "senderName": ctx.user_name, "messageId": ctx.message_id},
    }
    result = await server_client.request("POST", "/assign", json=body)
    if "error" in result:
        return {"error": result["error"]}
    _remember(ctx, result["eventId"], result.get("event") or body, assignees)
    return _summary(result, missing)


async def _update(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    if not ctx.can_assign and (args.get("them_nguoi") or args.get("bo_nguoi")):
        return {"error": ONLY_SELF}
    event_id, denied = _event_id(ctx, args)
    if denied:
        return {"error": denied}
    if not event_id:
        return {"error": "Chưa có lịch nào được giao trong nhóm này để sửa."}
    body = _event_fields(args)
    add, missing_add = resolve_people(ctx, args.get("them_nguoi"), use_mentions=False,
                                      include_sender=bool(args.get("gom_nguoi_gui")))
    remove, missing_remove = resolve_people(ctx, args.get("bo_nguoi"), use_mentions=False)
    if add:
        body["add"] = add
    if remove:
        body["remove"] = [{"zaloUid": p["zaloUid"]} for p in remove]
    if not body:
        return {"error": "Không có gì để sửa: cần giờ mới, tiêu đề mới, hoặc người thêm / bớt."}
    result = await server_client.request("PATCH", f"/assign/{quote(event_id, safe='')}", json=body)
    if "error" in result:
        return {"error": result["error"]}
    record = next((r for r in recent_in_chat(ctx, KEEP) if r.get("eventId") == event_id), {})
    assignees = [p for p in record.get("assignees", []) if p.get("zaloUid") not in {r["zaloUid"] for r in remove}]
    assignees += [p for p in add if p["zaloUid"] not in {a.get("zaloUid") for a in assignees}]
    _remember(ctx, event_id, result.get("event") or {}, assignees)
    return _summary(result, missing_add + missing_remove, show_op=True)


async def _cancel(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    event_id, denied = _event_id(ctx, args)
    if denied:
        return {"error": denied}
    if not event_id:
        return {"error": "Chưa có lịch nào được giao trong nhóm này để huỷ."}
    result = await server_client.request("DELETE", f"/assign/{quote(event_id, safe='')}")
    if "error" in result:
        return {"error": result["error"]}
    _forget(ctx, event_id)
    return {"ok": True, "ma_lich": event_id, "da_huy": result.get("event", {}).get("title"),
            "xoa_khoi_lich_cua": _names(result.get("assigned", []))}


async def _list(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    try:
        n = max(1, min(10, int(args.get("so_luong") or 5)))
    except (TypeError, ValueError):
        n = 5
    items = []
    for r in recent_in_chat(ctx, n):
        item = {"ma_lich": r["eventId"], "tieu_de": r.get("title"), "bat_dau": r.get("start"), "ca_ngay": r.get("allDay"),
                "nguoi_nhan": _names(r.get("assignees", []))}
        status = await server_client.request("GET", f"/assign/{quote(r['eventId'], safe='')}", timeout=10)
        if "error" not in status:
            item["da_vao_app"] = [a.get("name") or a.get("zaloUid") for a in status.get("assignees", []) if a.get("fetchedAt")]
            item["chua_lien_ket"] = [a.get("name") or a.get("zaloUid") for a in status.get("assignees", []) if not a.get("linked")]
        items.append(item)
    return {"lich_da_giao": items} if items else {"lich_da_giao": [], "ghi_chu": "Chưa giao lịch nào trong nhóm này."}


def _start_dt(record: dict[str, Any]) -> datetime | None:
    raw = str(record.get("start") or "")
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=VN_TZ)  # "2026-11-02" (cả ngày) tính theo giờ Việt Nam


async def _mine(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    """Lịch sắp tới của chính người hỏi (trong mọi nhóm), lấy từ các lịch bot đã giao, không hỏi lại web."""
    try:
        n = max(1, min(10, int(args.get("so_luong") or 5)))
    except (TypeError, ValueError):
        n = 5
    store = _store(ctx)
    now = datetime.now(VN_TZ)
    upcoming: list[tuple[datetime, dict[str, Any]]] = []
    for r in (store.read_all() if store else []):
        if r.get("cancelled") or ctx.user_id not in {a.get("zaloUid") for a in r.get("assignees", [])}:
            continue
        start = _start_dt(r)
        if start is not None and (start >= now or (r.get("allDay") and start.date() >= now.date())):
            upcoming.append((start, r))
    upcoming.sort(key=lambda x: x[0])
    items = [{"ma_lich": r["eventId"], "tieu_de": r.get("title"), "bat_dau": r.get("start"), "ca_ngay": r.get("allDay")}
             for _, r in upcoming[:n]]
    return {"lich_cua_toi": items} if items else {"lich_cua_toi": [], "ghi_chu": "Bạn chưa có lịch nào sắp tới qua bot."}


_EVENT_PROPS = {
    "tieu_de": {"type": "string", "description": "Tên lịch ngắn gọn, ví dụ 'Họp kế hoạch quý IV'"},
    "bat_dau": {"type": "string", "description": "Thời điểm bắt đầu, " + _TIME_HINT},
    "ket_thuc": {"type": "string", "description": "Thời điểm kết thúc (không bắt buộc), " + _TIME_HINT},
    "ca_ngay": {"type": "boolean", "description": "true nếu là lịch cả ngày, không có giờ"},
    "ghi_chu": {"type": "string", "description": "Địa điểm, link, ghi chú (không bắt buộc)"},
}
_PEOPLE = {"type": "array", "items": {"type": "string"}}


def _tools() -> list[Tool]:
    if not server_client.configured():
        return []
    return [
        Tool(
            name="giao_lich",
            description=(
                "Giao lịch (họp, hẹn, việc có giờ) cho người được @tag, được nhắc tên, hoặc cho cả một đội (tham số nhom). "
                "Leader / owner giao được cho người khác; basic-user chỉ thêm được lịch cho CHÍNH MÌNH (bỏ trống nguoi_nhan). "
                "Lịch tự vào Google Lịch của từng người qua app iforgotmywayhome. Sau khi giao, trả lời trong nhóm: "
                "ai đã nhận, ai chưa liên kết app (nhắc họ làm theo huong_dan_chua_lien_ket), ai không tìm thấy."
            ),
            handler=_assign,
            parameters={
                "type": "object",
                "properties": {
                    **_EVENT_PROPS,
                    "nguoi_nhan": {**_PEOPLE, "description": "Tên những người nhận như trong tin (không cần @). "
                                                             "Người được @tag thật luôn được tính, kể cả khi bỏ sót ở đây."},
                    "nhom": {**_PEOPLE, "description": "Tên các đội (đặt bằng /team) được giao: mọi thành viên đội đều nhận lịch. "
                                                       "Chỉ leader / owner."},
                    "gom_nguoi_gui": {"type": "boolean", "description": "true nếu người gửi tin cũng nhận lịch (vd 'giao cho tôi và An')"},
                },
                "required": ["tieu_de", "bat_dau"],
            },
        ),
        Tool(
            name="sua_lich",
            description=(
                "Sửa lịch đã giao: đổi giờ, tiêu đề, ghi chú, thêm hoặc bớt người nhận. Không có ma_lich thì sửa lịch "
                "giao gần nhất trong nhóm này ('dời cuộc họp lúc nãy sang 10h'). Người bị bớt sẽ bị xoá lịch khỏi Google Lịch."
            ),
            handler=_update,
            parameters={
                "type": "object",
                "properties": {
                    "ma_lich": {"type": "string", "description": "Mã lịch (từ giao_lich / lich_da_giao); bỏ trống = lịch gần nhất"},
                    **_EVENT_PROPS,
                    "them_nguoi": {**_PEOPLE, "description": "Tên người được thêm vào lịch"},
                    "bo_nguoi": {**_PEOPLE, "description": "Tên người bị bỏ khỏi lịch"},
                    "gom_nguoi_gui": {"type": "boolean", "description": "true nếu thêm chính người gửi tin"},
                },
            },
        ),
        Tool(
            name="huy_lich",
            description="Huỷ lịch đã giao: xoá khỏi Google Lịch của mọi người đã nhận. Không có ma_lich thì huỷ lịch giao gần nhất trong nhóm này.",
            handler=_cancel,
            parameters={"type": "object", "properties": {"ma_lich": {"type": "string"}}},
        ),
        Tool(
            name="lich_cua_toi",
            description="Xem các lịch sắp tới của chính người đang nhắn (đã được giao qua bot, ở mọi nhóm). Ai cũng dùng được.",
            handler=_mine,
            parameters={"type": "object", "properties": {"so_luong": {"type": "integer", "description": "Số lịch (1–10), mặc định 5"}}},
        ),
        Tool(
            name="lich_da_giao",
            description="Xem các lịch đã giao gần đây trong nhóm này (mã lịch, giờ, người nhận, ai đã nhận vào app). Dùng trước khi sửa / huỷ khi không rõ lịch nào.",
            handler=_list,
            parameters={"type": "object", "properties": {"so_luong": {"type": "integer", "description": "Số lịch (1–10), mặc định 5"}}},
        ),
    ]


TOOLS = _tools()
