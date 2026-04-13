# 50-commerce — Cheatsheet

## Mental model

| Surface | Direction | Strategy |
|---------|-----------|----------|
| Products / line-items | Local → HubSpot | Define catalog locally; push via API. HubDB is the primary catalog for the customer portal — keep aligned. |
| Orders | Pull only | Shopify is source of truth. Pull HubSpot order records for CRM views and reporting snapshots. |
| Quotes | Pull weekly | UI-managed. Pull for reporting. No local edits. |
| Invoices | Pull as needed | Read-only audit trail for service/support context. |
| Subscriptions | Pull + watch | Sync subscription status to contact properties for segmentation. |
| Payments | Blocked | Scope missing — see below. |
| Taxes | Blocked | Scope missing — see below. |

## Scopes in the internal app manifest

All of the following are present in `hubspot-internal-app/src/app/app-hsmeta.json`:

- `e-commerce`
- `accounting`
- `crm.objects.quotes.*` + `crm.schemas.quotes.read`
- `crm.objects.line_items.*` + `crm.schemas.line_items.read`
- `crm.objects.products.*`
- `crm.objects.orders.*` + `crm.schemas.orders.read` + `crm.pipelines.orders.read/write`
- `crm.objects.carts.*` + `crm.schemas.carts.read`
- `crm.objects.invoices.*` + `crm.schemas.invoices.read`
- `crm.objects.subscriptions.*` + `crm.schemas.subscriptions.read`

## Scope gaps — action required before using these endpoints

| Scope | Status | Action |
|-------|--------|--------|
| `crm.objects.commercepayments.read` | **NOT in manifest** | Add to `app-hsmeta.json` before calling `/crm/v3/objects/payments` |
| `tax_rates.read` | **NOT in manifest** | Add to `app-hsmeta.json` before calling `/tax-rates/v3/tax-rates` |

Do not assume payment or tax endpoints are authorized. Add scopes, redeploy app, then test.

## Key API calls by subfolder

**invoices** — `GET/POST/PATCH /crm/v3/objects/invoices`, `POST /crm/v3/objects/invoices/search`

**orders** — `GET/POST/PATCH /crm/v3/objects/orders`, `POST /crm/v3/objects/orders/search`

**payments** — `GET /crm/v3/objects/payments`, `POST /crm/v3/objects/payments/search` *(scope required first)*

**products-line-items** — `GET/POST/PATCH /crm/v3/objects/products`, `GET/POST /crm/v3/objects/line_items`

**quotes** — `GET/POST/PATCH/DELETE /crm/v3/objects/quotes`, `POST /crm/v3/objects/quotes/search`

**subscriptions** — `GET/POST/PATCH /crm/v3/objects/subscriptions`, `POST /crm/v3/objects/subscriptions/search`

**taxes** — `GET /tax-rates/v3/tax-rates`, `GET /tax-rates/v3/tax-rates/{taxRateId}` *(scope required first)*

## Customer portal note

Orders in the customer portal are Deals (mirror), not native HubSpot orders — membership GraphQL doesn't expose commerce orders. The `50-commerce/orders/` folder covers the HubSpot commerce orders API, which is separate from the portal's Deals-as-orders pattern in `99-development/`.

HubDB is the product catalog for the portal: `products`, `affiliated_locations`, `subscription_plans` tables. Keep HubDB in sync with this folder's product definitions.

## What not to do

- Do not use HubSpot as the source of truth for orders — Shopify owns orders
- Do not touch payment or tax endpoints until scopes are added to the manifest
- Do not duplicate product definitions between HubDB and `products/` — treat them as one canonical source
