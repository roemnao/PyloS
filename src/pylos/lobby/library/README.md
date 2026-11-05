# library (Toà thư viện)

Zone: `lobby`.

Knowledge and skills written or vetted by the owner. All bots read.

## Apartments

| Apartment | Holds |
|---|---|
| `skills` | skills (may carry scripts) |
| `knowledge` | documents, guides |

## Rules

- Code is moved here step by step (see the migration plan); until then the apartments are empty packages.
- Anything that leaves the zone goes through `lobby/dispatch`.
- Details and access rules: [city.md](../../../../docs/architecture/city.md).

## Vetting rule

- Anything that comes from outside the city (a skill, a document, a script) is read by the owner **before** it is copied here.
- A skill may carry scripts only if it is stored here; scripts run through `lobby/office`, never straight from a bot's own apartment.
