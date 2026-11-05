# office (Toà văn phòng)

Zone: `lobby`.

Plugins and agent tools, plus the warehouse for generated files. Only the owner adds plugins.

## Apartments

| Apartment | Holds |
|---|---|
| `drawing` | drawing plugin |
| `documents` | docx / text presentation plugins |
| `code` | code plugin |
| `agent_tools` | tools the agent can call |
| `warehouse` | generated files, stored by type |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
