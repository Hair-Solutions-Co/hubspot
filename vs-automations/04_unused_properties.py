#!/usr/bin/env python3
"""
04_unused_properties.py — Unused Property Cleanup Candidates
=============================================================
Reports custom properties that have zero records with a value set.
These are cleanup candidates that may be safely archived if they were
never populated.

Also flags properties that have very low usage (<5 records) separately
as "low usage" candidates for review.

Output:
  outputs/unused-properties/<timestamp>/
    unused_properties.csv
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/04_unused_properties.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, simple_filter, filter_group
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "unused-properties"
log = AutomationLogger(AUTOMATION_NAME)

SCAN_OBJECTS = ["contacts", "companies", "deals", "tickets", "leads"]
LOW_USAGE_THRESHOLD = 5  # flag properties with fewer records than this


def _count_with_property(client: Any, object_type: str, property_name: str) -> int:
    fg = [filter_group(simple_filter(property_name, "HAS_PROPERTY"))]
    resp = client.search_records(object_type, properties=[], filter_groups=fg, limit=1)
    return int(resp.get("total", 0))


def _analyze_object(client: Any, object_type: str) -> list[dict]:
    props = client.get_properties(object_type)
    custom_props = [
        p for p in props
        if not p.get("archived", False)
        and not p.get("hubspotDefined", False)
    ]
    log.info(f"  {object_type}: {len(custom_props)} custom properties to check")

    rows: list[dict] = []
    for i, p in enumerate(custom_props):
        name = p["name"]
        if (i + 1) % 20 == 0:
            log.info(f"    … {i + 1}/{len(custom_props)}")
        count = _count_with_property(client, object_type, name)
        rows.append({
            "object": object_type,
            "property": name,
            "label": p.get("label", name),
            "type": p.get("type", ""),
            "fieldType": p.get("fieldType", ""),
            "groupName": p.get("groupName", ""),
            "records_with_value": count,
            "status": "UNUSED" if count == 0 else ("LOW_USAGE" if count < LOW_USAGE_THRESHOLD else "IN_USE"),
        })

    return rows


def _build_summary(rows: list[dict], run_date: str) -> str:
    unused = [r for r in rows if r["status"] == "UNUSED"]
    low = [r for r in rows if r["status"] == "LOW_USAGE"]
    in_use = [r for r in rows if r["status"] == "IN_USE"]

    lines = [
        f"# Unused Property Candidates — {run_date}",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| UNUSED (0 records) | {len(unused)} |",
        f"| LOW_USAGE (<{LOW_USAGE_THRESHOLD} records) | {len(low)} |",
        f"| IN_USE | {len(in_use)} |",
        "",
        "> Before archiving any property, confirm it isn't used by workflows, reports, or integrations.",
        "",
    ]

    for obj in SCAN_OBJECTS:
        obj_unused = [r for r in unused if r["object"] == obj]
        obj_low = [r for r in low if r["object"] == obj]
        if not obj_unused and not obj_low:
            continue
        lines.append(f"## {obj.capitalize()}")
        if obj_unused:
            lines.append(f"\n### Unused ({len(obj_unused)})")
            lines.append("| Property | Label | Type |")
            lines.append("|----------|-------|------|")
            for r in obj_unused:
                lines.append(f"| `{r['property']}` | {r['label']} | {r['type']} |")
        if obj_low:
            lines.append(f"\n### Low Usage — < {LOW_USAGE_THRESHOLD} records ({len(obj_low)})")
            lines.append("| Property | Label | Records | Type |")
            lines.append("|----------|-------|---------|------|")
            for r in sorted(obj_low, key=lambda x: x["records_with_value"]):
                lines.append(f"| `{r['property']}` | {r['label']} | {r['records_with_value']} | {r['type']} |")
        lines.append("")

    return "\n".join(lines)


def run() -> int:
    log.section("Unused Property Cleanup Candidates")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)
    all_rows: list[dict] = []

    for obj in SCAN_OBJECTS:
        log.info(f"Analyzing {obj} …")
        try:
            all_rows.extend(_analyze_object(client, obj))
        except Exception as exc:  # noqa: BLE001
            log.error(f"Failed to analyze {obj}: {exc}")

    csv_fields = ["object", "property", "label", "type", "fieldType", "groupName",
                  "records_with_value", "status"]
    csv_path = writer.write_csv("unused_properties", all_rows, csv_fields)
    log.info(f"CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(all_rows, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("Custom properties audited", len(all_rows))
    log.result("UNUSED (safe to archive)", sum(1 for r in all_rows if r["status"] == "UNUSED"))
    log.result(f"LOW_USAGE (<{LOW_USAGE_THRESHOLD} records)", sum(1 for r in all_rows if r["status"] == "LOW_USAGE"))
    return 0


if __name__ == "__main__":
    sys.exit(run())
