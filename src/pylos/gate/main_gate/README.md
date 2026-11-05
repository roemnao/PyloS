# main_gate (Cổng chính)

Zone: `gate`.

Connections to the outer city, sessions, outside logs.

## Apartments

| Apartment | Holds |
|---|---|
| `zalo` | personal account, Bot Platform, QR login, polling, webhook |
| `external_apps` | third-party apps and APIs |
| `external_bots` | bots outside PyloS |
| `sessions` | sessions between bots and the outside |
| `logs` | logs of outside traffic |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
