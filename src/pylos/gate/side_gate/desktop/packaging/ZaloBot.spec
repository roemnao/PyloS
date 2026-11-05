# -*- mode: python ; coding: utf-8 -*-
# Build: powershell -ExecutionPolicy Bypass -File src\pylos\gate\side_gate\desktop\packaging\build-exe.ps1
# Một file ZaloBot.exe, dạng cửa sổ (không console). Không bao giờ đóng gói userdata/ (khoá, dữ liệu, log).
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = next(p for p in Path(SPECPATH).parents if (p / "pyproject.toml").is_file())  # thư mục dự án (đi ngược từ packaging/)
PACK = Path(SPECPATH)
sys.path.insert(0, str(ROOT / "src"))

from pylos.gate.side_gate.desktop.icon_images import write_ico  # noqa: E402

icon = write_ico(ROOT / "build" / "zalobot.ico")

# File không phải .py trong package: ui/admin/static/*, templates/* (mẫu .env, SYSTEM.md, MEMORY.md, tool mẫu).
# pylos: chỉ lấy file mẫu (templates) và file tĩnh của trang quản trị: phải khớp package-data trong pyproject.toml. KHÔNG đóng gói lịch sử/kế hoạch riêng (owner/history), tài liệu, bản đồ, script build.
datas = collect_data_files("bot") + collect_data_files(
    "pylos", includes=["lobby/dispatch/shared/templates/*", "management/owner/admin_web/static/*",
                       "management/owner/admin_web/static/fonts/*"])

hiddenimports = (
    collect_submodules("bot")
    + collect_submodules("pylos")
    + collect_submodules("uvicorn")
    + collect_submodules("google.genai")
    # Chế độ acc Zalo cá nhân (đăng nhập QR) import zlapi lúc chạy nên PyInstaller không tự thấy.
    + collect_submodules("zlapi")
    + ["webview.platforms.edgechromium", "webview.platforms.winforms", "pystray._win32"]
)

a = Analysis(
    [str(PACK / "zalobot_entry.py")],
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
    version=str(PACK / "version_info.txt"),
    upx=False,  # UPX làm Windows Defender báo nhầm nhiều hơn
    debug=False,
    strip=False,
    runtime_tmpdir=None,
)
