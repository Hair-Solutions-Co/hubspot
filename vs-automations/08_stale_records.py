#!/usr/bin/env python3
"""
08_stale_records.py — Stale Record Resurfacer
==============================================
Finds deals that haven't been modified in N days but are still in active
pipeline stages (not Closed Won/Lost). Also finds contacts in active lifecycle
stages with no recent activity.

These are the records slipping through the cracks.

Output:
  outputs/stale-records/<timestamp>/
    stale_deals.csv
    stale_contacts.csv
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/08_stale_records.py
  bash ./scripts/op_run.sh python3 automations/08_stale_records.py --days 21
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import (
    get_client, simple_filter, filter_group, iter_all_records,
    format_hs_date, days_since, days_ago_ms,
)
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "stale-records"
log = AutomationLogger(AUTOMATION_NAME)

DEFAULT_STALE_DAYS = 30

DEAL_PROPERTIES = [
    "dealname", "amount", "closedate", "createdate",
    "hs_lastmodifieddate", "dealstage", "hs_pipeline",
    "hubspot_owner_id",
]

CONTACT_PROPERTIES = [
    "firstname", "lastname", "email", "phone",
    "lifecyclestage", "hubspot_owner_id",
    "hs_lastmodifieddate", "notes_last_updated",
    "createdate",
]

# Stage IDs/names that indicate a closed/terminal state for deals.
TERMINAL_STAGE_IDS = {
    # HubSpot built-in defaults
    "closedwon", "closedlost",
    # From id_manifest.json for this portal
    "1296488762", "1296488763",  # Old Deals Pipeline: Closed Won / Lost
    "1325233958", "1325233963",  # Sales: Closed Won / Lost
    "1325321646", "1325321647",  # Plans: Plan Complete / Cancelled
    "1325321656", "1325321657", "1325321728",  # Shopify Orders: Fulfilled/Cancelled/Refunded
}

# Lifecycle stages that are effectively "done" for contacts.
TERMINAL_LIFECYCLE = {"customer", "evangelist"}


def _load_terminal_stage_ids() -> set[str]:
    """
    Load terminal stage IDs from id_manifest for more complete filtering.
    Falls back gracefully if manifest is missing.
    """
    manifest_path = Path(__file__).parent.parent / "config" / "id_manifest.json"
    terminal: set[str] = set(TERMINAL_STAGE_IDS)
    if not manifest_path.exists():
        return terminal
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for obj_pipelines in manifest.get("pipelines", {}).values():
            for pipeline in obj_pipelines:
                for stage_label, stage_id in (pipeline.get("stages") or {}).items():
                    lc = stage_label.lower()
                    if any(w in lc for w in ("closed", "won", "lost", "cancelled", "fulfilled",
                                             "complete", "refunded", "inactive")):
                        terminal.add(str(stage_id))
    except Exception:  # noqa: BLE001
        pass
    return terminal


def _stale_deals(client, stale_days: int, terminal_ids: set[str]) -> list[dict]:
    cutoff_ms = days_ago_ms(stale_days)
    fg = [filter_group(simple_filter("hs_lastmodifieddate", "LT", cutoff_ms))]
    log.info(f"  Fetching deals not modified in {stale_days}+ days …")
    all_deals = iter_all_records(client, "deals", DEAL_PROPERTIES, fg)
    log.info(f"  {len(all_deals)} deals fetched (pre-filter)")

    rows: list[dict] = []
    for deal in all_deals:
        p = deal.get("properties", {})
        stage_id = p.get("dealstage", "")
        if stage_id in terminal_ids:
            continue  # skip closed deals
        days_stale = days_since(p.get("hs_lastmodifieddate"))
        rows.append({
            "record_id": deal.get("id", ""),
            "deal_name": p.get("dealname", ""),
            "pipeline": p.get("hs_pipeline", ""),
            "stage_id": stage_id,
            "amount": p.get("amount", ""),
            "close_date": format_hs_date(p.get("closedate")),
            "last_modified": format_hs_date(p.get("hs_lastmodifieddate")),
            "days_stale": days_stale,
            "owner_id": p.get("hubspot_owner_id", ""),
            "portal_url": f"https://app.hubspot.com/contacts/50966981/deal/{deal.get('id', '')}",
        })

    rows.sort(key=lambda r: (r["days_stale"] or 0), reverse=True)
    log.info(f"  {len(rows)} active stale deals found")
    return rows


def _stale_contacts(client, stale_days: int) -> list[dict]:
    cutoff_ms = days_ago_ms(stale_days)
    # Contacts not modified in N days and not in terminal lifecycle stages.
    fg = [filter_group(simple_filter("hs_lastmodifieddate", "LT", cutoff_ms))]
    log.info(f"  Fetching contacts not modified in {stale_days}+ days …")
    # We'll sample up to 500 to keep reasonable runtime; comment out limit for full run.
    from lib.client import HubSpotClient
    resp = client.search_records(
        "contacts", properties=CONTACT_PROPERTIES, filter_groups=fg, limit=100
    )
    contacts = resp.get("results", [])
    after = resp.get("paging", {}).get("next", {}).get("after")
    while after and len(contacts) < 500:
        resp = client.search_records(
            "contacts", properties=CONTACT_PROPERTIES, filter_groups=fg,
            after=after, limit=100
        )
        contacts.extend(resp.get("results", []))
        after = resp.get("paging", {}).get("next", {}).get("after")

    log.info(f"  {len(contacts)} contacts fetched (pre-filter, cap 500)")

    rows: list[dict] = []
    for rec in contacts:
        p = rec.get("properties", {})
        lifecycle = p.get("lifecyclestage", "")
        if lifecycle in TERMINAL_LIFECYCLE:
            continue
        days_stale = days_since(p.get("hs_lastmodifieddate"))
        name = f"{p.get('firstname', '')} {p.get('lastname', '')}".strip()
        rows.append({
            "record_id": rec.get("id", ""),
            "name": name or "—",
            "email": p.get("email", ""),
            "lifecycle_stage": lifecycle,
            "last_modified": format_hs_date(p.get("hs_lastmodifieddate")),
            "days_stale": days_stale,
            "owner_id": p.get("hubspot_owner_id", ""),
            "portal_url": f"https://app.hubspot.com/contacts/50966981/contact/{rec.get('id', '')}",
        })

    rows.sort(key=lambda r: (r["days_stale"] or 0), reverse=True)
    log.info(f"  {len(rows)} active stale contacts found")
    return rows


def _build_summary(deal_rows: list[dict], contact_rows: list[dict], stale_days: int, run_date: str) -> str:
    lines = [
        f"# Stale Record Resurfacer — {run_date}",
        "",
        f"Records not modified in **{stale_days}+ days** that are still in active stages.",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| Stale active deals | {len(deal_rows)} |",
        f"| Stale active contacts | {len(contact_rows)} |",
        "",
    ]

    if deal_rows[:20]:
        lines += ["## Top 20 Stale Deals", "",
                  "| Deal | Stage ID | Amount | Close Date | Last Modified | Days Stale | Owner |",
                  "|------|----------|--------|------------|---------------|------------|-------|"]
        for r in deal_rows[:20]:
            lines.append(
                f"| [{r['deal_name'] or r['record_id']}]({r['portal_url']}) | {r['stage_id']}"
                f" | {r['amount'] or '—'} | {r['close_date'] or '—'}"
                f" | {r['last_modified']} | {r['days_stale']} | {r['owner_id'] or '—'} |"
            )
        lines.append("")

    if contact_rows[:20]:
        lines += ["## Top 20 Stale Contacts", "",
                  "| Name | Email | Lifecycle | Last Modified | Days Stale | Owner |",
                  "|------|-------|-----------|---------------|------------|-------|"]
        for r in contact_rows[:20]:
            lines.append(
                f"| [{r['name']}]({r['portal_url']}) | {r['email'] or '—'}"
                f" | {r['lifecycle_stage']} | {r['last_modified']}"
                f" | {r['days_stale']} | {r['owner_id'] or '—'} |"
            )

    return "\n".join(lines)


def run(stale_days: int = DEFAULT_STALE_DAYS) -> int:
    log.section("Stale Record Resurfacer")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)

    terminal_ids = _load_terminal_stage_ids()
    log.info(f"Loaded {len(terminal_ids)} terminal stage IDs from manifest")

    log.info("Scanning deals …")
    deal_rows = _stale_deals(client, stale_days, terminal_ids)

    log.info("Scanning contacts …")
    contact_rows = _stale_contacts(client, stale_days)

    deal_fields = ["record_id", "deal_name", "pipeline", "stage_id", "amount",
                   "close_date", "last_modified", "days_stale", "owner_id", "portal_url"]
    cp = writer.write_csv("stale_deals", deal_rows, deal_fields)
    log.info(f"Deals CSV → {cp.relative_to(Path(__file__).parent.parent)}")

    contact_fields = ["record_id", "name", "email", "lifecycle_stage",
                      "last_modified", "days_stale", "owner_id", "portal_url"]
    cp2 = writer.write_csv("stale_contacts", contact_rows, contact_fields)
    log.info(f"Contacts CSV → {cp2.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(deal_rows, contact_rows, stale_days, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("Stale active deals", len(deal_rows))
    log.result("Stale active contacts", len(contact_rows))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stale record resurfacer.")
    parser.add_argument("--days", type=int, default=DEFAULT_STALE_DAYS,
                        help=f"Stale threshold in days (default: {DEFAULT_STALE_DAYS}).")
    args = parser.parse_args()
    sys.exit(run(stale_days=args.days))
