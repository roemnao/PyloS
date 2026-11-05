# PyloS — rules for Claude Code

PyloS is organised as a city: `<zone>/<building>/<apartment>/`. Read [docs/architecture/city.md](docs/architecture/city.md)
before adding, moving or naming anything. Where each existing file goes: [docs/architecture/atlas.md](docs/architecture/atlas.md).

## Hard rules

1. **Merging into `main` deploys to the VPS.** `pylos-update` pulls `main` and restarts the bot. Run the tests before any merge.
2. **Keep `python -m bot run` and `python -m bot gui` working.** The VPS systemd unit (root-owned) runs
   `python -m bot run` with `PYTHONPATH=/opt/pylos/src`. Do not rename or remove the `bot` package.
3. **Never add a zone** (`management`, `gate`, `lobby`, `residential`) without asking the owner. A new building is
   allowed: add it to the atlas and tell the owner.
4. **Every tracked file has a place in the atlas.** After adding or moving a file: update
   `docs/architecture/atlas_map.toml`, `git add` the new files, run `python scripts/atlas.py` (`--check` runs in the tests).
5. **Do not change where data lives in `userdata/`** (settings, Zalo session, lock file, standby file, handover bundle)
   unless that is the task. Data moves need a backup and must be safe to run twice.

## Conventions

- New folders, files and documents in the city: **English**, folders in `snake_case`, package names lower case.
- City names, not function names: `lobby`, `gate`, `guest_house`, `hut`, `bookshelf`…
- Existing code comments and docstrings are Vietnamese: match the surrounding code when editing it.
- Status of the migration: Phase 3 done (empty skeleton in `src/pylos/`, code still in `src/bot/`). The plan is `src/pylos/management/owner/history/5-11-2026/PyloS-PLAN-thanh-chinh.md`; open owner decisions
  are listed at the end of `city.md`. The owner accepted the working assumptions (2026-11-05), so moving code (Phase 4, lobby first) may start, one PR per step.

## Finding things: one map, two layers

- **Detailed map = graphify** (`graphify-out/graph.json`: every symbol and the links between them). Rebuilt after each
  commit by the graphify git hook; by hand: `graphify update .`. Do not draw small maps of your own.
- **Zoning = the atlas** (`atlas_map.toml`: which file belongs to which building). Owner and manager bot keep it right.
- Look at one region instead of the whole city:
  - `python scripts/atlas.py region gate/fence` — files of the region and every graph link crossing its border.
  - `python scripts/atlas.py where RateLimiter` — which building a file or symbol belongs to.
- Before moving or adding code, run `region` on the target building: links to other zones that do not go through the
  `lobby` are what the migration has to remove.

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
