"""regions.json: tệp phân vùng duy nhất (tiền tố đường dẫn -> toà). Mỗi file trong một toà phải rơi đúng toà đó."""

import json
import subprocess
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
DATA = json.loads((ROOT / "src" / "pylos" / "lobby" / "atlas" / "regions.json").read_text(encoding="utf-8"))
IDS = {r["id"] for r in DATA["regions"]}


def region_of(path: str) -> str:
    """Giống graphify-regions: file lẻ thắng, rồi tiền tố dài nhất, không khớp thì unplaced_region."""
    if path in DATA.get("files", {}):
        return DATA["files"][path]
    hits = [r for r in DATA.get("rules", []) if path.startswith(r["prefix"])]
    return max(hits, key=lambda r: len(r["prefix"]))["region"] if hits else DATA["unplaced_region"]


def test_every_region_named_in_rules_and_files_exists():
    used = {r["region"] for r in DATA["rules"]} | set(DATA["files"].values())
    used |= {DATA["unplaced_region"], DATA["external_region"], DATA["tests_region"]}
    assert used <= IDS, used - IDS


def test_pinned_regions_are_only_the_grey_outside_ones():
    pinned = {r["id"] for r in DATA["regions"] if r.get("pos") or r.get("color")}
    assert pinned == {"outside/tests", "outside/repo_root", "outside/external"}


def test_every_file_under_a_building_lands_in_that_building():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for f in out.splitlines():
        parts = f.split("/")
        if parts[:2] == ["src", "pylos"] and len(parts) > 4:
            assert region_of(f) == f"{parts[2]}/{parts[3]}", f


def test_tests_and_root_files_have_their_regions():
    assert region_of("tests/lobby/dispatch/test_x.py") == "outside/tests"
    assert region_of("README.md") == "outside/repo_root"
