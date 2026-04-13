# Service

This folder owns Service Hub API surfaces.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- `tickets`
- `conversations.read`, `conversations.write`, `conversations.visitor_identification.tokens.create`
- `crm.objects.feedback_submissions.read`

`cms.knowledge_base.*` is **not** on the internal app manifest. Knowledge base API work requires adding the appropriate KB scopes to the app (and updating this README).

