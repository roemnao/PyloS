"""Server giao diện quản lý: FastAPI, chỉ lắng nghe 127.0.0.1.

Bảo mật (PLAN.md mục 11.5):
- Mọi /api/* cần header `Authorization: Bearer <ADMIN_TOKEN>`.
- Header Host phải là 127.0.0.1/localhost đúng cổng (chặn DNS rebinding).
- Yêu cầu ghi có Origin thì Origin phải là chính trang này; không bật CORS.
- API không bao giờ trả về token/khóa; chỉ trả "đã đặt / chưa đặt".
- Trang tĩnh có CSP chặt: chỉ chạy script/style của chính nó.
"""

from __future__ import annotations

import asyncio
import hmac
import logging
import os
import re
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from bot import gateway
from bot.admin import envfile
from bot.agent import EchoAgent, GeminiAgent, PromptBuilder, ToolContext, Turn, discover
from bot.config import ConfigError, Settings
from bot.storage import (
    MODES,
    ActivityStore,
    FailedStore,
    GroupStore,
    HistoryStore,
    StatsStore,
    UsageStore,
    atomic_write_text,
)
from bot.text import split_message
from bot.timeutil import now_ms, now_vn
from bot.zalo import ZaloClient, ZaloError

log = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
WORKSPACE_FILES = {"SYSTEM": "SYSTEM.md", "MEMORY": "MEMORY.md"}
MAX_WORKSPACE_CHARS = 200_000
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_LOG_LINE = re.compile(r"^\d{4}-\d{2}-\d{2} [\d:,]+ (DEBUG|INFO|WARNING|ERROR|CRITICAL) ")

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


class AdminContext:
    """Đọc lại .env ở mỗi yêu cầu để trang Cài đặt có hiệu lực ngay trong giao diện."""

    def __init__(self, env_path: Path, base_dir: Path) -> None:
        self.env_path = env_path
        self.base_dir = base_dir

    def settings(self) -> Settings:
        return Settings.from_env({**os.environ, **envfile.read_values(self.env_path)}, base_dir=self.base_dir)


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status, headers=SECURITY_HEADERS)


def create_app(ctx: AdminContext, port: int) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    allowed_origins = {f"http://{h}" for h in allowed_hosts}

    @app.middleware("http")
    async def guard(request: Request, call_next):
        if request.headers.get("host", "") not in allowed_hosts:
            return _error(400, "Host không hợp lệ. Hãy mở bằng http://127.0.0.1:%d" % port)
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            origin = request.headers.get("origin")
            if origin is not None and origin not in allowed_origins:
                return _error(403, "Origin không hợp lệ")
            if request.headers.get("sec-fetch-site") == "cross-site":
                return _error(403, "Yêu cầu từ trang khác bị chặn")
        if request.url.path.startswith("/api/"):
            try:
                token = ctx.settings().admin_token
            except ConfigError as exc:
                return _error(500, f"Lỗi cấu hình .env: {exc}")
            supplied = request.headers.get("authorization", "")
            if not token or not hmac.compare_digest(supplied.encode(), f"Bearer {token}".encode()):
                return _error(401, "Sai hoặc thiếu mã truy cập")
        response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        return response

    @app.exception_handler(ConfigError)
    async def config_error(request: Request, exc: ConfigError) -> JSONResponse:
        return _error(400, str(exc))

    # ---------- trang tĩnh ----------

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # ---------- tổng quan & điều khiển ----------

    @app.get("/api/status")
    def status() -> dict[str, Any]:
        settings = ctx.settings()
        info = gateway.status_info(settings)
        alerts = []
        if not info["zalo_token_set"]:
            alerts.append("Chưa đặt ZALO_BOT_TOKEN (trang Cài đặt).")
        if not info["gemini_key_set"]:
            alerts.append("Chưa đặt GEMINI_API_KEY (trang Cài đặt).")
        if not info["owner_set"]:
            alerts.append("Chưa đặt OWNER_ZALO_ID: chưa ai dùng được lệnh /allow, /mode trên Zalo.")
        if info["failed_pending"]:
            alerts.append(f"{info['failed_pending']} tin gửi lỗi chưa xử lý (trang Tin lỗi).")
        last_poll = info.get("last_poll_at")
        if info["running"] and settings.receive_mode == "polling" and last_poll and now_ms() - int(last_poll) > 180_000:
            alerts.append("Bot đang chạy nhưng hơn 3 phút chưa nhận được phản hồi từ Zalo (mất mạng?).")
        if info["token_budget"] and info["tokens_today"] >= info["token_budget"]:
            alerts.append("Đã hết hạn mức token hôm nay: nhóm chế độ all đang chạy như default.")
        return {
            **info,
            "alerts": alerts,
            "days": StatsStore(settings.data_dir / "stats.txt").days(14),
            "show_history": settings.admin_show_history,
            "now": now_ms(),
        }

    @app.post("/api/bot/{action}")
    def control(action: str) -> dict[str, Any]:
        settings = ctx.settings()
        actions = {"start": gateway.start, "stop": gateway.stop, "restart": gateway.restart}
        if action not in actions:
            raise HTTPException(404, "Không có thao tác này")
        try:
            result = actions[action](settings, gateway.BOT)
        except ConfigError as exc:
            return {"ok": False, "message": f"Lỗi cấu hình: {exc}"}
        return {"ok": result.ok, "message": result.message}

    # ---------- nhóm ----------

    def _groups(settings: Settings) -> GroupStore:
        return GroupStore(settings.data_dir / "groups.txt")

    @app.get("/api/groups")
    def list_groups() -> dict[str, Any]:
        settings = ctx.settings()
        store = _groups(settings)
        groups = {g.chat_id: g for g in store.all()}
        activity = ActivityStore(settings.data_dir / "activity.txt").all()
        rows = []
        for chat_id in set(groups) | set(activity):
            g = groups.get(chat_id)
            seen = activity.get(chat_id) or {}
            chat_type = str(seen.get("type") or ("GROUP" if g else "?"))
            rows.append({
                "chat_id": chat_id,
                "type": chat_type,
                "label": g.label if g else "",
                "allowed": store.is_allowed(chat_id, settings.allow_all_chats),
                "blocked": bool(g and g.blocked),
                "mode": g.mode if g else "default",
                "last_seen": seen.get("last_seen"),
                "last_name": seen.get("last_name", ""),
                "owner_private": chat_type == "PRIVATE" and chat_id == settings.owner_zalo_id,
            })
        rows.sort(key=lambda r: -(r["last_seen"] or 0))
        return {"groups": rows, "modes": list(MODES), "allow_all": settings.allow_all_chats}

    @app.patch("/api/groups/{chat_id}")
    def update_group(chat_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        settings = ctx.settings()
        store = _groups(settings)
        if not chat_id or len(chat_id) > 120:
            raise HTTPException(400, "chat_id không hợp lệ")
        if "allowed" in body:
            store.set_allowed(chat_id, bool(body["allowed"]))
        if "mode" in body:
            if body["mode"] not in MODES:
                raise HTTPException(400, "Chế độ phải là all hoặc default")
            store.set_mode(chat_id, body["mode"])
        if "label" in body:
            store.set_label(chat_id, str(body["label"]))
        state = store.get(chat_id)
        return {"chat_id": chat_id, "allowed": state.allowed, "mode": state.mode, "label": state.label}

    @app.delete("/api/groups/{chat_id}/history")
    def clear_history(chat_id: str) -> dict[str, Any]:
        HistoryStore(ctx.settings().data_dir / "history").clear(chat_id)
        return {"ok": True}

    @app.get("/api/history/{chat_id}")
    def history(chat_id: str, n: int = 100) -> dict[str, Any]:
        settings = ctx.settings()
        if not settings.admin_show_history:
            raise HTTPException(403, "Trang Hội thoại đang tắt (ADMIN_SHOW_HISTORY=false).")
        records = HistoryStore(settings.data_dir / "history").recent(chat_id, max(1, min(n, 500)))
        return {"chat_id": chat_id, "messages": [
            {"role": r.get("role"), "name": r.get("name", ""), "text": r.get("text", ""), "t": r.get("t")}
            for r in records
        ]}

    # ---------- chỉ dẫn (workspace .md) ----------

    def _workspace_path(settings: Settings, name: str) -> Path:
        if name not in WORKSPACE_FILES:
            raise HTTPException(404, "Chỉ sửa được SYSTEM hoặc MEMORY")
        return settings.workspace_dir / WORKSPACE_FILES[name]

    @app.get("/api/workspace/{name}")
    def read_workspace(name: str) -> dict[str, Any]:
        path = _workspace_path(ctx.settings(), name)
        try:
            return {"name": name, "content": path.read_text(encoding="utf-8"), "updated_at": int(path.stat().st_mtime * 1000)}
        except FileNotFoundError:
            return {"name": name, "content": "", "updated_at": None}

    @app.put("/api/workspace/{name}")
    def write_workspace(name: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        path = _workspace_path(ctx.settings(), name)
        content = body.get("content")
        if not isinstance(content, str) or len(content) > MAX_WORKSPACE_CHARS:
            raise HTTPException(400, "Nội dung không hợp lệ hoặc quá dài")
        if path.is_file():
            backup_dir = path.parent / ".backup"
            atomic_write_text(backup_dir / f"{name}-{now_vn():%Y%m%d-%H%M%S}.md", path.read_text(encoding="utf-8"))
            for old in sorted(backup_dir.glob(f"{name}-*.md"))[:-20]:
                old.unlink(missing_ok=True)
        atomic_write_text(path, content.replace("\r\n", "\n"))
        return {"ok": True, "updated_at": int(path.stat().st_mtime * 1000)}

    # ---------- cài đặt ----------

    @app.get("/api/settings")
    def read_settings() -> dict[str, Any]:
        values = envfile.read_values(ctx.env_path)
        settings = ctx.settings()
        defaults = {
            "GEMINI_MODEL": settings.gemini_model, "BOT_TRIGGERS": ",".join(settings.bot_triggers),
            "RECEIVE_MODE": settings.receive_mode, "LOG_LEVEL": settings.log_level,
            "ADMIN_SHOW_HISTORY": "true" if settings.admin_show_history else "false",
            "ALLOW_ALL_CHATS": "true" if settings.allow_all_chats else "false",
        }
        return {
            "fields": [
                {"key": f.key, "label": f.label, "help": f.help, "kind": f.kind, "choices": list(f.choices),
                 "group": f.group, "value": values.get(f.key) or defaults.get(f.key, "")}
                for f in envfile.FIELDS
            ],
            "secrets": [{"key": k, "label": label, "set": bool(values.get(k))} for k, label in envfile.SECRETS.items()],
        }

    @app.put("/api/settings")
    def write_settings(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        changes = body.get("values")
        if not isinstance(changes, dict) or not changes:
            raise HTTPException(400, "Không có gì để lưu")
        unknown = set(changes) - envfile.FIELD_KEYS
        if unknown:
            raise HTTPException(400, f"Không được sửa: {', '.join(sorted(unknown))}")
        cleaned = envfile.validate(ctx.env_path, {k: str(v) for k, v in changes.items()}, ctx.base_dir)
        envfile.update(ctx.env_path, cleaned)
        return {"ok": True, "message": "Đã lưu. Khởi động lại bot để áp dụng."}

    @app.put("/api/secrets/{key}")
    def write_secret(key: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        if key not in envfile.SECRETS:
            raise HTTPException(404, "Không có khóa này")
        value = body.get("value")
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(400, "Giá trị trống")
        cleaned = envfile.validate(ctx.env_path, {key: value}, ctx.base_dir)
        envfile.update(ctx.env_path, cleaned)
        return {"ok": True, "set": True, "message": f"Đã đặt {key}. Khởi động lại bot để áp dụng."}

    # ---------- log ----------

    def _log_path(settings: Settings, source: str) -> Path:
        service = {"bot": gateway.BOT, "admin": gateway.ADMIN}.get(source)
        if service is None:
            raise HTTPException(404, "Nguồn log phải là bot hoặc admin")
        return settings.log_dir / service.log_file

    @app.get("/api/logs")
    def logs(source: str = "bot", n: int = 200, level: str = "") -> dict[str, Any]:
        path = _log_path(ctx.settings(), source)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except FileNotFoundError:
            return {"entries": []}
        entries: list[dict[str, str]] = []
        for line in lines[-5000:]:
            match = _LOG_LINE.match(line)
            if match or not entries:
                entries.append({"level": match.group(1) if match else "INFO", "text": line})
            else:
                entries[-1]["text"] += "\n" + line  # dòng tiếp theo của traceback
        level = level.upper()
        if level in LOG_LEVELS:
            minimum = LOG_LEVELS.index(level)
            entries = [e for e in entries if LOG_LEVELS.index(e["level"]) >= minimum]
        return {"entries": entries[-max(1, min(n, 2000)):]}

    @app.get("/api/logs/stream")
    async def stream_logs(request: Request, source: str = "bot") -> StreamingResponse:
        path = _log_path(ctx.settings(), source)

        async def tail():
            position = path.stat().st_size if path.is_file() else 0
            idle = 0.0
            while not await request.is_disconnected():
                size = path.stat().st_size if path.is_file() else 0
                if size < position:  # file vừa được xoay vòng
                    position = 0
                if size > position:
                    with open(path, "rb") as fh:
                        fh.seek(position)
                        chunk = fh.read(size - position)
                    position = size
                    idle = 0.0
                    yield chunk.decode("utf-8", errors="replace")
                elif idle >= 15:
                    idle = 0.0
                    yield "\n"  # giữ kết nối
                await asyncio.sleep(0.7)
                idle += 0.7

        return StreamingResponse(tail(), media_type="text/plain; charset=utf-8")

    # ---------- tin lỗi ----------

    def _failed(settings: Settings) -> FailedStore:
        return FailedStore(settings.data_dir / "failed.txt")

    @app.get("/api/failed")
    def failed() -> dict[str, Any]:
        return {"items": _failed(ctx.settings()).pending()}

    @app.post("/api/failed/{failed_id}/{action}")
    async def failed_action(failed_id: str, action: str) -> dict[str, Any]:
        settings = ctx.settings()
        store = _failed(settings)
        item = next((r for r in store.pending() if r["id"] == failed_id), None)
        if item is None:
            raise HTTPException(404, "Không tìm thấy tin này (có thể đã xử lý)")
        if action == "dismiss":
            store.mark_done(failed_id, "dismissed")
            return {"ok": True, "message": "Đã bỏ qua."}
        if action != "retry":
            raise HTTPException(404, "Không có thao tác này")
        settings.require(zalo=True, gemini=False)
        client = ZaloClient(settings.zalo_bot_token)
        try:
            for chunk in split_message(str(item.get("text", ""))):
                await client.send_message(str(item["chat_id"]), chunk)
        except ZaloError as exc:
            return {"ok": False, "message": f"Gửi lại thất bại: {exc}"}
        finally:
            await client.aclose()
        store.mark_done(failed_id, "resent")
        return {"ok": True, "message": "Đã gửi lại."}

    # ---------- chat thử & tool ----------

    @app.post("/api/playground")
    async def playground(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        settings = ctx.settings()
        messages = body.get("messages")
        if not isinstance(messages, list) or not messages or len(messages) > 40:
            raise HTTPException(400, "Danh sách tin không hợp lệ")
        turns = []
        for m in messages:
            text = str((m or {}).get("text", ""))[:4000]
            role = "model" if (m or {}).get("role") == "model" else "user"
            turns.append(Turn(role, text, "" if role == "model" else str((m or {}).get("name") or "Bạn")[:40]))
        tools = discover()
        if settings.gemini_api_key:
            agent: Any = GeminiAgent(
                settings.gemini_api_key, settings.gemini_model, tools,
                max_tool_rounds=settings.max_tool_rounds, max_output_tokens=settings.max_output_tokens,
                timeout_seconds=settings.llm_timeout_seconds,
            )
        else:
            agent = EchoAgent()
        system = PromptBuilder(settings.workspace_dir).build(is_group=bool(body.get("is_group")), tool_names=tools.names())
        ctx_tool = ToolContext("admin-playground", settings.owner_zalo_id or "admin", "Chủ bot", is_owner=True)
        try:
            reply = await agent.reply(system, turns, ctx_tool)
        except Exception as exc:  # noqa: BLE001 - báo lỗi Gemini cho người dùng
            log.exception("Chat thử lỗi")
            return {"ok": False, "reply": "", "tokens": 0, "message": f"Gemini lỗi: {type(exc).__name__}: {exc}"}
        # Token là chi phí thật nên vẫn tính vào hạn mức ngày, nhưng không ghi vào lịch sử nhóm nào.
        UsageStore(settings.data_dir / "usage.txt").add(reply.tokens)
        StatsStore(settings.data_dir / "stats.txt").incr("tokens", reply.tokens)
        return {"ok": True, "reply": reply.text, "tokens": reply.tokens, "echo": not settings.gemini_api_key}

    @app.get("/api/tools")
    def tools() -> dict[str, Any]:
        registry = discover()
        return {"tools": [
            {"name": d["name"], "description": d["description"]} for d in registry.declarations()
        ]}

    return app
