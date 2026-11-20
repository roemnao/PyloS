"""Tool tao_anh: bot tạo ảnh từ lời mô tả (model theo nhiệm vụ `image` trong modelShift.md, key theo model_keys.md).

Tool tạo ảnh, lưu vào túp lều của chat (tự xoá cùng ảnh người dùng gửi) rồi đưa vào ToolContext.outbox;
Bot gửi ảnh vào chat sau khi model trả lời. Tool ẩn khỏi model khi IMAGE_GEN tắt hoặc chưa có key dùng được."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from pylos.gate.fence.token_limit.image_limit import ImageLimit
from pylos.gate.main_gate.media.media_store import hut_media_dir
from pylos.lobby.dispatch.shared.data_stores import DailyCounter
from pylos.lobby.dispatch.shared.userdata_paths import IMAGE_USAGE_FILE
from pylos.lobby.office.agent_tools import OutgoingImage, Tool, ToolContext
from pylos.lobby.office.model_calls import ModelCallError

MAX_PROMPT = 1000
MAX_CAPTION = 300


@dataclass
class ImageConfig:
    enabled: bool = False
    steps: int = 4
    timeout: float = 60
    calls: Any = None  # ModelCalls (lobby/office/model_calls)
    task: Callable[[], tuple[str, tuple[str, ...]]] | None = None  # () -> (model, model dự phòng) của nhiệm vụ image
    limit: ImageLimit | None = None
    limit_path: Any = None  # file đếm ảnh trong ngày; đổi thì dựng bộ đếm mới


CONFIG = ImageConfig()


def configure(settings: Any, *, model_calls: Any = None, task: Callable[[], tuple[str, tuple[str, ...]]] | None = None) -> None:
    """Gọi lúc dựng bot (có model_calls và task) và mỗi khi đổi cấu hình (chỉ settings, xem Bot.apply_settings)."""
    CONFIG.enabled = bool(settings.image_gen)
    CONFIG.steps = int(settings.image_steps)
    CONFIG.timeout = float(settings.llm_timeout_seconds)
    if model_calls is not None:
        CONFIG.calls = model_calls
    if task is not None:
        CONFIG.task = task
    path = settings.data_dir / IMAGE_USAGE_FILE
    if CONFIG.limit is None or CONFIG.limit_path != path:
        CONFIG.limit, CONFIG.limit_path = ImageLimit(DailyCounter(path), settings.image_per_day, settings.user_images_per_hour), path
    else:
        CONFIG.limit.per_day, CONFIG.limit.per_user_hour = settings.image_per_day, settings.user_images_per_hour


def ready() -> bool:
    """Bật và model của nhiệm vụ image có key dùng được trong model_keys.md."""
    if not CONFIG.enabled or CONFIG.calls is None or CONFIG.task is None or CONFIG.limit is None:
        return False
    return CONFIG.calls.resolve(CONFIG.task()[0]) is not None


async def _create(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    prompt = str(args.get("prompt") or "").strip()
    if not prompt:
        return {"error": "Thiếu prompt."}
    if not ready() or ctx.huts_dir is None:
        return {"error": "Tạo ảnh chưa dùng được."}
    refused = CONFIG.limit.check(ctx.user_id)
    if refused:
        return {"error": refused}
    model, fallbacks = CONFIG.task()
    try:
        result = await CONFIG.calls.generate_image(prompt[:MAX_PROMPT], model, fallbacks=fallbacks,
                                                   steps=CONFIG.steps, timeout=CONFIG.timeout)
    except ModelCallError as exc:
        return {"error": f"Không tạo được ảnh: {exc}"}
    folder = hut_media_dir(ctx.huts_dir, ctx.chat_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"gen_{int(time.time() * 1000)}{result.extension}"
    path.write_bytes(result.data)
    CONFIG.limit.record(ctx.user_id)
    ctx.outbox.append(OutgoingImage(path, str(args.get("caption") or "").strip()[:MAX_CAPTION]))
    return {"ok": True, "model": result.model,
            "ghi_chu": "Ảnh đã tạo xong và sẽ được gửi kèm câu trả lời của bạn. Chỉ cần trả lời ngắn, đừng tả lại ảnh dài dòng."}


TOOLS = [
    Tool(
        name="tao_anh",
        description=(
            "Tạo một ảnh mới từ lời mô tả và gửi vào cuộc trò chuyện. Dùng khi người dùng nhờ vẽ, tạo, thiết kế một hình ảnh. "
            "Không dùng để sửa ảnh người dùng gửi. Mỗi lần gọi tạo đúng một ảnh; có hạn mức mỗi ngày."
        ),
        handler=_create,
        parameters={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Mô tả ảnh bằng TIẾNG ANH, chi tiết: chủ thể, bối cảnh, phong cách, ánh sáng."},
                "caption": {"type": "string", "description": "Chú thích ngắn bằng tiếng Việt gửi kèm ảnh (không bắt buộc)."},
            },
            "required": ["prompt"],
        },
        enabled=ready,
    ),
]
