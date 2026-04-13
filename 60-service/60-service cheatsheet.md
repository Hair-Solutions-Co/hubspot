# 60-service Cheatsheet

## The Model

| Subfolder | Direction | Strategy |
|-----------|-----------|----------|
| `tickets/` | **HubSpot → Local** | Daily pull of open tickets by status |
| `conversations/` | Runtime only | Read/write in real-time via agent, never batch sync |
| `knowledge-base/` | **Local → HubSpot** (pending scope) | Write as Markdown locally now; push via API once scope added |
| `feedback/` | **HubSpot → Local** | Weekly pull of submission counts |
| `visitor-identification/` | Runtime only | Generate tokens on-demand for chat widget |

---

## Tickets — Daily Pull (Operationally Critical)

Tickets are your most important service surface. The Hair Concierge agent needs fresh ticket context to answer "what's open", "what's urgent", "what needs my attention".

### What to pull daily

```bash
# Open tickets by status — append to daily snapshot
bash ./scripts/op_run.sh python3 -c "
import json, sys, datetime
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.search_records(
    'tickets',
    properties=['subject', 'hs_pipeline', 'hs_pipeline_stage', 'hs_ticket_priority', 'createdate', 'hs_lastmodifieddate'],
    filter_groups=[{'filters': [{'propertyName': 'hs_pipeline_stage', 'operator': 'NEQ', 'value': 'closed'}]}],
    limit=100,
)
print(json.dumps(resp, indent=2))
" > 60-service/tickets/snapshots/$(date +%F)-open-tickets.json
```

### What to look for in the snapshot

- Tickets open > 48 hours without a note (stale)
- High-priority tickets with no recent activity
- Tickets missing `hsc_consultation_completed_at` or `hsc_consultation_variant` (incomplete service records)

---

## Conversations — Runtime Only

**Never batch-sync conversations.** Too high volume, changes constantly, no value in a local snapshot.

Use the conversations API only in real-time agent flows:
```
GET  /conversations/v3/conversations                → list threads
GET  /conversations/v3/conversations/{id}/messages  → thread messages
POST /conversations/v3/conversations/{id}/messages  → send a message
```

Pair with tickets: every support conversation should have an associated ticket.

---

## Knowledge Base — Write Locally, Push Later

The `cms.knowledge_base.*` scope is **not in the internal app manifest** yet.

**What to do now:**
- Write all KB articles as Markdown in `60-service/knowledge-base/articles/`
- Use this naming: `{category}/{article-slug}.md`
- Each file = one KB article with frontmatter:

```markdown
---
title: "How to measure your head for a hair system"
category: "Getting Started"
slug: "measure-head-hair-system"
status: draft  # or: published
---

Article body here...
```

**When the scope is added:**
- Build a `kb_push.py` script using `POST /cms/v2/knowledge-base/articles`
- Push all local Markdown files → HubSpot KB
- Local files remain the source of truth

**Why do this now even without the scope:** You get version history, diffs, AI-assisted drafting, and bulk editing. Much easier than the HubSpot KB UI for multiple articles.

---

## Visitor Identification — Runtime Only

Used to identify logged-in portal users in the chat widget. Generate tokens server-side, never store them locally.

```
POST /visitor-identification/v3/tokens/create
Body: { "email": "contact@example.com", "firstName": "...", "lastName": "..." }
```

This is called by your Cloudflare Worker when a logged-in customer opens the chat. Token is JWT, short-lived.

---

## Feedback — Weekly Pull

Pull feedback submission counts weekly for business review:

```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
count = client.count_records('feedback_submissions')
print(json.dumps({'count': count, 'date': '$(date +%F)'}, indent=2))
" >> 60-service/feedback/snapshots/weekly-counts.json
```

---

## Scopes Available

| Scope | What it unlocks |
|-------|----------------|
| `tickets` | Full CRUD on ticket records |
| `conversations.read` | Read conversation threads + messages |
| `conversations.write` | Send messages into conversations |
| `conversations.visitor_identification.tokens.create` | Generate visitor ID tokens |
| `crm.objects.feedback_submissions.read` | Read feedback submissions |
| ❌ `cms.knowledge_base.*` | **Not in manifest** — KB API blocked |

---

## Ticket Custom Properties (from sales vault)

Two custom ticket properties to be aware of:
- `hsc_consultation_completed_at` — datetime when consultation was completed
- `hsc_consultation_variant` — which consultation flow was used

These are created by `20-marketing/programmable-emails/scripts/create_email_properties.py` (Phase 1 — not yet run).

---

## What NOT to Do

- Don't batch-sync conversations locally — use real-time API only
- Don't write KB articles in HubSpot UI — write them locally as Markdown first
- Don't add the KB scope to the manifest without also building the push script
- Don't let tickets go more than 48 hours without a logged note (violates communication-logging-rules from the sales vault)
