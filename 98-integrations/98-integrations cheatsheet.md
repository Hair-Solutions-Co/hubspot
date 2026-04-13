# 98-integrations Cheatsheet

## The Vision: Master Datasets

This folder owns the **canonical data contracts** between HubSpot and every other system. The goal is one authoritative dataset per business domain — not five different copies of "customers" scattered across Google Sheets, ClickUp, Notion, and Shopify.

**One dataset to rule them all. Everything else subscribes from it.**

---

## Master Dataset Architecture

| Dataset | Source of Truth | Consumers | Sync direction |
|---------|----------------|-----------|----------------|
| **Contacts (Customers)** | HubSpot CRM | Google Sheets, ClickUp, Notion | HubSpot → GSheets → others |
| **Deals (Opportunities)** | HubSpot CRM | Google Sheets, ClickUp | HubSpot → GSheets |
| **Orders** | HubSpot CRM (+ Shopify) | Google Sheets, ClickUp | Shopify → HubSpot → GSheets |
| **Products / Catalog** | HubDB (pushed from local JSON) | Customer portal, Google Sheets | Local JSON → HubDB → portal |
| **Tickets (Service)** | HubSpot CRM | ClickUp | HubSpot → GSheets |
| **Knowledge Base** | Local Markdown | Notion, HubSpot KB, Hair Concierge | Local MD → HubSpot KB + Notion |

---

## Folder Layout to Build

```
98-integrations/
  master-datasets/
    contacts-schema.json         ← Canonical field list for the contacts master sheet
    deals-schema.json            ← Canonical field list for the deals master sheet
    orders-schema.json
    products-schema.json
    tickets-schema.json
  google-sheets/
    README.md                    ← Sheet IDs + tab names
    sync_hubspot_to_sheets.py    ← Main sync script
    schemas/
      contacts.json              ← Which HubSpot properties → which columns
      deals.json
      orders.json
  clickup/
    README.md                    ← Space/list IDs
    sync_specs.md                ← What syncs to ClickUp + from where
  notion/
    README.md                    ← Database IDs
    sync_specs.md
  shopify/
    README.md
    sync_specs.md
    webhooks.md                  ← Webhook endpoints + event types
```

---

## Google Sheets — The Hub

Google Sheets is the **relay layer**. HubSpot data lands here first, then ClickUp and Notion read from it. This is simpler than building direct connectors to every system.

### Sheet structure

One Google Sheet per master dataset. Each sheet has:
- A `raw` tab (direct HubSpot export, no transforms)
- A `formatted` tab (human-readable, formulas applied)
- A `metadata` tab (last_synced, record_count, sync_status)

### Contact master sheet — columns to include

```json
{
  "sheet_name": "Contacts Master",
  "hubspot_properties": [
    "hs_object_id", "email", "firstname", "lastname", "phone",
    "hsc_customer_class", "hsc_experience_level", "hsc_relationship_state",
    "hsc_primary_goal", "hsc_base_preference", "hsc_density_preference",
    "hsc_last_known_system_family", "hsc_specs_locked",
    "hsc_customer_health_score", "hsc_risk_band", "hsc_reengagement_priority",
    "hsc_reorder_window_open", "hsc_subscription_status",
    "hs_recent_closed_order_date", "lifecyclestage", "createdate", "lastmodifieddate"
  ]
}
```

### Sync script pattern

```bash
# Pull fresh contact data from HubSpot → write to Google Sheet
bash ./scripts/op_run.sh python3 98-integrations/google-sheets/sync_hubspot_to_sheets.py --object contacts

# Schedule this daily (e.g., via cron or GitHub Actions)
```

---

## Shopify Integration

### What Shopify owns

Shopify is the **source of truth for orders, products, and payment transactions**. HubSpot mirrors order data but Shopify wins on conflicts.

### Sync contract

| Shopify event | What syncs to HubSpot | How |
|---------------|----------------------|-----|
| `orders/create` | New deal (order) created in HubSpot | Webhook → Cloudflare Worker → HubSpot API |
| `orders/paid` | Deal status updated to `payment_confirmed` | Webhook |
| `orders/fulfilled` | Deal property `hsc_fulfillment_status` updated | Webhook |
| `orders/cancelled` | Deal closed lost | Webhook |
| `products/update` | HubDB `products` table row updated | Manual or scheduled sync |

**Webhook validation:** Always verify `X-Shopify-Hmac-SHA256` header using `SHOPIFY_WEBHOOK_SECRET`.

### Product catalog sync (Shopify → HubDB)

```bash
# Pull products from Shopify, update HubDB products table
bash ./scripts/op_run.sh python3 98-integrations/shopify/sync_products_to_hubdb.py
```

---

## ClickUp Integration

The current sync pattern (from obsidian vault): **HubSpot → CSV → GitHub Actions (every 10 min) → ClickUp**.

### What syncs to ClickUp

| HubSpot object | ClickUp destination | Sync rule |
|----------------|--------------------|-----------| 
| Open tickets | Service tasks list | HubSpot wins |
| Open deals | Sales tasks list | HubSpot wins |
| Contact activity | Not synced | ClickUp is execution-only |

### 12 synced scopes (from vault)

`contacts, deals, orders, companies, hair_systems, purchase_orders, payments, subscriptions, invoices, emails, communications, carts`

**ClickUp wins on:** Execution tasks (assigned to someone, has a due date). **HubSpot wins on:** Identity, commercial data, history.

---

## Notion Integration

Notion is used for **knowledge content** — help articles, care guides, onboarding docs. The customer portal reads Notion via the `NotionClient` in the portal's backend.

### What lives in Notion

| Content type | Notion DB | Who reads it |
|-------------|-----------|-------------|
| Help articles | `NOTION_HELP_DATABASE_ID` | Customer portal + Hair Concierge agent |
| Care guides | Same DB | Customer portal |
| Personal notes | Customer-mapped pages | Customer portal (access-controlled per userId) |

### Sync flow

```
Notion (published articles) → portal backend (NotionClient.syncHelpArticles()) → Prisma DB → Customer portal pages
```

**Note:** Notion sync is live in the customer portal backend. The `NOTION_API_KEY` and `NOTION_HELP_DATABASE_ID` env vars must be set.

---

## Existing Integration Code

Code that already exists (don't rebuild):

| Integration | File | What it does |
|-------------|------|-------------|
| HubDB sync | `99-development/design-manager/customer-portal/scripts/hubspot_sync_hubdb.py` | Pushes JSON seed tables to HubDB |
| Shopify client | `99-development/design-manager/customer-portal/app/lib/shopify.ts` | Order fetch, webhook verify |
| Notion client | `99-development/design-manager/customer-portal/app/lib/notion.ts` | Help article sync, access control |
| HubSpot CRM export | `scripts/hubspot_object_reports.py` | All-object export + snapshot |

**Put the integration contracts here. The code lives in `99-development/` or `scripts/`.**

---

## Environment Variables Required

```bash
# HubSpot
HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN   # main token (all CRM ops)

# Google Sheets (to be configured)
GOOGLE_SHEETS_CREDENTIALS_JSON
GOOGLE_SHEETS_CONTACTS_ID
GOOGLE_SHEETS_DEALS_ID
GOOGLE_SHEETS_ORDERS_ID

# Shopify
SHOPIFY_STORE_DOMAIN
SHOPIFY_ADMIN_API_TOKEN
SHOPIFY_WEBHOOK_SECRET

# Notion
NOTION_API_KEY
NOTION_HELP_DATABASE_ID

# ClickUp (to be configured)
CLICKUP_API_TOKEN
CLICKUP_TEAM_ID
```

---

## Priority Build Order

1. **Google Sheets sync** — contacts + deals master sheets. This is the highest-leverage first build — once you have live HubSpot data in a Sheet, ClickUp and Notion can read from it.
2. **Shopify → HubSpot order webhook** — make sure every Shopify order becomes a HubSpot deal/order record.
3. **HubDB product sync** — keep the customer portal product catalog current.
4. **ClickUp sync spec** — document exactly which ClickUp lists map to which HubSpot objects, then automate.
5. **Notion help article sync** — this already works in the portal, just needs the env vars.

---

## What NOT to Do

- Don't build direct ClickUp ↔ Notion connectors — go through Google Sheets as the relay
- Don't duplicate master data — if contacts are in HubSpot, don't maintain a separate Notion "customer database"
- Don't push data from Google Sheets back to HubSpot — it's one-way (HubSpot wins)
- Don't store Shopify webhook secrets in code — they must come from env vars / 1Password
- Don't sync Notion personal-note pages to all contacts — access control is per-userId mapping
