"""Server giao diện quản lý: FastAPI, chỉ lắng nghe 127.0.0.1.

Bảo mật (PLAN.md mục 11.5):
- Mọi /api/* (trừ /api/auth/*) cần header `Authorization: Bearer <ADMIN_TOKEN>` hoặc token phiên của đăng nhập Gmail
  (web iforgotmywayhome làm chứng, chỉ Gmail của chủ web được nhận; xem /api/auth/gmail/*).
- Header Host phải là 127.0.0.1/localhost đúng cổng (chặn DNS rebinding).
- Yêu cầu ghi có Origin thì Origin phải là chính trang này; không bật CORS.
- API không bao giờ trả về token/khóa; chỉ trả "đã đặt / chưa đặt".
- Trang tĩnh có CSP chặt: chỉ chạy script/style của chính nó.
"""

from __future__ import annotations

import asyncio
import hmac
import json
import logging
import os
import re
import threading
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from bot.system import bot_process, server_client
from bot.ui.admin.admin_sessions import AdminSessions
from bot.system.remote_config import REMOTE_KEYS, read_cached
from bot.ui.admin import settings_file
from bot.agent import EchoAgent, GeminiAgent, PromptBuilder, ToolContext, Turn, discover
from bot.config import ConfigError, Settings
from bot.storage import (
    MODES,
    ActivityStore,
    FailedStore,
    GroupStore,
    HistoryStore,
    MemoryDataStore,
    StatsStore,
    UsageStore,
    atomic_write_text,
)
from bot.core.reply_formatting import split_message
from bot.core.vietnam_time import now_ms, now_vn
from bot.zalo import ZaloClient, ZaloError
from bot.userdata_paths import (
    CHAT_ACTIVITY_FILE,
    DAILY_STATS_FILE,
    FAILED_REPLIES_FILE,
    GROUP_SETTINGS_FILE,
    MEMORYDATA_DIR,
    PENDING_UPDATES_FILE,
    SESSION_HISTORY_DIR,
    TOKEN_USAGE_FILE,
    UPDATE_REQUEST,
)

log = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
WORKSPACE_FILES = {"SYSTEM": "SYSTEM.md", "MEMORY": "MEMORY.md"}
MAX_WORKSPACE_CHARS = 200_000
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_LOG_LINE = re.compile(r"^\d{4}-\d{2}-\d{2} [\d:,]+ (DEBUG|INFO|WARNING|ERROR|CRITICAL) ")

def _remote_text(value: Any) -> str:
    if isinstance(value, bool):
        return "Bật" if value else "Tắt"
    return str(value)


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
        return Settings.from_env({**os.environ, **settings_file.read_values(self.env_path)}, base_dir=self.base_dir)


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status, headers=SECURITY_HEADERS)


def create_app(ctx: AdminContext, port: int) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    allowed_origins = {f"http://{h}" for h in allowed_hosts}
    sessions = AdminSessions()

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
        path = request.url.path
        if path.startswith("/api/") and not path.startswith("/api/auth/"):
            try:
                token = ctx.settings().admin_token
            except ConfigError as exc:
                return _error(500, f"Lỗi cấu hình .env: {exc}")
            supplied = request.headers.get("authorization", "")
            by_token = bool(token) and hmac.compare_digest(supplied.encode(), f"Bearer {token}".encode())
            if not by_token and not sessions.valid(supplied.removeprefix("Bearer ").strip()):
                return _error(401, "Sai hoặc thiếu mã truy cập")
        response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        return response

    @app.exception_handler(ConfigError)
    async def config_error(request: Request, exc: ConfigError) -> JSONResponse:
        return _error(400, str(exc))

    # ---------- đăng nhập bằng Gmail (không cần mã truy cập) ----------

    @app.get("/api/auth/options")
    async def auth_options() -> dict[str, Any]:
        return {"gmail": server_client.configured()}

    @app.post("/api/auth/gmail/start")
    async def gmail_start() -> JSONResponse:
        data = await server_client.request("POST", "/device-login", timeout=15)
        if not isinstance(data, dict) or "error" in data or not data.get("code") or not data.get("url"):
            message = (data or {}).get("message") or (data or {}).get("error") or "Không gọi được web iforgotmywayhome"
            return _error(502, str(message))
        return JSONResponse({"code": data["code"], "url": data["url"], "expiresIn": data.get("expiresIn", 600)},
                            headers=SECURITY_HEADERS)

    @app.post("/api/auth/gmail/poll")
    async def gmail_poll(body: dict[str, Any] = Body(...)) -> JSONResponse:
        code = str(body.get("code") or "")
        if not re.fullmatch(r"[0-9a-f]{32}", code):
            return _error(400, "Mã không hợp lệ")
        data = await server_client.request("GET", f"/device-login/{code}", timeout=15)
        if not isinstance(data, dict) or "error" in data:
            return _error(502, str((data or {}).get("message") or "Không gọi được web iforgotmywayhome"))
        status = data.get("status")
        if status == "approved":
            email = str(data.get("email") or "")
            if not data.get("isAdmin"):
                return JSONResponse({"status": "denied", "message": f"Gmail {email} không phải tài khoản quản trị của web. "
                                     "Đăng nhập bằng đúng Gmail đã liên kết vào tài khoản quản trị."}, headers=SECURITY_HEADERS)
            log.info("Đăng nhập trang quản lý bằng Gmail %s", email)
            return JSONResponse({"status": "ok", "token": sessions.issue(email), "email": email}, headers=SECURITY_HEADERS)
        return JSONResponse({"status": "expired" if status == "expired" else "pending"}, headers=SECURITY_HEADERS)

    # ---------- trang tĩnh ----------

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # ---------- tổng quan & điều khiển ----------

    @app.get("/api/status")
    def status() -> dict[str, Any]:
        settings = ctx.settings()
        info = bot_process.status_info(settings)
        alerts = []
        if settings.personal:
            if not settings.zalo_session_file.is_file():
                alerts.append("Chưa đăng nhập acc Zalo cá nhân: vào Cài đặt → Đăng nhập bằng mã QR.")
        elif not info["zalo_token_set"]:
            alerts.append("Chưa kết nối Zalo: đặt ZALO_BOT_TOKEN, hoặc dùng acc Zalo cá nhân "
                          "(Cài đặt → Đăng nhập bằng mã QR).")
        if not info["gemini_key_set"]:
            alerts.append("Chưa đặt GEMINI_API_KEY (trang Cài đặt).")
        if not info["owner_set"]:
            alerts.append("Chưa đặt OWNER_ZALO_ID: chưa ai dùng được lệnh /allow, /mode trên Zalo.")
        try:
            info["updates_pending"] = int((settings.system_dir / PENDING_UPDATES_FILE).read_text(encoding="utf-8").strip() or 0)
        except (OSError, ValueError):
            info["updates_pending"] = 0
        if info["failed_pending"]:
            alerts.append(f"{info['failed_pending']} tin gửi lỗi chưa xử lý (trang Tin lỗi).")
        last_poll = info.get("last_poll_at")
        if info["running"] and settings.receive_mode in ("polling", "personal") and last_poll and now_ms() - int(last_poll) > 180_000:
            alerts.append("Bot đang chạy nhưng hơn 3 phút chưa nhận được phản hồi từ Zalo (mất mạng?).")
        if info["token_budget"] and info["tokens_today"] >= info["token_budget"]:
            alerts.append("Đã hết hạn mức token hôm nay: nhóm chế độ all đang chạy như default.")
        return {
            **info,
            "alerts": alerts,
            "days": StatsStore(settings.data_dir / DAILY_STATS_FILE).days(14),
            "show_history": settings.admin_show_history,
            "now": now_ms(),
        }

    @app.post("/api/bot/{action}")
    def control(action: str) -> dict[str, Any]:
        settings = ctx.settings()
        actions = {"start": bot_process.start, "stop": bot_process.stop, "restart": bot_process.restart}
        if action not in actions:
            raise HTTPException(404, "Không có thao tác này")
        try:
            result = actions[action](settings, bot_process.BOT)
        except ConfigError as exc:
            return {"ok": False, "message": f"Lỗi cấu hình: {exc}"}
        return {"ok": result.ok, "message": result.message}

    # ---------- nhóm ----------

    def _groups(settings: Settings) -> GroupStore:
        return GroupStore(settings.data_dir / GROUP_SETTINGS_FILE)

    @app.get("/api/groups")
    def list_groups() -> dict[str, Any]:
        settings = ctx.settings()
        store = _groups(settings)
        groups = {g.chat_id: g for g in store.all()}
        activity = ActivityStore(settings.data_dir / CHAT_ACTIVITY_FILE).all()
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
                "leaders": list(g.leaders) if g else [],
                "leaders_all": bool(g and g.leaders_all),
                "teams": [{"name": t["name"], "members": len(t["members"])} for t in g.teams.values()] if g else [],
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
        HistoryStore(ctx.settings().data_dir / SESSION_HISTORY_DIR).clear(chat_id)
        return {"ok": True}

    @app.get("/api/history/{chat_id}")
    def history(chat_id: str, n: int = 100) -> dict[str, Any]:
        settings = ctx.settings()
        if not settings.admin_show_history:
            raise HTTPException(403, "Trang Hội thoại đang tắt (ADMIN_SHOW_HISTORY=false).")
        records = HistoryStore(settings.data_dir / SESSION_HISTORY_DIR).recent(chat_id, max(1, min(n, 500)))
        return {"chat_id": chat_id, "messages": [
            {"role": r.get("role"), "name": r.get("name", ""), "text": r.get("text", ""), "t": r.get("t")}
            for r in records
        ]}

    @app.get("/api/memorydata/{chat_id}")
    def memorydata(chat_id: str, n: int = 200) -> dict[str, Any]:
        """Mọi tin của hội thoại kèm kết quả bộ lọc (khác /api/history: chỉ session)."""
        settings = ctx.settings()
        if not settings.admin_show_history:
            raise HTTPException(403, "Trang Hội thoại đang tắt (ADMIN_SHOW_HISTORY=false).")
        records = MemoryDataStore(settings.data_dir / MEMORYDATA_DIR).recent(chat_id, max(1, min(n, 2000)))
        return {"chat_id": chat_id, "messages": [
            {"role": r.get("role"), "name": r.get("name", ""), "text": r.get("text", ""), "t": r.get("t"),
             "type": r.get("type", "text"), "filter": r.get("filter")}
            for r in records
        ]}

    # ---------- chỉ dẫn (workspace .md) ----------

    def _workspace_path(settings: Settings, name: str) -> Path:
        if name not in WORKSPACE_FILES:
            raise HTTPException(404, "Chỉ sửa được SYSTEM hoặc MEMORY")
        return settings.workspace_dir / WORKSPACE_FILES[name]

    @app.get("/api/workspace/{name}")
    def read_workspace(name: str) -> dict[str, Any]:
        settings = ctx.settings()
        path = _workspace_path(settings, name)
        managed = WORKSPACE_FILES[name] in (read_cached(settings).get("files") or {})
        try:
            return {"name": name, "content": path.read_text(encoding="utf-8"), "updated_at": int(path.stat().st_mtime * 1000),
                    "managed_by_web": managed}
        except FileNotFoundError:
            return {"name": name, "content": "", "updated_at": None, "managed_by_web": managed}

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
        values = settings_file.read_values(ctx.env_path)
        settings = ctx.settings()
        defaults = {
            "GEMINI_MODEL": settings.gemini_model, "BOT_TRIGGERS": ",".join(settings.bot_triggers),
            "RECEIVE_MODE": settings.receive_mode, "LOG_LEVEL": settings.log_level,
            "ADMIN_SHOW_HISTORY": "true" if settings.admin_show_history else "false",
            "ALLOW_ALL_CHATS": "true" if settings.allow_all_chats else "false",
            "SCHEDULE_OWNER_ONLY": "true",
            "BOT_NAMES": ",".join(settings.bot_names),
            "FILTER_AI": "true" if settings.filter_ai else "false",
            "FILTER_MODEL": settings.filter_model or settings.gemini_model,
            "FILTER_CONTEXT_LINES": str(settings.filter_context_lines),
            "MEMORYDATA_KEEP": str(settings.memorydata_keep),
            "ASSIGN_ALLOWED": settings.assign_allowed,
            "SESSION_UPLOAD": "true" if settings.session_upload else "false",
        }
        # Thông số chủ hệ thống đặt trên web (bot lưu bản gần nhất): đè lên giá trị ở đây khi bot chạy.
        remote = read_cached(settings)
        remote_values = {k: v for k, v in (remote.get("values") or {}).items() if k in REMOTE_KEYS}
        return {
            "fields": [
                {"key": f.key, "label": f.label, "help": f.help, "kind": f.kind, "choices": list(f.choices),
                 "group": f.group, "value": values.get(f.key) or defaults.get(f.key, ""),
                 "remote": _remote_text(remote_values[f.key]) if f.key in remote_values else None}
                for f in settings_file.FIELDS
            ],
            "secrets": [{"key": k, "label": label, "set": bool(values.get(k))} for k, label in settings_file.SECRETS.items()],
            "remote": {"version": remote.get("version"), "fetched_at": remote.get("fetched_at"),
                       "count": len(remote_values), "files": sorted(remote.get("files") or {})} if remote else None,
        }

    @app.put("/api/settings")
    def write_settings(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        changes = body.get("values")
        if not isinstance(changes, dict) or not changes:
            raise HTTPException(400, "Không có gì để lưu")
        unknown = set(changes) - settings_file.FIELD_KEYS
        if unknown:
            raise HTTPException(400, f"Không được sửa: {', '.join(sorted(unknown))}")
        cleaned = settings_file.validate(ctx.env_path, {k: str(v) for k, v in changes.items()}, ctx.base_dir)
        settings_file.update(ctx.env_path, cleaned)
        return {"ok": True, "message": "Đã lưu. Khởi động lại bot để áp dụng."}

    @app.put("/api/secrets/{key}")
    def write_secret(key: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
        if key not in settings_file.SECRETS:
            raise HTTPException(404, "Không có khóa này")
        value = body.get("value")
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(400, "Giá trị trống")
        cleaned = settings_file.validate(ctx.env_path, {key: value}, ctx.base_dir)
        settings_file.update(ctx.env_path, cleaned)
        return {"ok": True, "set": True, "message": f"Đã đặt {key}. Khởi động lại bot để áp dụng."}

    # ---------- cập nhật (chạy từ mã nguồn) ----------

    @app.post("/api/update")
    def update_app() -> dict[str, Any]:
        from bot.system import auto_update

        reason = auto_update.unavailable_reason()
        if reason:
            return {"ok": False, "message": reason}
        settings = ctx.settings()
        if bot_process.gui_running(settings):
            # Ứng dụng quản lý tự cập nhật, khởi động lại bot và mở lại chính nó (có thể đang chứa trang này).
            atomic_write_text(settings.system_dir / UPDATE_REQUEST, "1")
            return {"ok": True, "message": "Đang cập nhật. Ứng dụng sẽ tự đóng và mở lại sau ít giây."}
        try:
            result = auto_update.update()
        except auto_update.UpdateError as exc:
            return {"ok": False, "message": f"Cập nhật lỗi: {exc}"}
        (settings.system_dir / PENDING_UPDATES_FILE).unlink(missing_ok=True)
        message = result.message
        if result.changed:
            if bot_process.is_running(settings, bot_process.BOT):
                message += "\n" + bot_process.restart(settings, bot_process.BOT).message
            message += "\nKhởi động lại giao diện (python -m bot admin restart) để dùng giao diện mới."
        return {"ok": True, "message": message}

    # ---------- đăng nhập acc Zalo cá nhân bằng mã QR ----------

    qr: dict[str, Any] = {"login": None}

    def qr_payload() -> dict[str, Any]:
        login = qr["login"]
        settings = ctx.settings()
        session = {"exists": settings.zalo_session_file.is_file(), "personal": settings.personal}
        if session["exists"]:
            try:
                saved = json.loads(settings.zalo_session_file.read_text(encoding="utf-8"))
                session.update(display_name=str(saved.get("display_name") or ""), saved_at=saved.get("saved_at"))
            except (OSError, ValueError, AttributeError):
                pass
        if login is None:
            return {"state": "idle", "session": session}
        st = login.status
        return {"state": st.state, "message": st.message, "display_name": st.display_name,
                "image": st.image if st.state == "waiting_scan" else "", "session": session}

    @app.get("/api/zalo-login")
    def zalo_login_status() -> dict[str, Any]:
        return qr_payload()

    @app.post("/api/zalo-login/start")
    def zalo_login_start() -> dict[str, Any]:
        try:
            from bot.zalo import qr_login
        except ImportError:
            raise HTTPException(400, "Thiếu thư viện. Cài bằng: pip install -e \".[personal]\"") from None
        current = qr["login"]
        if current is not None and current.status.state not in qr_login.FINISHED:
            return qr_payload()
        settings = ctx.settings()
        login = qr["login"] = qr_login.QrLogin()

        def work() -> None:
            try:
                session = login.run()
            except qr_login.QrLoginError:
                return  # trạng thái lỗi/hết hạn/huỷ đã được ghi vào login.status
            except Exception as exc:  # noqa: BLE001
                log.exception("Đăng nhập QR lỗi")
                login.report(qr_login.ERROR, f"Lỗi không mong đợi: {exc}")
                return
            try:
                qr_login.apply_session(session, settings.zalo_session_file, ctx.env_path)
                message = login.status.message + " Đã bật chế độ acc cá nhân (RECEIVE_MODE=personal)."
                fresh = ctx.settings()
                if bot_process.is_running(fresh):
                    message += " " + bot_process.restart(fresh).message
                else:
                    message += " Bấm Bật bot ở trang Tổng quan."
                login.report(qr_login.SUCCESS, message, display_name=session.display_name)
                log.info("Đã đăng nhập acc Zalo cá nhân %s bằng QR", session.display_name)
            except Exception as exc:  # noqa: BLE001
                log.exception("Lưu phiên Zalo lỗi")
                login.report(qr_login.ERROR, f"Đăng nhập được nhưng lưu phiên lỗi: {exc}")

        threading.Thread(target=work, name="zalo-qr-login", daemon=True).start()
        return qr_payload()

    @app.post("/api/zalo-login/cancel")
    def zalo_login_cancel() -> dict[str, Any]:
        if qr["login"] is not None:
            qr["login"].cancel()
        return qr_payload()

    # ---------- log ----------

    def _log_path(settings: Settings, source: str) -> Path:
        service = {"bot": bot_process.BOT, "admin": bot_process.ADMIN}.get(source)
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
        return FailedStore(settings.data_dir / FAILED_REPLIES_FILE)

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
        if settings.personal:
            return {"ok": False, "message": "Chế độ acc Zalo cá nhân chưa hỗ trợ gửi lại từ giao diện."}
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
        ctx_tool = ToolContext("admin-playground", settings.owner_zalo_id or "admin", "Chủ bot", is_owner=True, can_assign=True)
        try:
            reply = await agent.reply(system, turns, ctx_tool)
        except Exception as exc:  # noqa: BLE001 - báo lỗi Gemini cho người dùng
            log.exception("Chat thử lỗi")
            return {"ok": False, "reply": "", "tokens": 0, "message": f"Gemini lỗi: {type(exc).__name__}: {exc}"}
        # Token là chi phí thật nên vẫn tính vào hạn mức ngày, nhưng không ghi vào lịch sử nhóm nào.
        UsageStore(settings.data_dir / TOKEN_USAGE_FILE).add(reply.tokens)
        StatsStore(settings.data_dir / DAILY_STATS_FILE).incr("tokens", reply.tokens)
        return {"ok": True, "reply": reply.text, "tokens": reply.tokens, "echo": not settings.gemini_api_key}

    @app.get("/api/tools")
    def tools() -> dict[str, Any]:
        registry = discover()
        return {"tools": [
            {"name": d["name"], "description": d["description"]} for d in registry.declarations()
        ]}

    return app
