"""Ứng dụng quản lý: cửa sổ WebView2 hiển thị giao diện quản lý, kèm biểu tượng khay.

- Server giao diện (FastAPI) chạy trong một luồng của chính ứng dụng; nếu `python -m bot admin`
  đã chạy sẵn thì dùng luôn server đó.
- Bot vẫn là tiến trình riêng (gateway), nên đóng cửa sổ hay thoát ứng dụng không làm bot dừng.
- Chỉ một bản chạy cùng lúc: mở lần hai thì chỉ đưa cửa sổ đang chạy lên.
"""

from __future__ import annotations

import logging
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any

from bot.system import gateway
from bot.system.bootstrap import ensure_admin_token, ensure_home
from bot.config import APP_HOME, ENV_FILE, ConfigError, Settings
from bot.system.logging_setup import setup_logging
from bot.storage.lock import AlreadyRunning, InstanceLock

log = logging.getLogger("bot.ui.desktop")

TITLE = "Quản lý Bot Zalo"


def _message_box(text: str, title: str = TITLE, error: bool = True) -> None:
    """Hộp thoại Windows đơn giản, dùng được cả trước khi cửa sổ chính tồn tại."""
    if os.name == "nt":
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, text, title, 0x10 if error else 0x40)
    else:
        print(text)


def _free_port(start: int, attempts: int = 20) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise OSError(f"Không tìm được cổng trống từ {start} đến {start + attempts - 1}")


class Desktop:
    def __init__(self, settings: Settings, tray_only: bool, start_bot: bool) -> None:
        self.settings = settings
        self.tray_only = tray_only
        self.start_bot = start_bot
        self.window: Any = None
        self.tray: Any = None
        self.server: Any = None
        self.admin_lock: InstanceLock | None = None
        self.port = settings.admin_port
        self.quitting = False
        self.busy = False
        self.bot_running = False
        self.bot_state = "stopped"
        self._told_about_tray = False
        self._stopped = threading.Event()
        self.updates_pending = 0  # số thay đổi mới trên GitHub (chỉ khi chạy từ mã nguồn)
        self._told_about_update = False

    # ---------- server giao diện ----------

    def start_admin_server(self) -> None:
        lock = gateway.lock_for(self.settings, gateway.ADMIN)
        try:
            lock.acquire()
        except AlreadyRunning:
            # `python -m bot admin` (hoặc task chạy nền) đang phục vụ: dùng luôn, không bật server thứ hai.
            log.info("Giao diện quản lý đã chạy sẵn ở cổng %d, dùng lại", self.settings.admin_port)
            return
        self.admin_lock = lock
        gateway.write_pid(self.settings, gateway.ADMIN)

        import uvicorn

        from bot.ui.admin.server import AdminContext, create_app

        self.port = _free_port(self.settings.admin_port)
        app = create_app(AdminContext(ENV_FILE, APP_HOME), self.port)
        self.server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=self.port, log_config=None, access_log=False))
        threading.Thread(target=self.server.run, name="admin-server", daemon=True).start()
        deadline = time.monotonic() + 15
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("Server giao diện không khởi động được, xem logs/gui.log")
            time.sleep(0.05)
        log.info("Server giao diện: http://127.0.0.1:%d", self.port)

    def url(self, page: str = "overview") -> str:
        return f"http://127.0.0.1:{self.port}/#token={self.settings.admin_token}&page={page}"

    # ---------- cửa sổ ----------

    def show_window(self, *_: Any) -> None:
        if self.window is None:
            webbrowser.open(self.url())
            return
        self.window.show()
        self.window.restore()

    def _on_closing(self) -> bool:
        if self.quitting:
            return True
        # Bấm X: thu xuống khay, bot và giao diện vẫn chạy.
        self.window.hide()
        if not self._told_about_tray and self.tray is not None:
            self._told_about_tray = True
            self.tray.notify("Ứng dụng vẫn chạy ở khay hệ thống. Bấm biểu tượng để mở lại.")
        return False

    # ---------- bot ----------

    def _run_bot_action(self, action: str) -> None:
        if self.busy:
            return
        self.busy = True
        self.refresh_tray()
        try:
            func = {"start": gateway.start, "stop": gateway.stop, "restart": gateway.restart}[action]
            result = func(self.settings_now(), gateway.BOT)
            message = result.message.splitlines()[0]
        except ConfigError as exc:
            message = f"Thiếu cấu hình: {exc}"
            self.show_window()
        except Exception as exc:  # noqa: BLE001 - báo lỗi lên khay thay vì làm sập ứng dụng
            log.exception("Thao tác %s bot lỗi", action)
            message = f"Lỗi: {exc}"
        finally:
            self.busy = False
        self.update_status()
        if self.tray is not None:
            self.tray.notify(message)

    def bot_action(self, action: str) -> None:
        threading.Thread(target=self._run_bot_action, args=(action,), daemon=True).start()

    def toggle_bot(self, *_: Any) -> None:
        self.bot_action("stop" if self.bot_running else "start")

    def restart_bot(self, *_: Any) -> None:
        self.bot_action("restart")

    def settings_now(self) -> Settings:
        """Đọc lại .env (có thể vừa sửa ở trang Cài đặt)."""
        from bot.ui.admin.server import AdminContext

        return AdminContext(ENV_FILE, APP_HOME).settings()

    def update_status(self) -> None:
        try:
            info = gateway.status_info(self.settings_now())
        except Exception:  # noqa: BLE001
            log.exception("Không đọc được trạng thái bot")
            return
        self.bot_running = info["running"]
        stale = info["running"] and info.get("last_poll_at") and time.time() * 1000 - int(info["last_poll_at"]) > 180_000
        if not info["running"]:
            self.bot_state = "stopped"
        elif info["failed_pending"] or stale:
            self.bot_state = "warning"
        else:
            self.bot_state = "running"
        self.refresh_tray()

    def refresh_tray(self) -> None:
        if self.tray is not None:
            self.tray.refresh()

    # ---------- cập nhật (chạy từ mã nguồn) ----------

    def check_updates(self) -> None:
        from bot.system import updater

        try:
            self.updates_pending = updater.pending_commits()
        except updater.UpdateError as exc:
            log.info("Không kiểm tra được bản mới: %s", exc)
            return
        update_flag_file(self.settings).write_text(str(self.updates_pending), encoding="utf-8")
        self.refresh_tray()
        if self.updates_pending and not self._told_about_update and self.tray is not None:
            self._told_about_update = True
            self.tray.notify(f"Có {self.updates_pending} thay đổi mới. Chuột phải biểu tượng → Cập nhật.")

    def update_app(self, *_: Any) -> None:
        threading.Thread(target=self._update_app, name="update", daemon=True).start()

    def _update_app(self) -> None:
        from bot.system import updater

        if self.busy:
            return
        self.busy = True
        self.refresh_tray()
        if self.tray is not None:
            self.tray.notify("Đang cập nhật…")
        try:
            result = updater.update()
        except updater.UpdateError as exc:
            self.busy = False
            self.refresh_tray()
            if self.tray is not None:
                self.tray.notify(f"Cập nhật lỗi: {exc}")
            return
        self.updates_pending = 0
        update_flag_file(self.settings).unlink(missing_ok=True)
        if not result.changed:
            self.busy = False
            self.refresh_tray()
            if self.tray is not None:
                self.tray.notify(result.message)
            return
        settings = self.settings_now()
        # Bot và giao diện chạy riêng (nếu có) phải khởi động lại mới dùng code mới.
        if gateway.is_running(settings, gateway.BOT):
            gateway.restart(settings, gateway.BOT)
        if self.admin_lock is None and gateway.is_running(settings, gateway.ADMIN):
            gateway.restart(settings, gateway.ADMIN)
        if self.tray is not None:
            self.tray.notify(result.message.splitlines()[0] + " Đang mở lại ứng dụng…")
        # Mở bản mới (nó chờ bản này thoát để nhận khoá), rồi thoát bản này.
        args = [sys.executable, "-m", "bot", "gui", "--after-update"]
        if self.window is None or self.tray_only:
            args.append("--tray")
        kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        subprocess.Popen(args, cwd=APP_HOME, **kwargs)
        self.quit()

    # ---------- vòng nền ----------

    def _background(self) -> None:
        show_flag = self.settings.system_dir / "gui.show"
        # Trang Tổng quan (bấm "Cập nhật") ghi file này để nhờ ứng dụng tự cập nhật và mở lại.
        update_request = self.settings.system_dir / "gui.update"
        last_status = 0.0
        next_update_check = time.monotonic() + 20
        while not self._stopped.is_set():
            if show_flag.exists():
                show_flag.unlink(missing_ok=True)
                self.show_window()
            if update_request.exists():
                update_request.unlink(missing_ok=True)
                self.update_app()
            if time.monotonic() - last_status > 5:
                last_status = time.monotonic()
                self.update_status()
            if self.can_update and time.monotonic() > next_update_check:
                next_update_check = time.monotonic() + 6 * 3600
                threading.Thread(target=self.check_updates, name="update-check", daemon=True).start()
            self._stopped.wait(0.5)

    @property
    def can_update(self) -> bool:
        from bot.system import updater

        return updater.unavailable_reason() is None

    def _auto_start_bot(self) -> None:
        if gateway.is_running(self.settings, gateway.BOT):
            return
        try:
            self.settings_now().require(zalo=True, gemini=True)
        except ConfigError as exc:
            if self.tray is not None:
                self.tray.notify(f"Chưa bật được bot: {exc}")
            return
        self._run_bot_action("start")

    # ---------- thư mục, thoát ----------

    def open_folder(self, *_: Any) -> None:
        if os.name == "nt":
            os.startfile(str(APP_HOME))  # noqa: S606 - mở Explorer ở thư mục dữ liệu
        else:
            subprocess.Popen(["xdg-open", str(APP_HOME)])

    def quit(self, *_: Any) -> None:
        self.quitting = True
        self._stopped.set()
        if self.tray is not None:
            self.tray.stop()
        if self.server is not None:
            self.server.should_exit = True
        if self.window is not None:
            self.window.destroy()

    def quit_and_stop_bot(self, *_: Any) -> None:
        def work() -> None:
            self.busy = True
            self.refresh_tray()
            try:
                gateway.stop(self.settings_now(), gateway.BOT)
            finally:
                self.quit()

        threading.Thread(target=work, daemon=True).start()

    # ---------- chạy ----------

    def run(self) -> int:
        self.start_admin_server()
        from bot.ui.desktop import autostart

        autostart.migrate()
        from bot.ui.desktop.tray import Tray

        self.tray = Tray(self)
        threading.Thread(target=self.tray.run, name="tray", daemon=True).start()
        threading.Thread(target=self._background, name="background", daemon=True).start()

        zalo_ready = self.settings.zalo_session_file.is_file() if self.settings.personal else self.settings.zalo_bot_token
        needs_setup = not (zalo_ready and self.settings.gemini_api_key)
        if self.start_bot:
            threading.Thread(target=self._auto_start_bot, daemon=True).start()

        try:
            import webview

            self.window = webview.create_window(
                TITLE,
                self.url("settings" if needs_setup else "overview"),
                width=1200,
                height=820,
                min_size=(420, 520),
                hidden=self.tray_only and not needs_setup,
                text_select=True,
            )
            self.window.events.closing += self._on_closing
            webview.start(
                gui="edgechromium" if os.name == "nt" else None,
                private_mode=False,  # giữ mã đăng nhập giữa các lần mở
                storage_path=str(self.settings.system_dir / "webview"),
            )
        except Exception:  # noqa: BLE001 - thiếu WebView2: dùng trình duyệt, ứng dụng vẫn chạy ở khay
            log.exception("Không mở được cửa sổ WebView2, chuyển sang trình duyệt")
            self.window = None
            if not self.tray_only:
                webbrowser.open(self.url())
            self._stopped.wait()
        finally:
            self.quitting = True
            self._stopped.set()
            if self.tray is not None:
                self.tray.stop()
            if self.server is not None:
                self.server.should_exit = True
            if self.admin_lock is not None:
                gateway.clear_pid(self.settings, gateway.ADMIN)
                self.admin_lock.release()
        return 0


def update_flag_file(settings: Settings) -> Path:
    """data/update.txt: số thay đổi mới chưa cập nhật, để trang Tổng quan hiện nút Cập nhật."""
    return settings.system_dir / "update.txt"


def run_gui(tray_only: bool = False, start_bot: bool = False, after_update: bool = False) -> int:
    from bot import paths

    # Vừa cập nhật và chuyển dữ liệu sang userdata/: bot cũ đã tắt trong lúc chuyển, bật lại luôn.
    start_bot = start_bot or (after_update and bool(paths.LAST_MIGRATED))
    try:
        ensure_home()
        settings = Settings.from_env()
        settings, _ = ensure_admin_token(settings, ENV_FILE)
    except (ConfigError, OSError) as exc:
        _message_box(f"Không khởi động được:\n{exc}\n\nThư mục dữ liệu: {APP_HOME}")
        return 2
    setup_logging(settings.log_level, settings.log_dir, settings.secrets, filename="gui.log")

    lock = InstanceLock(settings.system_dir / "gui.lock")
    try:
        # Mở lại sau khi cập nhật: chờ bản cũ thoát hẳn rồi mới nhận khoá.
        lock.acquire(wait=30.0 if after_update else 0.0)
    except AlreadyRunning:
        # Đã có một bản đang chạy: nhờ nó hiện cửa sổ rồi thoát.
        if not tray_only:
            (settings.system_dir / "gui.show").write_text("1", encoding="utf-8")
        return 0
    try:
        log.info("Mở ứng dụng quản lý (thư mục dữ liệu: %s)", APP_HOME)
        return Desktop(settings, tray_only, start_bot).run()
    except Exception as exc:  # noqa: BLE001 - lỗi bất ngờ: báo bằng hộp thoại thay vì im lặng biến mất
        log.exception("Ứng dụng quản lý lỗi")
        _message_box(f"Ứng dụng gặp lỗi:\n{exc}\n\nXem {Path(settings.log_dir) / 'gui.log'}")
        return 1
    finally:
        lock.release()
