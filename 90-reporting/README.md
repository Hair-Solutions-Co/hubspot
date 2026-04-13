# Reporting

This folder owns reporting overlays, not a single standalone HubSpot scope family.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations). There is no single “reporting” scope there; reporting pulls compose other APIs (CRM, conversations, optional `marketing-email`, etc.). `crm.export` is **not** on the internal app manifest.

## Important

- The old general reports scope was deprecated.
- Modern reporting usually composes campaign, CRM, conversation, email, and export surfaces—each with its own scope requirements.

