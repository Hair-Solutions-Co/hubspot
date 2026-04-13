#!/usr/bin/env python3
"""
06_new_contact_triage.py — Daily New-Contact Triage
=====================================================
Fetches contacts created in the last 24 hours (configurable via --hours) and
produces a triage report highlighting:
  - Missing owner
  - Missing email
  - Missing phone
  - Lifecycle stage

This is the daily "who just came in?" report.

Output:
  outputs/new-contact-triage/<timestamp>/
    new_contacts.csv
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/06_new_contact_triage.py
  bash ./scripts/op_run.sh python3 automations/06_new_contact_triage.py --hours 48
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, epoch_ms_ago, simple_filter, filter_group, iter_all_records, format_hs_date
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "new-contact-triage"
log = AutomationLogger(AUTOMATION_NAME)

FETCH_PROPERTIES = [
    "firstname",
    "lastname",
    "email",
    "phone",
    "company",
    "lifecyclestage",
    "hubspot_owner_id",
    "hs_lead_status",
    "createdate",
    "hs_latest_source",
    "jobtitle",
]

LIFECYCLE_LABELS = {
    "subscriber": "Subscriber",
    "lead": "Lead",
    "marketingqualifiedlead": "MQL",
    "salesqualifiedlead": "SQL",
    "opportunity": "Opportunity",
    "customer": "Customer",
    "evangelist": "Evangelist",
    "other": "Other",
}


def _build_row(rec: dict) -> dict:
    p = rec.get("properties", {})
    owner_id = p.get("hubspot_owner_id", "")
    email = p.get("email", "")
    phone = p.get("phone", "")
    lifecycle = p.get("lifecyclestage", "")

    flags: list[str] = []
    if not owner_id:
        flags.append("NO_OWNER")
    if not email:
        flags.append("NO_EMAIL")
    if not phone:
        flags.append("NO_PHONE")

    return {
        "record_id": rec.get("id", ""),
        "created": format_hs_date(p.get("createdate")),
        "firstname": p.get("firstname", ""),
        "lastname": p.get("lastname", ""),
        "email": email,
        "phone": phone,
        "company": p.get("company", ""),
        "lifecycle_stage": LIFECYCLE_LABELS.get(lifecycle, lifecycle or "—"),
        "lead_status": p.get("hs_lead_status", ""),
        "owner_id": owner_id,
        "source": p.get("hs_latest_source", ""),
        "flags": "; ".join(flags) if flags else "OK",
        "portal_url": f"https://app.hubspot.com/contacts/50966981/contact/{rec.get('id', '')}",
    }


def _build_summary(rows: list[dict], hours: int, run_date: str) -> str:
    total = len(rows)
    no_owner = sum(1 for r in rows if "NO_OWNER" in r["flags"])
    no_email = sum(1 for r in rows if "NO_EMAIL" in r["flags"])
    no_phone = sum(1 for r in rows if "NO_PHONE" in r["flags"])
    ok = sum(1 for r in rows if r["flags"] == "OK")

    lines = [
        f"# New Contact Triage — {run_date} (last {hours}h)",
        "",
        f"**{total} new contact(s)** in the last {hours} hours.",
        "",
        f"| Flag | Count |",
        f"|------|-------|",
        f"| No Owner | {no_owner} |",
        f"| No Email | {no_email} |",
        f"| No Phone | {no_phone} |",
        f"| Clean (OK) | {ok} |",
        "",
    ]

    if rows:
        lines += [
            "## Contact List",
            "",
            "| Name | Email | Company | Lifecycle | Flags | Owner | Link |",
            "|------|-------|---------|-----------|-------|-------|------|",
        ]
        for r in rows:
            name = f"{r['firstname']} {r['lastname']}".strip() or "—"
            owner = r["owner_id"] or "—"
            lines.append(
                f"| {name} | {r['email'] or '—'} | {r['company'] or '—'}"
                f" | {r['lifecycle_stage']} | {r['flags']} | {owner}"
                f" | [View]({r['portal_url']}) |"
            )
    else:
        lines.append("_No new contacts in this window._")

    return "\n".join(lines)


def run(hours: int = 24) -> int:
    log.section("Daily New-Contact Triage")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)

    since_ms = epoch_ms_ago(hours=hours)
    log.info(f"Fetching contacts created in the last {hours} hours …")

    fg = [filter_group(simple_filter("createdate", "GT", since_ms))]
    records = iter_all_records(client, "contacts", FETCH_PROPERTIES, fg)
    log.info(f"Fetched {len(records)} new contact(s)")

    rows = [_build_row(rec) for rec in records]
    # Sort newest first
    rows.sort(key=lambda r: r["created"], reverse=True)

    csv_fields = ["record_id", "created", "firstname", "lastname", "email", "phone",
                  "company", "lifecycle_stage", "lead_status", "owner_id", "source",
                  "flags", "portal_url"]
    csv_path = writer.write_csv("new_contacts", rows, csv_fields)
    log.info(f"CSV → {csv_path.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(rows, hours, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("New contacts", len(rows))
    log.result("Need owner", sum(1 for r in rows if "NO_OWNER" in r["flags"]))
    log.result("Need email", sum(1 for r in rows if "NO_EMAIL" in r["flags"]))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily new-contact triage report.")
    parser.add_argument("--hours", type=int, default=24, help="Look-back window in hours (default: 24).")
    args = parser.parse_args()
    sys.exit(run(hours=args.hours))
