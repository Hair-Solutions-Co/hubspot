# HubSpot OAuth Scopes Reference
**App:** HSC Internal Integrations
**Last reviewed:** 2026-04-05
**Source of truth:** [HubSpot OAuth Scopes docs](https://developers.hubspot.com/docs/api-reference/overview)

---

## How This File is Organised

Scopes are grouped by functional area. Each entry shows:
- The exact scope string that appears in `app-hsmeta.json`
- Why it's present for this integration
- Which bucket it lives in (`required` vs `optional`)

A scope marked **`TODO: verify`** means its exact string was not confirmed from today's official docs pull — verify at https://developers.hubspot.com/docs/api/overview before promoting it.

---

## 1. Core Authentication

| Scope | Bucket | Why |
|-------|--------|-----|
| `oauth` | required | Base OAuth scope — required for all OAuth-based public apps. Grants access to basic account information and is the prerequisite for every other scope. |

---

## 2. CRM Objects — Read / Write

These scopes power the core CRM sync between HubSpot and downstream connectors (Shopify customer data, ClickUp contact tasks).

| Scope | Bucket | Why |
|-------|--------|-----|
| `crm.objects.contacts.read` | required | Read customer contact records — needed by every connector that looks up contacts before taking action. |
| `crm.objects.contacts.write` | required | Create/update contacts — needed for Shopify → HubSpot customer sync and Hair Concierge app enrollments. |
| `crm.objects.companies.read` | required | Read company records — needed for B2B context lookups. |
| `crm.objects.deals.write` | required | Create and update deals — needed for order-to-deal sync from Shopify. |
| `crm.objects.leads.read` | required | Read lead objects — needed for intake pipeline reads. |
| `crm.objects.leads.write` | required | Create/update leads — needed for enrollment automations triggered by Shopify checkouts. |
| `crm.objects.line_items.read` | required | Read deal line items — needed to reconcile order products in HubSpot. |
| `crm.objects.line_items.write` | required | Write deal line items — needed to push Shopify product lines into deals. |
| `crm.objects.products.read` | required | Read the Products library — needed to match Shopify SKUs against HubSpot products. |
| `crm.objects.products.write` | required | Write to the Products library — needed to sync the Shopify product catalog. |
| `crm.objects.quotes.read` | required | Read quote objects — needed to audit outstanding proposals. |
| `crm.objects.quotes.write` | required | Create/update quotes — needed if generating proposals from HubSpot data. |
| `tickets` | required | Read and write service tickets — needed for support integrations and service routing workflows. |

### Not yet confirmed — mark required before promoting:

> **TODO: verify** `crm.objects.companies.write` — write access to company records. The exact scope string was not seen in today's docs pull. Verify at https://developers.hubspot.com/docs/api/crm/companies before adding to `requiredScopes`.

> **TODO: verify** `crm.objects.deals.read` — the read variant of the deals scope. The `.write` form was confirmed; verify that `.read` is the expected string for read-only access.

---

## 3. E-Commerce Objects

These scopes support the Shopify connector and any payment/subscription syncs.

| Scope | Bucket | Why |
|-------|--------|-----|
| `crm.objects.orders.read` | optional | Read HubSpot order objects — needed for order status lookups. |
| `crm.objects.orders.write` | optional | Write order objects — needed to create/update orders from Shopify webhook data. |
| `crm.objects.carts.read` | optional | Read cart objects — needed for abandoned cart workflows. |
| `crm.objects.carts.write` | optional | Write cart objects — needed to persist Shopify cart events in HubSpot. |
| `crm.objects.subscriptions.read` | optional | Read subscription objects — needed to check active plans for hair system maintenance. |
| `crm.objects.subscriptions.write` | optional | Write subscription objects — needed to enroll/unenroll customers in recurring plans. |
| `crm.objects.invoices.read` | optional | Read invoice objects — needed for billing reconciliation. |
| `crm.objects.invoices.write` | optional | Write invoice objects — needed to sync invoices from payment processor. |
| `e-commerce` | optional | Broad e-commerce access (carts, checkouts, orders) — acts as a compatibility scope for older e-commerce API calls. Keep optional until Shopify connector is fully wired. |

---

## 4. Media / Files

| Scope | Bucket | Why |
|-------|--------|-----|
| `media_bridge.read` | optional | Read media assets and media events — needed if syncing Cloudinary media references into HubSpot. |

### Not yet confirmed:

> **TODO: verify** `files` — File Manager read/write scope. Required if you want to upload or manage files directly in HubSpot's File Manager (e.g., product images). Verify the exact scope string at https://developers.hubspot.com/docs/api/files/files.

---

## 5. Workflows / Automation

| Scope | Bucket | Why |
|-------|--------|-----|
| `automation` | required | Read and write HubSpot workflows — needed to trigger, enrol, and inspect workflow runs from external connectors. Confirmed scope string from official docs (described as "Workflows"). |

---

## 6. Pipeline / Deal Stages

| Scope | Bucket | Why |
|-------|--------|-----|
| `crm.pipelines.orders.read` | optional | Read order pipeline and stage definitions — needed for Shopify order status → stage mapping. |
| `crm.pipelines.orders.write` | optional | Manage order pipeline configuration — needed to add stages when new fulfilment states are introduced. |

---

## 7. Other CRM Objects (utility)

| Scope | Bucket | Why |
|-------|--------|-----|
| `crm.objects.custom.read` | optional | Read custom CRM objects — needed to access any bespoke objects created for HSC (e.g., Hair System, Production Unit). |
| `crm.objects.custom.write` | optional | Write custom CRM objects — needed to create/update bespoke records from integration events. |
| `crm.objects.goals.read` | optional | Read goal objects — needed for reporting dashboards. |
| `crm.objects.goals.write` | optional | Write goal objects — needed if automating target-setting from ClickUp milestones. |
| `crm.objects.appointments.read` | optional | Read appointment objects — needed for consultation scheduling reads. |
| `crm.objects.appointments.write` | optional | Write appointment objects — needed if a Calendly/booking integration is added. |
| `crm.objects.users.read` | optional | Read HubSpot user CRM objects — needed for internal assignment and routing logic. |
| `crm.objects.users.write` | optional | Write user CRM objects — needed if auto-assigning contacts to reps from external events. |

---

## 8. Scopes NOT Yet Added (pending verification)

The following scope categories are relevant to this integration but were not confirmed from the current official docs pull. Verify the exact strings before adding them.

| Intended Access | Likely Scope String | Verify At |
|----------------|---------------------|-----------|
| CMS blog / website pages read+write | `content` | https://developers.hubspot.com/docs/api/cms/blog-post |
| File Manager read+write | `files` | https://developers.hubspot.com/docs/api/files/files |
| HubDB tables read+write | `hubdb` | https://developers.hubspot.com/docs/api/cms/hubdb |
| Conversations inbox read | `conversations.read` | https://developers.hubspot.com/docs/api/conversations/conversations |
| Conversations inbox write | `conversations.write` | same as above |
| CRM property schemas read | `crm.schemas.contacts.read` | https://developers.hubspot.com/docs/api/crm/properties |
| Custom object schemas read | `crm.schemas.custom.read` | same as above |
| User management settings | `settings.users.read` | https://developers.hubspot.com/docs/api/settings/user-management |
| User management write | `settings.users.write` | same as above |

---

## Expanding Scopes Later

1. Open `src/app/app-hsmeta.json`.
2. Add the new scope string to `requiredScopes` or `optionalScopes`.
3. Run `hs project upload` to push the updated config.
4. HubSpot will prompt users to re-authorise if new required scopes were added.
5. Document the change in this file with the date and reason.
