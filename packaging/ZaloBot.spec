# -*- mode: python ; coding: utf-8 -*-
# Build: powershell -ExecutionPolicy Bypass -File scripts\build-exe.ps1
# Một file ZaloBot.exe, dạng cửa sổ (không console). Không bao giờ đóng gói .env, data/, workspace/.
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent
sys.path.insert(0, str(ROOT / "src"))

from bot.ui.desktop.icons import write_ico  # noqa: E402

icon = write_ico(ROOT / "build" / "zalobot.ico")

# File không phải .py trong package: admin/static/*, templates/* (mẫu .env, SYSTEM.md, MEMORY.md, tool mẫu).
datas = collect_data_files("bot")

hiddenimports = (
    collect_submodules("bot")
    + collect_submodules("uvicorn")
    + collect_submodules("google.genai")
    # Chế độ acc Zalo cá nhân (đăng nhập QR) import zlapi lúc chạy nên PyInstaller không tự thấy.
    + collect_submodules("zlapi")
    + ["webview.platforms.edgechromium", "webview.platforms.winforms", "pystray._win32"]
)

a = Analysis(
    [str(ROOT / "packaging" / "zalobot_entry.py")],
    pathex=[str(ROOT / "src")],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "pytest", "_pytest", "IPython"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ZaloBot",
    console=False,
    icon=str(icon),
    version=str(ROOT / "packaging" / "version_info.txt"),
    upx=False,  # UPX làm Windows Defender báo nhầm nhiều hơn
    debug=False,
    strip=False,
    runtime_tmpdir=None,
)
