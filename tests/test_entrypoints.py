"""Lưới an toàn khi dời code: lối vào `python -m bot`, gói trong exe, package-data và lệnh cài đặt phải còn đúng.

VPS chạy `python -m bot run` với PYTHONPATH=/opt/pylos/src (service do root cài), nên các test này phải đỏ
trước khi một thay đổi cấu trúc làm bot không lên lại sau lần cập nhật tự động.
"""

from __future__ import annotations

import importlib
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OPTIONAL_LIBS = {"webview", "pystray", "PIL", "zlapi", "requests"}  # nhóm desktop / personal, có thể chưa cài


def top_packages() -> list[str]:
    return sorted(p.name for p in SRC.iterdir() if (p / "__init__.py").is_file())


def all_modules() -> list[str]:
    mods = []
    for path in SRC.rglob("*.py"):
        parts = path.relative_to(SRC).with_suffix("").parts
        if "__pycache__" in parts:
            continue
        mods.append(".".join(parts[:-1] if parts[-1] == "__init__" else parts))
    return sorted(mods)


@pytest.mark.parametrize("module", [m for m in all_modules() if not m.endswith("__main__")])
def test_every_module_imports(module):
    try:
        importlib.import_module(module)
    except ModuleNotFoundError as exc:
        if (exc.name or "").split(".")[0] in OPTIONAL_LIBS:
            pytest.skip(f"thiếu thư viện tuỳ chọn {exc.name}")
        raise


def test_python_dash_m_bot_still_works():
    """Lối vào của service trên VPS: `python -m bot ...` với PYTHONPATH=src."""
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONIOENCODING": "utf-8"}
    done = subprocess.run([sys.executable, "-m", "bot", "--help"], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=60)
    assert done.returncode == 0, done.stderr
    for command in ("run", "gui", "gateway", "admin", "update"):
        assert command in done.stdout


def test_console_script_targets_exist():
    scripts = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
    for name, target in scripts.items():
        module, _, func = target.partition(":")
        assert callable(getattr(importlib.import_module(module), func, None)), f"{name} = {target} không tồn tại"


def test_package_data_patterns_match_files():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["setuptools"]["package-data"]
    for package, patterns in data.items():
        for pattern in patterns:
            assert list((SRC / package).glob(pattern)), f"package-data {package}/{pattern} không khớp file nào"


def test_every_top_level_package_is_bundled_into_the_exe():
    spec = (ROOT / "scripts" / "packaging" / "ZaloBot.spec").read_text(encoding="utf-8")
    for package in top_packages():
        assert re.search(rf'collect_submodules\("{package}"\)', spec), f"ZaloBot.spec thiếu collect_submodules({package!r})"
        assert re.search(rf'collect_data_files\("{package}"\)', spec), f"ZaloBot.spec thiếu collect_data_files({package!r})"
