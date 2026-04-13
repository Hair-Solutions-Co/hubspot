#!/usr/bin/env python3
"""
03_enum_mismatch.py — Enum Mismatch Detector
=============================================
Finds enumeration/select properties where records have values that are NOT in
the property's defined option list. These phantom values typically come from API
writes, imports, or legacy data and silently break filters and reports.

Approach:
  1. Fetch all enum properties for each object.
  2. For each enum property, get the set of defined option values.
  3. Sample up to MAX_SAMPLE records that have the property set.
  4. Compare sample values against known options.
  5. If any unknown value is found, use a search to count how many records are
     affected.

Output:
  outputs/enum-mismatch/<timestamp>/
    mismatches.csv    — one row per phantom value
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/03_enum_mismatch.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, simple_filter, filter_group, iter_all_records
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "enum-mismatch"
log = AutomationLogger(AUTOMATION_NAME)

# Objects to scan; extend as needed.
SCAN_OBJECTS = ["contacts", "companies", "deals", "tickets"]

# How many sample records to fetch per object (not per property).
MAX_SAMPLE = 200

# Max properties per API call.
_PROP_CHUNK = 200

# Skip very high-cardinality internal properties that are never user-editable.
SKIP_PREFIXES = ("hs_v2_", "hs_analytics_", "hs_email_", "hs_sequences_",
                 "hs_date_", "hs_time_")


def _is_skip(name: str) -> bool:
    return any(name.startswith(p) for p in SKIP_PREFIXES)


def _enum_properties(client: Any, object_type: str) -> list[dict]:
    props = client.get_properties(object_type)
    return [
        p for p in props
        if p.get("type") == "enumeration"
        and not p.get("archived", False)
        and not _is_skip(p["name"])
        and p.get("options")
    ]


def _sample_values(client: Any, object_type: str, property_name: str) -> list[str]:
    """Return up to MAX_SAMPLE non-empty values for this property (single-property fallback)."""
    fg = [filter_group(simple_filter(property_name, "HAS_PROPERTY"))]
    results = iter_all_records(client, object_type, [property_name], fg, page_size=100)
    values: list[str] = []
    for rec in results[:MAX_SAMPLE]:
        val = rec.get("properties", {}).get(property_name, "")
        if val:
            values.append(val)
    return values


def _count_with_value(client: Any, object_type: str, property_name: str, value: str) -> int:
    fg = [filter_group(simple_filter(property_name, "EQ", value))]
    resp = client.search_records(object_type, properties=[], filter_groups=fg, limit=1)
    return int(resp.get("total", 0))


def _analyze_object(client: Any, object_type: str) -> tuple[list[dict], int]:
    rows: list[dict] = []
    props = _enum_properties(client, object_type)
    log.info(f"  {object_type}: {len(props)} enum properties to check")
    if not props:
        return rows, 0

    prop_meta: dict[str, dict] = {p["name"]: p for p in props}
    prop_names = list(prop_meta.keys())

    # Bulk-fetch sample records with all enum properties at once.
    records_by_id: dict[str, dict] = {}
    for i in range(0, len(prop_names), _PROP_CHUNK):
        chunk = prop_names[i:i + _PROP_CHUNK]
        log.info(f"    fetching sample ({i}..{i+len(chunk)}) …")
        results = iter_all_records(client, object_type, chunk, [], page_size=100)
        sample = results[:MAX_SAMPLE]
        for rec in sample:
            rid = rec.get("id", "")
            if rid not in records_by_id:
                records_by_id[rid] = {"id": rid, "properties": {}}
            records_by_id[rid]["properties"].update(rec.get("properties", {}))

    log.info(f"    {len(records_by_id)} sample records fetched")

    # Find phantom values across all records and properties.
    phantom_values: dict[str, set[str]] = {}  # property_name → set of phantom values
    for rid, rec in records_by_id.items():
        for pname, meta in prop_meta.items():
            val = rec["properties"].get(pname)
            if not val:
                continue
            defined_values = {o["value"] for o in (meta.get("options") or []) if not o.get("hidden", False)}
            if not defined_values:
                continue
            parts = val.split(";") if meta.get("fieldType") in ("checkbox", "booleancheckbox") else [val]
            for part in parts:
                part = part.strip()
                if part and part not in defined_values:
                    phantom_values.setdefault(pname, set()).add(part)

    # Count records affected by each phantom value (separate API call per phantom).
    for pname, phantoms in sorted(phantom_values.items()):
        meta = prop_meta[pname]
        label = meta.get("label", pname)
        defined_values = {o["value"] for o in (meta.get("options") or []) if not o.get("hidden", False)}
        for phantom in sorted(phantoms):
            count = _count_with_value(client, object_type, pname, phantom)
            rows.append({
                "object": object_type,
                "property": pname,
                "label": label,
                "phantom_value": phantom,
                "records_affected": count,
                "defined_options": "; ".join(sorted(defined_values)),
            })
            log.warn(f"    {object_type}.{pname}: phantom '{phantom}' ({count} records)")

    return rows, len(props)


def _build_summary(rows: list[dict], run_date: str) -> str:
    if not rows:
        return (
            f"# Enum Mismatch Report — {run_date}\n\n"
            "**No phantom enum values detected.** All sampled records use defined option values.\n"
        )

    lines = [
        f"# Enum Mismatch Report — {run_date}",
        "",
        f"**{len(rows)} phantom value(s) detected** across "
        f"{len(set(r['object'] for r in rows))} objects.\n",
        "Phantom values are enum field values that don't appear in the property's option list.",
        "They silently break filters, workflows, and reports.",
        "",
        "| Object | Property | Phantom Value | Records Affected |",
        "|--------|----------|---------------|-----------------|",
    ]
    for r in sorted(rows, key=lambda x: (-x["records_affected"], x["object"], x["property"])):
        lines.append(
            f"| {r['object']} | `{r['property']}` | `{r['phantom_value']}` | {r['records_affected']} |"
        )

    lines += ["", "## Recommended actions", ""]
    lines.append("1. Update records with phantom values to use defined options.")
    lines.append("2. Or add the phantom value as a new option to the property definition.")
    lines.append("3. Run `automation:schema-drift` after fixing to confirm no new options were added.")
    return "\n".join(lines)


def run() -> int:
    log.section("Enum Mismatch Detector")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)
    all_rows: list[dict] = []
    total_props = 0

    for obj in SCAN_OBJECTS:
        log.info(f"Scanning {obj} …")
        try:
            obj_rows, obj_count = _analyze_object(client, obj)
            all_rows.extend(obj_rows)
            total_props += obj_count
        except Exception as exc:  # noqa: BLE001
            log.error(f"Failed to scan {obj}: {exc}")

    csv_fields = ["object", "property", "label", "phantom_value", "records_affected", "defined_options"]
    csv_path = writer.write_csv("mismatches", all_rows, csv_fields)
    log.info(f"CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(all_rows, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("Properties scanned", total_props)
    log.result("Phantom values found", len(all_rows))
    affected = sum(r["records_affected"] for r in all_rows)
    log.result("Total records affected", affected)
    return 0


if __name__ == "__main__":
    sys.exit(run())
