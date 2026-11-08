"""Dòng lệnh: python -m bot <lệnh>.

  run            chạy bot (polling, webhook hoặc personal = acc Zalo cá nhân, theo RECEIVE_MODE)
  console        chat thử ngay trên terminal, không cần bot token Zalo
  me             gọi getMe (xem bot có vào được nhóm không: can_join_groups)
  set-webhook    đăng ký webhook URL với WEBHOOK_SECRET
  delete-webhook gỡ webhook
  webhook-info   xem webhook hiện tại
  gateway        quản lý bot chạy nền: start | stop | restart | status | logs [-n N] [-f]
  admin          giao diện web quản lý: [run] | start | stop | restart | status  [--open]
  health         kiểm tra bot còn poll đều không (dùng cho giám sát)
  zalo-login     đăng nhập acc Zalo cá nhân (acc phụ) bằng mã QR, bật RECEIVE_MODE=personal
  update         lấy code mới từ GitHub (git pull), cài thư viện nếu cần, khởi động lại bot
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

from pylos.residential.residents.pylos import EchoAgent, GeminiAgent, PromptBuilder, discover
from pylos.residential.residents.pylos.message_handler import Bot
from pylos.lobby.dispatch.shared.config import ENV_FILE, PROJECT_ROOT, ConfigError, Settings, is_frozen
from pylos.gate.main_gate.logs.log_files import setup_logging
from pylos.lobby.dispatch.shared.storage import StateStore
from pylos.lobby.dispatch.lifecycle.process_lock import AlreadyRunning, InstanceLock
from pylos.lobby.dispatch.clock.vietnam_time import now_ms
from pylos.gate.main_gate.zalo import ZaloClient, ZaloError
from pylos.lobby.dispatch.shared.userdata_paths import BOT_STATUS_FILE, CONSOLE_TEST_DIR, ZALO_LOGIN_QR_FILE

log = logging.getLogger("bot")

# Mã thoát, dùng bởi scripts/run-forever.ps1: 2 = lỗi cấu hình (đừng khởi động lại), 3 = đã có bot khác chạy.
EXIT_CONFIG = 2
EXIT_ALREADY_RUNNING = 3


def _build_agent(settings: Settings, allow_echo: bool = False):
    tools = discover()
    if not settings.gemini_api_key and allow_echo:
        return EchoAgent(), tools
    agent = GeminiAgent(
        settings.gemini_api_key,
        settings.gemini_model,
        tools,
        max_tool_rounds=settings.max_tool_rounds,
        max_output_tokens=settings.max_output_tokens,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    return agent, tools


async def _run(settings: Settings) -> int:
    if settings.personal:
        from pylos.gate.main_gate.zalo.personal_account import PersonalZalo

        zalo = PersonalZalo(settings)
    else:
        zalo = ZaloClient(settings.zalo_bot_token)
    agent, tools = _build_agent(settings)
    bot = Bot(settings, zalo, agent, PromptBuilder(settings.workspace_dir, settings.system_file), tools.names())
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            pass  # Windows: Ctrl+C sẽ ném KeyboardInterrupt, xử lý ở main()

    if settings.personal:
        log.warning("Đang chạy trên acc Zalo cá nhân (không chính thức): acc có thể bị Zalo khoá. Chỉ dùng acc phụ.")
        try:
            await asyncio.to_thread(zalo.login)
        except (ZaloError, ConfigError) as exc:
            log.error("%s", exc)
            await bot.stop()
            # Lỗi mạng thì để supervisor khởi động lại; cookies hết hạn/IMEI sai thì khởi động lại cũng không khỏi.
            return 1 if isinstance(exc, ZaloError) and exc.network else EXIT_CONFIG
        log.info("Acc Zalo cá nhân: %s (id=%s)", zalo.self_name or "?", zalo.self_id)
        if not settings.owner_zalo_id:
            log.warning("OWNER_ZALO_ID chưa đặt. Nhắn /id cho acc bot từ acc chính của bạn để lấy ID.")
    else:
        try:
            me = await zalo.get_me()
            log.info("Bot: %s (id=%s, can_join_groups=%s)", me.get("account_name"), me.get("id"), me.get("can_join_groups"))
        except ZaloError as exc:
            if exc.error_code == 401 and not exc.network:
                log.error("ZALO_BOT_TOKEN không hợp lệ (401 Unauthorized). Kiểm tra lại .env.")
                await bot.stop()
                await zalo.aclose()
                return EXIT_CONFIG
            # Lỗi mạng lúc khởi động (ví dụ máy vừa bật chưa có mạng): vẫn chạy, polling sẽ tự thử lại.
            log.warning("getMe lỗi: %s", exc)
    # Token đã qua kiểm tra (hoặc chỉ lỗi mạng tạm thời): báo cho `gateway start` biết bot đã sẵn sàng.
    bot.state.update(ready_at=now_ms())
    background_stop = asyncio.Event()
    background: list[asyncio.Task] = []
    # Bản cũ lấy thông số từ web và lưu ở remote_config.json; nay không dùng nữa nên xoá để không ai tưởng còn hiệu lực.
    stale = settings.system_dir / "remote_config.json"
    if stale.exists():
        stale.unlink(missing_ok=True)
        log.info("Đã xoá %s (thông số không còn lấy từ web, hãy đặt ở trang Cài đặt)", stale.name)

    from pylos.gate.side_gate.vps import bot_process

    flag = bot_process.stop_flag(settings)
    flag.unlink(missing_ok=True)  # cờ cũ còn sót lại không được làm bot tắt ngay khi vừa bật
    stopping = False

    try:
        if settings.receive_mode == "webhook":
            import uvicorn

            from pylos.gate.main_gate.zalo.receive_webhook import WEBHOOK_PATH, create_app

            app = create_app(settings.webhook_secret, bot.handle_payload, bot.state)
            log.info("Webhook lắng nghe tại http://%s:%d%s", settings.webhook_host, settings.webhook_port, WEBHOOK_PATH)
            server = uvicorn.Server(uvicorn.Config(app, host=settings.webhook_host, port=settings.webhook_port, log_config=None))
            main_task = asyncio.create_task(server.serve())

            def request_stop() -> None:
                server.should_exit = True
        elif settings.personal:
            main_task = asyncio.create_task(zalo.run(bot.handle_message, bot.state, stop))

            def request_stop() -> None:
                stop.set()
        else:
            from pylos.gate.main_gate.zalo.receive_polling import run_polling

            main_task = asyncio.create_task(run_polling(zalo, bot.handle_payload, bot.state, stop))

            def request_stop() -> None:
                stop.set()
                main_task.cancel()  # getUpdates có thể đang chờ tới 30 giây

        async def watch_stop_flag() -> None:
            nonlocal stopping
            while not flag.exists():
                await asyncio.sleep(1)
            log.info("Nhận yêu cầu dừng từ giao diện/gateway")
            stopping = True
            request_stop()

        watcher = asyncio.create_task(watch_stop_flag())
        try:
            await main_task
        except asyncio.CancelledError:
            if not stopping:
                raise
        finally:
            watcher.cancel()
    finally:
        background_stop.set()
        if background:
            await asyncio.wait(background, timeout=5)  # cho lô session cuối kịp gửi
            for task in background:
                task.cancel()
        await bot.stop()
        await zalo.aclose()
    if stopping:
        log.info("Đã dừng bot")
    return 0


class ConsoleZalo:
    """Giả lập Zalo: in câu trả lời ra terminal."""

    async def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        print(f"\n[bot -> {chat_id}]\n{text}\n", flush=True)
        return {"message_id": str(now_ms())}

    async def send_chat_action(self, chat_id: str, action: str = "typing") -> None:
        return None


async def _console(settings: Settings, chat_id: str, user_id: str, name: str, group: bool) -> None:
    agent, tools = _build_agent(settings, allow_echo=True)
    bot = Bot(settings, ConsoleZalo(), agent, PromptBuilder(settings.workspace_dir, settings.system_file), tools.names())
    kind = "GROUP" if group else "PRIVATE"
    print(
        f"Chat thử: chat_id={chat_id} ({kind}), bạn là {name} (user_id={user_id}).\n"
        f"Agent: {'Gemini ' + settings.gemini_model if settings.gemini_api_key else 'echo (chưa có GEMINI_API_KEY)'}.\n"
        f"Chủ bot: {settings.owner_zalo_id}. Dữ liệu chat thử lưu ở {settings.data_dir}.\n"
        "Gõ /help để xem lệnh, /allow để cho phép chat này, 'exit' để thoát.",
        flush=True,
    )
    counter = 0
    try:
        while True:
            line = await asyncio.to_thread(input, "> ")
            if line.strip().lower() in ("exit", "quit"):
                break
            counter += 1
            event = {
                "event_name": "message.text.received",
                "message": {
                    "from": {"id": user_id, "display_name": name, "is_bot": False},
                    "chat": {"id": chat_id, "chat_type": kind},
                    "text": line,
                    "message_id": f"console-{now_ms()}-{counter}",
                    "date": now_ms(),
                },
            }
            await bot.handle_payload(event)
            await bot.drain()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        await bot.stop()


async def _zalo_call(settings: Settings, method: str, **params: Any) -> Any:
    zalo = ZaloClient(settings.zalo_bot_token)
    try:
        return await zalo.call(method, params or None)
    finally:
        await zalo.aclose()


def _health(settings: Settings, max_age_seconds: int) -> int:
    state = StateStore(settings.system_dir / BOT_STATUS_FILE).data
    last = int(state.get("last_poll_at") or 0)
    if settings.receive_mode == "webhook":
        print("Chế độ webhook: dùng GET /health trên server để kiểm tra.")
        return 0
    if not last:
        print("Chưa có lần poll nào được ghi nhận (bot chưa chạy?).")
        return 1
    age = (now_ms() - last) / 1000
    print(f"Lần poll cuối cách đây {age:.0f} giây.")
    return 0 if age <= max_age_seconds else 1


def _zalo_login(settings: Settings, open_image: bool) -> int:
    import webbrowser

    from pylos.gate.side_gate.vps import bot_process
    from pylos.gate.main_gate.zalo.qr_login import EXPIRED, WAITING_SCAN, QrLogin, QrLoginError, apply_session, save_qr_png

    qr_path = settings.system_dir / ZALO_LOGIN_QR_FILE

    def on_update(status) -> None:
        if status.state == WAITING_SCAN:
            save_qr_png(status.image, qr_path)
            print(f"\nMã QR đã lưu ở: {qr_path}")
            if open_image:
                webbrowser.open(qr_path.resolve().as_uri())
            else:
                print("Máy không có màn hình? Mở giao diện quản lý (Cài đặt → Đăng nhập bằng mã QR) qua SSH tunnel, "
                      "hoặc chép file ảnh trên về máy để quét.")
        print(status.message, flush=True)

    print("Đăng nhập acc Zalo cá nhân. Dùng ACC PHỤ: chạy bot trên acc cá nhân có thể bị Zalo khoá acc.")
    try:
        for attempt in range(3):  # mã QR sống ~100 giây; hết hạn thì tự tạo mã mới
            login = QrLogin(on_update)
            try:
                session = login.run()
                break
            except QrLoginError as exc:
                if login.status.state != EXPIRED or attempt == 2:
                    print(f"Đăng nhập thất bại: {exc}", file=sys.stderr)
                    return 1
                print("Tạo mã QR mới...")
    except KeyboardInterrupt:
        print("\nĐã huỷ.")
        return 1
    finally:
        qr_path.unlink(missing_ok=True)

    apply_session(session, settings.zalo_session_file, ENV_FILE)
    print(f"Đã lưu phiên đăng nhập vào {settings.zalo_session_file} và đặt RECEIVE_MODE=personal trong src/pylos/management/owner/secrets/settings.env.")
    if session.user_id:
        print(f"ID của acc phụ: {session.user_id}")
    if bot_process.is_running(settings):
        from pylos.management.owner.admin_web import settings_file

        # Đọc lại .env: RECEIVE_MODE vừa đổi, còn os.environ vẫn giữ giá trị cũ.
        fresh = Settings.from_env({**os.environ, **settings_file.read_values(ENV_FILE)})
        print(bot_process.restart(fresh).message)
    else:
        print("Chạy bot: python -m bot run (hoặc gateway start).")
    if not settings.owner_zalo_id:
        print("Tiếp theo: từ acc CHÍNH, nhắn /id cho acc phụ rồi điền user_id vào OWNER_ZALO_ID trong src/pylos/management/owner/secrets/settings.env.")
    return 0


def _update(settings: Settings) -> int:
    from pylos.gate.side_gate.vps import bot_process
    from pylos.lobby.dispatch.updater import auto_update

    try:
        result = auto_update.update()
    except auto_update.UpdateError as exc:
        print(f"Cập nhật lỗi: {exc}", file=sys.stderr)
        return 1
    print(result.message)
    if result.changed:
        for service in (bot_process.BOT, bot_process.ADMIN):
            if bot_process.is_running(settings, service):
                print(bot_process.restart(settings, service).message)
        if bot_process.gui_running(settings):
            print("Nếu ứng dụng quản lý (cửa sổ/khay) đang mở, thoát và mở lại để dùng giao diện mới.")
    return 0


GOOD_AFTER_SECONDS = 90


def _mark_good(system_dir) -> None:
    from pylos.lobby.dispatch.updater import auto_update

    try:
        auto_update.mark_good(system_dir)
    except Exception:  # mốc bản tốt không được làm hỏng giao diện
        log.exception("Không ghi được mốc bản tốt")


def _rollback(settings: Settings, resume: bool, status: bool) -> int:
    from pylos.gate.side_gate.vps import bot_process
    from pylos.lobby.dispatch.updater import auto_update

    system_dir = settings.system_dir
    if status:
        state = auto_update.hold_state(system_dir)
        print(f"Bản tốt gần nhất: {auto_update.last_good(system_dir)[:7] or '(chưa có)'}")
        print(f"Đang giữ ở bản tốt: {'có, bỏ qua ' + state['from'][:7] if state else 'không'}")
        return 0
    try:
        result = auto_update.resume(system_dir) if resume else auto_update.rollback(system_dir)
    except auto_update.UpdateError as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    print(result.message)
    if result.changed:
        for service in (bot_process.BOT, bot_process.ADMIN):
            if bot_process.is_running(settings, service):
                print(bot_process.restart(settings, service).message)
    return 0


def _admin(settings: Settings, action: str, open_browser: bool) -> int:
    import webbrowser

    from pylos.gate.side_gate.vps import bot_process
    from pylos.lobby.dispatch.shared.first_run_setup import ensure_admin_token

    env_path = ENV_FILE
    if action in ("run", "start", "restart"):
        settings, created = ensure_admin_token(settings, env_path)
        if created:
            print(f"Đã tạo ADMIN_TOKEN mới và lưu vào {env_path}.")
    url = f"http://127.0.0.1:{settings.admin_port}/"
    login_url = f"{url}#token={settings.admin_token}"

    if action == "status":
        running = bot_process.is_running(settings, bot_process.ADMIN)
        print(f"Giao diện quản lý: {'ĐANG CHẠY tại ' + url if running else 'DỪNG'}")
        return 0 if running else 1
    if action in ("start", "stop", "restart"):
        result = {"start": bot_process.start, "stop": bot_process.stop, "restart": bot_process.restart}[action](settings, bot_process.ADMIN)
        print(result.message)
        if result.ok and action != "stop":
            print(f"Mở {url} và nhập ADMIN_TOKEN trong src/pylos/management/owner/secrets/settings.env (hoặc chạy lại với --open).")
            if open_browser:
                webbrowser.open(login_url)
        return result.code

    lock = bot_process.lock_for(settings, bot_process.ADMIN)
    try:
        lock.acquire(wait=2.0)
    except AlreadyRunning:
        print(f"Giao diện quản lý đã chạy tại {url}", file=sys.stderr)
        if open_browser:
            webbrowser.open(login_url)
        return EXIT_ALREADY_RUNNING
    bot_process.write_pid(settings, bot_process.ADMIN)
    setup_logging(settings.log_level, settings.log_dir, settings.secrets, filename="admin.log")
    try:
        import threading

        import uvicorn

        from pylos.management.owner.admin_web.admin_web_server import AdminContext, create_app

        app = create_app(AdminContext(env_path, PROJECT_ROOT), settings.admin_port)
        print(f"Giao diện quản lý: {url}\nMã truy cập: ADMIN_TOKEN trong {env_path}\nCtrl+C để dừng.", flush=True)
        if open_browser:
            threading.Timer(1.5, webbrowser.open, [login_url]).start()
        threading.Timer(GOOD_AFTER_SECONDS, _mark_good, [settings.system_dir]).start()  # sống tới lúc này = bản tốt
        uvicorn.run(app, host="127.0.0.1", port=settings.admin_port, log_config=None, access_log=False)
    except KeyboardInterrupt:
        pass
    finally:
        bot_process.clear_pid(settings, bot_process.ADMIN)
        lock.release()
    return 0


def _prepare_home(command: str) -> str | None:
    """Chuyển dữ liệu bản cũ vào Thành (một lần, có sao lưu) rồi tạo thư mục/file mẫu còn thiếu.

    Trả về thông báo lỗi nếu chưa chuyển được vì bản cũ còn chạy (không được tạo thư mục dữ liệu mới lúc đó,
    kẻo dữ liệu cũ bị bỏ lại).
    """
    from pylos.lobby.dispatch.shared import userdata_paths
    from pylos.lobby.dispatch.shared.first_run_setup import ensure_home

    # Sau khi bấm Cập nhật, bản cũ của ứng dụng cần vài giây để thoát: ứng dụng mới chờ lâu hơn bot.
    userdata_paths.migrate_all(wait_old=30.0 if command == "gui" else 5.0)
    if userdata_paths.pending_migration():
        return (
            "Bản cũ của bot hoặc ứng dụng quản lý vẫn đang chạy nên chưa chuyển được dữ liệu vào Thành.\n"
            "Thoát hẳn bản cũ (chuột phải biểu tượng Z ở khay → Thoát và tắt bot) rồi mở lại."
        )
    ensure_home()
    return None


def _utf8_console() -> None:
    # Console/pipe trên Windows thường là cp1252, không in được tiếng Việt.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def _attach_parent_console() -> None:
    """ZaloBot.exe là ứng dụng cửa sổ (không console). Khi được gọi từ cmd với một lệnh
    như `ZaloBot.exe gateway status`, gắn vào console của cmd để in được kết quả."""
    if os.name != "nt" or sys.stdout is not None:
        return
    import ctypes

    if not ctypes.windll.kernel32.AttachConsole(-1):  # -1 = ATTACH_PARENT_PROCESS
        return
    sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")  # noqa: SIM115
    sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")  # noqa: SIM115
    print()  # cmd đã in lại dấu nhắc; xuống dòng cho dễ đọc


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if is_frozen() and argv and argv[0] not in ("gui", "run"):
        _attach_parent_console()
    _utf8_console()
    parser = argparse.ArgumentParser(prog="ZaloBot.exe" if is_frozen() else "python -m bot",
                                     description="Bot trợ lý Zalo dùng Gemini")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="chạy bot")
    gui = sub.add_parser("gui", help="ứng dụng quản lý: cửa sổ + biểu tượng khay (mặc định của ZaloBot.exe)")
    gui.add_argument("--tray", action="store_true", help="chỉ hiện ở khay, không mở cửa sổ (dùng khi khởi động cùng Windows)")
    gui.add_argument("--start-bot", action="store_true", help="bật bot luôn nếu đang tắt")
    gui.add_argument("--after-update", action="store_true", help=argparse.SUPPRESS)
    console = sub.add_parser("console", help="chat thử trên terminal, không cần Zalo")
    console.add_argument("--chat-id", default="console-group")
    console.add_argument("--user-id", default=None, help="mặc định = OWNER_ZALO_ID hoặc 'console-user'")
    console.add_argument("--name", default="Tôi")
    console.add_argument("--private", action="store_true", help="giả lập chat riêng thay vì nhóm")
    sub.add_parser("me", help="gọi getMe")
    set_wh = sub.add_parser("set-webhook", help="đăng ký webhook")
    set_wh.add_argument("url", help="URL HTTPS công khai, kết thúc bằng /webhook/zalo")
    sub.add_parser("delete-webhook", help="gỡ webhook")
    sub.add_parser("webhook-info", help="xem webhook hiện tại")
    gw = sub.add_parser("gateway", help="quản lý bot chạy nền: start/stop/restart/status/logs")
    gw.add_argument("action", choices=["start", "stop", "restart", "status", "logs"])
    gw.add_argument("-n", "--lines", type=int, default=30, help="số dòng log (với logs)")
    gw.add_argument("-f", "--follow", action="store_true", help="theo dõi log liên tục (với logs)")
    adm = sub.add_parser("admin", help="giao diện web quản lý bot (http://127.0.0.1:8081)")
    adm.add_argument("action", nargs="?", default="run", choices=["run", "start", "stop", "restart", "status"],
                     help="run: chạy trong cửa sổ này (mặc định); start/stop/restart: chạy nền; status")
    adm.add_argument("--open", action="store_true", help="mở trình duyệt và đăng nhập sẵn")
    health = sub.add_parser("health", help="kiểm tra bot còn chạy")
    health.add_argument("--max-age", type=int, default=180, help="số giây tối đa từ lần poll cuối")
    sub.add_parser("update", help="lấy code mới từ GitHub và khởi động lại bot")
    rb = sub.add_parser("rollback", help="quay về bản code chạy ổn định gần nhất (VPS giữ ở đó, không tự cập nhật)")
    rb.add_argument("--resume", action="store_true", help="thôi giữ ở bản tốt, nhận code mới nhất")
    rb.add_argument("--status", action="store_true", help="chỉ xem bản tốt và trạng thái giữ")
    zlogin = sub.add_parser("zalo-login", help="đăng nhập acc Zalo cá nhân bằng mã QR (chế độ personal)")
    zlogin.add_argument("--no-open", action="store_true", help="không tự mở ảnh mã QR (máy không có màn hình)")
    args = parser.parse_args(argv)
    # Bấm đúp ZaloBot.exe (không tham số) thì mở ứng dụng quản lý; `python -m bot` vẫn chạy bot như trước.
    command = args.command or ("gui" if is_frozen() else "run")
    blocked = _prepare_home(command)
    if blocked:
        if command == "gui":
            from pylos.gate.side_gate.desktop.desktop_app import _message_box

            _message_box(blocked)
        else:
            print(blocked, file=sys.stderr)
        return EXIT_CONFIG
    if command == "gui":
        from pylos.gate.side_gate.desktop.desktop_app import run_gui

        return run_gui(tray_only=getattr(args, "tray", False), start_bot=getattr(args, "start_bot", False),
                       after_update=getattr(args, "after_update", False))

    try:
        settings = Settings.from_env()
        if command == "run":
            settings.require(zalo=True, gemini=True)
        elif command in ("me", "set-webhook", "delete-webhook", "webhook-info"):
            settings.require(zalo=True, gemini=False)
        if command in ("me", "set-webhook", "delete-webhook", "webhook-info") and settings.personal:
            raise ConfigError(f"Lệnh {command} chỉ dùng với Zalo Bot (token), không dùng với RECEIVE_MODE=personal.")
        if command == "set-webhook" and not (8 <= len(settings.webhook_secret) <= 256):
            raise ConfigError("Cần WEBHOOK_SECRET dài 8–256 ký tự trong src/pylos/management/owner/secrets/settings.env.")
    except ConfigError as exc:
        print(f"Lỗi cấu hình: {exc}", file=sys.stderr)
        return EXIT_CONFIG

    log_dir = settings.log_dir if command == "run" else None
    setup_logging(settings.log_level if command != "console" else "WARNING", log_dir, settings.secrets)

    if command == "health":
        return _health(settings, args.max_age)

    if command == "zalo-login":
        return _zalo_login(settings, open_image=not args.no_open)

    if command == "update":
        return _update(settings)

    if command == "rollback":
        return _rollback(settings, args.resume, args.status)

    if command == "gateway":
        from pylos.gate.side_gate.vps import bot_process

        try:
            if args.action == "status":
                info = bot_process.status_info(settings)
                print(bot_process.format_status(info))
                return 0 if info["running"] else 1
            if args.action == "logs":
                if args.follow:
                    return bot_process.follow_log(settings, args.lines)
                print(bot_process.tail_log(settings, args.lines))
                return 0
            result = {"start": bot_process.start, "stop": bot_process.stop, "restart": bot_process.restart}[args.action](settings)
            print(result.message)
            return result.code
        except ConfigError as exc:
            print(f"Lỗi cấu hình: {exc}", file=sys.stderr)
            return EXIT_CONFIG

    if command == "admin":
        return _admin(settings, args.action, args.open)

    if command in ("me", "set-webhook", "delete-webhook", "webhook-info"):
        method, params = {
            "me": ("getMe", {}),
            "set-webhook": ("setWebhook", {"url": getattr(args, "url", ""), "secret_token": settings.webhook_secret}),
            "delete-webhook": ("deleteWebhook", {}),
            "webhook-info": ("getWebhookInfo", {}),
        }[command]
        try:
            result = asyncio.run(_zalo_call(settings, method, **params))
        except ZaloError as exc:
            print(f"Zalo trả lỗi: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if command == "run":
        from pylos.gate.side_gate.vps import bot_process

        standby = bot_process.standby_info(settings)
        if standby:
            log.warning("Máy này đang ở chế độ chờ, không chạy bot: %s", standby["reason"])
            print(f"Chế độ chờ: {standby['reason']}", file=sys.stderr)
            return bot_process.EXIT_STANDBY

    lock_dir = settings.data_dir / CONSOLE_TEST_DIR if command == "console" else settings.system_dir
    lock = InstanceLock(Path(lock_dir) / "bot.lock")
    try:
        lock.acquire(wait=2.0)
    except AlreadyRunning as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ALREADY_RUNNING
    exit_code = 0
    if command == "run":
        from pylos.gate.side_gate.vps import bot_process

        bot_process.write_pid(settings)
    try:
        if command == "console":
            user_id = args.user_id or settings.owner_zalo_id or "console-user"
            # Dữ liệu chat thử để riêng, không lẫn với bot thật; chưa có chủ bot thì coi bạn là chủ.
            console_settings = dataclasses.replace(
                settings,
                data_dir=settings.data_dir / CONSOLE_TEST_DIR,
                system_dir=settings.data_dir / CONSOLE_TEST_DIR / "system",  # không lẫn state/seen với bot thật
                owner_zalo_id=settings.owner_zalo_id or user_id,
            )
            asyncio.run(_console(console_settings, args.chat_id, user_id, args.name, not args.private))
        else:
            log.info("Khởi động bot (chế độ nhận tin: %s, model: %s)", settings.receive_mode, settings.gemini_model)
            exit_code = asyncio.run(_run(settings))
    except KeyboardInterrupt:
        log.info("Đã dừng bot")
    finally:
        if command == "run":
            from pylos.gate.side_gate.vps import bot_process

            bot_process.clear_pid(settings)
        lock.release()
    return exit_code
