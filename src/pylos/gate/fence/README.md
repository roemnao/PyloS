# fence (Hàng rào)

Zone: `gate`.

Limits, inbound and outbound: the rules and the code that enforces them.

## Apartments

| Apartment | Holds |
|---|---|
| `token_limit` | token limit (whole system, per month) and rate limits |
| `speech_limit` | what may be said / what is a request to the bot |
| `ethics` | ethics rules |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).
