"""Chèn bản đồ vùng vào chuỗi HTML của graphify theo các mốc. Thiếu mốc nào thì không chèn gì (RegionsSkip)."""

from __future__ import annotations

import json

from . import assets


class RegionsSkip(Exception):
    """Không vẽ được bản đồ vùng (mẫu HTML đổi, cấu hình sai...): graphify ghi graph.html gốc."""


BEGIN, END = "/* graphify-regions:begin */", "/* graphify-regions:end */"
HBEGIN, HEND = "<!-- graphify-regions:begin -->", "<!-- graphify-regions:end -->"

# (nguyên bản graphify, bản đã chèn). Bản "đã chèn" dùng @Region@ cho từ cấp vùng.
SEED = """  x: 30 * Math.sqrt(i) * Math.cos(i * 2.4),
  y: 30 * Math.sqrt(i) * Math.sin(i * 2.4),"""
SEED_PATCHED = "  x: (GREG_LAYOUT.pos[n.id] || [0, 0])[0], y: (GREG_LAYOUT.pos[n.id] || [0, 0])[1], /* greg */"
PHYS = "  physics: {\n    enabled: true,"
PHYS_PATCHED = "  physics: {\n    enabled: false, /* greg */"
NODE_LINE = "  id: n.id, label: n.label, color: n.color, size: n.size,"
NODE_LINE_PATCHED = "  id: n.id, label: n.label, color: GREG.nodeColor(n.id), shape: GREG.nodeShape(n.id), size: n.size, /* greg */"
EDGE_LINES = "  width: e.width,\n  color: e.color,"
EDGE_LINES_PATCHED = "  width: GREG.edgeWidth(e), /* greg */\n  color: GREG.edgeColor(e), hidden: GREG.edgeHidden(e),"
SEARCH_LINE = "el.style.borderLeft = `3px solid ${n.color.background}`;"
SEARCH_LINE_PATCHED = "el.style.borderLeft = `3px solid ${nodesDS.get(n.id).color.background}`; /* greg */"
INFO_ANCHOR = '  html += `<div class="field">Community: '
INFO_PATCHED = ('  html += `<div class="field">@Region@: ${esc(GREG.regionLabel(n.id))}</div><div class="field">Loại code: '
                '${esc(GREG.kindLabel(n.id))}</div>`; /* greg */\n') + INFO_ANCHOR
DOT = '<div class="legend-dot" style="background:${c.color}"></div>'
DOT_PATCHED = '<div class="legend-dot" style="background:transparent;border:1.5px dashed var(--text-2)"></div>'
ANCHOR = "const nodesDS = new vis.DataSet("
THEME = "// Theme toggle"
STYLE_END = "</style>"
GRAPH_DIV = '<div id="graph"></div>'
REPLACEMENTS = [(SEED, SEED_PATCHED), (PHYS, PHYS_PATCHED), (NODE_LINE, NODE_LINE_PATCHED), (EDGE_LINES, EDGE_LINES_PATCHED),
                (SEARCH_LINE, SEARCH_LINE_PATCHED), (INFO_ANCHOR, INFO_PATCHED), (DOT, DOT_PATCHED)]
INSERT_BEFORE = [ANCHOR, THEME, STYLE_END]
INSERT_AFTER = [GRAPH_DIV]


def _wrap(begin: str, end: str, body: str) -> str:
    return f"{begin}\n{body}\n{end}"


def missing_anchors(html: str) -> list[str]:
    return [a for a in [o for o, _ in REPLACEMENTS] + INSERT_BEFORE + INSERT_AFTER if a not in html]


def apply_patch(html: str, data: dict) -> str:
    """Chèn bản đồ vùng vào graph.html mới sinh. Thiếu mốc nào thì ném RegionsSkip, không trả về HTML nửa vời."""
    if BEGIN in html:
        raise RegionsSkip("graph.html đã có bản đồ vùng")
    lost = missing_anchors(html)
    if lost:
        raise RegionsSkip("graphify đổi mẫu graph.html, thiếu mốc: " + "; ".join(repr(a[:50]) for a in lost))
    levels = data.get("levels") or {}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    for original, patched in REPLACEMENTS:
        html = html.replace(original, assets.fill(patched, levels), 1)
    js_data = assets.fill(assets.JS_DATA, levels).replace("__DATA__", blob)
    html = html.replace(ANCHOR, _wrap(BEGIN, END, js_data) + "\n" + ANCHOR, 1)
    html = html.replace(THEME, _wrap(BEGIN, END, assets.fill(assets.JS_BEHAVIOR, levels)) + "\n" + THEME, 1)
    html = html.replace(STYLE_END, _wrap(BEGIN, END, assets.CSS) + "\n" + STYLE_END, 1)
    html = html.replace(GRAPH_DIV, GRAPH_DIV + "\n" + _wrap(HBEGIN, HEND, assets.HTML), 1)
    return html
