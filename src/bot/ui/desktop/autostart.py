"""Khởi động cùng Windows: một mục trong HKCU\\...\\Run (không cần quyền admin).

Khi đăng nhập, Windows chạy `ZaloBot.exe gui --tray --start-bot`: ứng dụng nằm ở khay và bật bot nếu đang tắt.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from bot.config import APP_NAME, is_frozen

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = APP_NAME


def command() -> str:
    if is_frozen():
        return f'"{sys.executable}" gui --tray --start-bot'
    # Chạy từ mã nguồn: dùng pythonw.exe để không hiện cửa sổ console.
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    exe = pythonw if pythonw.exists() else Path(sys.executable)
    return f'"{exe}" -m bot gui --tray --start-bot'


def is_enabled() -> bool:
    if os.name != "nt":
        return False
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, VALUE_NAME)
    except OSError:
        return False
    return value == command()


def set_enabled(enabled: bool) -> None:
    if os.name != "nt":
        raise OSError("Chỉ hỗ trợ Windows")
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, command())
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass


def migrate() -> None:
    """Đã bật "Khởi động cùng Windows" bằng cách chạy khác (vd ZaloBot.exe cũ, nay dùng ZaloBot.cmd):
    trỏ lại vào cách đang chạy, để lúc đăng nhập Windows mở đúng bản này."""
    if os.name != "nt" or is_frozen():
        return
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, VALUE_NAME)
    except OSError:
        return  # chưa bật: không tự bật
    if value != command():
        try:
            set_enabled(True)
        except OSError:
            pass
