"""MẪU tool, không được nạp (tên bắt đầu bằng "_").

Để dùng: sao chép file này trong thư mục tools/ (cạnh ZaloBot.exe) thành ví dụ
`current_time.py` (không có dấu "_" ở đầu), khởi động lại bot, tool sẽ tự được đăng ký.
"""

from bot.agent.tools import Tool, ToolContext
from bot.core.vietnam_time import now_vn


def _current_time(args: dict, ctx: ToolContext) -> dict:
    return {"now": now_vn().strftime("%H:%M %A %d/%m/%Y"), "timezone": "UTC+7"}


TOOLS = [
    Tool(
        name="current_time",
        description="Lấy ngày giờ hiện tại ở Việt Nam.",
        handler=_current_time,
    ),
]
