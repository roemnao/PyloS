"""Khung của Thành (`src/pylos/`): đủ 4 khu, đủ toà đã chốt, tên snake_case chữ thường, đường dẫn không quá dài.
Toà không cần README: mô tả nằm trong city.md và bản đồ (lobby/atlas)."""

from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
CITY = ROOT / "src" / "pylos"
ZONES = {"management", "gate", "lobby", "residential"}
BUILDINGS = {
    "management": {"owner", "managers"},
    "gate": {"main_gate", "fence", "side_gate", "guest_house"},
    "lobby": {"library", "atlas", "dispatch", "office"},
    "residential": {"residents"},
}
NAME = re.compile(r"^[a-z][a-z0-9_]*$")
# Windows giới hạn 260 ký tự cho cả đường dẫn; chừa chỗ cho thư mục cài đặt và dữ liệu người dùng.
MAX_RELATIVE_PATH = 120


def folders(path: Path) -> list[Path]:
    return sorted(p for p in path.iterdir() if p.is_dir() and p.name != "__pycache__")


def test_four_zones_exactly():
    assert {p.name for p in folders(CITY)} == ZONES


def test_every_zone_has_its_agreed_buildings():
    for zone, buildings in BUILDINGS.items():
        assert {p.name for p in folders(CITY / zone)} == buildings, zone


def test_every_folder_is_a_lowercase_snake_case_package():
    for path in CITY.rglob("*"):
        if path.relative_to(CITY).parts[2:3] == ("history",) and len(path.relative_to(CITY).parts) > 3:
            continue  # trong căn hộ history chỉ có dữ liệu (thư mục theo ngày), không phải gói Python
        if path.relative_to(CITY).parts[:2] == ("lobby", "atlas"):
            continue  # Toà bản đồ: đầu ra của graphify (dữ liệu), không phải gói Python
        if {"static", "packaging", "windows_task", "templates"} & set(path.relative_to(CITY).parts):
            continue  # file tĩnh, script build/Windows: không phải gói Python
        if path.is_dir() and path.name != "__pycache__":
            assert NAME.match(path.name), f"tên thư mục không hợp lệ: {path.relative_to(CITY)}"
            assert (path / "__init__.py").is_file(), f"thiếu __init__.py: {path.relative_to(CITY)}"


def test_longest_path_stays_short_for_windows():
    atlas = CITY / "lobby" / "atlas"  # đầu ra graphify (bộ đệm tên dài), không đóng gói vào exe
    longest = max((str(p.relative_to(ROOT)) for p in CITY.rglob("*") if atlas not in p.parents), key=len)
    assert len(longest) <= MAX_RELATIVE_PATH, longest


def test_lobby_dispatch_imports():
    assert importlib.import_module("pylos.lobby.dispatch")
