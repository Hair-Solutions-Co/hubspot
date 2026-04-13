# 40-sales Cheatsheet

## Two Folders, One System

Sales spans two locations. They serve different jobs and should never be confused:

| Location | What it is | Who reads it |
|----------|------------|--------------|
| `04_hubspot/40-sales/` | HubSpot API control surface — leads, deals, goals, email reads | Scripts, agents pulling live CRM data |
| `06_knowledge/obsidian-vault/30-sales/` | Sales intelligence brain — processes, playbooks, personas, objections | Hair Concierge AI agent, you |

**The vault is the source of truth for how to sell. The HubSpot folder is the source of truth for what's happening in the pipeline.**

---

## HubSpot Folder — What to Pull and When

### Daily (already covered by `crm_daily_snapshot.py`)
- Deal counts by pipeline stage
- Lead counts
- Open ticket counts

### Weekly pull — goals snapshot
```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.request_json('GET', '/crm/v3/objects/goals', params={'limit': 100})
print(json.dumps(resp, indent=2))
" > 40-sales/goals/snapshots/goals-$(date +%F).json
```

### On-demand — sales email log
```
GET /crm/v3/objects/emails    → one-to-one sales emails (read-only)
```
Use this when you need to see what was sent to a specific contact. Don't try to send via API — sales email is read-only scope.

---

## API Scope Reality

| Subfolder | API scope | What you can do |
|-----------|-----------|-----------------|
| `leads-and-deals/` | `crm.objects.deals.*`, `crm.objects.leads.*` | Full CRUD on deals + leads |
| `goals/` | Covered by CRM read scopes | Read only |
| `sales-email/` | `sales-email-read` | **Read only** — no send |
| `sequences/` | `automation.sequences.read`, `automation.sequences.enrollments.write` | Read sequences, enroll contacts |
| `meetings/` | `scheduler.*` | Read meeting links only |

**No sequence creation/editing via API. No meeting link creation via API. These are UI-only in HubSpot.**

---

## Obsidian Vault — The Sales Brain

Location: `/Users/vMac/00-hair-solutions-co/06_knowledge/obsidian-vault/30-sales/`

62 files organized in 6 clusters. **Keep these updated whenever a process changes** — the Hair Concierge AI reads them.

### Cluster Map

| Cluster | Key files to update regularly |
|---------|-------------------------------|
| CRM & Data Governance | `crm-data-dictionary.md`, `field-definitions-and-naming-rules.md` |
| Qualification & Pipeline | `deal-stage-definitions.md`, `lead-qualification-framework.md`, `lost-deal-reasons-guide.md` |
| Risk, Finance & Recovery | `customer-risk-scoring-rules.md`, `reengagement-playbook.md` |
| Sales Communication | `objection-handling-library.md`, `follow-up-message-frameworks.md` |
| Product & Pricing | `recommendation-decision-framework.md`, `pricing-reference-table.md` |
| Implementation & Rollout | `recommended-implementation-sequence.md` |

### Critical Rules to Never Break (from the vault)

- **Meaningful cadence** = minimum 4 touches, 2 channels, 14+ days before Closed Lost
- **Quote validity** = 14 days default, 72 hours for exception pricing
- **Spec change** = mandatory logging every time
- **Risk override** = confirmed chargeback → Critical band immediately
- **No manual installments** — use Shop Pay / PayPal / Alma only
- **Deal creation threshold** = only when payment is negotiated or forecastable (not every inquiry)
- **Fast-lane reorder** = `hsc_specs_locked = true` → skip full qualification

### Discount approval thresholds

| Discount | Who approves |
|----------|-------------|
| 0–5% | Agent |
| 5–10% | Founder |
| > 10% | Founder (rare) |
| > 50% remedy | Founder + learning case |

---

## Spec Lifecycle (from vault — critical for reorder automation)

```
Created → Refined → Locked (hsc_specs_locked = true) → Fast-lane reorder
```

Product reorder windows by base type:
- Nano Skin: 1–2 months
- Lace (Swiss/French): 2–4 months
- Dura Skin: 4–8 months

---

## Sales Flows (8 paths — from vault)

| Flow | Scenario |
|------|----------|
| 1 | First-timer → premade |
| 2 | First-timer → custom |
| 3 | Competitor switcher → premade |
| 4 | Competitor switcher → custom |
| 5 | Returning → premade reorder |
| 6 | Returning → custom reorder |
| 7 | Plan — first |
| 8 | Plan — renewal |

---

## HubSpot → ClickUp Sync (from vault)

GitHub Actions syncs every 10 minutes. 12 scopes:
`contacts, deals, orders, companies, hair_systems, purchase_orders, payments, subscriptions, invoices, emails, communications, carts`

HubSpot wins on: identity, commercial data. ClickUp wins on: execution tasks.

---

## What NOT to Do

- Don't try to create/edit sequences via API (no write scope)
- Don't create meeting links via API (no write scope)
- Don't update the obsidian vault knowledge files from CRM data — it's one-way (vault → agent)
- Don't put sales playbooks in the HubSpot folder — they belong in the obsidian vault
