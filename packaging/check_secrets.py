"""Kiểm tra bản build không chứa bí mật: chạy sau PyInstaller, trước khi dùng/chia sẻ exe.

- Không có file .env / data/ / workspace/ / logs/ nào bị đóng gói.
- Không có giá trị bí mật nào (đọc từ .env) xuất hiện trong exe (kể cả phần đã nén) hay thư mục build.

Mã thoát 0 = sạch, 1 = có vấn đề.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import dotenv_values
from PyInstaller.archive.readers import CArchiveReader

SECRET_KEYS = ("ZALO_BOT_TOKEN", "GEMINI_API_KEY", "ADMIN_TOKEN", "WEBHOOK_SECRET")
FORBIDDEN_NAMES = (".env", "data/", "data\\", "workspace/", "workspace\\", "logs/", "logs\\")


def secrets_from_env(env_path: Path) -> list[bytes]:
    values = dotenv_values(env_path) if env_path.is_file() else {}
    found = []
    for key in SECRET_KEYS:
        value = (values.get(key) or "").strip()
        if len(value) >= 8:  # giá trị quá ngắn dễ trùng ngẫu nhiên
            found += [value.encode("utf-8"), value.encode("utf-16-le")]
    return found


def check_exe(exe: Path, secrets: list[bytes]) -> list[str]:
    problems = []
    reader = CArchiveReader(str(exe))
    for name in reader.toc:
        lowered = name.replace("\\", "/").lower()
        if lowered == ".env" or lowered.endswith("/.env") or any(lowered.startswith(p.replace("\\", "/")) for p in FORBIDDEN_NAMES[1:]):
            problems.append(f"exe chứa file không được đóng gói: {name}")
        try:
            data = reader.extract(name)
        except Exception:  # noqa: BLE001 - mục đặc biệt (PYZ...) kiểm tra theo dạng thô bên dưới
            continue
        if isinstance(data, (bytes, bytearray)) and any(s in data for s in secrets):
            problems.append(f"exe chứa giá trị bí mật trong {name}")
    raw = exe.read_bytes()
    if any(s in raw for s in secrets):
        problems.append("exe chứa giá trị bí mật (dạng thô)")
    return problems


def check_dir(directory: Path, secrets: list[bytes]) -> list[str]:
    problems = []
    for path in directory.rglob("*"):
        if path.is_file() and path.stat().st_size < 200_000_000:
            data = path.read_bytes()
            if any(s in data for s in secrets):
                problems.append(f"{path} chứa giá trị bí mật")
    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    exe = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "dist" / "ZaloBot.exe"
    build_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "build"
    secrets = secrets_from_env(root / ".env")
    problems = check_exe(exe, secrets)
    if build_dir.is_dir():
        problems += check_dir(build_dir, secrets)
    if problems:
        print("KIỂM TRA BÍ MẬT THẤT BẠI:")
        for p in problems:
            print("  -", p)
        return 1
    print(f"Kiểm tra bí mật: sạch ({len(secrets) // 2} giá trị đã đối chiếu, exe {exe.stat().st_size / 1e6:.0f} MB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
