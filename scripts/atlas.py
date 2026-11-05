"""Atlas of the PyloS city: renders docs/architecture/atlas.md from docs/architecture/atlas_map.toml.

    python scripts/atlas.py                  regenerate atlas.md
    python scripts/atlas.py --check          exit 1 if a tracked file has no place, the map is invalid, or atlas.md is stale
    python scripts/atlas.py region gate/fence   look at one region: its files and the links crossing its border
    python scripts/atlas.py where <file|symbol> which zone/building a file or a code symbol belongs to

The zoning (which file belongs to which building) comes from atlas_map.toml. The detailed map (symbols and the links
between them) comes from graphify: graphify-out/graph.json, rebuilt after each commit by the graphify git hook.
Only files tracked by git are checked (`git add` a new file before checking).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_FILE = ROOT / "docs" / "architecture" / "atlas_map.toml"
ATLAS_FILE = ROOT / "docs" / "architecture" / "atlas.md"
GRAPH_FILE = ROOT / "graphify-out" / "graph.json"

STATUSES = {
    "agreed": "owner agreed",
    "proposed": "suggested by Claude, not reviewed by the owner yet",
    "correction": "differs from what the owner agreed; see the note",
    "open": "not decided",
}
MARK = {"agreed": "", "proposed": "🟡 proposed", "correction": "🟠 correction", "open": "🔴 open"}


@dataclass
class Rule:
    pattern: str
    target: str
    status: str
    note: str = ""
    optional: bool = False
    files: list[str] = field(default_factory=list)


def load_map(path: Path = MAP_FILE) -> tuple[list[dict], list[Rule]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rules = [Rule(r["pattern"], r["target"], r["status"], r.get("note", ""), r.get("optional", False))
             for r in data.get("file", [])]
    return data.get("zone", []), rules


def tracked_files(root: Path = ROOT) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    return sorted(p for p in out.decode("utf-8").split("\0") if p)


def places(zones: list[dict]) -> set[str]:
    """Every valid target: zone, zone/building, zone/building/apartment."""
    found = set()
    for zone in zones:
        found.add(zone["name"])
        for building in zone.get("building", []):
            found.add(f"{zone['name']}/{building['name']}")
            for apartment in building.get("apartments", []):
                found.add(f"{zone['name']}/{building['name']}/{apartment['name']}")
    return found


def specificity(pattern: str) -> tuple[bool, int]:
    # An exact path beats any glob; among globs the longest pattern wins.
    return (not any(ch in pattern for ch in "*?["), len(pattern))


def assign(files: list[str], rules: list[Rule]) -> list[str]:
    """Attach each file to its most specific rule. Returns the files no rule matches."""
    unplaced = []
    for path in files:
        matches = [r for r in rules if fnmatch.fnmatchcase(path, r.pattern)]
        if not matches:
            unplaced.append(path)
            continue
        max(matches, key=lambda r: specificity(r.pattern)).files.append(path)
    return unplaced


def problems(zones: list[dict], rules: list[Rule], unplaced: list[str]) -> list[str]:
    valid = places(zones)
    found = [f"no place in the atlas: {p}" for p in unplaced]
    for zone in zones:
        for building in zone.get("building", []):
            for apartment in building.get("apartments", []):
                if apartment.get("status", "agreed") not in STATUSES:
                    found.append(f"unknown status {apartment.get('status')!r} for apartment {apartment['name']}")
    for r in rules:
        if r.status not in STATUSES:
            found.append(f"unknown status {r.status!r} for {r.pattern}")
        if not (r.target == "open" or r.target.startswith("outside/") or r.target in valid):
            found.append(f"target {r.target!r} of {r.pattern} is not a place in the city")
        if not r.files and not r.optional:
            found.append(f"pattern matches no tracked file (remove it or set optional = true): {r.pattern}")
    return found


def render(zones: list[dict], rules: list[Rule]) -> str:
    lines = [
        "# PyloS Atlas",
        "",
        "> **Generated** by `scripts/atlas.py` from [`atlas_map.toml`](atlas_map.toml). Do not edit by hand:",
        "> edit the TOML, then run `python scripts/atlas.py`. What the city is and why: [city.md](city.md).",
        ">",
        "> Phase 1: the code has **not** moved yet. \"Current path\" is where a file is today, \"Goes to\" is its place in the city.",
        "",
        "Status: " + " · ".join(f"**{s}** = {d}" for s, d in STATUSES.items()) + ".",
        "",
        "## City tree",
        "",
        "```",
        "src/pylos/",
    ]
    for zi, zone in enumerate(zones):
        last_zone = zi == len(zones) - 1
        lines.append(f"{'└──' if last_zone else '├──'} {zone['name']}/  ({zone['vi']})")
        buildings = zone.get("building", [])
        for bi, building in enumerate(buildings):
            stem = "    " if last_zone else "│   "
            last_building = bi == len(buildings) - 1
            lines.append(f"{stem}{'└──' if last_building else '├──'} {building['name']}/  ({building['vi']})")
            apartments = building.get("apartments", [])
            for ai, apartment in enumerate(apartments):
                inner = stem + ("    " if last_building else "│   ")
                flag = "" if apartment.get("status", "agreed") == "agreed" else f"  [{apartment['status']}]"
                branch = "└──" if ai == len(apartments) - 1 else "├──"
                lines.append(f"{inner}{branch} {apartment['name']}/{flag}")
    lines += ["```", ""]

    by_target: dict[str, list[tuple[str, Rule]]] = {}
    for r in rules:
        for path in r.files:
            by_target.setdefault(r.target, []).append((path, r))

    def table(targets: list[str]) -> list[str]:
        out = ["| Current path | Goes to | Status | Note |", "|---|---|---|---|"]
        for target in targets:
            for path, r in sorted(by_target.get(target, [])):
                out.append(f"| `{path}` | `{target}` | {MARK[r.status] or 'agreed'} | {r.note} |")
        return out

    lines += ["## Where every file goes", ""]
    for zone in zones:
        lines += [f"### `{zone['name']}` — {zone['vi']}", "", zone["purpose"], ""]
        for building in zone.get("building", []):
            key = f"{zone['name']}/{building['name']}"
            lines += [f"#### `{key}` — {building['vi']}", "", building["purpose"], ""]
            apartments = building.get("apartments", [])
            lines += ["| Apartment | Holds | Status |", "|---|---|---|"]
            for apartment in apartments:
                status = apartment.get("status", "agreed")
                lines.append(f"| `{apartment['name']}` | {apartment['purpose']} | {MARK[status] or 'agreed'} |")
            lines.append("")
            targets = sorted(t for t in by_target if t == key or t.startswith(key + "/"))
            if targets:
                lines += table(targets) + [""]
            else:
                lines += ["_No existing file goes here yet._", ""]

    outside = sorted(t for t in by_target if t.startswith("outside/"))
    lines += ["## Outside the citadel", "", *table(outside), ""]
    lines += ["## Undecided (`open`)", "", "These files have no place yet; the owner decides.", "", *table(["open"]), ""]

    review = [(path, r) for r in rules if r.status in ("proposed", "correction") for path in r.files]
    lines += ["## Waiting for owner review", "", f"{len(review)} file(s) placed as `proposed` or `correction`.", ""]
    lines += ["| Current path | Goes to | Status | Note |", "|---|---|---|---|"]
    for path, r in sorted(review, key=lambda item: item[0]):
        lines.append(f"| `{path}` | `{r.target}` | {MARK[r.status]} | {r.note} |")
    lines.append("")
    return "\n".join(lines)


def build(root: Path = ROOT) -> tuple[str, list[str]]:
    zones, rules = load_map(root / MAP_FILE.relative_to(ROOT))
    unplaced = assign(tracked_files(root), rules)
    return render(zones, rules), problems(zones, rules, unplaced)


# ---------------------------------------------------------------- graphify overlay


@dataclass
class Graph:
    nodes: dict[str, dict]
    links: list[dict]
    built_at_commit: str = ""


def load_graph(path: Path = GRAPH_FILE) -> Graph | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Graph({n["id"]: n for n in data.get("nodes", [])}, data.get("links") or data.get("edges") or [],
                 data.get("built_at_commit") or "")


def file_targets(rules: list[Rule]) -> dict[str, Rule]:
    return {path: r for r in rules for path in r.files}


def district(target: str) -> str:
    """The building a target belongs to (zone/building, outside/<area> or open)."""
    return "/".join(target.split("/")[:2])


def in_region(target: str, place: str) -> bool:
    return target == place or target.startswith(place + "/")


def crossings(graph: Graph, owner: dict[str, Rule], place: str, with_tests: bool) -> tuple[list, list, dict]:
    """Links leaving and entering `place`, plus per-file link counts by the other side's building."""
    out_links, in_links = [], []
    per_file: dict[str, Counter] = defaultdict(Counter)

    def where(node: dict | None) -> tuple[str, str] | None:
        path = (node or {}).get("source_file", "")
        rule = owner.get(path)
        return (path, rule.target) if rule else None

    for link in graph.links:
        src, dst = graph.nodes.get(link.get("source")), graph.nodes.get(link.get("target"))
        a, b = where(src), where(dst)
        if not a or not b or a[0] == b[0]:
            continue
        a_in, b_in = in_region(a[1], place), in_region(b[1], place)
        if a_in == b_in:
            continue
        other = district(b[1] if a_in else a[1])
        if other == "outside/tests" and not with_tests:
            continue
        entry = (src, link.get("relation", "?"), dst, other)
        (out_links if a_in else in_links).append(entry)
        per_file[a[0] if a_in else b[0]][other] += 1
    return out_links, in_links, per_file


def graph_age(graph: Graph, root: Path = ROOT) -> str:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
    if graph.built_at_commit and head and not head.startswith(graph.built_at_commit[:12]):
        return (f"note: graph built at {graph.built_at_commit[:8]}, HEAD is {head[:8]}; "
                "run `graphify update .` if code changed since")
    return ""


def region_report(place: str, rules: list[Rule], graph: Graph | None, with_tests: bool = False, examples: int = 3) -> str:
    owner = file_targets(rules)
    files = sorted(p for p, r in owner.items() if in_region(r.target, place))
    lines = [f"# Region {place}", ""]
    if not files:
        return "\n".join(lines + ["No tracked file is placed here yet.", ""])
    if graph is None:
        lines += ["(no graphify-out/graph.json: showing files only; build it with /graphify or `graphify update .`)", ""]
    out_links, in_links, per_file = crossings(graph, owner, place, with_tests) if graph else ([], [], {})
    symbols = Counter(n.get("source_file") for n in graph.nodes.values()) if graph else Counter()

    lines += ["## Files", ""]
    for path in files:
        rule = owner[path]
        status = "" if rule.status == "agreed" else f"  [{rule.status}]"
        lines.append(f"- {path} -> {rule.target}{status}")
        if graph:
            links = ", ".join(f"{b} {n}" for b, n in per_file.get(path, Counter()).most_common()) or "none"
            lines.append(f"    {symbols.get(path, 0)} symbols; links across the border: {links}")
        if rule.note:
            lines.append(f"    note: {rule.note}")
    lines.append("")

    for title, entries in (("Links leaving the region", out_links), ("Links entering the region", in_links)):
        if not graph:
            break
        lines += [f"## {title} ({len(entries)})", ""]
        by_district: dict[str, list] = defaultdict(list)
        for entry in entries:
            by_district[entry[3]].append(entry)
        for other, group in sorted(by_district.items(), key=lambda item: -len(item[1])):
            lines.append(f"- {other}: {len(group)}")
            for src, relation, dst, _ in group[:examples]:
                lines.append(f"    {src.get('label')} ({src.get('source_file')}) --{relation}--> "
                             f"{dst.get('label')} ({dst.get('source_file')})")
        if not entries:
            lines.append("none")
        lines.append("")
    return "\n".join(lines)


def where_report(query: str, rules: list[Rule], graph: Graph | None) -> str:
    owner = file_targets(rules)
    query = query.replace("\\", "/").removeprefix("./")
    if query in owner:
        rule = owner[query]
        line = f"{query} -> {rule.target} [{rule.status}]"
        return line + (f"\n  note: {rule.note}" if rule.note else "")
    if graph is None:
        return f"{query}: not a tracked file, and there is no graph to look up symbols"
    wanted = query.lower()
    hits = [n for n in graph.nodes.values() if wanted in (n.get("label", "").lower(), n.get("norm_label", ""))]
    if not hits:
        return f"{query}: no tracked file or graph symbol with that name"
    rows = []
    for node in sorted(hits, key=lambda n: n.get("source_file", "")):
        path = node.get("source_file", "")
        rule = owner.get(path)
        place = f"{rule.target} [{rule.status}]" if rule else "(file not in the atlas)"
        rows.append(f"{node.get('label')}  {path}:{node.get('source_location', '')} -> {place}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="check only, do not write atlas.md")
    sub = parser.add_subparsers(dest="command")
    region = sub.add_parser("region", help="files of one region and the links crossing its border")
    region.add_argument("place", help="zone, zone/building, zone/building/apartment, outside/<area> or open")
    region.add_argument("--tests", action="store_true", help="also count links from tests")
    region.add_argument("--examples", type=int, default=3, help="example links per neighbouring building")
    where = sub.add_parser("where", help="which building a file or a code symbol belongs to")
    where.add_argument("query", help="a tracked path (src/bot/zalo/qr_login.py) or a symbol name (RateLimiter)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.command:
        zones, rules = load_map()
        assign(tracked_files(), rules)
        graph = load_graph()
        if args.command == "region":
            if args.place != "open" and not args.place.startswith("outside/") and args.place not in places(zones):
                print(f"{args.place!r} is not a place in the city", file=sys.stderr)
                return 2
            print(region_report(args.place, rules, graph, args.tests, args.examples))
        else:
            print(where_report(args.query, rules, graph))
        if graph and (age := graph_age(graph)):
            print(age, file=sys.stderr)
        return 0

    text, found = build()
    if args.check:
        current = ATLAS_FILE.read_text(encoding="utf-8").replace("\r\n", "\n") if ATLAS_FILE.exists() else ""
        if current != text:
            found.append(f"{ATLAS_FILE.relative_to(ROOT).as_posix()} is stale: run python scripts/atlas.py")
    else:
        ATLAS_FILE.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {ATLAS_FILE.relative_to(ROOT).as_posix()}")
    for problem in found:
        print(problem, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
