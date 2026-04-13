# Content

This folder owns CMS and content-delivery surfaces.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- `content`
- `files`, `files.ui_hidden.read`
- `hubdb`

`cms.membership.access_groups.*` is **not** on the internal app manifest. Membership API work requires adding the appropriate CMS membership scopes to the app (and updating this README).

