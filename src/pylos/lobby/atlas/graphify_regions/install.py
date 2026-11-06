r"""Cài graphify-regions vào graphify đã cài bằng `uv tool` (chạy lại sau mỗi lần nâng cấp graphify).

    python install.py              # cài (chạy lại bao nhiêu lần cũng được)
    python install.py --target <thư mục site-packages\graphify>   # cài vào chỗ khác (dùng cho test)
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEGIN = "    # graphify-regions:begin"
END = "    # graphify-regions:end"
LAST_LINE = "    write_text_atomic(output_path, html)"
BLOCK = f"""{BEGIN} ({HERE} - go bang uninstall.py)
    if not member_counts:
        try:
            from graphify.regions import apply_regions
            html = apply_regions(html, G, communities, community_labels, vis_nodes, output_path)
        except Exception as exc:  # khong bao gio lam hong graph.html goc
            print(f"[graphify regions] bo qua: {{exc}}")
{END}
"""
TESTED = "0.9.100"


def find_target() -> Path:
    out = subprocess.run(["uv", "tool", "dir"], capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        raise SystemExit("khong chay duoc `uv tool dir`: dung --target <thu muc site-packages/graphify>")
    cand = Path(out.stdout.strip()) / "graphifyy" / "Lib" / "site-packages" / "graphify"
    if not cand.is_dir():
        raise SystemExit(f"khong thay graphify o {cand}")
    return cand


def strip_block(text: str) -> str:
    return re.sub(rf"{re.escape(BEGIN)}.*?{re.escape(END)}\n", "", text, flags=re.S)


def install(target: Path) -> str:
    html_py = target / "exporters" / "html.py"
    if not html_py.is_file():
        raise SystemExit(f"khong thay {html_py}")
    text = strip_block(html_py.read_text(encoding="utf-8"))
    start = text.find("def to_html(")
    if start < 0 or text.count(LAST_LINE, start) != 1:
        raise SystemExit("khong tim thay dung mot cho chen trong to_html: khong ghi gi")
    pos = text.index(LAST_LINE, start)
    html_py.write_text(text[:pos] + BLOCK + text[pos:], encoding="utf-8")
    dest = target / "regions"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(HERE / "regions", dest, ignore=shutil.ignore_patterns("__pycache__"))
    for pyc in (target / "exporters" / "__pycache__").glob("html*.pyc"):
        pyc.unlink(missing_ok=True)
    meta = list(target.parent.glob("graphifyy-*.dist-info"))
    version = meta[0].name.split("-")[1].replace(".dist", "") if meta else "?"
    return version


def main() -> int:
    target = Path(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else find_target()
    version = install(target)
    print(f"da cai graphify-regions vao {target} (graphify {version})")
    if version != TESTED:
        print(f"canh bao: moi thu voi graphify {TESTED}; graphify {version} chua thu. Chay pytest trong {HERE / 'tests'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
