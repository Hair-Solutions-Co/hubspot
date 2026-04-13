# CRM Phase 1 Automations

10 production-validated automations across two categories: CRM Schemas (01–05) and CRM Objects (06–10).

All scripts live in `automations/` and use the shared `automations/lib/` framework. Run any of them with:

```bash
bash ./scripts/op_run.sh python3 automations/<script>.py
```

Or via npm:
```bash
npm run automation:<name>
```

---

## CRM Schema Automations

### 01 — Schema Drift Audit
**Script:** `01_schema_drift_audit.py`
**NPM:** `automation:schema-drift`
**Cadence:** Weekly
**Purpose:** Detects property additions, removals, and type changes across all six CRM objects (contacts, companies, deals, tickets, leads, products) compared to a saved baseline.

**How it works:**
1. Fetches all properties for each object via `/crm/v3/properties/{object}`.
2. Compares against `config/schema_baseline.json`.
3. Writes a CSV of all diffs and a Markdown summary.
4. On first run (or after `npm run automation:schema-drift:reset`), saves the current state as the new baseline.

**Output:** `outputs/schema-drift-audit/<timestamp>/drift_report.csv`, `summary.md`

---

### 02 — Required Field Gap
**Script:** `02_required_field_gap.py`
**NPM:** `automation:required-field-gap`
**Cadence:** Weekly
**Purpose:** For each active pipeline stage (deals + tickets), counts records missing key business fields. Highlights stages where >50% of records are missing critical data.

**Key fields checked:**
- Deals: `dealname`, `amount`, `closedate`, `hubspot_owner_id`
- Tickets: `subject`, `hubspot_owner_id`, `hs_ticket_priority`

**HubSpot quirk:** Deal pipeline filter uses property name `pipeline` (not `hs_pipeline`). The `hs_pipeline` property exists in the schema but is not filterable in the CRM Search API and returns `null` for all deals.

**Output:** `outputs/required-field-gap/<timestamp>/gap_report.csv`, `summary.md`

---

### 03 — Enum Mismatch Detector
**Script:** `03_enum_mismatch.py`
**NPM:** `automation:enum-mismatch`
**Cadence:** Weekly
**Purpose:** Finds enum/select properties where stored record values are not in the property's defined option list. Phantom values silently break filters, workflows, and reports.

**How it works:**
- Bulk-fetches 200 sample records per object with all enum properties at once (instead of one API call per property).
- Compares stored values against `options[]` in the property definition.
- For any phantom value, counts total affected records.
- Skips `hs_v2_*`, `hs_analytics_*`, `hs_email_*`, `hs_sequences_*`, `hs_date_*`, `hs_time_*` prefixes.

**Output:** `outputs/enum-mismatch/<timestamp>/mismatches.csv`, `summary.md`

---

### 04 — Unused Properties
**Script:** `04_unused_properties.py`
**NPM:** `automation:unused-properties`
**Cadence:** Monthly
**Purpose:** Counts how many records have a value set for each custom property. Properties with zero records are candidates for archiving.

**Threshold:** `LOW_USAGE_THRESHOLD = 5` — reports both UNUSED (0 records) and LOW_USAGE (<5 records).

**Real data result:** 242 of 324 custom properties are unused; 8 have fewer than 5 records.

**Output:** `outputs/unused-properties/<timestamp>/unused_properties.csv`, `summary.md`

---

### 05 — Data-Type Mismatch
**Script:** `05_data_type_mismatch.py`
**NPM:** `automation:data-type-mismatch`
**Cadence:** Weekly
**Purpose:** Validates that stored values match their declared property types. Catches corrupt imports and API writes using wrong formats.

**Type checks:**
- `date` / `datetime` → must be epoch-ms integer or ISO date string
- `number` → must be float-parseable
- `phonenumber` → must contain at least 7 consecutive digits
- `email` → must contain `@` and `.`

**How it works:** Bulk-fetches 200 sample records per object with up to 200 type-checkable properties per API call (chunks of `_PROP_CHUNK=200`). No per-property API calls.

**Real data result:** 38 violations found (35 in companies, 3 in contacts).

**Output:** `outputs/data-type-mismatch/<timestamp>/violations.csv`, `summary.md`

---

## CRM Object Automations

### 06 — New Contact Triage
**Script:** `06_new_contact_triage.py`
**NPM:** `automation:new-contact-triage`
**Cadence:** Daily
**Purpose:** Lists all contacts created in the last 24 hours (configurable via `--hours N`) with triage flags for missing owner, email, or phone.

**Flags per contact:**
- `no_owner` — `hubspot_owner_id` is null
- `no_email` — `email` is null
- `no_phone` — `phone` is null

**Output:** `outputs/new-contact-triage/<timestamp>/new_contacts.csv`, `summary.md`

---

### 07 — Pipeline Health Snapshot
**Script:** `07_pipeline_health.py`
**NPM:** `automation:pipeline-health`
**Cadence:** Daily
**Purpose:** For each deal pipeline, shows deal count, total value, average age (days), and overdue count per stage.

**Metrics per stage:**
- `deal_count` — total deals in stage
- `total_value` — sum of `amount`
- `avg_age_days` — average days since `createdate`
- `overdue_count` — deals past `closedate` in active stages

**HubSpot quirk:** Same as Automation 02 — filter uses `pipeline` property (not `hs_pipeline`).

**Real data result:** 1,001 deals in "Deals pipeline", 8 active deals, $18,668 total active value.

**Output:** `outputs/pipeline-health/<timestamp>/pipeline_health.csv`, `active_deals.csv`, `summary.md`

---

### 08 — Stale Record Resurfacer
**Script:** `08_stale_records.py`
**NPM:** `automation:stale-records`
**Cadence:** Weekly
**Purpose:** Finds deals and contacts not modified in the last 30 days (configurable via `--days N`) that are still in active (non-terminal) stages.

**Terminal stage IDs** are loaded from `config/id_manifest.json` — any stage whose label contains "closed", "won", "lost", "inactive", "complete", or "cancelled" is excluded.

**Output:** `outputs/stale-records/<timestamp>/stale_deals.csv`, `stale_contacts.csv`, `summary.md`

---

### 09 — Duplicate Detection
**Script:** `09_duplicate_detection.py`
**NPM:** `automation:duplicate-detection`
**Cadence:** Weekly
**Purpose:** Two-pass contact deduplication:
1. **Email duplicates** — contacts sharing the same email address (HIGH confidence).
2. **Name + company duplicates** — contacts with same normalized firstname + lastname + company (MEDIUM confidence).

Outputs a prioritized review queue sorted by confidence then alphabetically.

**Real data result:** 0 email dupes, 72 name+company candidate pairs found.

**Output:** `outputs/duplicate-detection/<timestamp>/duplicates_by_email.csv`, `duplicates_by_name.csv`, `summary.md`

---

### 10 — Ownerless Records
**Script:** `10_ownerless_records.py`
**NPM:** `automation:ownerless-records`
**Cadence:** Weekly
**Purpose:** Lists all contacts, companies, and active deals with no `hubspot_owner_id` set. Exports per-object CSVs with portal links for bulk reassignment.

**Real data result:** 2,966 ownerless contacts (99.8% of 2,973 total), 503 ownerless companies, 998 ownerless deals.

**Output:** `outputs/ownerless-records/<timestamp>/ownerless_contacts.csv`, `ownerless_companies.csv`, `ownerless_deals.csv`, `summary.md`

---

## Grouped Runner

Run all 10 in sequence:
```bash
bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py
```

Skip slow automations (03, 04, 05):
```bash
bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py --skip-slow
# or: npm run automation:crm-phase-1:fast
```

Run specific automations only:
```bash
bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py --only 06,07,10
```

Skip specific automations:
```bash
bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py --skip 03,04
```

The runner writes a `run_manifest.json` to `outputs/crm-phase1/<timestamp>/` summarizing each automation's status and duration.

---

## Output Structure

All outputs are timestamped and gitignored:
```
outputs/
  schema-drift-audit/20260413T024004Z/
    drift_report.csv
    summary.md
  pipeline-health/20260413T024600Z/
    pipeline_health.csv
    active_deals.csv
    summary.md
  crm-phase1/20260413T031122Z/
    run_manifest.json
  ...
```
