"""regions.json: tệp phân vùng duy nhất. Mỗi file theo dõi phải rơi đúng toà (theo tiền tố đường dẫn)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
ATLAS = ROOT / "src" / "pylos" / "lobby" / "atlas"
sys.path.insert(0, str(ATLAS / "graphify_regions"))

from regions import zoning  # noqa: E402

REGIONS = ATLAS / "regions.json"


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if (ROOT / f).is_file()]


def test_regions_file_loads_and_has_the_inner_buildings():
    z = zoning.from_file(REGIONS)
    ids = {r["id"] for r in z.regions}
    assert {"lobby/dispatch", "gate/fence", "management/owner", "residential/residents"} <= ids
    assert z.external in ids and z.tests in ids


def test_pinned_regions_are_only_the_grey_outside_ones():
    data = json.loads(REGIONS.read_text(encoding="utf-8"))
    pinned = {r["id"] for r in data["regions"] if r.get("pos") or r.get("color")}
    assert pinned == {"outside/tests", "outside/repo_root", "outside/external"}


def test_every_file_under_a_building_lands_in_that_building():
    z = zoning.from_file(REGIONS)
    for f in tracked():
        parts = f.split("/")
        if parts[:2] == ["src", "pylos"] and len(parts) > 4 and parts[2] != "history":
            building = f"{parts[2]}/{parts[3]}"
            assert z.node_region("n", {"source_file": f}) == building, f


def test_tests_and_root_files_have_their_regions():
    z = zoning.from_file(REGIONS)
    assert z.node_region("n", {"source_file": "tests/lobby/dispatch/test_x.py"}) == "outside/tests"
    assert z.node_region("n", {"source_file": "README.md"}) == "outside/repo_root"
    assert z.node_region("n", {}) == "outside/external"
