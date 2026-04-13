"""
automations/lib/client.py
=========================
Thin wrapper that re-exports the shared HubSpotClient from scripts/ and adds
automation-specific helpers (date ranges, filter builders, pagination, etc.).

Usage inside an automation:
    from lib.client import get_client, epoch_ms_ago, days_ago_ms, filter_group
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from typing import Any, Sequence

# Make scripts/ importable so we can reuse the battle-tested HubSpotClient.
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from hubspot_object_reports import HubSpotClient, get_token, STANDARD_OBJECTS, ObjectDescriptor  # noqa: E402

__all__ = [
    "HubSpotClient",
    "ObjectDescriptor",
    "STANDARD_OBJECTS",
    "get_client",
    "get_token",
    "epoch_ms_ago",
    "days_ago_ms",
    "now_epoch_ms",
    "filter_group",
    "simple_filter",
    "AUTOMATION_OBJECTS",
]

# ---------------------------------------------------------------------------
# Standard objects that most automations care about.
# Custom objects are discovered at runtime via client.list_custom_objects().
# ---------------------------------------------------------------------------
AUTOMATION_OBJECTS = [
    "contacts",
    "companies",
    "deals",
    "tickets",
]


def get_client() -> HubSpotClient:
    """Return a HubSpotClient using the token from environment (via op_run.sh)."""
    return HubSpotClient(get_token())


# ---------------------------------------------------------------------------
# Date helpers (HubSpot search filters use epoch milliseconds)
# ---------------------------------------------------------------------------

def now_epoch_ms() -> int:
    return int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)


def epoch_ms_ago(*, days: int = 0, hours: int = 0) -> int:
    """Return epoch-ms for `days` days and `hours` hours ago."""
    delta = dt.timedelta(days=days, hours=hours)
    past = dt.datetime.now(dt.timezone.utc) - delta
    return int(past.timestamp() * 1000)


def days_ago_ms(n: int) -> int:
    """Shorthand: epoch milliseconds for exactly n days ago."""
    return epoch_ms_ago(days=n)


def format_hs_date(epoch_ms: int | str | None) -> str:
    """Convert a HubSpot epoch-ms timestamp string to a human-readable date."""
    if epoch_ms is None or epoch_ms == "":
        return ""
    try:
        ts_ms = int(epoch_ms)
        return dt.datetime.fromtimestamp(ts_ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return str(epoch_ms)


def days_since(epoch_ms: int | str | None) -> int | None:
    """Return number of days since the given epoch-ms timestamp, or None if missing."""
    if epoch_ms is None or epoch_ms == "":
        return None
    try:
        ts_s = int(epoch_ms) / 1000
        past = dt.datetime.fromtimestamp(ts_s, tz=dt.timezone.utc)
        now = dt.datetime.now(dt.timezone.utc)
        return max(0, (now - past).days)
    except (ValueError, OSError):
        return None


# ---------------------------------------------------------------------------
# Search filter builders
# ---------------------------------------------------------------------------

def simple_filter(property_name: str, operator: str, value: Any = None) -> dict[str, Any]:
    """Build a single CRM search filter dict."""
    f: dict[str, Any] = {"propertyName": property_name, "operator": operator}
    if value is not None:
        f["value"] = str(value)
    return f


def filter_group(*filters: dict[str, Any]) -> dict[str, Any]:
    """Wrap one or more filter dicts into a filterGroup (AND)."""
    return {"filters": list(filters)}


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def iter_all_records(
    client: HubSpotClient,
    object_type: str,
    properties: Sequence[str],
    filter_groups: list[dict[str, Any]] | None = None,
    *,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """Fetch ALL matching records, handling cursor-based pagination automatically."""
    all_records: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        resp = client.search_records(
            object_type,
            properties=list(properties),
            filter_groups=filter_groups or [],
            after=after,
            limit=page_size,
        )
        all_records.extend(resp.get("results", []))
        after = resp.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
    return all_records


def count_filtered(
    client: HubSpotClient,
    object_type: str,
    filter_groups: list[dict[str, Any]],
) -> int:
    """Return the total count for a filtered search without fetching records."""
    resp = client.search_records(object_type, properties=[], filter_groups=filter_groups, limit=1)
    return int(resp.get("total", 0))
