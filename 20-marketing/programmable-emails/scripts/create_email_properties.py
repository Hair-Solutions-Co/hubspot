#!/usr/bin/env python3
"""
create_email_properties.py
Phase 1 — Email System Property Layer

Creates the 41 CRM properties required by the programmable email system.
Based on: audit-report.md (2026-04-07)

Auth: Uses HUBSPOT_PRIVATE_APP__CRM_SCHEMA__ACCESS_TOKEN from env.
      Falls back to HUBSPOT_SERVICE_KEY if the schema token is not set.

Run:
  python3 scripts/create_email_properties.py

Flags:
  --dry-run       Print what would be created without making any API calls.
  --object TYPE   Only process one object type: contact | deal | ticket
  --skip-existing Skip properties that already exist (default: True)
  --force         Re-attempt creation even if the property already exists.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from typing import Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://api.hubapi.com"
PROPERTY_GROUP_LABEL = "Email System Properties"
PROPERTY_GROUP_NAME  = "email_system_properties"

RATE_LIMIT_DELAY = 0.25  # seconds between API calls (4 req/s, well under 10/s limit)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def hs_get(path: str, token: str) -> Optional[dict]:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def hs_post(path: str, body: dict, token: str) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(f"POST {path} → {e.code}: {body_text}") from e


# ---------------------------------------------------------------------------
# Property group helpers
# ---------------------------------------------------------------------------

def ensure_group(object_type: str, token: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [dry-run] Would ensure property group '{PROPERTY_GROUP_NAME}' on {object_type}")
        return

    path = f"/crm/v3/properties/{object_type}/groups/{PROPERTY_GROUP_NAME}"
    existing = hs_get(path, token)
    if existing:
        print(f"  [group] '{PROPERTY_GROUP_NAME}' already exists on {object_type}")
        return
    hs_post(
        f"/crm/v3/properties/{object_type}/groups",
        {"name": PROPERTY_GROUP_NAME, "label": PROPERTY_GROUP_LABEL, "displayOrder": 99},
        token,
    )
    print(f"  [group] Created '{PROPERTY_GROUP_NAME}' on {object_type}")
    time.sleep(RATE_LIMIT_DELAY)


def property_exists(object_type: str, name: str, token: str) -> bool:
    result = hs_get(f"/crm/v3/properties/{object_type}/{name}", token)
    return result is not None


# ---------------------------------------------------------------------------
# Property definitions — sourced from audit-report.md
# ---------------------------------------------------------------------------

# Helper: enumeration options list → HubSpot options format
def opts(*values: str) -> list:
    options = []
    for i, value in enumerate(values):
        label = value.replace("_", " ")
        if not label.isupper():
            label = label.title()
        options.append({"label": label, "value": value, "displayOrder": i, "hidden": False})
    return options


CONTACT_PROPERTIES = [
    # ── Priority 1: Order / Reorder summary ─────────────────────────────────
    {
        "name": "hsc_reorder_window_open",
        "label": "HSC Reorder Window Open",
        "type": "bool",
        "fieldType": "booleancheckbox",
        "description": "True when contact is within their reorder window. Used for J4 workflow enrollment.",
    },
    {
        "name": "hsc_reorder_message_angle",
        "label": "HSC Reorder Message Angle",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Which reorder messaging variant to use in J4-E2.",
        "options": opts("refresh", "upgrade", "loyalty", "default"),
    },
    {
        "name": "hsc_total_orders_last_12m",
        "label": "HSC Total Orders Last 12m",
        "type": "number",
        "fieldType": "number",
        "description": "Rolling 12-month order count. Used for J5/J6 eligibility.",
    },
    {
        "name": "hsc_total_orders_lifetime",
        "label": "HSC Total Orders Lifetime",
        "type": "number",
        "fieldType": "number",
        "description": "Lifetime order count. Used for J5 elite routing.",
    },
    {
        "name": "hsc_last_order_value",
        "label": "HSC Last Order Value",
        "type": "number",
        "fieldType": "number",
        "description": "Last order total in USD. Used in commercial summary emails.",
    },
    {
        "name": "hsc_current_system_user",
        "label": "HSC Current System User",
        "type": "bool",
        "fieldType": "booleancheckbox",
        "description": "True if contact already wears a hair system.",
    },
    {
        "name": "hsc_has_local_partner",
        "label": "HSC Has Local Partner",
        "type": "bool",
        "fieldType": "booleancheckbox",
        "description": "True if a nearby affiliated stylist/location exists for this contact.",
    },
    {
        "name": "hsc_nearest_partner_location",
        "label": "HSC Nearest Partner Location",
        "type": "string",
        "fieldType": "text",
        "description": "Name/city of the nearest affiliated stylist or salon location.",
    },
    # ── Priority 2: Subscription mirror ─────────────────────────────────────
    {
        "name": "hsc_subscription_status",
        "label": "HSC Subscription Status",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Mirror of Shopify subscription status. Drives J6, J8, and dunning flows.",
        "options": opts("active", "paused", "unpaid", "expired", "cancelled", "none"),
    },
    {
        "name": "hsc_subscription_eligible",
        "label": "HSC Subscription Eligible",
        "type": "bool",
        "fieldType": "booleancheckbox",
        "description": "True when contact meets the criteria for a subscription plan offer (3+ orders in 12m, no active plan).",
    },
    {
        "name": "hsc_subscription_renewal_date",
        "label": "HSC Subscription Renewal Date",
        "type": "date",
        "fieldType": "date",
        "description": "Next subscription renewal date. Triggers J8 renewal sequence at -30 days.",
    },
    {
        "name": "hsc_subscription_plan_name",
        "label": "HSC Subscription Plan Name",
        "type": "string",
        "fieldType": "text",
        "description": "Human-readable plan tier label, e.g. '3-Unit Plan' or '6-Unit Plan'.",
    },
    {
        "name": "hsc_subscription_plan_amount",
        "label": "HSC Subscription Plan Amount",
        "type": "number",
        "fieldType": "number",
        "description": "Recurring plan amount in USD.",
    },
    {
        "name": "hsc_subscription_deliveries_last_12m",
        "label": "HSC Subscription Deliveries Last 12m",
        "type": "number",
        "fieldType": "number",
        "description": "Number of units delivered under the subscription in the trailing 12 months.",
    },
    {
        "name": "hsc_subscription_payment_link",
        "label": "HSC Subscription Payment Link",
        "type": "string",
        "fieldType": "text",
        "description": "Self-service payment update URL. Used in dunning emails.",
    },
    {
        "name": "hsc_subscription_last4",
        "label": "HSC Subscription Last 4",
        "type": "string",
        "fieldType": "text",
        "description": "Last 4 digits of the payment method on file. Used in dunning emails.",
    },
    # ── Priority 2: Commercial summary ──────────────────────────────────────
    {
        "name": "hsc_estimated_annual_spend_individual",
        "label": "HSC Estimated Annual Spend (Individual)",
        "type": "number",
        "fieldType": "number",
        "description": "Projected annual cost if contact continues buying individually (12m extrapolation).",
    },
    {
        "name": "hsc_estimated_annual_spend_plan",
        "label": "HSC Estimated Annual Spend (Plan)",
        "type": "number",
        "fieldType": "number",
        "description": "Projected annual cost if contact moved to a subscription plan.",
    },
    {
        "name": "hsc_estimated_plan_savings",
        "label": "HSC Estimated Plan Savings",
        "type": "number",
        "fieldType": "number",
        "description": "Individual annual spend minus plan annual cost. Used in J6-E2 Math of Value email.",
    },
    {
        "name": "hsc_customer_milestone_summary",
        "label": "HSC Customer Milestone Summary",
        "type": "string",
        "fieldType": "textarea",
        "description": "Pre-rendered milestone text for J5-E1 and J8-E1 annual recap emails.",
    },
    {
        "name": "hsc_anniversary_type",
        "label": "HSC Anniversary Type",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Which anniversary event triggers the J5-E3 birthday/anniversary email.",
        "options": opts("first_purchase", "fitting", "birthday"),
    },
    {
        "name": "hsc_vip_reward_choice",
        "label": "HSC VIP Reward Choice",
        "type": "string",
        "fieldType": "text",
        "description": "VIP reward selected by the contact in J5-E3.",
    },
    {
        "name": "hsc_specs_locked",
        "label": "HSC Specs Locked",
        "type": "bool",
        "fieldType": "booleancheckbox",
        "description": "True when hair system specs are finalized on the contact record.",
    },
    {
        "name": "hsc_last_spec_summary",
        "label": "HSC Last Spec Summary",
        "type": "string",
        "fieldType": "textarea",
        "description": "Human-readable spec snapshot (base type, density, hair type). Used in reorder and consultation emails.",
    },
]

DEAL_PROPERTIES = [
    {
        "name": "hsc_recommended_path",
        "label": "HSC Recommended Path",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Consultation recommended path. Drives consultation recap email variant selection.",
        "options": opts("standard", "remote_fitting", "salon_partner"),
    },
    {
        "name": "hsc_quote_currency",
        "label": "HSC Quote Currency",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Currency used in the quoted price. Drives currency display in consultation recap emails.",
        "options": opts("USD", "CAD", "EUR", "GBP"),
    },
    {
        "name": "hsc_quote_base_price",
        "label": "HSC Quote Base Price",
        "type": "number",
        "fieldType": "number",
        "description": "Quoted unit price in customer currency.",
    },
    {
        "name": "hsc_quote_shipping_price",
        "label": "HSC Quote Shipping Price",
        "type": "number",
        "fieldType": "number",
        "description": "Shipping cost in customer currency.",
    },
    {
        "name": "hsc_quote_template_shipping_price",
        "label": "HSC Quote Template Shipping Price",
        "type": "number",
        "fieldType": "number",
        "description": "Template kit shipping cost if applicable.",
    },
    {
        "name": "hsc_quote_down_payment",
        "label": "HSC Quote Down Payment",
        "type": "number",
        "fieldType": "number",
        "description": "Down payment amount for this quote.",
    },
    {
        "name": "hsc_quote_consultation_fee",
        "label": "HSC Quote Consultation Fee",
        "type": "number",
        "fieldType": "number",
        "description": "Consultation fee, if applicable.",
    },
    {
        "name": "hsc_quote_fitting_fee_estimate",
        "label": "HSC Quote Fitting Fee Estimate",
        "type": "number",
        "fieldType": "number",
        "description": "Estimated fitting service fee.",
    },
    {
        "name": "hsc_quote_maintenance_fee_estimate",
        "label": "HSC Quote Maintenance Fee Estimate",
        "type": "number",
        "fieldType": "number",
        "description": "Estimated ongoing maintenance service fee.",
    },
    {
        "name": "hsc_quote_base_type",
        "label": "HSC Quote Base Type",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Base material quoted. Used in consultation recap and care instruction emails.",
        "options": opts("nano_skin", "micro_skin", "thin_skin", "dura_skin", "swiss_lace", "french_lace", "mono", "hybrid"),
    },
    {
        "name": "hsc_quote_density_percent",
        "label": "HSC Quote Density %",
        "type": "number",
        "fieldType": "number",
        "description": "Quoted density percentage (e.g. 80, 100, 120).",
    },
    {
        "name": "hsc_quote_hair_type",
        "label": "HSC Quote Hair Type",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Hair type used in the quoted system.",
        "options": opts("remy", "virgin", "synthetic", "blend"),
    },
    {
        "name": "hsc_quote_plan_3_monthly_price",
        "label": "HSC Quote Plan 3 Monthly Price",
        "type": "number",
        "fieldType": "number",
        "description": "Monthly price for the 3-unit plan, in customer currency.",
    },
    {
        "name": "hsc_quote_plan_4_monthly_price",
        "label": "HSC Quote Plan 4 Monthly Price",
        "type": "number",
        "fieldType": "number",
        "description": "Monthly price for the 4-unit plan, in customer currency.",
    },
    {
        "name": "hsc_quote_plan_6_monthly_price",
        "label": "HSC Quote Plan 6 Monthly Price",
        "type": "number",
        "fieldType": "number",
        "description": "Monthly price for the 6-unit plan, in customer currency.",
    },
]

TICKET_PROPERTIES = [
    {
        "name": "hsc_consultation_completed_at",
        "label": "HSC Consultation Completed At",
        "type": "datetime",
        "fieldType": "date",
        "description": "Timestamp of consultation completion. Triggers the consultation recap email send.",
    },
    {
        "name": "hsc_consultation_variant",
        "label": "HSC Consultation Variant",
        "type": "enumeration",
        "fieldType": "select",
        "description": "Which consultation recap template variant to send.",
        "options": opts("standard", "no_local_partner", "current_system_user", "front_partial"),
    },
]

PROPERTY_SETS = {
    "contacts": CONTACT_PROPERTIES,
    "deals":    DEAL_PROPERTIES,
    "tickets":  TICKET_PROPERTIES,
}

SKIP_PROPERTIES = {
    # Use native HubSpot properties instead — per audit-report.md Section 1.2
    "contacts": {
        "hsc_last_order_date",       # → hs_recent_closed_order_date
        "hsc_predicted_reorder_date", # → next_expected_reorder_date
        "hsc_preferred_language",    # → hs_language
    }
}


# ---------------------------------------------------------------------------
# Core creation logic
# ---------------------------------------------------------------------------

def build_payload(prop: dict, object_type: str) -> dict:
    payload = {
        "name":        prop["name"],
        "label":       prop["label"],
        "type":        prop["type"],
        "fieldType":   prop["fieldType"],
        "groupName":   PROPERTY_GROUP_NAME,
        "description": prop.get("description", ""),
    }
    if prop.get("options"):
        payload["options"] = prop["options"]
    return payload


def process_object(object_type: str, props: list, token: str, dry_run: bool,
                   skip_existing: bool, force: bool) -> dict:
    results = {"created": 0, "skipped": 0, "failed": 0, "errors": []}
    skipped_names = SKIP_PROPERTIES.get(object_type, set())

    print(f"\n── {object_type.upper()} ({len(props)} properties) ──────────────────────────")
    ensure_group(object_type, token, dry_run)

    for prop in props:
        name = prop["name"]

        if name in skipped_names:
            print(f"  [skip-native] {name}")
            results["skipped"] += 1
            continue

        if skip_existing and not force:
            exists = False if dry_run else property_exists(object_type, name, token)
            if exists:
                print(f"  [exists] {name}")
                results["skipped"] += 1
                time.sleep(RATE_LIMIT_DELAY)
                continue

        if dry_run:
            print(f"  [dry-run] Would create: {name} ({prop['type']})")
            results["created"] += 1
            continue

        try:
            payload = build_payload(prop, object_type)
            hs_post(f"/crm/v3/properties/{object_type}", payload, token)
            print(f"  [created] {name}")
            results["created"] += 1
        except RuntimeError as e:
            err_str = str(e)
            if "PROPERTY_EXISTS" in err_str or "already exists" in err_str.lower():
                print(f"  [exists]  {name}")
                results["skipped"] += 1
            else:
                print(f"  [FAILED]  {name}: {err_str[:120]}")
                results["failed"] += 1
                results["errors"].append({"property": name, "error": err_str})

        time.sleep(RATE_LIMIT_DELAY)

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Create email system CRM properties in HubSpot.")
    parser.add_argument("--dry-run",      action="store_true", help="Print actions without calling the API.")
    parser.add_argument("--object",       choices=["contact", "deal", "ticket"], help="Only process one object type.")
    parser.add_argument(
        "--skip-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip already-existing properties (default: on). Use --no-skip-existing to disable.",
    )
    parser.add_argument("--force",        action="store_true", help="Attempt creation even if property already exists.")
    args = parser.parse_args()

    token = get_token() if not args.dry_run else ""

    if args.dry_run:
        print("── DRY RUN — no API calls will be made ──────────────────────────────────")

    target_sets = {}
    if args.object:
        key = args.object + ("s" if not args.object.endswith("s") else "")
        target_sets = {key: PROPERTY_SETS[key]}
    else:
        target_sets = PROPERTY_SETS

    totals = {"created": 0, "skipped": 0, "failed": 0, "errors": []}
    for object_type, props in target_sets.items():
        r = process_object(object_type, props, token, args.dry_run, args.skip_existing, args.force)
        totals["created"] += r["created"]
        totals["skipped"] += r["skipped"]
        totals["failed"]  += r["failed"]
        totals["errors"]  += r["errors"]

    print(f"""
══ SUMMARY ═══════════════════════════════════════════════════════════════════
  Created : {totals["created"]}
  Skipped : {totals["skipped"]}  (already existed or native substitute)
  Failed  : {totals["failed"]}
══════════════════════════════════════════════════════════════════════════════""")

    if totals["errors"]:
        print("\nFailed properties:")
        for e in totals["errors"]:
            print(f"  {e['property']}: {e['error'][:100]}")
        sys.exit(1)

    if not args.dry_run:
        print("\nRun `search_properties` on each object in HubSpot to verify.")


if __name__ == "__main__":
    main()
