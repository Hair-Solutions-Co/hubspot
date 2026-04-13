#!/usr/bin/env python3
"""
10_ownerless_records.py — Ownerless Record Cleanup Report
==========================================================
Finds contacts, companies, and deals that have no assigned owner
(hubspot_owner_id is not set).

Ownerless records can't benefit from sequence enrollment, task assignment, or
rep-specific automation. This report gives you the full list to bulk-assign.

Output:
  outputs/ownerless-records/<timestamp>/
    ownerless_contacts.csv
    ownerless_companies.csv
    ownerless_deals.csv
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/10_ownerless_records.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, simple_filter, filter_group, iter_all_records, format_hs_date
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "ownerless-records"
log = AutomationLogger(AUTOMATION_NAME)

CONTACT_PROPERTIES = [
    "firstname", "lastname", "email", "phone",
    "company", "lifecyclestage", "createdate",
    "hs_lastmodifieddate",
]

COMPANY_PROPERTIES = [
    "name", "domain", "industry", "city",
    "createdate", "hs_lastmodifieddate",
]

DEAL_PROPERTIES = [
    "dealname", "amount", "closedate", "dealstage",
    "hs_pipeline", "createdate", "hs_lastmodifieddate",
]

# Closed deal stages — ownerless closed deals are less action-critical.
_CLOSED_KEYWORDS = ("closed", "won", "lost", "cancelled", "fulfilled", "complete")


def _portal_url(object_type: str, record_id: str) -> str:
    if object_type == "contacts":
        return f"https://app.hubspot.com/contacts/50966981/contact/{record_id}"
    if object_type == "companies":
        return f"https://app.hubspot.com/contacts/50966981/company/{record_id}"
    if object_type == "deals":
        return f"https://app.hubspot.com/contacts/50966981/deal/{record_id}"
    return ""


def _fetch_ownerless(client, object_type: str, properties: list[str]) -> list[dict]:
    fg = [filter_group(simple_filter("hubspot_owner_id", "NOT_HAS_PROPERTY"))]
    log.info(f"  Fetching ownerless {object_type} …")
    records = iter_all_records(client, object_type, properties, fg)
    log.info(f"  {len(records)} ownerless {object_type}")
    return records


def _contact_row(rec: dict) -> dict:
    p = rec.get("properties", {})
    return {
        "record_id": rec.get("id", ""),
        "name": f"{p.get('firstname', '')} {p.get('lastname', '')}".strip() or "—",
        "email": p.get("email", ""),
        "phone": p.get("phone", ""),
        "company": p.get("company", ""),
        "lifecycle_stage": p.get("lifecyclestage", ""),
        "created": format_hs_date(p.get("createdate")),
        "last_modified": format_hs_date(p.get("hs_lastmodifieddate")),
        "portal_url": _portal_url("contacts", rec.get("id", "")),
    }


def _company_row(rec: dict) -> dict:
    p = rec.get("properties", {})
    return {
        "record_id": rec.get("id", ""),
        "name": p.get("name", "—"),
        "domain": p.get("domain", ""),
        "industry": p.get("industry", ""),
        "city": p.get("city", ""),
        "created": format_hs_date(p.get("createdate")),
        "last_modified": format_hs_date(p.get("hs_lastmodifieddate")),
        "portal_url": _portal_url("companies", rec.get("id", "")),
    }


def _deal_row(rec: dict) -> dict:
    p = rec.get("properties", {})
    stage = p.get("dealstage", "")
    is_closed = any(w in stage.lower() for w in _CLOSED_KEYWORDS)
    return {
        "record_id": rec.get("id", ""),
        "deal_name": p.get("dealname", "—"),
        "pipeline": p.get("hs_pipeline", ""),
        "stage_id": stage,
        "amount": p.get("amount", ""),
        "close_date": format_hs_date(p.get("closedate")),
        "created": format_hs_date(p.get("createdate")),
        "last_modified": format_hs_date(p.get("hs_lastmodifieddate")),
        "is_closed": is_closed,
        "portal_url": _portal_url("deals", rec.get("id", "")),
    }


def _build_summary(
    contact_rows: list[dict],
    company_rows: list[dict],
    deal_rows: list[dict],
    run_date: str,
) -> str:
    active_deals = [r for r in deal_rows if not r["is_closed"]]

    lines = [
        f"# Ownerless Record Report — {run_date}",
        "",
        "| Object | Ownerless Count |",
        "|--------|----------------|",
        f"| Contacts | {len(contact_rows)} |",
        f"| Companies | {len(company_rows)} |",
        f"| Deals (all) | {len(deal_rows)} |",
        f"| Deals (active only) | {len(active_deals)} |",
        "",
        "> Assign owners via HubSpot → Contacts/Companies/Deals → Filter 'No owner' → Bulk assign.",
        "",
    ]

    if contact_rows[:20]:
        lines += [
            "## Sample: Ownerless Contacts (first 20)",
            "",
            "| Name | Email | Lifecycle | Created | Link |",
            "|------|-------|-----------|---------|------|",
        ]
        for r in contact_rows[:20]:
            lines.append(
                f"| {r['name']} | {r['email'] or '—'} | {r['lifecycle_stage']}"
                f" | {r['created']} | [View]({r['portal_url']}) |"
            )
        lines.append("")

    if active_deals[:20]:
        lines += [
            "## Sample: Ownerless Active Deals (first 20)",
            "",
            "| Deal | Stage | Amount | Close Date | Created |",
            "|------|-------|--------|------------|---------|",
        ]
        for r in active_deals[:20]:
            lines.append(
                f"| [{r['deal_name']}]({r['portal_url']}) | {r['stage_id']}"
                f" | {r['amount'] or '—'} | {r['close_date'] or '—'} | {r['created']} |"
            )

    return "\n".join(lines)


def run() -> int:
    log.section("Ownerless Record Cleanup Report")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)

    contact_recs = _fetch_ownerless(client, "contacts", CONTACT_PROPERTIES)
    company_recs = _fetch_ownerless(client, "companies", COMPANY_PROPERTIES)
    deal_recs = _fetch_ownerless(client, "deals", DEAL_PROPERTIES)

    contact_rows = [_contact_row(r) for r in contact_recs]
    company_rows = [_company_row(r) for r in company_recs]
    deal_rows = [_deal_row(r) for r in deal_recs]

    # Sort: newest first for contacts/companies, by last modified for deals
    contact_rows.sort(key=lambda r: r["created"], reverse=True)
    company_rows.sort(key=lambda r: r["created"], reverse=True)
    deal_rows.sort(key=lambda r: (not r["is_closed"], r["last_modified"]), reverse=True)

    contact_fields = ["record_id", "name", "email", "phone", "company", "lifecycle_stage",
                      "created", "last_modified", "portal_url"]
    cp = writer.write_csv("ownerless_contacts", contact_rows, contact_fields)
    log.info(f"Contacts CSV → {cp.relative_to(Path(__file__).parent.parent)}")

    company_fields = ["record_id", "name", "domain", "industry", "city",
                      "created", "last_modified", "portal_url"]
    cp2 = writer.write_csv("ownerless_companies", company_rows, company_fields)
    log.info(f"Companies CSV → {cp2.relative_to(Path(__file__).parent.parent)}")

    deal_fields = ["record_id", "deal_name", "pipeline", "stage_id", "amount",
                   "close_date", "created", "last_modified", "is_closed", "portal_url"]
    cp3 = writer.write_csv("ownerless_deals", deal_rows, deal_fields)
    log.info(f"Deals CSV → {cp3.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(contact_rows, company_rows, deal_rows, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("Ownerless contacts", len(contact_rows))
    log.result("Ownerless companies", len(company_rows))
    log.result("Ownerless deals (active)", sum(1 for r in deal_rows if not r["is_closed"]))
    return 0


if __name__ == "__main__":
    sys.exit(run())
