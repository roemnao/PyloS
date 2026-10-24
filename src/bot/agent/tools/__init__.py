"""Registry công cụ cho agent.

Thêm tool mới: tạo một file .py trong thư mục này (tên không bắt đầu bằng "_")
và khai báo biến TOOLS = [Tool(...), ...]. Không cần sửa vòng lặp agent.
Xem _example.py để có mẫu.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import pkgutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolContext:
    chat_id: str
    user_id: str
    user_name: str
    is_owner: bool


Handler = Callable[[dict[str, Any], ToolContext], Any | Awaitable[Any]]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Handler
    # JSON Schema cho tham số, ví dụ {"type": "object", "properties": {...}, "required": [...]}
    parameters: dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})
    # Tool ghi/xóa hoặc nhạy cảm: chỉ chủ bot được gọi, kiểm tra ở đây chứ không tin lời model.
    owner_only: bool = False


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool trùng tên: {tool.name}")
        self._tools[tool.name] = tool

    def __len__(self) -> int:
        return len(self._tools)

    def names(self) -> list[str]:
        return list(self._tools)

    def declarations(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description, "parameters_json_schema": t.parameters}
            for t in self._tools.values()
        ]

    async def call(self, name: str, args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
        """Luôn trả về dict để đưa lại cho model; lỗi cũng được báo cho model thay vì làm sập."""
        tool = self._tools.get(name)
        if tool is None:
            return {"error": f"Không có tool tên {name}"}
        if tool.owner_only and not ctx.is_owner:
            return {"error": "Chỉ chủ bot được dùng tool này."}
        try:
            result = tool.handler(args, ctx)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:  # noqa: BLE001 - lỗi tool trả về cho model
            log.exception("Tool %s lỗi", name)
            return {"error": f"{type(exc).__name__}: {exc}"}
        return result if isinstance(result, dict) else {"result": result}


def _load_external(directory: Path, registry: ToolRegistry) -> None:
    """Nạp tool từ thư mục tools/ bên ngoài (cạnh ZaloBot.exe), vì trong exe không thêm file .py được."""
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        name = f"bot_user_tools.{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            for tool in getattr(module, "TOOLS", []):
                registry.register(tool)
        except Exception:  # noqa: BLE001 - một tool hỏng không được làm sập bot
            log.exception("Không nạp được tool %s", path)


def discover(external_dir: Path | None = None) -> ToolRegistry:
    """Nạp mọi module có biến TOOLS: trong package này, và trong thư mục tools/ của APP_HOME."""
    registry = ToolRegistry()
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        for tool in getattr(module, "TOOLS", []):
            registry.register(tool)
    if external_dir is None:
        from bot.config import APP_HOME

        external_dir = APP_HOME / "tools"
    if external_dir.is_dir():
        _load_external(external_dir, registry)
    if len(registry):
        log.info("Đã nạp tool: %s", ", ".join(registry.names()))
    return registry
