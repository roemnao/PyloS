# dispatch (Toà điều phối)

Zone: `lobby`.

Core of PyloS: bus, clock, registry, queue, permissions, scheduling. Owner only.

## Apartments

| Apartment | Holds |
|---|---|
| `bus` | message bus / router between zones |
| `clock` | shared clock (Vietnam time) |
| `registry` | which bots exist, which are running or asleep |
| `queue` | job queue |
| `envelope_log` | log of envelopes (never message content) |
| `permissions` | roles of each bot and each person |
| `scheduler` | runs scheduled jobs |
| `lifecycle` | start/stop, single-instance lock; split with side_gate is round 3 A1 |
| `handover` | moving the bot between this machine and the VPS |
| `updater` | self-update from git |
| `shared` | code every zone uses (config, data paths, file formats) |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
