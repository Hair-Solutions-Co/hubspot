# Marketing

This folder owns HubSpot marketing API surfaces and their operational boundaries.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- **Required:** `crm.objects.marketing_events.read`, `crm.objects.marketing_events.write`, `forms`, `social`
- **Optional (install-time):** `marketing-email`, `transactional-email`

Campaigns, communication preferences, business units, business intelligence, and related scope families are **not** on the internal app manifest; add scopes there (and document here) before relying on those APIs.

