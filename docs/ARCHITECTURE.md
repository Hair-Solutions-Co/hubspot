# CRM Automation Framework — Architecture

## Overview

All 10 Phase 1 automations share a lightweight framework in `automations/lib/`. The design is intentionally minimal: no external dependencies, no ORM, no async. Just Python 3.9 stdlib + the existing `HubSpotClient` class.

---

## Directory Layout

```
automations/
  lib/
    __init__.py
    client.py      — HubSpotClient re-export + helpers
    output.py      — Timestamped CSV/JSON/Markdown writers
    log.py         — AutomationLogger
  01_schema_drift_audit.py
  02_required_field_gap.py
  03_enum_mismatch.py
  04_unused_properties.py
  05_data_type_mismatch.py
  06_new_contact_triage.py
  07_pipeline_health.py
  08_stale_records.py
  09_duplicate_detection.py
  10_ownerless_records.py
  run_crm_phase1.py   — Grouped runner
```

---

## lib/client.py

Wraps `scripts/hubspot_object_reports.HubSpotClient` with convenience helpers:

| Function | Description |
|----------|-------------|
| `get_client()` | Returns authenticated `HubSpotClient` using `HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN` |
| `epoch_ms_ago(days, hours)` | Returns epoch-ms for N days/hours ago |
| `days_ago_ms(n)` | Shorthand for `epoch_ms_ago(days=n)` |
| `now_epoch_ms()` | Current time as epoch-ms |
| `format_hs_date(value)` | Converts epoch-ms or ISO string to `YYYY-MM-DD` |
| `days_since(value)` | Days elapsed since epoch-ms or ISO timestamp |
| `simple_filter(prop, op, val?)` | Builds a single CRM Search filter dict |
| `filter_group(*filters)` | Wraps filters into an AND group |
| `iter_all_records(client, object, props, filter_groups, page_size)` | Paginates through all matching records |
| `count_filtered(client, object, filter_groups)` | Returns total count without fetching records |

---

## lib/output.py

`OutputWriter(automation_name)` creates a timestamped output directory under `outputs/<automation_name>/<UTC_timestamp>/`.

| Method | Description |
|--------|-------------|
| `write_csv(name, rows, fields)` | Writes rows to `<name>.csv` |
| `write_json(name, data)` | Writes data to `<name>.json` |
| `write_markdown(name, text)` | Writes text to `<name>.md` |
| `date_str()` | Returns `YYYY-MM-DD` for use in report headers |

---

## lib/log.py

`AutomationLogger(name)` prefixes all output with `[name]` and timestamps.

| Method | Description |
|--------|-------------|
| `.section(title)` | Prints a horizontal rule with title |
| `.info(msg)` | Regular log line |
| `.warn(msg)` | Warning line (same format, no colour in terminal) |
| `.error(msg)` | Error line |
| `.result(label, value)` | Prints `→ label: value` in the Results section |

---

## HubSpot API Facts Discovered

These were confirmed by real testing against portal `50966981`:

### Deal pipeline property
The `pipeline` property name (not `hs_pipeline`) must be used to filter deals by pipeline in the CRM Search API. `hs_pipeline` exists in the schema and is displayed in the HubSpot UI, but:
- Returns `null` for all deals when requested as a property
- Returns HTTP 400 when used as a filter operator

Use `pipeline EQ <pipeline_id>` where pipeline IDs come from `/crm/v3/pipelines/deals`. The "Deals pipeline" (default) has the special ID `"default"`.

### Date formats
The 2026-03 API version (`/crm/objects/2026-03/{object}/search`) returns ISO date strings in response property values (e.g., `"2026-04-03T16:23:55.681Z"`), not epoch-ms integers. However, filter `value` fields still accept epoch-ms integers. `format_hs_date()` handles both formats.

### Bulk property fetching
HubSpot's CRM Search API accepts up to ~250 properties per request. For automations that need to scan many properties, always request properties in a single bulk call then validate in-memory — instead of one API call per property. This reduces a 258-property scan from 258+ API calls to 2 calls.

### NOT_HAS_PROPERTY filter
The `NOT_HAS_PROPERTY` operator works correctly on both `/crm/v3/` and `/crm/objects/2026-03/` endpoints. Does not require a `value` field.

### Ownerless contact rate
Portal 50966981 has 99.8% ownerless contacts (2,966 of 2,973). This is expected for a DTC e-commerce Shopify integration where contacts are created by order sync rather than sales reps.

---

## Adding New Automations

1. Create `automations/NN_my_automation.py` following the existing pattern.
2. Import from `lib.client`, `lib.log`, `lib.output`.
3. Implement a `run() -> int` function returning 0 on success.
4. Add to `run_crm_phase1.py`'s `AUTOMATIONS` list with its category and slow flag.
5. Add an npm script to `package.json`.

---

## Security Notes

- No tokens are ever hardcoded. Auth is injected via `bash ./scripts/op_run.sh` (1Password CLI).
- `outputs/` is gitignored — no customer data is ever committed.
- All API requests go through the existing `HubSpotClient` which validates HTTPS and enforces 60s timeouts with up to 5 retries.
