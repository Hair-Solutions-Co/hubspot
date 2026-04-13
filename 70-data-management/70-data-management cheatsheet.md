# 70-data-management Cheatsheet

## The Model

| Subfolder | Direction | Strategy |
|-----------|-----------|----------|
| `data-model/` | Pointer only | Covered by `crm_schema_pull.py` in `10-crm/schemas/` — don't duplicate |
| `event-management/` | **Local → HubSpot** | Define behavioral event schemas locally, push via API |
| `data-quality/` | Scripts + docs | Audit scripts that validate property completeness |
| `data-integration/` | Specs + coordination | Import/export job specs; scripts already in `scripts/` |
| `data-enrichment/` | Workflow specs | Define enrichment rules; execution is remote |
| `users-teams/` | **HubSpot → Local** | Weekly pull of user + team list for agent context |
| `data-studio/` | On-demand | Ad-hoc analysis notebooks + extract specs |
| `data-agent/` | Prompt templates | AI agent prompts for data operations |
| `graphql/` | Blocked | Scope not in manifest — document queries, can't run yet |

---

## data-model — Don't Duplicate

This surface (CRM schemas, custom objects, properties) is already handled by `crm_schema_pull.py`.

```
10-crm/schemas/     ← the actual schema files live here
config/id_manifest.json ← the ID map
```

Use `data-model/` only to document **decisions** about the data model — why a property was designed a certain way, what was rejected and why. Not for the actual schema files.

---

## event-management — Local Source of Truth

Behavioral events are how you track custom actions (e.g., "viewed product page", "started consultation", "clicked reorder link"). Define them locally, push to HubSpot.

### Folder layout

```
70-data-management/event-management/
  definitions/
    {event-name}.json     ← one file per event definition
  scripts/
    push_event_definitions.py
```

### Event definition JSON format

```json
{
  "name": "hsc_reorder_link_clicked",
  "label": "Reorder Link Clicked",
  "description": "Contact clicked a reorder CTA link in an email or portal",
  "properties": [
    { "name": "source", "label": "Source", "type": "enumeration",
      "options": [{ "label": "Email", "value": "email" }, { "label": "Portal", "value": "portal" }] },
    { "name": "product_family", "label": "Product Family", "type": "string" }
  ]
}
```

### Push command

```
POST /events/v3/event-definitions
```

### Sending an event (at runtime, from Cloudflare Worker or backend)

```
POST /events/v3/send
Body: {
  "eventName": "hsc_reorder_link_clicked",
  "email": "contact@example.com",
  "properties": { "source": "email", "product_family": "nano_skin" }
}
```

---

## data-quality — Audit Scripts

These scripts run on-demand to find data problems. Store output in `data-quality/reports/`.

### Most useful audits to build

**1. Property completeness audit** — which contacts are missing key fields
```bash
# Finds contacts where hsc_base_preference is empty
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.search_records(
    'contacts',
    properties=['email', 'hsc_base_preference', 'hsc_customer_class'],
    filter_groups=[{'filters': [{'propertyName': 'hsc_base_preference', 'operator': 'NOT_HAS_PROPERTY'}]}],
    limit=100,
)
print(json.dumps({'missing_base_preference': resp.get('total', 0)}, indent=2))
"
```

**2. Deal stage completeness** — deals missing required fields for their stage
```
Search deals in Decision Pending with no closedate → data quality gap
Search deals in Payment Pending with no hsc_quote_base_price → missing quote data
```

**3. Duplicate contact detection**
```
Search contacts grouped by email → flag duplicates for manual merge
```

---

## data-integration — Import/Export Coordination

The import/export scripts already exist at `scripts/hubspot_object_reports.py`. This folder is for **job specs** — documents that describe what import goes where, column mappings, and deduplication rules.

### When to use an import

- Migrating legacy records (OneHead Hair Solutions crisis-era contacts)
- Bulk updating a property across many records
- Loading product catalog from Shopify export

### Import spec format (document here before running)

```markdown
## Import: Legacy Contact Migration 2026-04

Source: ohhs-contacts-2026-04.csv
Target object: contacts
Dedup field: email
Column mappings:
  "Email" → email
  "First Name" → firstname
  "Last Name" → lastname
  "Customer Class" → hsc_customer_class
Skip if exists: yes
```

---

## users-teams — Weekly Pull

Pull user and team assignments weekly. The Hair Concierge agent uses this to know who owns what.

```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
users = client.request_json('GET', '/settings/v3/users')
teams = client.request_json('GET', '/settings/v3/users/teams')
print(json.dumps({'users': users, 'teams': teams}, indent=2))
" > 70-data-management/users-teams/snapshots/users-$(date +%F).json
```

---

## graphql — Blocked (Scope Not in Manifest)

Required scopes not in manifest:
- `collector.graphql_query.execute`
- `collector.graphql_schema.read`
- `behavioral_events.event_definitions.read_write`

**What to do now:** Write your intended GraphQL queries in `graphql/queries/` as `.graphql` files. When scopes are added, you'll have the queries ready.

```
POST /collector/graphql
Body: { "query": "{ contacts { items { id email } } }" }
```

---

## Scopes Available

| Scope | What it unlocks |
|-------|----------------|
| `analytics.behavioral_events.send` | Send behavioral events |
| `crm.schemas.read` / `crm.schemas.write` | Custom object schema management |
| User/team read/write | Settings → Users + Teams |
| ❌ GraphQL scopes | **Not in manifest** |

---

## What NOT to Do

- Don't duplicate schema files here — `10-crm/schemas/` is the single source of truth for property definitions
- Don't run data quality audits on production contacts without a dry-run first
- Don't use GraphQL until scopes are added (will 403)
- Don't import records without writing a spec first — easy to create duplicates
