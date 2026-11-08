# PyloS — rules for Claude Code

PyloS is organised as a city: `<zone>/<building>/<apartment>/`. Read [city.md](src/pylos/lobby/atlas/city.md)
before adding, moving or naming anything. Which building a file belongs to: [regions.json](src/pylos/lobby/atlas/regions.json) (path prefix -> building).

## Hard rules

1. **Merging into `main` deploys to the VPS.** `pylos-update` pulls `main` and restarts the bot. Run the tests before any merge.
2. **Keep `python -m bot run` and `python -m bot gui` working.** The VPS systemd unit (root-owned) runs
   `python -m bot run` with `PYTHONPATH=/opt/pylos/src`. Do not rename or remove the `bot` package.
3. **Never add a zone** (`management`, `gate`, `lobby`, `residential`) without asking the owner. A new building is
   allowed: add a line to `regions.json` `rules` and tell the owner.
4. **Every tracked file has a building.** `src/pylos/lobby/atlas/regions.json` maps path prefixes to buildings; files under
   `src/pylos/<zone>/<building>/` need nothing. Only a new building or a new top-level folder needs one line in `rules` (the tests check it).
5. **Do not change where data lives** (settings in `management/owner/secrets`, Zalo session, lock/standby/log files in
   `management/owner/runtime`, chat data in `gate/guest_house/data`, the bot's `workspace/` in `residential/residents/pylos` (git tracks it; the bot reads every file in it), the bot's general rules `gate/fence/SYSTEM.md`,
   handover bundle) unless that is the task. Data moves need a backup and must be safe to run twice (see `userdata_paths.migrate_to_city`).

## Conventions

- New folders, files and documents in the city: **English**, folders in `snake_case`, package names lower case.
- City names, not function names: `lobby`, `gate`, `guest_house`, `hut`, `bookshelf`…
- Existing code comments and docstrings are Vietnamese: match the surrounding code when editing it.
- Status of the migration: phases 3–5 and 8.1 done (see city.md status); modules moved to `src/pylos/` leave an alias signpost in `src/bot/`. Edit the real module in `src/pylos/`, never the signpost. The plan is `src/pylos/management/owner/history/5-11-2026/PyloS-PLAN-thanh-chinh.md`; open owner decisions
  are listed at the end of `city.md`. The owner accepted the working assumptions (2026-11-05), so moving code (Phase 4, lobby first) may start, one PR per step.

## Finding things: one map

- **The map is `src/pylos/lobby/atlas/`**: all graphify output lives there (`graph.html` to look at, `GRAPH_REPORT.md` to
  read first, `graph.json`), plus `city.md` and `regions.json`. No `__init__.py`, no README: it is data, not a package.
  On the admin machine `graphify-out/` at the repo root is a junction to it, so every `graphify-out/...` path below works.
  Rebuilt after each commit by the graphify git hook; by hand: `graphify update .`, or `/graphify` to redraw everything.
  Do not draw small maps of your own. Buildings have no README either: their purpose is in `city.md` and on the map.
- **Zoning = `regions.json`** (the only zoning file): path prefix -> building. Owner and manager bot keep it right.
- The zone/building drawing is an add-on of the `/graphify` skill (`~/.claude/skills/graphify/regions_addon/`, backup and
  heavy tests in `C:/Users/tp/graphify-regions`). Step 0.5 of the skill re-installs it into graphify when missing (also after
  `uv tool upgrade graphifyy`) and makes `graphify-out` point at `regions.out` from `.graphifyrc`. Colour = building, shape = kind of code,
  dashed outline = community, `?` button = legend. ONE centre building is picked (call links + node count + biggest node;
  override: `"center"` in regions.json), the others go into rings by how many links reach the inner rings, each zone gets an
  angular sector, and colour follows the ring (centre and ring 1 distinct warm, ring 2+ cool, no yellow-green; lightness adapts
  to the theme). `outside/tests|repo_root|external` stay pinned and grey at the bottom. A machine without it builds a plain `graph.html`.
- Before moving or adding code, look at the target building in `graph.html` (click a building) or ask `graphify query`:
  links to other zones that do not go through the `lobby` are what the migration has to remove.

## Tests

```bash
pip install -e ".[dev,desktop,personal,build]"
pytest -q
```

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
