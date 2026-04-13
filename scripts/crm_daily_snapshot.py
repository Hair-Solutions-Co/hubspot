#!/usr/bin/env python3
"""
Daily CRM snapshot: pull record counts for all objects and write counts.json.

Output: 10-crm/imports-exports/snapshots/YYYY-MM-DD/counts.json

Run via:
  bash ./scripts/op_run.sh python3 scripts/crm_daily_snapshot.py
or:
  npm run hubspot:crm:snapshot
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

# Import shared infrastructure from existing module.
# op_run.sh always cd's to the repo root before running, so scripts/ is on sys.path.
sys.path.insert(0, str(Path(__file__).parent))
from hubspot_object_reports import HubSpotClient, get_token  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
SNAPSHOT_DIR = BASE_DIR / "10-crm" / "imports-exports" / "snapshots"

# Core objects to count every day.
DAILY_OBJECTS = [
    "contacts",
    "companies",
    "deals",
    "tickets",
    "leads",
    "products",
    "quotes",
    "orders",
    "subscriptions",
    "invoices",
    "line_items",
]

# Objects whose records break down by pipeline stage.
PIPELINE_OBJECTS = ["deals", "tickets"]

# Stage property name per object type.
_STAGE_PROP = {
    "deals": "dealstage",
    "tickets": "hs_pipeline_stage",
}


def _get_pipelines(client: HubSpotClient, object_type: str) -> list[dict]:
    try:
        return client.request_json("GET", f"/crm/v3/pipelines/{object_type}").get("results", [])
    except RuntimeError:
        return []


def _count_by_stage(client: HubSpotClient, object_type: str, pipeline_id: str, stage_id: str) -> int:
    stage_prop = _STAGE_PROP.get(object_type, "hs_pipeline_stage")
    try:
        resp = client.search_records(
            object_type,
            properties=(),
            filter_groups=[{
                "filters": [
                    {"propertyName": "hs_pipeline", "operator": "EQ", "value": pipeline_id},
                    {"propertyName": stage_prop, "operator": "EQ", "value": stage_id},
                ]
            }],
            limit=1,
        )
        return int(resp.get("total", 0))
    except RuntimeError:
        return -1  # -1 signals a failed count rather than zero


def _pull_counts(client: HubSpotClient) -> dict:
    counts: dict = {}

    for obj_type in DAILY_OBJECTS:
        print(f"  {obj_type}...", flush=True)
        try:
            counts[obj_type] = client.count_records(obj_type)
        except RuntimeError as exc:
            counts[obj_type] = {"error": str(exc)}

    # Custom objects
    for descriptor in client.list_custom_objects():
        key = descriptor.object_type
        print(f"  {descriptor.label} (custom)...", flush=True)
        try:
            counts[key] = {
                "count": client.count_records(key),
                "label": descriptor.label,
                "custom": True,
            }
        except RuntimeError as exc:
            counts[key] = {"error": str(exc), "label": descriptor.label, "custom": True}

    return counts


def _pull_pipeline_breakdowns(client: HubSpotClient) -> dict:
    breakdowns: dict = {}

    for obj_type in PIPELINE_OBJECTS:
        pipelines = _get_pipelines(client, obj_type)
        if not pipelines:
            continue
        breakdowns[obj_type] = []
        for pipeline in pipelines:
            pid = pipeline["id"]
            plabel = pipeline.get("label", pid)
            stages_out = []
            for stage in pipeline.get("stages", []):
                sid = stage["id"]
                slabel = stage.get("label", sid)
                print(f"  {obj_type} > {plabel} > {slabel}...", flush=True)
                stages_out.append({
                    "id": sid,
                    "label": slabel,
                    "count": _count_by_stage(client, obj_type, pid, sid),
                })
            breakdowns[obj_type].append({
                "id": pid,
                "label": plabel,
                "stages": stages_out,
            })

    return breakdowns


def main() -> int:
    today = dt.date.today().isoformat()
    output_dir = SNAPSHOT_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "counts.json"

    print(f"CRM daily snapshot — {today}", flush=True)
    client = HubSpotClient(get_token())

    print("\n[record counts]", flush=True)
    counts = _pull_counts(client)

    print("\n[pipeline breakdowns]", flush=True)
    breakdowns = _pull_pipeline_breakdowns(client)

    snapshot = {
        "pulled_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "portal_id": os.environ.get("HUBSPOT_ACCOUNT__PRIMARY__PORTAL_ID", ""),
        "counts": counts,
        "pipeline_breakdowns": breakdowns,
    }

    output_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten: {output_path.relative_to(BASE_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
