# 99-development Cheatsheet

## Three Active Surfaces

| Surface | Location | Status |
|---------|----------|--------|
| **Customer Portal** (HubSpot CMS theme) | `design-manager/customer-portal/theme/` | 🔄 Built, testing/go-live remaining |
| **Sales Quick Emails Card** (CRM UI extension) | `hubspot-ui-cards/` | ✅ Built |
| **Legacy Next.js app** | `design-manager/customer-portal/app/` | 🗄️ Archived — do not touch |

---

## Customer Portal — The Big Build

A HubSpot CMS membership portal hosted on portal `50966981`. Customers log in and see their orders, invoices, hair profile, customization templates, and product catalog.

### Tech stack

| Layer | Tech |
|-------|------|
| Templates + modules | HubL (HubSpot markup language) |
| Data | GraphQL (membership-scoped, 10 queries) + HubDB (catalog tables) |
| Styles | Tailwind CSS + custom CSS variables |
| Build/deploy | HubSpot CLI (`hs`) + Bash scripts |
| Property sync | Python 3 scripts |
| Secrets | 1Password via `op_env.sh` |

### 9 customer-facing pages

| Template | URL slug | What customer sees |
|----------|----------|-------------------|
| `portal-dashboard.html` | `/portal` | Stats, quick actions, recent orders |
| `portal-orders.html` | `/portal/orders` | Order list with status |
| `portal-order-detail.html` | `/portal/orders/{deal_id}` | Single order detail |
| `portal-billing.html` | `/portal/billing` | Current plan + invoices |
| `portal-profile.html` | `/portal/profile` | Hair profile + customization |
| `portal-customization.html` | `/portal/customization` | Template editor |
| `portal-settings.html` | `/portal/settings` | Account, notifications, security |
| `portal-shop.html` | `/portal/shop` | Product catalog (HubDB) |
| `portal-invoices.html` | `/portal/invoices` | Invoice archive |

### 23 modules (reusable HubL components)

Core: `portal-sidebar`, `portal-header`, `dashboard-stats`, `recent-orders`, `order-list`, `order-detail`, `production-alert`, `billing-current`, `billing-plans`, `invoice-table`, `hair-profile-display`, `hair-profile-form`, `customization-grid`, `settings-profile`, `settings-notifications`, `settings-security`, `product-grid`, `status-badge`, `quick-actions`

### Data model quirks

| What you'd expect | What actually happens | Why |
|-------------------|-----------------------|-----|
| Orders from native orders object | Orders pulled from **Deals** | Membership GraphQL doesn't expose native commerce orders on this account tier |
| Invoices as separate objects | Invoices stored as **JSON in contact property** `portal_invoices_json` | Simplicity |
| Hair profile as custom object | Stored as **JSON in contact property** `portal_hair_profile_json` | Avoids custom object GraphQL complexity |
| Catalog from HubSpot products | Catalog from **HubDB** (`products` table) | HubDB is accessible to CMS templates without membership scope |

---

## Daily Dev Commands

```bash
cd 99-development/design-manager

# Live development — streams changes to HubSpot Design Manager
hs watch customer-portal/theme customer-portal

# Full build → validate → ship cycle
npm run portal:build    # validate structure, JSON, GraphQL syntax
npm run portal:ship     # upload theme to HubSpot Design Manager

# Pull live theme for comparison (don't overwrite local)
npm run portal:fetch

# Sync contact properties to HubSpot (run when schema changes)
npm run portal:hubspot-props

# Sync HubDB tables from local seed JSON
npm run portal:hubdb-sync

# Full automation: build → props → HubDB → ship
bash scripts/portal_automation_full.sh
```

---

## Ship Checklist (Before Every Deploy)

```bash
# 1. Validate the theme
npm run portal:build

# 2. Verify contact properties exist in HubSpot
npm run portal:hubspot-props

# 3. Verify HubDB tables are current
npm run portal:hubdb-sync

# 4. Ship
npm run portal:ship

# 5. Tag the release
bash scripts/portal_release.sh
```

---

## GraphQL Queries (10 total)

All queries are in `customer-portal/theme/data-queries/*.graphql`. They're **contact-scoped** — each query reads data for the currently logged-in contact.

| Query | File | Data returned |
|-------|------|--------------|
| Dashboard | `dashboard.graphql` | Contact profile + recent deals (as orders) |
| Order list | `orders_list.graphql` | All deals for contact |
| Order detail | `order_detail.graphql` | Single deal, full properties |
| Billing | `billing.graphql` | Contact billing props + HubDB plan grid |
| Invoices | `invoices.graphql` | `portal_invoices_json` property |
| Hair profile | `hair_profile.graphql` | `portal_hair_profile_json` property |
| Customization | `customization_templates.graphql` | Saved templates on contact |
| Products | `products.graphql` | HubDB products table |
| Locations | `locations.graphql` | HubDB affiliated_locations table |
| Settings | `settings.graphql` | Account + notification flags |

**Important:** The `graphql` scope (`collector.graphql_query.execute`) must be active for these to work. Check `KNOWN_ISSUES.md` for HubSpot GraphQL quirks.

---

## HubDB Tables (Seeded from Local JSON)

| Table | Seed file | Contents |
|-------|-----------|----------|
| `products` | `data/hubdb/products.json` | 6 catalog items (systems, adhesives, maintenance) |
| `affiliated_locations` | `data/hubdb/affiliated_locations.json` | 3 partner locations |
| `subscription_plans` | `data/hubdb/subscription_plans.json` | 3 plans (Essential $199/mo, Professional $349/mo, Premium $549/mo) |

After editing a seed file:
```bash
npm run portal:hubdb-sync
# Or: bash ./scripts/op_run.sh python3 scripts/hubspot_sync_hubdb.py
```

---

## Contact Properties (Portal-Specific)

These properties are created by `scripts/hubspot_create_portal_contact_properties.py`:

| Property | Type | Purpose |
|----------|------|---------|
| `portal_hair_profile_json` | String (JSON) | Hair measurements + preferences |
| `portal_customization_templates_json` | String (JSON) | Saved design templates |
| `portal_invoices_json` | String (JSON) | Invoice history |
| `portal_billing_*` | Various | Billing/plan flags |

---

## Sales Quick Emails Card (CRM UI Extension)

A React card that lives in the HubSpot CRM contact detail sidebar. Loads email templates with one-click copy (subject + body) for sales use.

```bash
cd 99-development/hubspot-ui-cards

# Install deps
hs project install-deps

# Dev (live reload in HubSpot)
hs project dev

# Deploy
hs project upload
```

**The card reads:** `firstname`, `lastname`, `company`, `email`, `lifecyclestage`, `jobtitle` from the contact.

---

## Key Docs to Read Before Working on the Portal

| Doc | Location | Why |
|-----|----------|-----|
| `AGENT_PROMPT.md` | `customer-portal/docs/` | Full file-level technical spec (154KB — the bible) |
| `SCHEMA_REGISTRY.md` | `customer-portal/data/` | Property mappings, object aliases, HubDB IDs (41KB) |
| `KNOWN_ISSUES.md` | `customer-portal/docs/` | HubSpot CLI/GraphQL/HubDB quirks + fixes (5KB) |
| `IMPLEMENTATION_PLAN_SUBAGENTS.md` | `customer-portal/docs/` | Build waves, agent roles, dependency graph |

---

## CI/CD

GitHub Actions at `.github/workflows/portal-theme-build.yml`:
- Triggers on: pushes/PRs touching `customer-portal/theme/**`
- Runs: `portal_build.sh` (structure + JSON + HubL syntax validation)
- No HubSpot auth needed — validation only, no deploy
- Deploys are manual (`npm run portal:ship`)

---

## What NOT to Do

- Don't edit files in `app/`, `components/`, `lib/`, `prisma/` — that's the archived Next.js app
- Don't run `npm run legacy:*` commands unless you specifically need the old app
- Don't hardcode HubSpot object IDs in templates — read from `SCHEMA_REGISTRY.md` and use env vars
- Don't push the theme without running `portal:build` first — broken HubL syntax breaks the live portal
- Don't modify `portal_invoices_json` directly — it's managed by the backend sync, not manual editing
- Don't add new GraphQL queries without checking `KNOWN_ISSUES.md` first — there are known pagination + scope quirks
