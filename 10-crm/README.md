# CRM

This folder owns the API-operable CRM surface: records, properties, schemas, associations, imports, and sync logic.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- `crm.objects.contacts.*`, `companies.*`, `deals.*`, `leads.*`, `line_items.*`, `products.*`, `quotes.*`, `orders.*`, `carts.*`, `subscriptions.*`, `invoices.*`, `custom.*`, `goals.*`, `appointments.*`, `users.*`, `marketing_events.*`, `feedback_submissions.read`
- `crm.schemas.contacts.*`, `companies.*`, `deals.*`, `line_items.read`, `quotes.read`, `orders.read`, `carts.read`, `subscriptions.read`, `invoices.read`, `appointments.read`, `custom.*`
- `crm.pipelines.orders.*`
- `crm.lists.*`
- `crm.import`

`crm.export` is **not** listed on the internal app; add that scope to the app (or use another supported export path) before documenting export jobs here.

## Core Endpoint Patterns

- `GET /crm/v3/objects/{objectType}`
- `GET /crm/v3/objects/{objectType}/{id}`
- `POST /crm/v3/objects/{objectType}`
- `POST /crm/v3/objects/{objectType}/batch/read`
- `POST /crm/v3/objects/{objectType}/search`
- `PATCH /crm/v3/objects/{objectType}/{id}`
- `POST /crm/v3/objects/{objectType}/batch/update`
- `DELETE /crm/v3/objects/{objectType}/{id}`
- `POST /crm/v3/objects/{objectType}/batch/archive`

## References

- `https://developers.hubspot.com/docs/guides/crm/using-object-apis`
- `https://developers.hubspot.com/docs/api-reference/crm-associations-v4/guide`

