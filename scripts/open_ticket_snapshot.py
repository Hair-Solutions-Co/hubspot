#!/usr/bin/env python3
"""
Daily open-ticket snapshot: pull all non-closed tickets with key properties.

Output: 60-service/tickets/snapshots/YYYY-MM-DD-open-tickets.json

Run via:
  bash ./scripts/op_run.sh python3 scripts/open_ticket_snapshot.py
or:
  npm run hubspot:tickets:snapshot
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hubspot_object_reports import HubSpotClient, get_token  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
SNAPSHOT_DIR = BASE_DIR / "60-service" / "tickets" / "snapshots"

TICKET_PROPERTIES = [
    "subject",
    "content",
    "hs_pipeline",
    "hs_pipeline_stage",
    "hs_ticket_priority",
    "hs_ticket_category",
    "createdate",
    "hs_lastmodifieddate",
    "hubspot_owner_id",
    "hs_resolution",
]


def pull_open_tickets(client: HubSpotClient) -> list[dict]:
    """Fetch all tickets not in a closed stage, paginating if needed."""
    all_tickets: list[dict] = []
    after: str | None = None

    while True:
        resp = client.search_records(
            "tickets",
            properties=TICKET_PROPERTIES,
            filter_groups=[{
                "filters": [{
                    "propertyName": "hs_pipeline_stage",
                    "operator": "NEQ",
                    "value": "4",  # 4 = closed in default pipeline
                }]
            }],
            after=after,
            limit=100,
        )
        results = resp.get("results", [])
        all_tickets.extend(results)
        after = resp.get("paging", {}).get("next", {}).get("after")
        if not after:
            break

    return all_tickets


def main() -> None:
    today = dt.date.today().isoformat()
    out_path = SNAPSHOT_DIR / f"{today}-open-tickets.json"
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    client = HubSpotClient(get_token())
    print(f"Pulling open tickets...", flush=True)
    tickets = pull_open_tickets(client)

    snapshot = {
        "date": today,
        "total_open": len(tickets),
        "tickets": tickets,
    }

    out_path.write_text(json.dumps(snapshot, indent=2) + "\n")
    print(f"Wrote {len(tickets)} open tickets → {out_path}")


if __name__ == "__main__":
    main()
