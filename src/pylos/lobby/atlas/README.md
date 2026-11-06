# atlas (Toà bản đồ)

Zone: `lobby`.

Map of the whole inner city for people and bots: the city description, ONE zoning file and the graphify map drawer.

## Contents

| What | Holds |
|---|---|
| `city.md` | the city: zones, buildings, apartments, rules |
| `regions.json` | the only zoning file: path prefix -> building (`rules`), a few single files (`files`) |
| `graphify_regions` | draws graphify's `graph.html` as the zone/building map (admin machine; `install.py`) |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
