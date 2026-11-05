# managers (Toà quản lý)

Zone: `management`.

What manager bots read to manage other bots.

## Apartments

| Apartment | Holds |
|---|---|
| `guidelines` | principles for manager bots |
| `bot_commands` | commands that act on bots |
| `plans` | public plans |
| `evaluations` | weekly bot scores |
| `reports` | reports |
| `bot_list` | list of bots and their on/off switch |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
