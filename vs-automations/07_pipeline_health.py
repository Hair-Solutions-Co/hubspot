#!/usr/bin/env python3
"""
07_pipeline_health.py — Daily Pipeline Health Snapshot
=======================================================
For each deal pipeline, shows:
  - Count of deals per stage
  - Total value per stage
  - Average deal age (days since createdate) per stage
  - Number of deals past close date

Outputs a CSV + Markdown report useful for a quick Monday morning review.

Output:
  outputs/pipeline-health/<timestamp>/
    pipeline_health.csv
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/07_pipeline_health.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import (
    get_client, simple_filter, filter_group, iter_all_records,
    format_hs_date, days_since, now_epoch_ms,
)
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "pipeline-health"
log = AutomationLogger(AUTOMATION_NAME)

DEAL_PROPERTIES = [
    "dealname",
    "amount",
    "closedate",
    "createdate",
    "dealstage",
    "pipeline",
    "hubspot_owner_id",
    "hs_deal_stage_probability",
]

# Stages whose names indicate closed outcomes — exclude from "active" counts.
CLOSED_STAGE_NAMES = {"closedwon", "closedlost", "closed won", "closed lost"}


def _is_closed_stage(stage_label: str, stage_id: str) -> bool:
    return (
        stage_label.lower() in CLOSED_STAGE_NAMES
        or stage_id.lower() in CLOSED_STAGE_NAMES
        or "closed" in stage_label.lower()
    )


def _analyze_pipeline(
    client: Any,
    pipeline: dict,
    now_ms: int,
) -> tuple[list[dict], list[dict]]:
    """
    Returns (stage_summary_rows, deal_rows_for_active_stages).
    """
    pipeline_id = pipeline["id"]
    pipeline_label = pipeline.get("label", pipeline_id)
    stages = pipeline.get("stages", [])

    # Fetch all deals in this pipeline with relevant properties.
    log.info(f"  Pipeline: {pipeline_label}")
    fg = [filter_group(simple_filter("pipeline", "EQ", pipeline_id))]
    all_deals = iter_all_records(client, "deals", DEAL_PROPERTIES, fg)
    log.info(f"    {len(all_deals)} deals fetched")

    # Build a stage-id → label/is_closed map.
    stage_meta: dict[str, dict] = {}
    for s in stages:
        sid = s.get("stageId") or s.get("id", "")
        slabel = (s.get("metadata", {}) or {}).get("label") or s.get("label", sid)
        stage_meta[sid] = {"label": slabel, "is_closed": _is_closed_stage(slabel, sid)}

    # Group deals by stage.
    from collections import defaultdict
    by_stage: dict[str, list[dict]] = defaultdict(list)
    for deal in all_deals:
        stage_id = deal.get("properties", {}).get("dealstage", "unknown")
        by_stage[stage_id].append(deal)

    summary_rows: list[dict] = []
    deal_rows: list[dict] = []

    for stage_id, deals in by_stage.items():
        meta = stage_meta.get(stage_id, {"label": stage_id, "is_closed": False})
        stage_label = meta["label"]
        is_closed = meta["is_closed"]

        amounts = []
        ages: list[int] = []
        overdue = 0

        for deal in deals:
            p = deal.get("properties", {})
            amt_str = p.get("amount", "") or ""
            try:
                amounts.append(float(amt_str))
            except ValueError:
                pass

            create_ms = p.get("createdate")
            age = days_since(create_ms)
            if age is not None:
                ages.append(age)

            close_ms = p.get("closedate")
            if close_ms and not is_closed:
                try:
                    if int(close_ms) < now_ms:
                        overdue += 1
                except ValueError:
                    pass

        total_value = sum(amounts)
        avg_age = round(sum(ages) / len(ages), 1) if ages else 0.0

        summary_rows.append({
            "pipeline": pipeline_label,
            "stage": stage_label,
            "stage_id": stage_id,
            "is_closed": is_closed,
            "deal_count": len(deals),
            "total_value": round(total_value, 2),
            "avg_age_days": avg_age,
            "overdue_count": overdue,
        })

        # For active stages, include individual deal rows for the CSV.
        if not is_closed:
            for deal in deals:
                p = deal.get("properties", {})
                deal_rows.append({
                    "pipeline": pipeline_label,
                    "stage": stage_label,
                    "deal_id": deal.get("id", ""),
                    "deal_name": p.get("dealname", ""),
                    "amount": p.get("amount", ""),
                    "close_date": format_hs_date(p.get("closedate")),
                    "created": format_hs_date(p.get("createdate")),
                    "age_days": days_since(p.get("createdate")),
                    "owner_id": p.get("hubspot_owner_id", ""),
                    "probability": p.get("hs_deal_stage_probability", ""),
                    "portal_url": f"https://app.hubspot.com/contacts/50966981/deal/{deal.get('id', '')}",
                })

    return summary_rows, deal_rows


def _build_summary(summary_rows: list[dict], run_date: str) -> str:
    if not summary_rows:
        return f"# Pipeline Health Snapshot — {run_date}\n\nNo deals found.\n"

    lines = [
        f"# Pipeline Health Snapshot — {run_date}",
        "",
    ]

    # Group by pipeline
    pipelines = list(dict.fromkeys(r["pipeline"] for r in summary_rows))
    for pl in pipelines:
        pl_rows = [r for r in summary_rows if r["pipeline"] == pl]
        active = [r for r in pl_rows if not r["is_closed"]]
        closed = [r for r in pl_rows if r["is_closed"]]

        total_active_deals = sum(r["deal_count"] for r in active)
        total_active_value = sum(r["total_value"] for r in active)
        total_overdue = sum(r["overdue_count"] for r in active)

        lines += [
            f"## {pl}",
            "",
            f"Active deals: **{total_active_deals}** | "
            f"Active value: **${total_active_value:,.0f}** | "
            f"Overdue: **{total_overdue}**",
            "",
            "| Stage | Deals | Total Value | Avg Age (days) | Overdue |",
            "|-------|-------|-------------|----------------|---------|",
        ]
        for r in sorted(pl_rows, key=lambda x: (x["is_closed"], x["stage"])):
            closed_tag = " *(closed)*" if r["is_closed"] else ""
            lines.append(
                f"| {r['stage']}{closed_tag} | {r['deal_count']}"
                f" | ${r['total_value']:,.0f} | {r['avg_age_days']}"
                f" | {r['overdue_count']} |"
            )
        lines.append("")

    return "\n".join(lines)


def run() -> int:
    log.section("Daily Pipeline Health Snapshot")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)
    now_ms = now_epoch_ms()

    pipelines = client.request_json("GET", "/crm/v3/pipelines/deals").get("results", [])
    log.info(f"Found {len(pipelines)} deal pipeline(s)")

    all_summary: list[dict] = []
    all_deals: list[dict] = []

    for pipeline in pipelines:
        try:
            s_rows, d_rows = _analyze_pipeline(client, pipeline, now_ms)
            all_summary.extend(s_rows)
            all_deals.extend(d_rows)
        except Exception as exc:  # noqa: BLE001
            log.error(f"Failed to analyze pipeline {pipeline.get('label', pipeline['id'])}: {exc}")

    summary_fields = ["pipeline", "stage", "stage_id", "is_closed", "deal_count",
                      "total_value", "avg_age_days", "overdue_count"]
    csv_path = writer.write_csv("pipeline_health", all_summary, summary_fields)
    log.info(f"Summary CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    deal_fields = ["pipeline", "stage", "deal_id", "deal_name", "amount", "close_date",
                   "created", "age_days", "owner_id", "probability", "portal_url"]
    deals_csv = writer.write_csv("active_deals", all_deals, deal_fields)
    log.info(f"Active deals CSV → {deals_csv.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(all_summary, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    active = [r for r in all_summary if not r["is_closed"]]
    log.result("Total active deals", sum(r["deal_count"] for r in active))
    log.result("Total active value", f"${sum(r['total_value'] for r in active):,.0f}")
    log.result("Overdue deals", sum(r["overdue_count"] for r in active))
    return 0


if __name__ == "__main__":
    sys.exit(run())
