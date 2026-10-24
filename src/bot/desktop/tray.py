"""Biểu tượng khay hệ thống (pystray)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pystray

from bot.config import APP_NAME
from bot.desktop import autostart
from bot.desktop.icons import make_icon

if TYPE_CHECKING:
    from bot.desktop.app import Desktop

log = logging.getLogger(__name__)

TITLES = {
    "running": "Bot Zalo: đang chạy",
    "warning": "Bot Zalo: đang chạy, có cảnh báo",
    "stopped": "Bot Zalo: đã dừng",
}


class Tray:
    def __init__(self, desktop: Desktop) -> None:
        self.d = desktop
        self._state = None
        item = pystray.MenuItem
        self.icon = pystray.Icon(
            APP_NAME,
            icon=make_icon("stopped"),
            title=TITLES["stopped"],
            menu=pystray.Menu(
                item("Mở giao diện", desktop.show_window, default=True),
                pystray.Menu.SEPARATOR,
                item(lambda _: "Đang xử lý…" if desktop.busy else ("Tắt bot" if desktop.bot_running else "Bật bot"),
                     desktop.toggle_bot, enabled=lambda _: not desktop.busy),
                item("Khởi động lại bot", desktop.restart_bot,
                     enabled=lambda _: desktop.bot_running and not desktop.busy),
                pystray.Menu.SEPARATOR,
                item(lambda _: f"Cập nhật ({desktop.updates_pending} thay đổi mới)" if desktop.updates_pending else "Cập nhật",
                     desktop.update_app, enabled=lambda _: desktop.can_update and not desktop.busy),
                item("Khởi động cùng Windows", self.toggle_autostart, checked=lambda _: autostart.is_enabled()),
                item("Mở thư mục dữ liệu", desktop.open_folder),
                pystray.Menu.SEPARATOR,
                item("Thoát (bot vẫn chạy)", desktop.quit),
                item("Thoát và tắt bot", desktop.quit_and_stop_bot, enabled=lambda _: desktop.bot_running),
            ),
        )

    def run(self) -> None:
        self.icon.run()

    def stop(self) -> None:
        try:
            self.icon.stop()
        except Exception:  # noqa: BLE001 - có thể đã dừng
            pass

    def notify(self, message: str) -> None:
        try:
            self.icon.notify(message, "Bot Zalo")
        except Exception:  # noqa: BLE001 - thông báo là phụ
            log.debug("Không hiện được thông báo khay", exc_info=True)

    def refresh(self) -> None:
        state = self.d.bot_state
        if state != self._state:
            self._state = state
            self.icon.icon = make_icon(state)
            self.icon.title = TITLES.get(state, "Bot Zalo")
        self.icon.update_menu()

    def toggle_autostart(self, *_: object) -> None:
        enable = not autostart.is_enabled()
        try:
            autostart.set_enabled(enable)
        except OSError as exc:
            self.notify(f"Không đổi được: {exc}")
            return
        self.notify("Sẽ tự chạy (ở khay, kèm bật bot) khi đăng nhập Windows." if enable
                    else "Đã tắt tự chạy cùng Windows.")
        self.icon.update_menu()
