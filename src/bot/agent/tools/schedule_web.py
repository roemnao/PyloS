"""Tool nối với web Quản lý thời gian (quanlythoigian) qua API cho AI agent của web.

Bật khi có SCHEDULE_API_KEY (tạo ở web: Cài đặt → Kết nối AI agent → Tạo khoá cho agent).
Lịch/việc tạo ở đây hiện trên web, tự lên Google Lịch (nếu web đã kết nối) và được bot Zalo
của web nhắc trước giờ hẹn.

API (src/app.js của quanlythoigian), xác thực bằng "Authorization: Bearer <khoá>":
  POST  /events        {title, start, end?, allDay?, note?}
  POST  /tasks         {title, deadline?, quadrant?, note?}
  GET   /tasks
  PATCH /tasks/{id}    {done?, ...}
  GET   /agenda?date=today|tomorrow|YYYY-MM-DD
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

from bot.agent.tools import Tool, ToolContext
from bot.system.server_client import DEFAULT_URL, base_url, env_values, request, server_config  # noqa: F401

log = logging.getLogger(__name__)


def _config() -> tuple[str, str]:
    return server_config()


async def _request(method: str, path: str, *, json: Any = None, params: dict[str, str] | None = None) -> Any:
    result = await request(method, path, json=json, params=params)
    if isinstance(result, dict) and "error" in result:
        return {"error": result["error"]}
    return result


def _note(args: dict[str, Any], ctx: ToolContext) -> str:
    note = str(args.get("note") or "").strip()
    who = f"Tạo qua Zalo bởi {ctx.user_name}"
    return f"{note}\n{who}" if note else who


async def _create_event(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    body = {"title": args.get("title"), "start": args.get("start"), "note": _note(args, ctx)}
    for key in ("end", "allDay"):
        if args.get(key) not in (None, ""):
            body[key] = args[key]
    result = await _request("POST", "/events", json=body)
    return result if "error" in result else {"ok": True, "event": result}


async def _create_task(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    body = {"title": args.get("title"), "note": _note(args, ctx)}
    for key in ("deadline", "quadrant"):
        if args.get(key) not in (None, ""):
            body[key] = args[key]
    result = await _request("POST", "/tasks", json=body)
    return result if "error" in result else {"ok": True, "task": result}


async def _agenda(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    return await _request("GET", "/agenda", params={"date": str(args.get("date") or "today")})


async def _list_tasks(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    result = await _request("GET", "/tasks")
    return {"tasks": result} if isinstance(result, list) else result


async def _complete_task(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    task_id = str(args.get("id") or "").strip()
    if not task_id:
        return {"error": "Thiếu id việc (lấy bằng danh_sach_viec)."}
    result = await _request("PATCH", f"/tasks/{quote(task_id, safe='')}", json={"done": True})
    return result if "error" in result else {"ok": True, "task": result}


def _owner_only() -> bool:
    return env_values().get("SCHEDULE_OWNER_ONLY", "true").strip().lower() not in ("0", "false", "no", "off", "không")


_TIME_HINT = "ISO 8601 kèm múi giờ Việt Nam, ví dụ 2026-10-30T14:00:00+07:00. Tính từ ngày giờ hiện tại trong phần Bối cảnh."


def _tools() -> list[Tool]:
    if not _config()[1]:
        return []
    owner_only = _owner_only()
    return [
        Tool(
            name="them_lich_hen",
            description=(
                "Thêm lịch hẹn / sự kiện / lời nhắc có giờ cụ thể vào web quản lý thời gian của chủ bot. "
                "Web sẽ nhắc qua Zalo trước giờ hẹn. Dùng khi được bảo thêm lịch, đặt lịch, nhắc lúc mấy giờ."
            ),
            handler=_create_event,
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Tên lịch ngắn gọn, ví dụ 'Họp nhóm', 'Gọi cho mẹ'"},
                    "start": {"type": "string", "description": "Thời điểm bắt đầu, " + _TIME_HINT},
                    "end": {"type": "string", "description": "Thời điểm kết thúc (không bắt buộc), " + _TIME_HINT},
                    "allDay": {"type": "boolean", "description": "true nếu là sự kiện cả ngày, không có giờ"},
                    "note": {"type": "string", "description": "Ghi chú thêm (không bắt buộc)"},
                },
                "required": ["title", "start"],
            },
            owner_only=owner_only,
        ),
        Tool(
            name="them_viec",
            description=(
                "Thêm việc cần làm (to-do) vào web quản lý thời gian, có thể kèm hạn chót. "
                "Dùng cho việc không có giờ hẹn cố định, ví dụ 'nhớ nộp báo cáo trước thứ 6'."
            ),
            handler=_create_task,
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Tên việc"},
                    "deadline": {"type": "string", "description": "Hạn chót (không bắt buộc), " + _TIME_HINT},
                    "quadrant": {"type": "integer", "enum": [1, 2, 3, 4],
                                 "description": "Ma trận Eisenhower: 1 gấp+quan trọng, 2 quan trọng, 3 gấp, 4 khác. Mặc định 2."},
                    "note": {"type": "string", "description": "Ghi chú thêm (không bắt buộc)"},
                },
                "required": ["title"],
            },
            owner_only=owner_only,
        ),
        Tool(
            name="xem_lich",
            description="Xem lịch hẹn và việc đến hạn của một ngày trên web quản lý thời gian.",
            handler=_agenda,
            parameters={
                "type": "object",
                "properties": {"date": {"type": "string", "description": "today, tomorrow hoặc YYYY-MM-DD"}},
            },
            owner_only=owner_only,
        ),
        Tool(
            name="danh_sach_viec",
            description="Liệt kê các việc cần làm chưa xong (kèm id) trên web quản lý thời gian.",
            handler=_list_tasks,
            owner_only=owner_only,
        ),
        Tool(
            name="xong_viec",
            description="Đánh dấu một việc là đã xong. Lấy id bằng danh_sach_viec trước.",
            handler=_complete_task,
            parameters={"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]},
            owner_only=owner_only,
        ),
    ]


TOOLS = _tools()
