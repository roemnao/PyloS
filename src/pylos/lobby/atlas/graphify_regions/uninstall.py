"""Gỡ graphify-regions khỏi graphify (trả graphify về như cũ)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from install import find_target, strip_block

HERE = Path(__file__).resolve().parent


def main() -> int:
    target = Path(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else find_target()
    html_py = target / "exporters" / "html.py"
    html_py.write_text(strip_block(html_py.read_text(encoding="utf-8")), encoding="utf-8")
    shutil.rmtree(target / "regions", ignore_errors=True)
    for pyc in (target / "exporters" / "__pycache__").glob("html*.pyc"):
        pyc.unlink(missing_ok=True)
    backups = sorted((HERE / "backup").glob("html.py.*"))
    same = backups and html_py.read_text(encoding="utf-8") == backups[-1].read_text(encoding="utf-8")
    print("da go graphify-regions;", "html.py trung ban sao luu" if same else "html.py khac ban sao luu (graphify co the da nang cap)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
