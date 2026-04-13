# 30-content Cheatsheet

## The Model

| Subfolder | Direction | Strategy |
|-----------|-----------|----------|
| `hubdb/` | **Local → HubSpot** | Define tables + rows as JSON, push via API |
| `files/` | **HubSpot → Local** | Pull index on-demand only (heavy, don't commit files) |
| `pages-blog-email/` | **HubSpot → Local** | Pull metadata/sitemap weekly (don't try to push) |
| `design-manager/` | Separate repo | Already a separate git checkout, nothing to do here |
| `memberships/` | UI only | Scope not in manifest — document structure, use HubSpot UI |

---

## HubDB — Local Source of Truth

HubDB is the **best surface in this folder** for local-first management. It's structured data with a clean API — treat it like a database schema file.

### Folder layout to build

```
30-content/hubdb/
  tables/
    {table-name}.json     ← table schema + rows combined
  scripts/
    hubdb_pull.py         ← pull current state from HubSpot
    hubdb_push.py         ← push local JSON → HubSpot
```

### JSON format per table

```json
{
  "name": "table_name",
  "label": "Human Label",
  "useForPages": false,
  "columns": [
    { "name": "col_name", "label": "Label", "type": "TEXT" }
  ],
  "rows": [
    { "values": { "col_name": "value" } }
  ]
}
```

### Workflow

```bash
# First time: pull current HubDB state into local JSON
bash ./scripts/op_run.sh python3 30-content/hubdb/scripts/hubdb_pull.py

# After editing a table JSON locally:
bash ./scripts/op_run.sh python3 30-content/hubdb/scripts/hubdb_push.py --table table_name

# Commit the JSON after every push (git history = your changelog)
git add 30-content/hubdb/tables/ && git commit -m "hubdb: update table_name"
```

### Key HubDB API calls

```
GET    /cms/v3/hubdb/tables                    → list all tables
POST   /cms/v3/hubdb/tables                    → create table
PATCH  /cms/v3/hubdb/tables/{tableIdOrName}    → update table
GET    /cms/v3/hubdb/tables/{tableIdOrName}/rows
POST   /cms/v3/hubdb/tables/{tableIdOrName}/rows
POST   /cms/v3/hubdb/tables/{tableIdOrName}/rows/batch/upsert
POST   /cms/v3/hubdb/tables/{tableIdOrName}/draft/push-live
```

---

## Files — Pull Index Only

Don't manage file uploads locally — too heavy, stale immediately. Pull the index when you need to audit.

```bash
# On-demand: dump file index as JSON
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.request_json('GET', '/files/v3/files', params={'limit': 100})
print(json.dumps(resp, indent=2))
" > 30-content/files/index-$(date +%F).json
```

Use the index to: find orphaned files, audit CDN URLs in email templates, check storage usage.

---

## Pages/Blog — Pull Metadata as Sitemap

The CMS content API is good for reading metadata, not for pushing content. Pull a sitemap weekly.

```
GET /cms/v3/site-pages     → all landing/site pages
GET /cms/v3/blog/posts     → all blog posts
```

Output: `30-content/pages-blog-email/sitemap-{date}.json`
Fields worth pulling: `id`, `slug`, `name`, `state` (PUBLISHED/DRAFT), `publishDate`, `metaDescription`, `updatedAt`

Useful for: checking broken slugs, auditing SEO meta, finding unpublished drafts, agent context on what content exists.

---

## Scopes Available

| Scope | What it unlocks |
|-------|----------------|
| `content` | CMS pages, blog, email-adjacent assets |
| `files` | File manager read/write |
| `files.ui_hidden.read` | System/hidden file access |
| `hubdb` | HubDB tables and rows |
| ❌ `cms.membership.access_groups.*` | **Not in manifest** — memberships UI-only |

---

## What NOT to Do

- Don't try to push blog/page content via API — the CMS API isn't designed for it
- Don't commit actual image/video files here — just the file index JSON
- Don't use `design-manager/` in this repo — it's a separate git checkout
- Don't touch memberships until scope is added to the internal app manifest
