# atlas (Toà bản đồ)

Zone: `lobby`.

Map of the whole inner city: detailed map (graphify graph) + zoning (this file). Manager bot and owner keep it right.

## Apartments

| Apartment | Holds |
|---|---|
| `maps` | city description, zoning, the generated atlas, the graphify graph |
| `generator` | atlas script: render, check, look at one region over the graph |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
