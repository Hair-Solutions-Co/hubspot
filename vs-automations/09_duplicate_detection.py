#!/usr/bin/env python3
"""
09_duplicate_detection.py — Duplicate Detection & Merge Review Queue
====================================================================
Identifies likely duplicate contacts using two signals:

  1. Email duplicates       — two or more contacts share the exact same email.
  2. Name + Company match   — same normalized (first + last + company) combination.

Outputs a review queue CSV so you can evaluate and merge/reject each pair.
Does NOT auto-merge; safe to run at any time.

Output:
  outputs/duplicate-detection/<timestamp>/
    duplicates_by_email.csv     — confirmed email dupes
    duplicates_by_name.csv      — name+company matches (review required)
    summary.md

Usage:
  bash ./scripts/op_run.sh python3 automations/09_duplicate_detection.py
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.client import get_client, format_hs_date, iter_all_records
from lib.log import AutomationLogger
from lib.output import OutputWriter

AUTOMATION_NAME = "duplicate-detection"
log = AutomationLogger(AUTOMATION_NAME)

CONTACT_PROPERTIES = [
    "firstname", "lastname", "email", "phone",
    "company", "lifecyclestage", "hubspot_owner_id",
    "createdate",
]

# Max contacts to pull for name-based dedup (full email dedup is done via search).
# Set higher if your portal is large; each page is 100 records.
MAX_CONTACTS_FOR_NAME_DEDUP = 5000


def _normalize(s) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _portal_url(record_id: str) -> str:
    return f"https://app.hubspot.com/contacts/50966981/contact/{record_id}"


def _find_email_dupes(client) -> list[dict]:
    """
    For each contact that has an email, find others with the same email.
    Strategy: fetch all contacts with an email set, group by email.
    """
    log.info("Fetching contacts with email for email-dupe check …")
    from lib.client import simple_filter, filter_group
    fg = [filter_group(simple_filter("email", "HAS_PROPERTY"))]
    contacts = iter_all_records(client, "contacts", CONTACT_PROPERTIES, fg)
    log.info(f"  {len(contacts)} contacts with email address")

    by_email: dict[str, list[dict]] = defaultdict(list)
    for rec in contacts:
        email = _normalize(rec.get("properties", {}).get("email", ""))
        if email:
            by_email[email].append(rec)

    rows: list[dict] = []
    for email, group in sorted(by_email.items()):
        if len(group) < 2:
            continue
        # Emit one row per duplicate (all but the first are "duplicates").
        primary = group[0]
        pp = primary.get("properties", {})
        for dup in group[1:]:
            dp = dup.get("properties", {})
            rows.append({
                "email": email,
                "primary_id": primary.get("id", ""),
                "primary_name": f"{pp.get('firstname', '')} {pp.get('lastname', '')}".strip(),
                "primary_created": format_hs_date(pp.get("createdate")),
                "primary_lifecycle": pp.get("lifecyclestage", ""),
                "primary_url": _portal_url(primary.get("id", "")),
                "duplicate_id": dup.get("id", ""),
                "duplicate_name": f"{dp.get('firstname', '')} {dp.get('lastname', '')}".strip(),
                "duplicate_created": format_hs_date(dp.get("createdate")),
                "duplicate_lifecycle": dp.get("lifecyclestage", ""),
                "duplicate_url": _portal_url(dup.get("id", "")),
                "confidence": "HIGH",
            })

    log.info(f"  {len(rows)} email duplicate pair(s) found")
    return rows


def _find_name_company_dupes(client) -> list[dict]:
    """
    Fetch contacts and find cases where (normalized first + last + company)
    appears more than once. Excludes blank names.
    """
    log.info(f"Fetching up to {MAX_CONTACTS_FOR_NAME_DEDUP} contacts for name-based dupe check …")
    contacts = iter_all_records(client, "contacts", CONTACT_PROPERTIES, None, page_size=100)
    if len(contacts) > MAX_CONTACTS_FOR_NAME_DEDUP:
        log.warn(f"Portal has {len(contacts)} contacts — sampling first {MAX_CONTACTS_FOR_NAME_DEDUP}")
        contacts = contacts[:MAX_CONTACTS_FOR_NAME_DEDUP]

    by_key: dict[str, list[dict]] = defaultdict(list)
    for rec in contacts:
        p = rec.get("properties", {})
        first = _normalize(p.get("firstname", ""))
        last = _normalize(p.get("lastname", ""))
        company = _normalize(p.get("company", ""))
        if not first and not last:
            continue  # skip blank-name contacts
        key = f"{first}|{last}|{company}"
        by_key[key].append(rec)

    rows: list[dict] = []
    for key, group in sorted(by_key.items()):
        if len(group) < 2:
            continue
        first, last, company = key.split("|", 2)
        primary = group[0]
        pp = primary.get("properties", {})
        for dup in group[1:]:
            dp = dup.get("properties", {})
            rows.append({
                "match_key": key,
                "primary_id": primary.get("id", ""),
                "primary_email": pp.get("email", ""),
                "primary_created": format_hs_date(pp.get("createdate")),
                "primary_lifecycle": pp.get("lifecyclestage", ""),
                "primary_url": _portal_url(primary.get("id", "")),
                "duplicate_id": dup.get("id", ""),
                "duplicate_email": dp.get("email", ""),
                "duplicate_created": format_hs_date(dp.get("createdate")),
                "duplicate_lifecycle": dp.get("lifecyclestage", ""),
                "duplicate_url": _portal_url(dup.get("id", "")),
                "confidence": "MEDIUM",
            })

    log.info(f"  {len(rows)} name+company duplicate candidate(s) found")
    return rows


def _build_summary(email_rows: list[dict], name_rows: list[dict], run_date: str) -> str:
    lines = [
        f"# Duplicate Contact Review Queue — {run_date}",
        "",
        f"**Email duplicates (HIGH confidence):** {len(email_rows)} pair(s)",
        f"**Name+Company duplicates (MEDIUM confidence):** {len(name_rows)} pair(s)",
        "",
        "> Use HubSpot's native merge (Contacts → Actions → Merge) to resolve.",
        "> The primary contact (oldest) retains the record. Verify before merging.",
        "",
    ]

    if email_rows:
        lines += [
            "## Email Duplicates",
            "",
            "| Email | Primary | Duplicate | Primary Created | Dup Created |",
            "|-------|---------|-----------|-----------------|-------------|",
        ]
        for r in email_rows[:50]:
            lines.append(
                f"| {r['email']} | [{r['primary_name'] or r['primary_id']}]({r['primary_url']})"
                f" | [{r['duplicate_name'] or r['duplicate_id']}]({r['duplicate_url']})"
                f" | {r['primary_created']} | {r['duplicate_created']} |"
            )
        if len(email_rows) > 50:
            lines.append(f"_… and {len(email_rows) - 50} more (see CSV)_")
        lines.append("")

    if name_rows:
        lines += [
            "## Name + Company Matches (review required)",
            "",
            "| Match Key | Primary | Dup Email | Primary Email |",
            "|-----------|---------|-----------|---------------|",
        ]
        for r in name_rows[:50]:
            lines.append(
                f"| {r['match_key']} | [{r['primary_id']}]({r['primary_url']})"
                f" | {r['duplicate_email'] or '—'} | {r['primary_email'] or '—'} |"
            )

    return "\n".join(lines)


def run() -> int:
    log.section("Duplicate Detection & Merge Review Queue")
    client = get_client()
    writer = OutputWriter(AUTOMATION_NAME)

    email_rows = _find_email_dupes(client)
    name_rows = _find_name_company_dupes(client)

    email_fields = ["email", "primary_id", "primary_name", "primary_created", "primary_lifecycle",
                    "primary_url", "duplicate_id", "duplicate_name", "duplicate_created",
                    "duplicate_lifecycle", "duplicate_url", "confidence"]
    cp = writer.write_csv("duplicates_by_email", email_rows, email_fields)
    log.info(f"Email dupes CSV → {cp.relative_to(Path(__file__).parent.parent)}")

    name_fields = ["match_key", "primary_id", "primary_email", "primary_created", "primary_lifecycle",
                   "primary_url", "duplicate_id", "duplicate_email", "duplicate_created",
                   "duplicate_lifecycle", "duplicate_url", "confidence"]
    cp2 = writer.write_csv("duplicates_by_name", name_rows, name_fields)
    log.info(f"Name dupes CSV → {cp2.relative_to(Path(__file__).parent.parent)}")

    md = _build_summary(email_rows, name_rows, writer.date_str())
    md_path = writer.write_markdown("summary", md)
    log.info(f"Markdown → {md_path.relative_to(Path(__file__).parent.parent)}")

    log.section("Result")
    log.result("HIGH confidence email dupes", len(email_rows))
    log.result("MEDIUM confidence name dupes", len(name_rows))
    return 0


if __name__ == "__main__":
    sys.exit(run())
