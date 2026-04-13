#!/usr/bin/env python3
"""
05_data_type_mismatch.py — Data-Type Mismatch Warning
======================================================
Samples records and validates that stored values match the declared property
type. Catches corrupted imports and API writes with wrong formats.

Checks:
  - date / date_time properties → must parse as a valid timestamp
  - number properties          → stored value must be numeric
  - phone_number               → must contain at least 7 digits
  - email                      → must contain "@" and a "."

Outputs one row per violation found in the sample.

Output:
  outputs/data-type-mismatch/<timestamp>/
    violations.csv
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/05_data_type_mismatch.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, simple_filter, filter_group, iter_all_records
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "data-type-mismatch"
log = AutomationLogger(AUTOMATION_NAME)

SCAN_OBJECTS = ["contacts", "companies", "deals", "tickets"]

# How many sample records to fetch per object (not per property).
SAMPLE_SIZE = 200

# Max properties per API call (HubSpot limit is 250; stay conservative).
_PROP_CHUNK = 200

# Regex patterns for validation.
_PHONE_RE = re.compile(r"[0-9]{7,}")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_for_type(value: str, prop_type: str, field_type: str) -> tuple[bool, str]:
    """Return (is_valid, reason_if_invalid)."""
    if not value or value.strip() == "":
        return True, ""  # empty is handled by NOT_HAS_PROPERTY elsewhere

    if prop_type in ("date", "datetime"):
        # HubSpot stores as epoch-ms integer strings; API may also return ISO strings.
        try:
            int(value)
            return True, ""
        except ValueError:
            pass
        # Accept ISO date strings too (e.g. "2026-01-15T00:00:00Z")
        if re.match(r"^\d{4}-\d{2}-\d{2}", value):
            return True, ""
        return False, f"Expected epoch-ms or ISO date, got: {value!r}"

    if prop_type == "number":
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"Expected numeric, got: {value!r}"

    if field_type == "phonenumber" or prop_type == "phone_number":
        if not _PHONE_RE.search(value):
            return False, f"Fewer than 7 digits in phone: {value!r}"

    if field_type == "email" or (prop_type == "string" and "email" in field_type.lower()):
        if not _EMAIL_RE.match(value):
            return False, f"Looks like an invalid email: {value!r}"

    return True, ""


def _check_type(prop_type: str, field_type: str) -> bool:
    """Should we validate this property type?"""
    return prop_type in ("date", "datetime", "number") or field_type in ("phonenumber", "email")


def _properties_to_check(client: Any, object_type: str) -> list[dict]:
    props = client.get_properties(object_type)
    return [
        p for p in props
        if not p.get("archived", False)
        and _check_type(p.get("type", ""), p.get("fieldType", ""))
    ]


def _analyze_object(client: Any, object_type: str) -> list[dict]:
    props = _properties_to_check(client, object_type)
    log.info(f"  {object_type}: {len(props)} type-checkable properties")
    if not props:
        return []

    # Build a lookup dict for fast type access.
    prop_meta: dict[str, dict] = {p["name"]: p for p in props}
    prop_names = list(prop_meta.keys())

    # Fetch sample records in bulk, chunking property lists to stay under API limit.
    records_by_id: dict[str, dict] = {}
    for i in range(0, len(prop_names), _PROP_CHUNK):
        chunk = prop_names[i:i + _PROP_CHUNK]
        log.info(f"    fetching sample ({i}..{i+len(chunk)}) …")
        results = iter_all_records(client, object_type, chunk, [], page_size=100)
        sample = results[:SAMPLE_SIZE]
        for rec in sample:
            rid = rec.get("id", "")
            if rid not in records_by_id:
                records_by_id[rid] = {"id": rid, "properties": {}}
            records_by_id[rid]["properties"].update(rec.get("properties", {}))

    log.info(f"    {len(records_by_id)} sample records fetched")

    rows: list[dict] = []
    for rid, rec in records_by_id.items():
        for pname, meta in prop_meta.items():
            value = rec["properties"].get(pname)
            if not value:
                continue
            valid, reason = _is_valid_for_type(value, meta.get("type", ""), meta.get("fieldType", ""))
            if not valid:
                rows.append({
                    "object": object_type,
                    "record_id": rid,
                    "property": pname,
                    "label": meta.get("label", pname),
                    "declared_type": meta.get("type", ""),
                    "field_type": meta.get("fieldType", ""),
                    "stored_value": str(value)[:100],
                    "violation": reason,
                })

    return rows


def _build_summary(rows: list[dict], run_date: str) -> str:
    if not rows:
        return (
            f"# Data Type Mismatch Warning — {run_date}\n\n"
            f"**No type violations found** in sampled records.\n"
        )
    lines = [
        f"# Data Type Mismatch Warning — {run_date}",
        "",
        f"**{len(rows)} violation(s)** found in sample of up to {SAMPLE_SIZE} records per property.",
        "",
        "| Object | Record ID | Property | Type | Stored Value | Violation |",
        "|--------|-----------|----------|------|--------------|-----------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['object']} | {r['record_id']} | `{r['property']}` | {r['declared_type']}"
            f" | `{r['stored_value']}` | {r['violation']} |"
        )
    return "\n".join(lines)


def run() -> int:
    log.section("Data-Type Mismatch Warning")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)
    all_rows: list[dict] = []

    for obj in SCAN_OBJECTS:
        log.info(f"Scanning {obj} …")
        try:
            all_rows.extend(_analyze_object(client, obj))
        except Exception as exc:  # noqa: BLE001
            log.error(f"Failed to scan {obj}: {exc}")

    csv_fields = ["object", "record_id", "property", "label", "declared_type",
                  "field_type", "stored_value", "violation"]
    csv_path = writer.write_csv("violations", all_rows, csv_fields)
    log.info(f"CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(all_rows, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("Violations found", len(all_rows))
    if all_rows:
        from collections import Counter
        by_obj = Counter(r["object"] for r in all_rows)
        for obj, count in by_obj.most_common():
            log.result(f"  {obj}", count)
    return 0


if __name__ == "__main__":
    sys.exit(run())
