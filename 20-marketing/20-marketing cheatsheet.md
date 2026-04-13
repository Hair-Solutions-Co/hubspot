# 20-marketing Cheatsheet

## Two-Folder System

Marketing spans two locations. Each has a distinct job:

| Location | Job | Who writes here |
|----------|-----|----------------|
| `03_marketing/02_email_campaigns/` | Content brain — YAML specs, HTML builds, copy, strategy docs | You + AI writing emails |
| `04_hubspot/20-marketing/` | HubSpot API surface — modules, properties, forms, campaigns, analytics | You + scripts deploying to HubSpot |

**Content is authored in `03_marketing`. HubSpot-native infrastructure lives here.**

---

## Programmable Emails — Build Phases

The J1–J8 lifecycle email system is built in phases. Track where you are:

| Phase | What | Status |
|-------|------|--------|
| 0 — Foundation Audit | Confirm property state, existing emails | ✅ Done (`audit-report.md`) |
| 1 — Property Layer | Create 41 CRM properties (24 contact, 15 deal, 2 ticket) | ⏳ **Not yet run** |
| 2 — Workflow Computation | Precompute reorder timing, subscription eligibility, milestones | ⏳ Blocked on Phase 1 |
| 3 — Template System | Base layout + 4 modules + all email templates | 🔄 Modules built, templates in progress |
| 4 — Journey Rollout | Deploy J1–J8 + dunning in 6 waves | 📋 Planned |
| 5 — Consultation Library | Migrate Track B sales templates | 📋 Planned |

**Start here first:** Run Phase 1.

```bash
# Run Phase 1 — create the 41 CRM properties
bash ./scripts/op_run.sh python3 20-marketing/programmable-emails/scripts/create_email_properties.py --dry-run

# Review the dry-run output, then run for real:
bash ./scripts/op_run.sh python3 20-marketing/programmable-emails/scripts/create_email_properties.py

# Verify all properties were created:
bash ./scripts/op_run.sh python3 20-marketing/programmable-emails/scripts/verify_email_properties.py
```

---

## The 4 Programmable Modules

These are HubL modules built in `programmable-emails/modules/`. Each module renders conditional content based on a CRM property.

| Module | File | CRM property it reads | Used in |
|--------|------|-----------------------|---------|
| `hsc_goal_based_recommendation_block` | `module.html` | `hsc_primary_goal` | J1-E3 |
| `hsc_base_type_guidance_block` | `module.html` | `hsc_base_preference` | J3-E2, J3-E7, J4-E2, J5-E2, J7-E2 |
| `hsc_lifespan_next_step_block` | `module.html` | `hsc_last_known_system_family`, `hsc_reorder_readiness` | J3-E8, J4-E2 |
| `hsc_customer_snapshot_block` | `module.html` | 12 precomputed properties | J5-E1, J8-E1 — **BLOCKED until Phase 2** |

**Deploy modules via HubSpot CLI:**
```bash
cd 20-marketing/programmable-emails
hs project upload
```

---

## Email Classification (39 emails total)

| Type | Count | How they're built |
|------|-------|------------------|
| **S** Standard | 16 | HTML from `03_marketing` pipeline → push to HubSpot |
| **W** Workflow-triggered | 13 | HTML from `03_marketing` pipeline → push to HubSpot |
| **P** Programmable | 7 | HubL templates using the 4 modules above |
| **R** Redesign-blocked | 3 | Blocked until Phase 2 precomputed properties exist |

---

## `03_marketing` → HubSpot Push Flow

The content pipeline in `03_marketing/02_email_campaigns/` builds HTML from YAML specs and pushes to HubSpot:

```bash
# 1. Write/edit YAML spec in 03_marketing/02_email_campaigns/pipeline/email-specs/
# 2. Build HTML
python3 scripts/build_all_emails.py

# 3. Push to HubSpot (uses HUBSPOT_ACCESS_TOKEN, not op_run.sh)
python3 scripts/push_all_series_to_hubspot.py
```

HTML output lands in `pipeline/build/`. Series organized in `pipeline/series/{series-name}/`.

---

## Forms — Local JSON Definitions

Define form schemas locally, push via API. Don't use HubSpot UI for net-new forms.

```
20-marketing/forms/
  definitions/
    {form-name}.json    ← form schema (fields, groups, options)
  scripts/
    forms_push.py       ← to be built
```

**Key API calls:**
```
GET    /marketing/v3/forms              → list forms
POST   /marketing/v3/forms              → create form
PATCH  /marketing/v3/forms/{formId}     → update form
POST   /submissions/v3/integration/submit/{portalId}/{formGuid}  → external submit
```

---

## Campaigns — Pull Analytics

Campaigns are managed in HubSpot UI. Pull attribution data weekly for reporting.

```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.request_json('GET', '/marketing/v3/campaigns', params={'limit': 50})
print(json.dumps(resp, indent=2))
" > 20-marketing/campaigns/snapshots/campaigns-$(date +%F).json
```

---

## Subscription Preferences — Handle With Care

You have full read/write access to contact subscription preferences. **This is a high-risk surface** — unsubscribing contacts incorrectly destroys your email list.

```
GET  /communication-preferences/v3/status/email/{emailAddress}    → read one contact
POST /communication-preferences/v3/statuses/batch/read            → batch read
POST /communication-preferences/v3/statuses/batch/write           → batch update (⚠️ careful)
```

**Rules:**
- Never batch-write subscription preferences from a script without a dry-run step
- Only write if contact explicitly re-opted-in
- Pull only — for analytics and compliance audit

---

## Scopes Available

| Scope | What it unlocks |
|-------|----------------|
| `marketing-email` | Trigger + manage marketing emails |
| `transactional-email` | Single-send transactional emails |
| `marketing.campaigns.read/write` | Campaign CRUD + revenue attribution |
| `forms` + `forms-uploaded-files` | Form management + file uploads |
| `external_integrations.forms.access` | External form submissions |
| `social` | Social media integrations |
| `communication_preferences.*` | Subscription read/write |
| `automation` + `automation.sequences.*` | Workflow operations, sequence enrollment |
| `content` | CMS content access |

---

## What NOT to Do

- Don't run `create_email_properties.py` without a `--dry-run` first
- Don't deploy `hsc_customer_snapshot_block` until Phase 2 computation workflows are live
- Don't create email forms in HubSpot UI — define them as JSON locally first
- Don't try to use `active_lifestyle` as a `hsc_primary_goal` value — it doesn't exist in CRM
- Don't batch-write subscription preferences without explicit re-opt-in evidence
- Don't push S/W email HTML via HubSpot CLI — that's for programmable modules only; S/W emails go through `03_marketing` push scripts
