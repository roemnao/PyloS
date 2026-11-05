# residents (Toà nhà dân)

Zone: `residential`.

One apartment per bot: workspace, persona, bookshelf, memory. Only that bot and the owner enter.

## Apartments

| Apartment | Holds |
|---|---|


Apartments named `<bot_name>` are created at run time: workspace/ persona/ bookshelf/ memory/{muscle,short_term,long_term,archive}/.

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
