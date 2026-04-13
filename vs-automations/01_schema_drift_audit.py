#!/usr/bin/env python3
"""
01_schema_drift_audit.py — Weekly Schema Drift Audit
=====================================================
Compares the current HubSpot property definitions against a saved baseline
snapshot and reports any drift: added properties, removed properties, type
changes, fieldType changes, and label changes.

On the first run (or if --reset-baseline is passed) the current schema becomes
the new baseline.

Output:
  outputs/schema-drift-audit/<timestamp>/
    drift_report.csv      — row per changed property
    summary.md            — human-readable summary
    baseline.json         — written/updated when baseline is reset

Usage:
  bash ./scripts/op_run.sh python3 automations/01_schema_drift_audit.py
  bash ./scripts/op_run.sh python3 automations/01_schema_drift_audit.py --reset-baseline
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure lib/ is on sys.path when running from any cwd.
sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, AUTOMATION_OBJECTS
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "schema-drift-audit"
BASELINE_PATH = Path(__file__).parent.parent / "config" / "schema_baseline.json"

# Objects to audit — extend as needed.
SCHEMA_OBJECTS = [
    "contacts",
    "companies",
    "deals",
    "tickets",
    "leads",
    "products",
]

log = AutomationLogger(AUTOMATION_NAME)


def _pull_current_schema(client: Any) -> dict[str, list[dict]]:
    """Fetch current property definitions keyed by object type."""
    schema: dict[str, list[dict]] = {}
    for obj in SCHEMA_OBJECTS:
        log.info(f"Pulling properties for {obj} …")
        props = [p for p in client.get_properties(obj) if not p.get("archived", False)]
        # Normalise to the fields we care about for drift detection.
        schema[obj] = [
            {
                "name": p["name"],
                "label": p.get("label", ""),
                "type": p.get("type", ""),
                "fieldType": p.get("fieldType", ""),
                "groupName": p.get("groupName", ""),
                "hubspotDefined": bool(p.get("hubspotDefined", False)),
                "options": sorted(
                    [o.get("value", "") for o in (p.get("options") or []) if not o.get("hidden", False)]
                ),
            }
            for p in props
        ]
    return schema


def _load_baseline() -> dict[str, list[dict]] | None:
    if BASELINE_PATH.exists():
        try:
            return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            log.warn(f"Could not parse baseline file: {exc}")
    return None


def _save_baseline(schema: dict[str, list[dict]]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    log.info(f"Baseline saved → {BASELINE_PATH.relative_to(Path(__file__).parent.parent)}")


def _detect_drift(
    baseline: dict[str, list[dict]],
    current: dict[str, list[dict]],
) -> list[dict]:
    rows: list[dict] = []

    for obj in SCHEMA_OBJECTS:
        base_props = {p["name"]: p for p in (baseline.get(obj) or [])}
        curr_props = {p["name"]: p for p in (current.get(obj) or [])}

        # Added
        for name in sorted(set(curr_props) - set(base_props)):
            p = curr_props[name]
            rows.append({
                "object": obj,
                "property": name,
                "change": "added",
                "hubspot_defined": p["hubspotDefined"],
                "old_value": "",
                "new_value": f"type={p['type']} fieldType={p['fieldType']}",
                "label": p["label"],
            })

        # Removed
        for name in sorted(set(base_props) - set(curr_props)):
            p = base_props[name]
            rows.append({
                "object": obj,
                "property": name,
                "change": "removed",
                "hubspot_defined": p["hubspotDefined"],
                "old_value": f"type={p['type']} fieldType={p['fieldType']}",
                "new_value": "",
                "label": p["label"],
            })

        # Changed
        for name in sorted(set(base_props) & set(curr_props)):
            b = base_props[name]
            c = curr_props[name]
            changes: list[str] = []

            if b["type"] != c["type"]:
                changes.append(f"type: {b['type']} → {c['type']}")
            if b["fieldType"] != c["fieldType"]:
                changes.append(f"fieldType: {b['fieldType']} → {c['fieldType']}")
            if b["label"] != c["label"]:
                changes.append(f"label: {b['label']!r} → {c['label']!r}")

            # Enum option drift (only flag additions/removals, not reordering)
            b_opts = set(b.get("options") or [])
            c_opts = set(c.get("options") or [])
            added_opts = c_opts - b_opts
            removed_opts = b_opts - c_opts
            if added_opts:
                changes.append(f"options added: {sorted(added_opts)}")
            if removed_opts:
                changes.append(f"options removed: {sorted(removed_opts)}")

            for change_desc in changes:
                field, *parts = change_desc.split(": ", 1)
                rows.append({
                    "object": obj,
                    "property": name,
                    "change": f"modified ({field.strip()})",
                    "hubspot_defined": b["hubspotDefined"],
                    "old_value": parts[0].split(" → ")[0] if parts else "",
                    "new_value": parts[0].split(" → ")[1] if parts and " → " in parts[0] else parts[0] if parts else "",
                    "label": c["label"],
                })

    return rows


def _build_summary(rows: list[dict], run_date: str, had_baseline: bool) -> str:
    if not had_baseline:
        return f"# Schema Drift Audit — {run_date}\n\n**First run** — baseline captured. No drift to report.\n"

    if not rows:
        return f"# Schema Drift Audit — {run_date}\n\n**No schema drift detected.** All properties match baseline.\n"

    added = [r for r in rows if r["change"] == "added"]
    removed = [r for r in rows if r["change"] == "removed"]
    modified = [r for r in rows if r["change"].startswith("modified")]

    lines = [
        f"# Schema Drift Audit — {run_date}",
        "",
        f"**{len(rows)} changes detected** across {len(set(r['object'] for r in rows))} objects.\n",
        f"- Added: {len(added)}",
        f"- Removed: {len(removed)}",
        f"- Modified: {len(modified)}",
        "",
    ]

    for obj in SCHEMA_OBJECTS:
        obj_rows = [r for r in rows if r["object"] == obj]
        if not obj_rows:
            continue
        lines.append(f"## {obj.capitalize()} ({len(obj_rows)} changes)")
        for r in obj_rows:
            hd = " *(HubSpot-defined)*" if r["hubspot_defined"] else ""
            if r["old_value"] and r["new_value"]:
                lines.append(f"- `{r['property']}`{hd} — **{r['change']}**: `{r['old_value']}` → `{r['new_value']}`")
            elif r["new_value"]:
                lines.append(f"- `{r['property']}`{hd} — **{r['change']}**: {r['new_value']}")
            else:
                lines.append(f"- `{r['property']}`{hd} — **{r['change']}**")
        lines.append("")

    return "\n".join(lines)


def run(reset_baseline: bool = False) -> int:
    log.section("Weekly Schema Drift Audit")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)

    log.info("Fetching current schema from HubSpot …")
    current = _pull_current_schema(client)

    baseline = _load_baseline()
    had_baseline = baseline is not None

    if reset_baseline or baseline is None:
        if reset_baseline:
            log.info("--reset-baseline specified — writing new baseline.")
        else:
            log.info("No baseline found — writing initial baseline.")
        _save_baseline(current)
        baseline = current

    log.info("Comparing schemas …")
    drift_rows = _detect_drift(baseline, current)

    csv_fields = ["object", "property", "change", "hubspot_defined", "old_value", "new_value", "label"]
    csv_path = writer.write_csv("drift_report", drift_rows, csv_fields)
    log.info(f"CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    summary_md = _build_summary(drift_rows, writer.date_str(), had_baseline)
    md_path = writer.write_markdown("summary", summary_md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    if not had_baseline:
        log.info("First run — baseline captured. Re-run next week to detect drift.")
    elif drift_rows:
        log.result("Changes detected", len(drift_rows))
        for chtype, label in [("added", "Added"), ("removed", "Removed")]:
            n = sum(1 for r in drift_rows if r["change"] == chtype)
            if n:
                log.result(label, n)
        log.result("Modified", sum(1 for r in drift_rows if r["change"].startswith("modified")))
    else:
        log.info("No schema drift detected — schemas match baseline.")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly HubSpot schema drift audit.")
    parser.add_argument("--reset-baseline", action="store_true", help="Overwrite baseline with current schema.")
    args = parser.parse_args()
    sys.exit(run(reset_baseline=args.reset_baseline))
