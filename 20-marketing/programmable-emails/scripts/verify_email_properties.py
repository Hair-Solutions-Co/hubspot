#!/usr/bin/env python3
"""
verify_email_properties.py
Phase 1 — Email System Property Verification

Verifies that the programmable email CRM properties exist in HubSpot.

Uses the same property definitions as create_email_properties.py.

Auth:
  HUBSPOT_PRIVATE_APP__CRM_SCHEMA__ACCESS_TOKEN
  or HUBSPOT_SERVICE_KEY

Run:
  python3 scripts/verify_email_properties.py

Flags:
  --object TYPE   Only process one object type: contact | deal | ticket
  --json          Print machine-readable JSON summary
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from create_email_properties import CONTACT_PROPERTIES, DEAL_PROPERTIES, TICKET_PROPERTIES

BASE_URL = "https://api.hubapi.com"

PROPERTY_SETS = {
    "contacts": CONTACT_PROPERTIES,
    "deals": DEAL_PROPERTIES,
    "tickets": TICKET_PROPERTIES,
}


def get_token() -> str:
    token = (
        os.environ.get("HUBSPOT_PRIVATE_APP__CRM_SCHEMA__ACCESS_TOKEN")
        or os.environ.get("HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN")
        or os.environ.get("HUBSPOT_SERVICE_KEY")
    )
    if not token:
        print(
            "ERROR: Set HUBSPOT_PRIVATE_APP__CRM_SCHEMA__ACCESS_TOKEN, "
            "HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN, or HUBSPOT_SERVICE_KEY in env."
        )
        sys.exit(1)
    return token


def hs_get(path: str, token: str) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        body_text = e.read().decode()
        raise RuntimeError(f"GET {path} -> {e.code}: {body_text}") from e


def verify_object(object_type: str, token: str) -> dict[str, Any]:
    props = PROPERTY_SETS[object_type]
    names = [p["name"] for p in props]

    found: list[str] = []
    missing: list[str] = []
    failed: list[dict[str, str]] = []

    for name in names:
        try:
            result = hs_get(f"/crm/v3/properties/{object_type}/{name}", token)
            if result is None:
                missing.append(name)
            else:
                found.append(name)
        except RuntimeError as e:
            failed.append({"property": name, "error": str(e)})

    return {
        "object": object_type,
        "expected": len(names),
        "found_count": len(found),
        "missing_count": len(missing),
        "failed_count": len(failed),
        "found": found,
        "missing": missing,
        "failed": failed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify programmable email properties in HubSpot.")
    parser.add_argument("--object", choices=["contact", "deal", "ticket"], help="Only process one object type.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    token = get_token()

    targets = PROPERTY_SETS.keys()
    if args.object:
        targets = [args.object + "s"]

    results = []
    totals = {
        "expected": 0,
        "found": 0,
        "missing": 0,
        "failed": 0,
    }

    for object_type in targets:
        result = verify_object(object_type, token)
        results.append(result)
        totals["expected"] += result["expected"]
        totals["found"] += result["found_count"]
        totals["missing"] += result["missing_count"]
        totals["failed"] += result["failed_count"]

    payload = {
        "summary": totals,
        "objects": results,
        "ok": totals["missing"] == 0 and totals["failed"] == 0,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for result in results:
            print(f"\n{result['object'].upper()}")
            print(f"  expected: {result['expected']}")
            print(f"  found   : {result['found_count']}")
            print(f"  missing : {result['missing_count']}")
            print(f"  failed  : {result['failed_count']}")
            if result["missing"]:
                print("  missing properties:")
                for name in result["missing"]:
                    print(f"    - {name}")
            if result["failed"]:
                print("  failed lookups:")
                for item in result["failed"]:
                    print(f"    - {item['property']}: {item['error']}")

        print("\nSUMMARY")
        print(f"  expected: {totals['expected']}")
        print(f"  found   : {totals['found']}")
        print(f"  missing : {totals['missing']}")
        print(f"  failed  : {totals['failed']}")

    if not payload["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
