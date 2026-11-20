"""Tool tài liệu: bot đọc, tạo, sửa tệp .docx / .md / .txt trong huts/<chat>/docs/ của chính chat đó.

ds_tai_lieu và doc_tai_lieu chỉ đọc (không tính hạn mức); tao_tai_lieu và sua_tai_lieu có hạn mức riêng (DocLimit) và
xếp tệp vào ToolContext.outbox để Bot gửi vào chat sau khi model trả lời. Tool ẩn khi DOC_TOOLS tắt."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from pylos.gate.fence.token_limit.doc_limit import DocLimit
from pylos.lobby.dispatch.shared.data_stores import DailyCounter
from pylos.lobby.dispatch.shared.userdata_paths import DOC_USAGE_FILE
from pylos.lobby.office.agent_tools import OutgoingFile, Tool, ToolContext
from pylos.lobby.office.documents import editor, files, reader, writer
from pylos.lobby.office.documents.files import DocError

log = logging.getLogger(__name__)

MAX_CONTENT = 60000  # ký tự markdown model được ghi trong một lần gọi
MAX_FOLDER_BYTES = 50 * 1024 * 1024  # tổng dung lượng tài liệu của một chat
READ_CHARS = 12000


@dataclass
class DocConfig:
    enabled: bool = False
    keep_days: int = 30
    limit: DocLimit | None = None
    limit_path: Any = None


CONFIG = DocConfig()


def configure(settings: Any) -> None:
    """Gọi lúc dựng bot và mỗi khi đổi cấu hình (Bot.apply_settings)."""
    CONFIG.enabled = bool(settings.doc_tools)
    CONFIG.keep_days = int(settings.doc_keep_days)
    path = settings.data_dir / DOC_USAGE_FILE
    if CONFIG.limit is None or CONFIG.limit_path != path:
        CONFIG.limit, CONFIG.limit_path = DocLimit(DailyCounter(path), settings.docs_per_day, settings.user_docs_per_hour), path
    else:
        CONFIG.limit.per_day, CONFIG.limit.per_user_hour = settings.docs_per_day, settings.user_docs_per_hour


def ready() -> bool:
    return CONFIG.enabled and CONFIG.limit is not None


def _folder(ctx: ToolContext):
    if ctx.huts_dir is None:
        raise DocError("Tài liệu chưa dùng được.")
    folder = files.docs_dir(ctx.huts_dir, ctx.chat_id)
    try:
        files.prune(folder, CONFIG.keep_days)
    except OSError as exc:
        log.warning("Không dọn được thư mục tài liệu %s: %s", folder, exc)
    return folder


def _guard(fn):
    """Đổi DocError thành {"error"} cho model; lỗi lạ ghi log (kết quả tool chỉ về model nên cần log để tra)."""
    async def wrapper(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
        try:
            return fn(args, ctx)
        except DocError as exc:
            return {"error": str(exc)}
        except OSError as exc:
            log.warning("Tool tài liệu lỗi ở chat %s: %s", ctx.chat_id, exc)
            return {"error": f"Không ghi / đọc được tệp: {exc}"}
    return wrapper


def _list(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    docs = files.list_docs(_folder(ctx))
    return {"tai_lieu": [{"ten": d.name, "kich_thuoc_byte": d.size,
                          "sua_luc": time.strftime("%Y-%m-%d %H:%M", time.localtime(d.modified))} for d in docs]}


def _read(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    path = files.existing(_folder(ctx), str(args.get("ten") or ""))
    return reader.read_slice(path, int(args.get("tu_vi_tri") or 0), READ_CHARS)


def _check(ctx: ToolContext, content: str, folder) -> None:
    if len(content) > MAX_CONTENT:
        raise DocError(f"Nội dung quá dài (tối đa {MAX_CONTENT} ký tự một lần). Chia nhỏ rồi dùng sua_tai_lieu thao_tac=them_cuoi.")
    refused = CONFIG.limit.check(ctx.user_id)
    if refused:
        raise DocError(refused)
    if files.folder_size(folder) > MAX_FOLDER_BYTES:
        raise DocError("Thư mục tài liệu của chat này đã đầy, hãy dọn bớt rồi thử lại.")


def _queue(ctx: ToolContext, path, caption: str) -> None:
    CONFIG.limit.record(ctx.user_id)
    ctx.outbox.append(OutgoingFile(path, caption.strip()[:300]))


def _create(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    folder = _folder(ctx)
    content = str(args.get("noi_dung") or "")
    if not content.strip():
        raise DocError("Thiếu nội dung.")
    ext = ".md" if str(args.get("dinh_dang") or "docx").lower() in ("md", "markdown") else ".docx"
    name = str(args.get("ten") or "tai-lieu")
    if not name.lower().endswith(files.ALLOWED):
        name += ext
    _check(ctx, content, folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = files.unique_path(folder, name)  # không ghi đè tệp có sẵn; muốn sửa thì dùng sua_tai_lieu
    if path.suffix == ".docx":
        writer.markdown_to_docx(content, path)
    else:
        path.write_text(content, encoding="utf-8")
    _queue(ctx, path, str(args.get("chu_thich") or ""))
    return {"ok": True, "ten": path.name,
            "ghi_chu": "Tệp đã tạo và sẽ được gửi kèm câu trả lời. Chỉ cần báo ngắn gọn đã làm gì, đừng chép lại toàn bộ nội dung."}


def _edit(args: dict[str, Any], ctx: ToolContext) -> dict[str, Any]:
    folder = _folder(ctx)
    path = files.existing(folder, str(args.get("ten") or ""))
    action = str(args.get("thao_tac") or "")
    content = str(args.get("noi_dung") or "")
    result: dict[str, Any] = {"ok": True, "ten": path.name}
    if action == "hoan_tac":
        editor.restore(path)
        result["ghi_chu"] = "Đã khôi phục bản trước đó."
    elif action == "thay_the":
        find = str(args.get("tim") or "")
        if not find:
            raise DocError("Thiếu 'tim' (chuỗi cần thay).")
        _check(ctx, str(args.get("thay") or ""), folder)
        count = editor.replace_text(path, find, str(args.get("thay") or ""))
        if not count:
            return {"error": f"Không thấy '{find}' trong {path.name}. Gọi doc_tai_lieu để xem đúng chữ rồi thử lại."}
        result["so_cho_da_thay"] = count
    elif action in ("them_cuoi", "ghi_de"):
        if not content.strip():
            raise DocError("Thiếu 'noi_dung'.")
        _check(ctx, content, folder)
        (editor.append_markdown if action == "them_cuoi" else editor.overwrite_markdown)(path, content)
    else:
        raise DocError("thao_tac phải là thay_the, them_cuoi, ghi_de hoặc hoan_tac.")
    if action != "hoan_tac":
        CONFIG.limit.record(ctx.user_id)
    if args.get("gui_lai", True):
        ctx.outbox.append(OutgoingFile(path, ""))
        result["ghi_chu"] = result.get("ghi_chu", "") + " Tệp đã sửa sẽ được gửi kèm câu trả lời. Báo ngắn gọn đã sửa gì."
    return result


TOOLS = [
    Tool(
        name="ds_tai_lieu",
        description="Liệt kê các tệp tài liệu (.docx, .md, .txt) của cuộc trò chuyện này: tệp người dùng đã gửi và tệp bot đã tạo.",
        handler=_guard(_list),
        enabled=ready,
    ),
    Tool(
        name="doc_tai_lieu",
        description=(
            "Đọc nội dung một tệp tài liệu (.docx, .md, .txt) và trả về dạng markdown. Dùng khi người dùng gửi tệp hoặc nhờ xem / tóm tắt / sửa tệp. "
            "Tệp dài thì kết quả có 'doc_tiep_tu_vi_tri': gọi lại với tu_vi_tri đó để đọc tiếp."
        ),
        handler=_guard(_read),
        parameters={
            "type": "object",
            "properties": {
                "ten": {"type": "string", "description": "Tên tệp (xem ds_tai_lieu)."},
                "tu_vi_tri": {"type": "integer", "description": "Vị trí ký tự bắt đầu đọc (mặc định 0)."},
            },
            "required": ["ten"],
        },
        enabled=ready,
    ),
    Tool(
        name="tao_tai_lieu",
        description=(
            "Tạo tệp tài liệu mới từ nội dung markdown rồi gửi vào chat. Dùng khi người dùng nhờ soạn / viết ra một tệp Word (.docx) hoặc Markdown (.md). "
            "Markdown hỗ trợ: # tiêu đề, **đậm**, *nghiêng*, danh sách - và 1., bảng |a|b|, > trích dẫn, ``` khối mã. Có hạn mức mỗi ngày. "
            "Không ghi đè tệp có sẵn (trùng tên thì tự thêm -2); muốn sửa tệp có sẵn thì dùng sua_tai_lieu."
        ),
        handler=_guard(_create),
        parameters={
            "type": "object",
            "properties": {
                "ten": {"type": "string", "description": "Tên tệp, ví dụ bao-cao-thang-11 (đuôi tự thêm theo dinh_dang)."},
                "dinh_dang": {"type": "string", "enum": ["docx", "md"], "description": "docx (Word, mặc định) hoặc md (Markdown)."},
                "noi_dung": {"type": "string", "description": "Toàn bộ nội dung bằng markdown."},
                "chu_thich": {"type": "string", "description": "Chú thích ngắn gửi kèm tệp (không bắt buộc)."},
            },
            "required": ["ten", "noi_dung"],
        },
        enabled=ready,
    ),
    Tool(
        name="sua_tai_lieu",
        description=(
            "Sửa một tệp tài liệu có sẵn rồi gửi lại tệp đã sửa. thao_tac: 'thay_the' (đổi chữ 'tim' thành 'thay', giữ nguyên định dạng), "
            "'them_cuoi' (nối thêm noi_dung markdown vào cuối), 'ghi_de' (viết lại toàn bộ bằng noi_dung markdown), "
            "'hoan_tac' (trả về bản trước lần sửa gần nhất). Nên gọi doc_tai_lieu trước để biết đúng chữ trong tệp. Có hạn mức mỗi ngày."
        ),
        handler=_guard(_edit),
        parameters={
            "type": "object",
            "properties": {
                "ten": {"type": "string", "description": "Tên tệp (xem ds_tai_lieu)."},
                "thao_tac": {"type": "string", "enum": ["thay_the", "them_cuoi", "ghi_de", "hoan_tac"]},
                "tim": {"type": "string", "description": "Chuỗi cần tìm (thay_the)."},
                "thay": {"type": "string", "description": "Chuỗi thay vào (thay_the; rỗng = xoá)."},
                "noi_dung": {"type": "string", "description": "Nội dung markdown (them_cuoi, ghi_de)."},
                "gui_lai": {"type": "boolean", "description": "Gửi tệp đã sửa vào chat (mặc định true)."},
            },
            "required": ["ten", "thao_tac"],
        },
        enabled=ready,
    ),
]
