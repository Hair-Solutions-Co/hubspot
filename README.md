# HubSpot Workspace

HubSpot engineering is organized by operational boundary first, then by scope family or build surface.

## Primary Rules

- Use two-digit prefixes with gaps so folder order stays stable without constant renames.
- Keep the platform operating layer separate from business domains.
- Keep CRM sync patterns separate from schema/property management.
- Keep HubSpot-native build surfaces under `99-development/` (last numbered folder; mirrors HubSpot’s Development area).
- Keep agent wrappers under `00-platform/20-mcp/`, not mixed into product or API folders.
- Prefer official HubSpot docs as the source of truth when endpoint versions change.
- **OAuth scope inventory** for Hair Solutions’ internal app lives in `hubspot-internal-app/src/app/app-hsmeta.json` (folder READMEs align to that manifest).

## Top-Level Map

- `00-platform/` - operational layer for auth, CLI, and MCP.
- `10-crm/` - object, schema, association, import, and sync surfaces.
- `20-marketing/` - marketing event objects, forms, social; optional marketing/transactional email scopes (see manifest).
- `30-content/` - files, HubDB, memberships, CMS assets, Design Manager-adjacent content.
- `40-sales/` - deals, leads, goals, sales-email read, automation integration specs (see manifest).
- `50-commerce/` - quotes, products, line items, orders, carts, invoices, subscriptions, e-commerce, accounting (payments/taxes may need extra scopes—see `50-commerce/payments/README.md`).
- `60-service/` - tickets, inbox, conversations, feedback submissions, visitor identification (KB API scopes not in manifest).
- `70-data-management/` - behavioral event send, users/teams settings, schema overlays; GraphQL collectors not in manifest (see `70-data-management/graphql/README.md`).
- `80-automation/` - workflow-facing integration surfaces.
- `90-reporting/` - dashboard/reporting overlays and external reporting glue.
- `95-breeze/` - HubSpot AI and app-feature surfaces that do not belong to a narrower API family.
- `98-integrations/` - cross-system HubSpot bridges that span multiple domains.
- `99-development/` - Design Manager workspace, UI extension cards, and official example apps (HubSpot “Development” analogue; kept last in the sort order).

## Ordering Rule

- `00-*` is reserved for operational foundations.
- `10-*` through `70-*` are the primary business and API domains.
- `80-*` and `90-*` are cross-domain overlays.
- `95-*` is for emerging overlay capability that is useful but not core.
- `98-*` is for connective integration work that should stay visible but not dominate the domain map.
- `99-*` is reserved for **development/build** surfaces (themes, projects, local apps) so they sort after business domains and integrations.

## Best-Practice Notes

- `00-platform/00-auth/service-keys/` is for REST-only internal automation.
- `00-platform/00-auth/oauth-apps/` is for installable apps, refresh tokens, webhooks, app features, and custom workflow actions.
- `10-crm/object-sync/`, `10-crm/property-mappings/`, and `10-crm/associations-sync/` mirror HubSpot's official example repo boundaries.
- `99-development/example-apps/` contains official reference repos, not production integrations.
- **Customer portal / Design Manager** lives in a **separate Git repository** (not committed here). Clone it into `99-development/design-manager/` beside this repo so paths in `hubspot.code-workspace` and local scripts still resolve. Theme, app, data, and ops scripts live under that checkout’s `customer-portal/`.

## OPENCLAW Defaults (local shell helper)

`OPENCLAW` in `~/.zshrc` now uses these defaults:

- `OPENCLAW_HOSTINGER_HOST=hostinger-openclaw` (SSH alias fallback)
- `OPENCLAW_DOCKER_CONTAINER=openclaw-lgzr-openclaw-1`
- `OPENCLAW_SSH_USER=root`

Required at runtime:

- `OPENCLAW_GATEWAY_TOKEN` (export in shell before running `OPENCLAW`)

Optional setup helper inputs (`OPENCLAW_SETUP`):

- `HOSTINGER_API_KEY`
- `HOSTINGER_VPS_ID`
- `HOSTINGER_API_BASE_URL` (defaults to `https://developers.hostinger.com/api/v1`)

## Core References

- Scopes: `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/scopes`
- Auth overview: `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview`
- Service keys: `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys`
- Object APIs: `https://developers.hubspot.com/docs/guides/crm/using-object-apis`
- Associations: `https://developers.hubspot.com/docs/api-reference/crm-associations-v4/guide`
- Imports: `https://developers.hubspot.com/docs/api-reference/legacy/crm/imports/guide`
=======
# hubspot
>>>>>>> a9f6e0ee68f2a3da08ae02c03a46161746d26ee2
