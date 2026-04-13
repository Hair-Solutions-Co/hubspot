# 90-reporting Cheatsheet

## Reality First

There is **no dedicated "reporting" API scope** in HubSpot. `crm.export` is not in your manifest. Reporting is assembled by composing the APIs you already have:

| Data you want | API to call | Scope needed |
|---------------|-------------|--------------|
| Deal pipeline health | CRM search | `crm.objects.deals.read` ✅ |
| Contact counts by segment | CRM search | `crm.objects.contacts.read` ✅ |
| Ticket resolution stats | CRM search | `tickets` ✅ |
| Email campaign performance | Marketing email API | `marketing-email` ✅ |
| Campaign revenue attribution | Campaigns API | `marketing.campaigns.revenue.read` ✅ |
| Feedback/NPS submissions | Feedback API | `crm.objects.feedback_submissions.read` ✅ |
| Behavioral events | Events API | `analytics.behavioral_events.send` ✅ |
| Full record bulk export | Export API | `crm.export` ❌ **Not in manifest** |

**Workaround for bulk export:** Use `hubspot_object_reports.py exportcrm <object>` — it pages through the search API to reconstruct a full export.

---

## What to Pull and When

### Daily (already done by `crm_daily_snapshot.py`)
- Contact count, company count, deal count by stage, open ticket count

### Weekly — Business Health Report

Build a single weekly JSON that answers the key business questions:

```bash
bash ./scripts/op_run.sh python3 90-reporting/dashboards-reports/scripts/weekly_report.py
# Output: 90-reporting/dashboards-reports/snapshots/YYYY-MM-DD-weekly.json
```

**What goes in the weekly report:**

```json
{
  "week_ending": "2026-04-10",
  "pipeline": {
    "new_leads_this_week": 0,
    "deals_opened_this_week": 0,
    "deals_closed_won_this_week": 0,
    "deals_closed_lost_this_week": 0,
    "total_open_deal_value": 0
  },
  "service": {
    "tickets_opened_this_week": 0,
    "tickets_closed_this_week": 0,
    "tickets_older_than_48h": 0
  },
  "email": {
    "campaigns_sent_this_week": 0,
    "total_sends": 0,
    "open_rate": 0,
    "click_rate": 0
  },
  "reorder_signals": {
    "contacts_with_reorder_window_open": 0,
    "contacts_in_reengagement": 0
  }
}
```

### Monthly — Campaign Attribution Pull

```bash
bash ./scripts/op_run.sh python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token
client = HubSpotClient(get_token())
# Revenue attribution per campaign
resp = client.request_json('GET', '/marketing/v3/campaigns', params={'limit': 100})
print(json.dumps(resp, indent=2))
" > 90-reporting/dashboards-reports/snapshots/campaigns-$(date +%Y-%m).json
```

---

## KPI Definitions (define here, measure everywhere)

Put your KPI definitions in `90-reporting/dashboards-reports/kpi-definitions.md`. These are the single source of truth for what each metric means:

| KPI | Definition | Source |
|-----|-----------|--------|
| New Leads | Contacts created with `hsc_customer_class` set, in the last 7 days | CRM contacts search |
| Deal Conversion Rate | Closed Won / (Closed Won + Closed Lost) in period | CRM deals search |
| Avg Deal Value | Sum of `amount` on Closed Won deals / count | CRM deals search |
| Reorder Rate | Contacts with 2+ closed won deals / total customers | CRM contacts |
| Ticket SLA | % tickets resolved within 48 hours | CRM tickets search |
| Email Open Rate | Pulled from HubSpot marketing email API | Marketing email API |
| Reengagement Pipeline | Contacts with `hsc_reengagement_priority` set | CRM contacts search |

---

## Folder Layout to Build

```
90-reporting/dashboards-reports/
  kpi-definitions.md          ← What each metric means (write this first)
  snapshots/
    YYYY-MM-DD-weekly.json    ← Weekly business health
    YYYY-MM-campaign.json     ← Monthly campaign attribution
  scripts/
    weekly_report.py          ← Pulls all weekly KPIs in one shot
```

---

## What NOT to Do

- Don't try to use `crm.export` — it's not in your manifest (will 403)
- Don't pull full record exports for reporting — use `count_records()` + filtered searches
- Don't build dashboards in HubSpot UI and assume you can export them — pull the underlying data instead
- Don't define KPIs in multiple places — `kpi-definitions.md` is the single source
