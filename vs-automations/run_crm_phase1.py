#!/usr/bin/env python3
"""
run_crm_phase1.py — CRM Phase 1 Grouped Runner
===============================================
Runs all 10 Phase 1 automations in sequence.
Captures per-automation success/failure and writes a run manifest.

Usage:
  bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py

Skip specific automations with --skip (comma-separated numbers):
  bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py --skip 4,5

Run only specific automations with --only:
  bash ./scripts/op_run.sh python3 automations/run_crm_phase1.py --only 1,6

Flags for slow automations (cost many API calls):
  --skip-slow     skips automations 03, 04, 05 (enum scan + property usage scan)
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

# Ensure lib/ is importable from automation modules.
AUTOMATIONS_DIR = Path(__file__).parent
sys.path.insert(0, str(AUTOMATIONS_DIR))

AUTOMATION_MANIFEST = [
    {
        "id": 1,
        "name": "schema-drift-audit",
        "module": "01_schema_drift_audit",
        "category": "CRM Schemas",
        "slow": False,
    },
    {
        "id": 2,
        "name": "required-field-gap",
        "module": "02_required_field_gap",
        "category": "CRM Schemas",
        "slow": True,  # many search calls
    },
    {
        "id": 3,
        "name": "enum-mismatch",
        "module": "03_enum_mismatch",
        "category": "CRM Schemas",
        "slow": True,
    },
    {
        "id": 4,
        "name": "unused-properties",
        "module": "04_unused_properties",
        "category": "CRM Schemas",
        "slow": True,
    },
    {
        "id": 5,
        "name": "data-type-mismatch",
        "module": "05_data_type_mismatch",
        "category": "CRM Schemas",
        "slow": False,
    },
    {
        "id": 6,
        "name": "new-contact-triage",
        "module": "06_new_contact_triage",
        "category": "CRM Objects",
        "slow": False,
    },
    {
        "id": 7,
        "name": "pipeline-health",
        "module": "07_pipeline_health",
        "category": "CRM Objects",
        "slow": False,
    },
    {
        "id": 8,
        "name": "stale-records",
        "module": "08_stale_records",
        "category": "CRM Objects",
        "slow": False,
    },
    {
        "id": 9,
        "name": "duplicate-detection",
        "module": "09_duplicate_detection",
        "category": "CRM Objects",
        "slow": True,
    },
    {
        "id": 10,
        "name": "ownerless-records",
        "module": "10_ownerless_records",
        "category": "CRM Objects",
        "slow": False,
    },
]


def _load_module(module_name: str):
    """Dynamically import an automation module from the automations/ directory."""
    file_path = AUTOMATIONS_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_automation(entry: dict) -> dict:
    """Run a single automation and return a result record."""
    print(f"\n{'='*70}")
    print(f"  [{entry['id']:02d}/10] {entry['name']}  ({entry['category']})")
    print(f"{'='*70}")

    start = time.monotonic()
    result = {
        "id": entry["id"],
        "name": entry["name"],
        "category": entry["category"],
        "status": "unknown",
        "duration_s": 0.0,
        "error": None,
    }

    try:
        module = _load_module(entry["module"])
        exit_code = module.run()
        result["status"] = "success" if exit_code == 0 else "failed"
        result["exit_code"] = exit_code
    except SystemExit as exc:
        result["status"] = "failed" if (exc.code or 0) != 0 else "success"
        result["exit_code"] = exc.code or 0
    except Exception as exc:  # noqa: BLE001
        result["status"] = "error"
        result["error"] = traceback.format_exc()
        result["exit_code"] = 1
        print(f"\nERROR in {entry['name']}:\n{traceback.format_exc()}", file=sys.stderr)

    result["duration_s"] = round(time.monotonic() - start, 1)
    status_tag = "✓" if result["status"] == "success" else "✗"
    print(f"\n{status_tag} {entry['name']} finished in {result['duration_s']}s  [{result['status']}]")
    return result


def _write_manifest(results: list[dict]) -> None:
    """Write a JSON run manifest to outputs/crm-phase1/<timestamp>/run_manifest.json."""
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = AUTOMATIONS_DIR.parent / "outputs" / "crm-phase1" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] != "success"),
        "results": results,
    }
    out = out_dir / "run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nRun manifest → {out.relative_to(AUTOMATIONS_DIR.parent)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all CRM Phase 1 automations.")
    parser.add_argument("--skip", default="", help="Comma-separated automation IDs to skip (e.g. 3,4).")
    parser.add_argument("--only", default="", help="Comma-separated automation IDs to run only (e.g. 1,6,7).")
    parser.add_argument("--skip-slow", action="store_true", help="Skip automations marked slow=True.")
    args = parser.parse_args()

    skip_ids = {int(x.strip()) for x in args.skip.split(",") if x.strip()}
    only_ids = {int(x.strip()) for x in args.only.split(",") if x.strip()}

    to_run = [
        entry for entry in AUTOMATION_MANIFEST
        if (not only_ids or entry["id"] in only_ids)
        and entry["id"] not in skip_ids
        and (not args.skip_slow or not entry["slow"])
    ]

    print(f"\n{'='*70}")
    print(f"  CRM Phase 1 Runner — {len(to_run)} automation(s) queued")
    print(f"{'='*70}")

    results: list[dict] = []
    for entry in to_run:
        result = _run_automation(entry)
        results.append(result)

    _write_manifest(results)

    print(f"\n{'='*70}")
    print(f"  Phase 1 Complete: {sum(1 for r in results if r['status'] == 'success')}/{len(results)} succeeded")
    print(f"{'='*70}\n")
    for r in results:
        tag = "✓" if r["status"] == "success" else "✗"
        print(f"  {tag} [{r['id']:02d}] {r['name']} ({r['duration_s']}s)")

    return 0 if all(r["status"] == "success" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
