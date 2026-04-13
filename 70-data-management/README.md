# Data Management

This folder owns model-level and analytical data surfaces that sit above raw record CRUD.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- `analytics.behavioral_events.send`
- `settings.users.read`, `settings.users.write`, `settings.users.teams.read`, `settings.users.teams.write`
- `crm.schemas.*` (overlaps with `10-crm/`; object-type coverage matches the manifest)

`collector.graphql_query.execute`, `collector.graphql_schema.read`, and `behavioral_events.event_definitions.read_write` are **not** on the internal app manifest. See `graphql/README.md` for GraphQL scope gaps.

