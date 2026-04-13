# 80-automation Cheatsheet

## Reality Check First

HubSpot's workflow API is **mostly read-only for complex workflows**. You can read workflow metadata, but you cannot create or edit the full workflow graph via API. The real value of this folder is:

1. **Custom workflow actions** — these ARE deployable via HubSpot CLI (code in `99-development/`)
2. **Workflow logic documentation** — version-controlled specs for every workflow, even if you build them in the UI
3. **Trigger contracts** — defining exactly what data must be present to trigger a workflow, so your CRM properties and enrollment logic are consistent

---

## The Model

| What | Where | How |
|------|-------|-----|
| Complex workflow definitions | HubSpot UI | Build in UI, document here |
| Custom workflow action code | `99-development/hubspot-ui-cards/` | Deploy via `hs project upload` |
| Workflow trigger contracts | `80-automation/workflows/{name}/spec.md` | Local source of truth |
| Enrollment via API | Scripts | `POST /automation/v4/sequences/enrollments` |

---

## Folder Layout to Build

```
80-automation/workflows/
  {workflow-name}/
    spec.md         ← trigger, enrollment criteria, actions, exit conditions
    triggers.json   ← machine-readable trigger definition
```

---

## Workflow Spec Format (for every workflow you build in UI)

Document this before building in HubSpot. Agents read these to understand what's live.

```markdown
## Workflow: J1 — Initial Arrival Welcome

**Status:** draft | active | paused
**Object:** Contact
**Type:** Contact-based, event-triggered

### Enrollment trigger
- Contact created AND
- `hsc_customer_class` is known AND
- `hs_email_optout` = false

### Re-enrollment: No

### Actions (in order)
1. Wait 1 hour
2. Send email: J1-E1 (Welcome — What to Expect)
3. If `hsc_primary_goal` is known → branch
   - Yes: Send J1-E2 (Goal-Based Recommendation)
   - No: Wait 2 days, send J1-E2-generic
4. Wait 3 days
5. Send J1-E3 (Base Type Introduction)

### Exit conditions
- Deal created (contact becoming active buyer)
- Contact unsubscribes

### Required CRM properties (must exist before enrollment)
- `hsc_primary_goal` (for branch — fallback if empty)
- `hsc_base_preference` (for J1-E3 module)

### Dependencies
- Requires `create_email_properties.py` to have been run (Phase 1)
- Requires J1 email templates deployed to HubSpot
```

---

## What You CAN Do via API

### Enroll a contact in a sequence

```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.request_json('POST', '/automation/v4/sequences/enrollments', body={
    'sequenceId': 'YOUR_SEQUENCE_ID',
    'contactId': 'CONTACT_ID',
    'startingStepIndex': 0
})
print(json.dumps(resp, indent=2))
"
```

### List all sequences (read their IDs)

```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
resp = client.request_json('GET', '/automation/v4/sequences')
print(json.dumps(resp, indent=2))
" > 80-automation/workflows/sequences-list.json
```

### Trigger a workflow enrollment via CRM property update

Indirectly trigger workflows by updating a CRM property that the workflow watches:
```
PATCH /crm/v3/objects/contacts/{id}
Body: { "properties": { "hsc_reorder_window_open": "true" } }
```
If a workflow enrolls on `hsc_reorder_window_open = true`, this fires it. **This is the main automation lever.**

---

## Custom Workflow Actions

Custom workflow actions (coded blocks that run inside HubSpot workflows) live in `99-development/`. The `80-automation/` folder documents their contracts — what they receive, what they output.

### Action contract format

```markdown
## Custom Action: Reorder Window Calculator

**Input properties from workflow:**
- `hsc_last_known_system_family` (string)
- `hsc_base_preference` (enumeration)
- `hs_recent_closed_order_date` (date)

**Output:** Sets `hsc_reorder_window_open = true/false`

**Logic:** Based on base type → reorder window → compare to today's date

**Deployed at:** `99-development/hubspot-ui-cards/reorder-calculator/`
```

---

## Scopes Available

| Scope | What it unlocks |
|-------|----------------|
| `automation` | Read workflow metadata, trigger workflow-facing operations |
| `automation.sequences.read` | List sequences, read sequence steps |
| `automation.sequences.enrollments.write` | Enroll contacts in sequences |

**Cannot do via API:** Create workflows, edit workflow action graph, delete workflows.

---

## Priority Workflows to Document (from the sales vault)

These workflows are referenced across the obsidian vault knowledge system. Document specs here before or after building in HubSpot UI:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| J1 Welcome | Contact created + opted in | Initial arrival email journey |
| Reorder Window | Date-based + base type | Set `hsc_reorder_window_open` flag |
| Deal Stage Gate | Deal stage change | Enforce required fields before stage advance |
| Crisis Suppression | Risk band = Critical | Suppress from all automations |
| Subscription Renewal | `hsc_subscription_renewal_date` approaching | Renewal email series |
| Lost Deal Reengagement | `reengagement_eligible_on` reached | Re-enter deferred leads |

---

## What NOT to Do

- Don't try to create workflows via API — it won't work (no write scope for workflow graph)
- Don't skip writing the spec before building in HubSpot UI — you'll lose the logic history
- Don't enroll contacts in sequences without checking suppression rules first (Risk band High/Critical = suppress)
- Don't use `automation` scope to read workflow IDs for hardcoding — pull them via the sequences list and store in `id_manifest.json`
