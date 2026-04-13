# Sales

This folder owns sales-facing CRM and scheduler surfaces.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- `crm.objects.deals.read`, `crm.objects.deals.write`
- `crm.objects.leads.read`, `crm.objects.leads.write`
- `crm.objects.goals.read`, `crm.objects.goals.write`
- `sales-email-read`
- `automation` (workflow-related APIs; not the same as a dedicated “sequences” scope string)

Meeting links, scheduler APIs, and any `automation.sequences.*`-style scopes are **not** on the internal app manifest. Sequences and meetings can still be **documented or operated in the HubSpot UI** without implying those scopes are granted.

