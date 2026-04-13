#!/usr/bin/env python3
"""
02_required_field_gap.py — Required Field Gap Report by Pipeline Stage
======================================================================
For deals and tickets in each active pipeline stage, reports what proportion
of records are missing the key business properties that *should* be filled at
that stage.

"Key properties" can be configured per object in STAGE_REQUIRED_FIELDS below.
The script uses HubSpot's NOT_HAS_PROPERTY filter to count missing values per
property per stage, then outputs a CSV showing the gap rate.

Output:
  outputs/required-field-gap/<timestamp>/
    gap_report.csv    — by object / pipeline / stage / property
    summary.md        — table per pipeline

Usage:
  bash ./scripts/op_run.sh python3 automations/02_required_field_gap.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, simple_filter, filter_group
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "required-field-gap"
log = AutomationLogger(AUTOMATION_NAME)

# Properties that should be filled at some point in the deal lifecycle.
DEAL_REQUIRED_FIELDS = [
    "dealname",
    "amount",
    "closedate",
    "hubspot_owner_id",
    "dealstage",
]

# Properties that should be filled for tickets at relevant stages.
TICKET_REQUIRED_FIELDS = [
    "subject",
    "hs_pipeline",
    "hs_pipeline_stage",
    "hubspot_owner_id",
    "hs_ticket_priority",
]


def _stage_prop(object_type: str) -> str:
    if object_type == "deals":
        return "dealstage"
    return "hs_pipeline_stage"


def _pipeline_prop(object_type: str) -> str:
    if object_type == "deals":
        return "pipeline"
    return "hs_pipeline"


def _count(client, object_type: str, filter_groups: list) -> int:
    resp = client.search_records(object_type, properties=[], filter_groups=filter_groups, limit=1)
    return int(resp.get("total", 0))


def _analyze_object(client, object_type: str, pipelines: list[dict], required_fields: list[str]) -> list[dict]:
    rows: list[dict] = []
    stage_prop = _stage_prop(object_type)

    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        pipeline_label = pipeline.get("displayOrder", pipeline_id)
        # Prefer label from id_manifest enrichment, fallback to id
        pipeline_label = pipeline.get("label", pipeline_id)

        stages = pipeline.get("stages", [])
        # stages may be a list of dicts (from API) or a dict (from id_manifest)
        if isinstance(stages, dict):
            stage_items = [{"id": v, "label": k} for k, v in stages.items()]
        else:
            stage_items = stages

        for stage in stage_items:
            stage_id = stage.get("id") or stage.get("stageId")
            stage_label = stage.get("label") or stage.get("metadata", {}).get("label") or stage_id

            if not stage_id:
                continue

            # Total records in this stage
            total_fg = [filter_group(
                simple_filter(stage_prop, "EQ", stage_id),
            )]
            # For deals, also filter by pipeline to avoid cross-pipeline stage ID collisions
            if object_type == "deals":
                total_fg = [filter_group(
                    simple_filter("pipeline", "EQ", pipeline_id),
                    simple_filter(stage_prop, "EQ", stage_id),
                )]
            total = _count(client, object_type, total_fg)
            if total == 0:
                continue

            log.info(f"  {pipeline_label} / {stage_label}: {total} records")

            for field in required_fields:
                if field in (stage_prop, "pipeline", "hs_pipeline", "dealstage"):
                    # Skip the stage/pipeline fields themselves
                    continue
                if object_type == "deals":
                    missing_fg = [filter_group(
                        simple_filter("pipeline", "EQ", pipeline_id),
                        simple_filter(stage_prop, "EQ", stage_id),
                        simple_filter(field, "NOT_HAS_PROPERTY"),
                    )]
                else:
                    missing_fg = [filter_group(
                        simple_filter(stage_prop, "EQ", stage_id),
                        simple_filter(field, "NOT_HAS_PROPERTY"),
                    )]
                missing = _count(client, object_type, missing_fg)
                pct = round(missing / total * 100, 1) if total > 0 else 0.0

                rows.append({
                    "object": object_type,
                    "pipeline": pipeline_label,
                    "stage": stage_label,
                    "stage_id": stage_id,
                    "total_records": total,
                    "property": field,
                    "missing_count": missing,
                    "missing_pct": pct,
                    "severity": "HIGH" if pct >= 50 else "MEDIUM" if pct >= 20 else "OK",
                })

    return rows


def _build_summary(rows: list[dict], run_date: str) -> str:
    if not rows:
        return f"# Required Field Gap Report — {run_date}\n\nNo records found in any pipeline stage.\n"

    high = [r for r in rows if r["severity"] == "HIGH"]
    medium = [r for r in rows if r["severity"] == "MEDIUM"]

    lines = [
        f"# Required Field Gap Report — {run_date}",
        "",
        "Fields missing in >50% of records in a stage are **HIGH**. >20% is **MEDIUM**.",
        "",
        f"- HIGH gaps: {len(high)}",
        f"- MEDIUM gaps: {len(medium)}",
        "",
    ]

    # Group by object > pipeline
    from itertools import groupby
    for obj in sorted(set(r["object"] for r in rows)):
        obj_rows = [r for r in rows if r["object"] == obj and r["severity"] != "OK"]
        if not obj_rows:
            continue
        lines.append(f"## {obj.capitalize()}")
        for pipeline in sorted(set(r["pipeline"] for r in obj_rows)):
            p_rows = [r for r in obj_rows if r["pipeline"] == pipeline]
            lines.append(f"\n### Pipeline: {pipeline}")
            lines.append("| Stage | Property | Missing | % | Severity |")
            lines.append("|-------|----------|---------|---|----------|")
            for r in p_rows:
                lines.append(
                    f"| {r['stage']} | `{r['property']}` | {r['missing_count']}/{r['total_records']}"
                    f" | {r['missing_pct']}% | **{r['severity']}** |"
                )
        lines.append("")

    return "\n".join(lines)


def run() -> int:
    log.section("Required Field Gap Report")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)
    all_rows: list[dict] = []

    # Deals
    log.info("Analyzing deals pipelines …")
    deal_pipelines = client.request_json("GET", "/crm/v3/pipelines/deals").get("results", [])
    all_rows.extend(_analyze_object(client, "deals", deal_pipelines, DEAL_REQUIRED_FIELDS))

    # Tickets
    log.info("Analyzing tickets pipelines …")
    ticket_pipelines = client.request_json("GET", "/crm/v3/pipelines/tickets").get("results", [])
    all_rows.extend(_analyze_object(client, "tickets", ticket_pipelines, TICKET_REQUIRED_FIELDS))

    csv_fields = ["object", "pipeline", "stage", "stage_id", "total_records",
                  "property", "missing_count", "missing_pct", "severity"]
    csv_path = writer.write_csv("gap_report", all_rows, csv_fields)
    log.info(f"CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(all_rows, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    high_count = sum(1 for r in all_rows if r["severity"] == "HIGH")
    medium_count = sum(1 for r in all_rows if r["severity"] == "MEDIUM")
    log.section("Result")
    log.result("Total stage/field combinations audited", len(all_rows))
    log.result("HIGH gaps (>50% missing)", high_count)
    log.result("MEDIUM gaps (>20% missing)", medium_count)
    return 0


if __name__ == "__main__":
    sys.exit(run())
