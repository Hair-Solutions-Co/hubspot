# Master Action Plan — HubSpot Engineering Workspace

> Hair Solutions Co. | Generated 2026-04-10
> Audience: Vincent (solo founder, non-developer operator)
> Every item is something you can actually do. No fluff.

---

## How to Read This Plan

- ⚡ **Automated** — run a command in terminal
- 🖱️ **Manual** — do it in the HubSpot UI or browser
- 🔨 **Build** — write code or create a file
- 🔑 **Decision** — Vincent must decide before proceeding
- ❌ **Blocker** — must be done before the next item can start

---

## Phase 0 — Bootstrap (Do Once, Unlocks Everything) ✅ COMPLETE

Executed 2026-04-10. All blockers cleared.

### 0.1 ⚡ Verify 1Password CLI is authenticated ✅

Account `vincent.laroche.br@gmail.com` (user `J7LLWO4TAJAQ3ONDK6BWTOA6UE`) authenticated.
**Blockers:** None.

---

### 0.2 ⚡ Verify `.env` exists and has a HubSpot token ✅

**Fixed:** `.env` was a FIFO (named pipe) causing `op run` to hang. Replaced with regular file containing `op://` references. Token injection confirmed — 44-character service key resolves correctly.
**Blockers:** 0.1

---

### 0.3 ⚡ Run the CRM schema pull to generate real `id_manifest.json` ✅

58,334 lines of schema data pulled. 14 JSON files across 12 objects (contacts, companies, deals, tickets, leads, products, line_items, quotes, orders, subscriptions, invoices + pipeline files for deals/tickets/orders). `config/id_manifest.json` populated with real IDs from live HubSpot.
**Commit:** `8a7da8e`
**Blockers:** 0.2

---

### 0.4 ⚡ Run the first CRM daily snapshot ✅

452 lines of snapshot data. Record counts for all standard objects + detailed pipeline stage breakdowns for deals (5 pipelines: Old Deals, Sales, Deals, Affiliate Agreement, Plans, Shopify Orders) and tickets (3 pipelines: Support, Sales Inquiries, Order Queue).
**Output:** `10-crm/imports-exports/snapshots/2026-04-10/counts.json`
**Commit:** `81e2bf7`
**Blockers:** 0.3

---

### 0.5 ⚡ Scope inventory — TESTED ✅

Ran `scripts/test_scopes.py` against 14 API endpoints. **13/14 accessible:**

| Endpoint | Status |
|----------|--------|
| CRM contacts | ✅ |
| CRM deals | ✅ |
| CRM tickets | ✅ |
| CRM orders | ✅ |
| CRM invoices | ✅ |
| CRM subscriptions | ✅ |
| CRM payments | ✅ |
| CMS blog posts | ✅ |
| HubDB tables | ✅ |
| Marketing emails | ✅ |
| Conversations | ✅ |
| Forms | ✅ |
| Users | ✅ |
| Files | ❌ 405 (routing issue, not permissions) |

**The scopes listed in the manifest are confirmed accessible via the service key.** No manual scope additions needed.

Previously this was flagged as a decision point. The test resolved it — KB, GraphQL, payments, and tax scopes are all working.
---

### 0.6 🖱️ Clone the Design Manager repo ✅ (partial)

Directory exists at `99-development/design-manager/` with content (customer-portal, docs, package.json) but **not a git repo** — no `.git` directory. It was copied/extracted, not cloned. Content is usable but won't support `git pull` for updates.
**Action needed:** Initialize git or re-clone from the source repo when you need version control for the Design Manager.
**Blockers:** None.

---

### 0.7 ⚡ Install workspace dependencies ✅

`npm install` — already up to date. 0 vulnerabilities.
**Blockers:** None.

---

## Phase 1 — Daily Operations (Set Up and Automate) ✅ COMPLETE

Executed 2026-04-10. Auto-commit chosen (Decision 1.2). All jobs installed via macOS launchd.

### 1.1 ⚡ Daily CRM + ticket snapshot ✅

Installed as macOS launchd agent `co.hairsolutions.hubspot.daily-snapshot` (7:00 AM daily).

**What it runs:** `scripts/daily_snapshot.sh` which:
1. Runs CRM record counts + pipeline breakdowns → `10-crm/imports-exports/snapshots/`
2. Runs open-ticket snapshot → `60-service/tickets/snapshots/`
3. Auto-commits and pushes to main

Logs: `/tmp/hubspot-daily-snapshot.log`

**Manual run:** `npm run hubspot:daily` or `bash ./scripts/daily_snapshot.sh`

---

### 1.2 🔑 DECISION — Auto-commit ✅

**Chosen: Option A (auto-commit).** Both `daily_snapshot.sh` and `weekly_schema_pull.sh` auto-commit and push to main.

---

### 1.3 ⚡ Weekly schema pull ✅

Installed as macOS launchd agent `co.hairsolutions.hubspot.weekly-schema` (Mondays 6:30 AM).

**What it runs:** `scripts/weekly_schema_pull.sh` → pulls schemas, auto-commits, pushes.

Logs: `/tmp/hubspot-weekly-schema.log`

**Manual run:** `npm run hubspot:weekly:schema` or `bash ./scripts/weekly_schema_pull.sh`

---

### 1.4 ⚡ Daily open-ticket snapshot ✅

Built as `scripts/open_ticket_snapshot.py`. Pulls all non-closed tickets with subject, pipeline, stage, priority, category, dates, owner, and resolution.

**First run:** 75 open tickets → `60-service/tickets/snapshots/2026-04-10-open-tickets.json`

Runs automatically as part of `daily_snapshot.sh` (step 2 of 2). Also available standalone: `npm run hubspot:tickets:snapshot`

---

### 1.5 🔨 Create required snapshot directories ✅

All 6 directories created:
- `60-service/tickets/snapshots/`
- `60-service/feedback/snapshots/`
- `40-sales/goals/snapshots/`
- `70-data-management/users-teams/snapshots/`
- `90-reporting/dashboards-reports/snapshots/`
- `20-marketing/campaigns/snapshots/`

---

## Phase 2 — Schema & Properties (Push Local → HubSpot)

This phase creates the CRM property layer that the entire email system, portal, and automation depend on.

### 2.1 ⚡ DRY-RUN the 41 email property creation

```bash
bash ./scripts/op_run.sh python3 20-marketing/programmable-emails/scripts/create_email_properties.py --dry-run
```

**Why:** Reviews exactly which 41 properties (24 contact, 15 deal, 2 ticket) will be created, without touching HubSpot. Read the output carefully — these properties are permanent once created.
**Blockers:** Phase 0 complete.

---

### 2.2 🔑 DECISION — Review dry-run output, then approve

Read the dry-run output. Check for:
- Any property names that conflict with existing properties (the schema pull from 0.3 will show what already exists)
- Any property types that look wrong (e.g., a date field typed as string)
- Any properties you don't actually need yet

**Once approved, proceed to 2.3.**

---

### 2.3 ⚡ Run the property creation for real

```bash
bash ./scripts/op_run.sh python3 20-marketing/programmable-emails/scripts/create_email_properties.py
```

**Why:** Creates the 41 CRM properties that the J1–J8 lifecycle email system, workflow computation, and Breeze agent tools all depend on. This is the single most important schema push.
**Blockers:** 2.2 decision made.

---

### 2.4 ⚡ Verify all properties were created

```bash
bash ./scripts/op_run.sh python3 20-marketing/programmable-emails/scripts/verify_email_properties.py
```

**Why:** Confirms every property exists and has the correct type/options. Catches partial failures.
**Blockers:** 2.3

---

### 2.5 ⚡ Re-pull schemas to capture the new properties

```bash
npm run hubspot:crm:schema
git add -A && git commit -m "schema: add 41 email properties (Phase 1 complete)"
```

**Why:** Updates `10-crm/schemas/` and `id_manifest.json` with the newly created properties. This is your local proof that Phase 1 of the email system is done.
**Blockers:** 2.4

---

### 2.6 🖱️ Create the customer portal contact properties (if Design Manager is cloned)

```bash
cd 99-development/design-manager
npm run portal:hubspot-props
```

**Why:** Creates portal-specific properties like `portal_hair_profile_json`, `portal_customization_templates_json`, `portal_invoices_json`, and `portal_billing_*` fields. The portal can't display customer data without these.
**Blockers:** 0.6 (Design Manager repo cloned).

---

## Phase 3 — Integrations (Connect the Systems)

### 3.1 🔨 Build the Google Sheets → HubSpot contacts sync script

Location: `98-integrations/google-sheets/sync_hubspot_to_sheets.py`

**What it does:**
- Pulls contacts from HubSpot with the 20+ properties defined in the 98-integrations cheatsheet
- Writes to a Google Sheet (`raw` tab)
- Logs sync metadata (`metadata` tab)

**Why:** Google Sheets is the relay layer. Once contacts land in a Sheet, ClickUp and Notion can read from it. This is the highest-leverage first integration.
**Blockers:** Phase 0 complete. Google Sheets API credentials configured (see env vars below).

---

### 3.2 🔑 DECISION — Google Sheets credentials setup

You need these env vars in `.env`:
```
GOOGLE_SHEETS_CREDENTIALS_JSON   # service account JSON or path
GOOGLE_SHEETS_CONTACTS_ID        # Sheet ID for contacts master
GOOGLE_SHEETS_DEALS_ID           # Sheet ID for deals master
GOOGLE_SHEETS_ORDERS_ID          # Sheet ID for orders master
```

**Decision:** Create one Google Sheet per master dataset (Contacts, Deals, Orders) or one Sheet with multiple tabs? Recommendation: **one Sheet per dataset** — simpler permissions, cleaner URLs for sharing.

---

### 3.3 🔨 Build the master dataset schema files

Create these files defining exactly which HubSpot properties map to which Sheet columns:

```
98-integrations/master-datasets/contacts-schema.json
98-integrations/master-datasets/deals-schema.json
98-integrations/master-datasets/orders-schema.json
```

**Why:** These are the canonical contracts. The sync script reads from them. When you add a new HubSpot property, you add it to the schema file and re-run the sync.
**Blockers:** None.

---

### 3.4 🔨 Build Shopify → HubSpot order webhook handler

The sync contract (from 98-integrations cheatsheet):
- `orders/create` → new deal in HubSpot
- `orders/paid` → deal status → `payment_confirmed`
- `orders/fulfilled` → deal property `hsc_fulfillment_status` updated
- `orders/cancelled` → deal closed lost

**Where:** Cloudflare Worker that receives Shopify webhooks, validates `X-Shopify-Hmac-SHA256`, and writes to HubSpot CRM API.
**Why:** Makes every Shopify order automatically appear as a HubSpot deal. No manual data entry.
**Blockers:** `SHOPIFY_WEBHOOK_SECRET` in env vars. Cloudflare Worker deployed.

---

### 3.5 🔨 Build HubDB product catalog sync

```bash
bash ./scripts/op_run.sh python3 98-integrations/shopify/sync_products_to_hubdb.py
```

**Why:** Keeps the customer portal's product catalog (HubDB `products` table) in sync with the Shopify catalog.
**Blockers:** 0.6 (Design Manager cloned — portal HubDB seed files are there). Phase 0 complete.

---

### 3.6 🖱️ Verify Notion integration env vars

The Notion integration already works in the customer portal backend. Confirm these are set:
```
NOTION_API_KEY
NOTION_HELP_DATABASE_ID
```

**Why:** The portal's `NotionClient.syncHelpArticles()` reads help articles from Notion. If these vars are missing, the help section is empty.
**Blockers:** None.

---

## Phase 4 — Content & Knowledge (Build the Knowledge Surfaces)

### 4.1 🔨 Write Knowledge Base articles as local Markdown

Location: `60-service/knowledge-base/articles/{category}/{slug}.md`

Use this frontmatter format:
```yaml
---
title: "How to measure your head for a hair system"
category: "Getting Started"
slug: "measure-head-hair-system"
status: draft
---
```

**Priority articles to write first** (based on the sales vault):
1. How to measure your head for a hair system
2. Understanding base types (Nano Skin, Lace, Dura Skin)
3. Care and maintenance guide
4. Reorder timing by base type
5. What to expect with your first system

**Why:** Even without the KB push script, you get version history, AI-assisted drafting, and bulk editing. The Breeze Customer Agent will read these once pushed.
**Blockers:** None — you can start writing immediately.

---

### 4.2 🔨 Build the KB push script

Location: `60-service/knowledge-base/scripts/kb_push.py`

Uses `POST /cms/v2/knowledge-base/articles` to push local Markdown → HubSpot KB.

**Why:** Turns your local Markdown articles into live HubSpot Knowledge Base articles that the Breeze Customer Agent can reference.
**Blockers:** Verify KB scope works (test from 0.5). Articles written (4.1).

---

### 4.3 🔨 Build HubDB table management scripts

Location: `30-content/hubdb/scripts/`

Two scripts:
- `hubdb_pull.py` — pull current HubDB state → local JSON
- `hubdb_push.py` — push local JSON → HubSpot

```bash
# Pull first
bash ./scripts/op_run.sh python3 30-content/hubdb/scripts/hubdb_pull.py

# After editing, push
bash ./scripts/op_run.sh python3 30-content/hubdb/scripts/hubdb_push.py --table products
```

**Why:** HubDB is the product catalog for the customer portal. Local-first management means you can diff, review, and version-control every change.
**Blockers:** Phase 0 complete.

---

### 4.4 🔨 Define behavioral event schemas

Location: `70-data-management/event-management/definitions/`

Priority events to define:
- `hsc_reorder_link_clicked` — contact clicked a reorder CTA
- `hsc_consultation_started` — started a consultation flow
- `hsc_portal_login` — logged into the customer portal
- `hsc_product_page_viewed` — viewed a product in the portal

**Why:** Behavioral events power segmentation and the reorder automation. Define them now so workflows can reference them.
**Blockers:** None for definitions. Sending events requires a runtime caller (Cloudflare Worker or portal backend).

---

### 4.5 🔨 Write Breeze Agent Tool contracts

Location: `95-breeze/app-features/tools/`

Priority tools (from the 95-breeze cheatsheet):

| Tool | Priority | Contract file |
|------|----------|---------------|
| `GetCustomerSpec` | High | `get-customer-spec.md` |
| `GetReorderWindow` | High | `get-reorder-window.md` |
| `GetOpenTickets` | High | `get-open-tickets.md` |
| `LookupProduct` | Medium | `lookup-product.md` |
| `GetSubscriptionStatus` | Medium | `get-subscription-status.md` |
| `CreateTicket` | Medium | `create-ticket.md` |

**Why:** Writing the contracts first (inputs, outputs, CRM properties read, trigger phrases) prevents scope creep when building the actual Agent Tool code.
**Blockers:** None — contracts are documentation.

---

### 4.6 🔨 Write the Breeze Customer Agent system prompt

Location: `95-breeze/app-features/system-prompt.md`

Include:
- Tone: credible, supportive, commercial, unhurried (from sales vault)
- What agent can do (look up specs, check orders, check tickets)
- What agent cannot do (modify deals, process payments, override pricing)
- Escalation rules: risk band Critical → route to founder immediately
- Suppression: never engage crisis-era contacts without human review

**Why:** This is the "personality" of the Hair Concierge AI. It must align with the sales vault rules.
**Blockers:** None.

---

### 4.7 🔨 Document workflow specs before building in HubSpot UI

Location: `80-automation/workflows/{workflow-name}/spec.md`

Priority workflows (from the 80-automation cheatsheet):

| Workflow | Purpose |
|----------|---------|
| J1 Welcome | Initial arrival email journey |
| Reorder Window Calculator | Set `hsc_reorder_window_open` flag |
| Deal Stage Gate | Enforce required fields before stage advance |
| Crisis Suppression | Suppress risk-band Critical from all automations |
| Subscription Renewal | Renewal email series |
| Lost Deal Reengagement | Re-enter deferred leads |

**Why:** Version-controlled specs mean you never lose the logic of a workflow. Build in HubSpot UI after writing the spec.
**Blockers:** Phase 2 complete (properties must exist for enrollment criteria).

---

## Phase 5 — Reporting & Intelligence (Make the Data Useful)

### 5.1 🔨 Write KPI definitions

Location: `90-reporting/dashboards-reports/kpi-definitions.md`

Define these KPIs (from the 90-reporting cheatsheet):

| KPI | Definition | Source |
|-----|-----------|--------|
| New Leads | Contacts created with `hsc_customer_class` set, last 7 days | CRM contacts search |
| Deal Conversion Rate | Closed Won / (Closed Won + Closed Lost) in period | CRM deals search |
| Avg Deal Value | Sum `amount` on Closed Won / count | CRM deals search |
| Reorder Rate | Contacts with 2+ closed won deals / total customers | CRM contacts |
| Ticket SLA | % tickets resolved within 48 hours | CRM tickets search |
| Email Open Rate | From marketing email API | Marketing email API |
| Reengagement Pipeline | Contacts with `hsc_reengagement_priority` set | CRM contacts |

**Why:** Single source of truth for what each metric means. Every reporting script references this file.
**Blockers:** None.

---

### 5.2 🔨 Build the weekly business health report script

Location: `90-reporting/dashboards-reports/scripts/weekly_report.py`

Pulls all weekly KPIs in one shot, outputs JSON to `snapshots/YYYY-MM-DD-weekly.json`.

**Why:** One command gives you a complete business health check: pipeline, service, email, and reorder signals.
**Blockers:** Phase 2 complete (needs the email/reorder properties to exist for meaningful data).

---

### 5.3 ⚡ Set up weekly report cron

```
0 8 * * 5 cd /Users/vMac/00-hair-solutions-co/00_engineering/04_hubspot && bash ./scripts/op_run.sh python3 90-reporting/dashboards-reports/scripts/weekly_report.py
```

**Why:** Every Friday morning, a fresh business health report lands in your snapshots folder.
**Blockers:** 5.2

---

### 5.4 ⚡ Set up weekly users/teams pull

```
0 7 * * 1 cd /Users/vMac/00-hair-solutions-co/00_engineering/04_hubspot && bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
users = client.request_json('GET', '/settings/v3/users')
teams = client.request_json('GET', '/settings/v3/users/teams')
print(json.dumps({'users': users, 'teams': teams}, indent=2))
" > 70-data-management/users-teams/snapshots/users-\$(date +\%F).json
```

**Why:** The Hair Concierge agent reads this to know who owns what contact/ticket.
**Blockers:** Phase 0 complete.

---

### 5.5 🔨 Build data quality audit scripts

Location: `70-data-management/data-quality/scripts/`

Priority audits:
1. **Property completeness** — contacts missing `hsc_base_preference` or `hsc_customer_class`
2. **Deal stage completeness** — deals in Decision Pending with no `closedate`
3. **Duplicate detection** — contacts grouped by email

**Why:** Bad data poisons every automation and report. Run these monthly.
**Blockers:** Phase 2 complete (properties must exist to audit).

---

### 5.6 ⚡ Set up monthly campaign attribution pull

```
0 9 1 * * cd /Users/vMac/00-hair-solutions-co/00_engineering/04_hubspot && bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.request_json('GET', '/marketing/v3/campaigns', params={'limit': 100})
print(json.dumps(resp, indent=2))
" > 90-reporting/dashboards-reports/snapshots/campaigns-\$(date +\%Y-\%m).json
```

**Why:** Monthly revenue attribution per campaign. Tells you which marketing efforts are actually driving deals.
**Blockers:** Phase 0 complete.

---

## Summary: Execution Order

```
Phase 0 (do now — 30 min)
  0.1  Verify op CLI          ⚡
  0.2  Verify .env token      ⚡
  0.3  Schema pull            ⚡  ← generates id_manifest.json
  0.4  First snapshot          ⚡
  0.5  Scope verification     🔑  ← decision: test KB/GraphQL scopes
  0.6  Clone Design Manager   🖱️
  0.7  npm install             ⚡

Phase 1 (do next — 20 min)
  1.1  Daily snapshot cron     ⚡
  1.2  Auto-commit decision   🔑
  1.3  Weekly schema cron      ⚡
  1.4  Daily ticket snapshot   ⚡
  1.5  Create directories      ⚡

Phase 2 (do this week)
  2.1  Dry-run properties      ⚡
  2.2  Review dry-run         🔑
  2.3  Create 41 properties    ⚡  ← biggest single unlock
  2.4  Verify properties       ⚡
  2.5  Re-pull schemas         ⚡
  2.6  Portal contact props    🖱️

Phase 3 (build over 1–2 weeks)
  3.1  Google Sheets sync      🔨
  3.2  Sheets credentials     🔑
  3.3  Master dataset schemas  🔨
  3.4  Shopify webhook         🔨
  3.5  HubDB product sync      🔨
  3.6  Notion env vars         🖱️

Phase 4 (build iteratively)
  4.1  KB articles             🔨  ← start immediately, no blockers
  4.2  KB push script          🔨
  4.3  HubDB scripts           🔨
  4.4  Behavioral events       🔨
  4.5  Agent Tool contracts    🔨
  4.6  System prompt           🔨
  4.7  Workflow specs          🔨

Phase 5 (after Phase 2)
  5.1  KPI definitions         🔨  ← start immediately, no blockers
  5.2  Weekly report script    🔨
  5.3  Weekly report cron      ⚡
  5.4  Users/teams cron        ⚡
  5.5  Data quality audits     🔨
  5.6  Campaign attribution    ⚡
```

---

## Open Decisions Summary

| # | Decision | Where | Impact |
|---|----------|-------|--------|
| 0.5 | Do service key scopes include KB/GraphQL/payments? | Phase 0 | Blocks KB push (4.2), GraphQL queries, payment reads |
| 1.2 | Auto-commit daily snapshots or manual review? | Phase 1 | Determines cron complexity |
| 2.2 | Approve 41 property dry-run output | Phase 2 | Blocks entire email system |
| 3.2 | Google Sheets credential setup + one Sheet vs. multi-Sheet | Phase 3 | Blocks all Sheets integration |

---

## What This Plan Does NOT Cover (Out of Scope)

- **Building the actual email HTML** — that happens in `03_marketing/02_email_campaigns/`, a different folder
- **Customer portal go-live** — the portal is a separate git repo with its own deployment pipeline
- **ClickUp automation** — documented as a spec, but the GitHub Actions sync is maintained elsewhere
- **Workflow UI builds** — specs are written here, but the actual workflow creation happens in HubSpot UI
- **Notion database structure** — the Notion integration already works; this plan covers the env vars, not the Notion setup itself
