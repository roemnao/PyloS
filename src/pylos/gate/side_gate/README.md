# side_gate (Cổng phụ)

Zone: `gate`.

Technical entry: receives commands from the owner, the VPS and MCP.

## Apartments

| Apartment | Holds |
|---|---|
| `vps` | VPS connection and control |
| `mcp` | MCP connections |
| `owner_commands` | commands only the owner may run |
| `shell` | cmd/shell commands |
| `emergency` | emergency requests from the main gate |
| `desktop` | Windows desktop app (window + tray) |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
