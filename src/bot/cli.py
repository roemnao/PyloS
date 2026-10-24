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

from bot.agent import EchoAgent, GeminiAgent, PromptBuilder, discover
from bot.core.app import Bot
from bot.config import PROJECT_ROOT, ConfigError, Settings, is_frozen
from bot.system.logging_setup import setup_logging
from bot.storage import StateStore
from bot.storage.lock import AlreadyRunning, InstanceLock
from bot.core.timeutil import now_ms
from bot.zalo import ZaloClient, ZaloError

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
        from bot.zalo.personal import PersonalZalo

        zalo = PersonalZalo(settings)
    else:
        zalo = ZaloClient(settings.zalo_bot_token)
    agent, tools = _build_agent(settings)
    bot = Bot(settings, zalo, agent, PromptBuilder(settings.workspace_dir), tools.names())
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

    from bot.system import gateway

    flag = gateway.stop_flag(settings)
    flag.unlink(missing_ok=True)  # cờ cũ còn sót lại không được làm bot tắt ngay khi vừa bật
    stopping = False

    try:
        if settings.receive_mode == "webhook":
            import uvicorn

            from bot.zalo.webhook import WEBHOOK_PATH, create_app

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
            from bot.zalo.polling import run_polling

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
    bot = Bot(settings, ConsoleZalo(), agent, PromptBuilder(settings.workspace_dir), tools.names())
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
    state = StateStore(settings.data_dir / "state.txt").data
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

    from bot.system import gateway
    from bot.zalo.qrlogin import EXPIRED, WAITING_SCAN, QrLogin, QrLoginError, apply_session, save_qr_png

    qr_path = settings.data_dir / "zalo_qr.png"

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

    apply_session(session, settings.zalo_session_file, PROJECT_ROOT / ".env")
    print(f"Đã lưu phiên đăng nhập vào {settings.zalo_session_file} và đặt RECEIVE_MODE=personal trong .env.")
    if session.user_id:
        print(f"ID của acc phụ: {session.user_id}")
    if gateway.is_running(settings):
        from bot.ui.admin import envfile

        # Đọc lại .env: RECEIVE_MODE vừa đổi, còn os.environ vẫn giữ giá trị cũ.
        fresh = Settings.from_env({**os.environ, **envfile.read_values(PROJECT_ROOT / ".env")})
        print(gateway.restart(fresh).message)
    else:
        print("Chạy bot: python -m bot run (hoặc gateway start).")
    if not settings.owner_zalo_id:
        print("Tiếp theo: từ acc CHÍNH, nhắn /id cho acc phụ rồi điền user_id vào OWNER_ZALO_ID trong .env.")
    return 0


def _update(settings: Settings) -> int:
    from bot.system import gateway, updater

    try:
        result = updater.update()
    except updater.UpdateError as exc:
        print(f"Cập nhật lỗi: {exc}", file=sys.stderr)
        return 1
    print(result.message)
    if result.changed:
        for service in (gateway.BOT, gateway.ADMIN):
            if gateway.is_running(settings, service):
                print(gateway.restart(settings, service).message)
        if gateway.gui_running(settings):
            print("Nếu ứng dụng quản lý (cửa sổ/khay) đang mở, thoát và mở lại để dùng giao diện mới.")
    return 0


def _admin(settings: Settings, action: str, open_browser: bool) -> int:
    import webbrowser

    from bot.system import gateway
    from bot.system.bootstrap import ensure_admin_token

    env_path = PROJECT_ROOT / ".env"
    if action in ("run", "start", "restart"):
        settings, created = ensure_admin_token(settings, env_path)
        if created:
            print(f"Đã tạo ADMIN_TOKEN mới và lưu vào {env_path}.")
    url = f"http://127.0.0.1:{settings.admin_port}/"
    login_url = f"{url}#token={settings.admin_token}"

    if action == "status":
        running = gateway.is_running(settings, gateway.ADMIN)
        print(f"Giao diện quản lý: {'ĐANG CHẠY tại ' + url if running else 'DỪNG'}")
        return 0 if running else 1
    if action in ("start", "stop", "restart"):
        result = {"start": gateway.start, "stop": gateway.stop, "restart": gateway.restart}[action](settings, gateway.ADMIN)
        print(result.message)
        if result.ok and action != "stop":
            print(f"Mở {url} và nhập ADMIN_TOKEN trong .env (hoặc chạy lại với --open).")
            if open_browser:
                webbrowser.open(login_url)
        return result.code

    lock = gateway.lock_for(settings, gateway.ADMIN)
    try:
        lock.acquire(wait=2.0)
    except AlreadyRunning:
        print(f"Giao diện quản lý đã chạy tại {url}", file=sys.stderr)
        if open_browser:
            webbrowser.open(login_url)
        return EXIT_ALREADY_RUNNING
    gateway.write_pid(settings, gateway.ADMIN)
    setup_logging(settings.log_level, settings.log_dir, settings.secrets, filename="admin.log")
    try:
        import threading

        import uvicorn

        from bot.ui.admin.server import AdminContext, create_app

        app = create_app(AdminContext(env_path, PROJECT_ROOT), settings.admin_port)
        print(f"Giao diện quản lý: {url}\nMã truy cập: ADMIN_TOKEN trong {env_path}\nCtrl+C để dừng.", flush=True)
        if open_browser:
            threading.Timer(1.5, webbrowser.open, [login_url]).start()
        uvicorn.run(app, host="127.0.0.1", port=settings.admin_port, log_config=None, access_log=False)
    except KeyboardInterrupt:
        pass
    finally:
        gateway.clear_pid(settings, gateway.ADMIN)
        lock.release()
    return 0


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
    zlogin = sub.add_parser("zalo-login", help="đăng nhập acc Zalo cá nhân bằng mã QR (chế độ personal)")
    zlogin.add_argument("--no-open", action="store_true", help="không tự mở ảnh mã QR (máy không có màn hình)")
    args = parser.parse_args(argv)
    # Bấm đúp ZaloBot.exe (không tham số) thì mở ứng dụng quản lý; `python -m bot` vẫn chạy bot như trước.
    command = args.command or ("gui" if is_frozen() else "run")
    if command == "gui":
        from bot.ui.desktop.app import run_gui

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
            raise ConfigError("Cần WEBHOOK_SECRET dài 8–256 ký tự trong .env.")
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

    if command == "gateway":
        from bot.system import gateway

        try:
            if args.action == "status":
                info = gateway.status_info(settings)
                print(gateway.format_status(info))
                return 0 if info["running"] else 1
            if args.action == "logs":
                if args.follow:
                    return gateway.follow_log(settings, args.lines)
                print(gateway.tail_log(settings, args.lines))
                return 0
            result = {"start": gateway.start, "stop": gateway.stop, "restart": gateway.restart}[args.action](settings)
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

    lock_dir = settings.data_dir / "console" if command == "console" else settings.data_dir
    lock = InstanceLock(Path(lock_dir) / "bot.lock")
    try:
        lock.acquire(wait=2.0)
    except AlreadyRunning as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ALREADY_RUNNING
    exit_code = 0
    if command == "run":
        from bot.system import gateway

        gateway.write_pid(settings)
    try:
        if command == "console":
            user_id = args.user_id or settings.owner_zalo_id or "console-user"
            # Dữ liệu chat thử để riêng, không lẫn với bot thật; chưa có chủ bot thì coi bạn là chủ.
            console_settings = dataclasses.replace(
                settings,
                data_dir=settings.data_dir / "console",
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
            from bot.system import gateway

            gateway.clear_pid(settings)
        lock.release()
    return exit_code
