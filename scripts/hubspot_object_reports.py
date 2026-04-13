#!/usr/bin/env python3
"""
HubSpot object snapshot and export utilities.

Provides three workflows:
- `snapshot`   -> summary CSV for records, associations, and custom property usage
- `exportcrm`  -> full record export CSV for an object
- `exportprop` -> full property definition export CSV for an object

All commands expect a HubSpot bearer token to be present in the process
environment. Run through `bash ./scripts/op_run.sh ...` so 1Password-backed
injection is applied.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

BASE_URL = "https://api.hubapi.com"
OBJECTS_API_VERSION = "2026-03"
ASSOCIATIONS_API_VERSION = "2026-03"
DEFAULT_OUTPUT_DIR = Path("10-crm/imports-exports/exports")
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
DEFAULT_PAGE_SIZE = 100
ASSOCIATION_BATCH_SIZE = 1000
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 1.0


@dataclass(frozen=True)
class ObjectDescriptor:
    object_type: str
    label: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    associated_objects: tuple[str, ...] = field(default_factory=tuple)


STANDARD_OBJECTS: tuple[ObjectDescriptor, ...] = (
    ObjectDescriptor("contacts", "Contacts", ("contact", "contacts", "person", "people")),
    ObjectDescriptor("companies", "Companies", ("company", "companies", "account", "accounts")),
    ObjectDescriptor("deals", "Deals", ("deal", "deals")),
    ObjectDescriptor("tickets", "Tickets", ("ticket", "tickets")),
    ObjectDescriptor("leads", "Leads", ("lead", "leads")),
    ObjectDescriptor("products", "Products", ("product", "products")),
    ObjectDescriptor("line_items", "Line Items", ("line item", "line items", "line_item", "line_items")),
    ObjectDescriptor("quotes", "Quotes", ("quote", "quotes")),
    ObjectDescriptor("orders", "Orders", ("order", "orders")),
    ObjectDescriptor("subscriptions", "Subscriptions", ("subscription", "subscriptions")),
    ObjectDescriptor("invoices", "Invoices", ("invoice", "invoices")),
    ObjectDescriptor("payments", "Payments", ("payment", "payments", "commerce payment", "commerce payments")),
    ObjectDescriptor("carts", "Carts", ("cart", "carts")),
    ObjectDescriptor("appointments", "Appointments", ("appointment", "appointments")),
    ObjectDescriptor("goals", "Goals", ("goal", "goals")),
    ObjectDescriptor(
        "feedback_submissions",
        "Feedback Submissions",
        ("feedback", "feedback submission", "feedback submissions", "feedback_submissions"),
    ),
    ObjectDescriptor("calls", "Calls", ("call", "calls")),
    ObjectDescriptor("emails", "Emails", ("email", "emails")),
    ObjectDescriptor("meetings", "Meetings", ("meeting", "meetings")),
    ObjectDescriptor("notes", "Notes", ("note", "notes")),
    ObjectDescriptor("tasks", "Tasks", ("task", "tasks")),
    ObjectDescriptor("communications", "Communications", ("communication", "communications", "sms", "whatsapp")),
    ObjectDescriptor("postal_mail", "Postal Mail", ("postal mail", "postal_mail")),
    ObjectDescriptor("users", "Users", ("user", "users")),
    ObjectDescriptor("marketing_events", "Marketing Events", ("marketing event", "marketing events", "marketing_events")),
)


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _dedupe(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return tuple(ordered)


def _safe_slug(value: str) -> str:
    slug = _normalize_key(value)
    return slug or "object"


def _timestamp_label(now: dt.datetime | None = None) -> str:
    current = now or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    else:
        current = current.astimezone(dt.timezone.utc)
    return current.strftime("%Y%m%dT%H%M%SZ")


def _descriptor_from_mapping(item: Any) -> ObjectDescriptor:
    if isinstance(item, ObjectDescriptor):
        return item
    if isinstance(item, dict):
        return ObjectDescriptor(
            object_type=item["object_type"],
            label=item.get("label", item["object_type"]),
            aliases=tuple(item.get("aliases", ())),
            associated_objects=tuple(item.get("associated_objects", ())),
        )
    raise TypeError(f"Unsupported descriptor payload: {item!r}")


def _unknown_descriptor(raw: str) -> ObjectDescriptor:
    trimmed = raw.strip()
    if re.fullmatch(r"\d+-\d+", trimmed) or "." in trimmed:
        object_type = trimmed
    else:
        object_type = _normalize_key(trimmed)
    label = trimmed.replace("_", " ").strip() or object_type
    return ObjectDescriptor(object_type=object_type, label=label.title())


def normalize_object_type(
    raw: str,
    custom_objects: Sequence[ObjectDescriptor | dict[str, Any]] | None = None,
) -> ObjectDescriptor:
    if not raw or not raw.strip():
        raise ValueError("object type cannot be empty")

    descriptors = list(STANDARD_OBJECTS)
    if custom_objects:
        descriptors.extend(_descriptor_from_mapping(item) for item in custom_objects)

    alias_map: dict[str, ObjectDescriptor] = {}
    for descriptor in descriptors:
        candidates = (descriptor.object_type, descriptor.label, *descriptor.aliases)
        for candidate in candidates:
            alias_map[_normalize_key(candidate)] = descriptor

    return alias_map.get(_normalize_key(raw), _unknown_descriptor(raw))


# Order: broad service PAT first, then ops private app, then other static app tokens.
_TOKEN_ENV_NAMES: tuple[str, ...] = (
    "HUBSPOT_SERVICE_KEY",
    "HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN",
    "HUBSPOT_APP__CRM_OBJECT_SYNC__STATIC_ACCESS_TOKEN",
    "HUBSPOT_APP__ASSOCIATIONS_SYNC__STATIC_ACCESS_TOKEN",
    "HUBSPOT_APP__PROPERTY_MAPPING__STATIC_ACCESS_TOKEN",
    "HUBSPOT_PRIVATE_APP__CRM_SCHEMA__ACCESS_TOKEN",
    "HUBSPOT_ACCESS_TOKEN",
)


def resolve_token_env_name() -> str:
    """First env var that supplies a token (for diagnostics). Does not print secret values."""
    for name in _TOKEN_ENV_NAMES:
        value = os.environ.get(name)
        if value and value.strip():
            return name
    message = (
        "ERROR: no HubSpot token found in env. Run through `bash ./scripts/op_run.sh ...` "
        "so 1Password-backed tokens are injected."
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)


def get_token() -> str:
    for name in _TOKEN_ENV_NAMES:
        value = os.environ.get(name)
        if value and value.strip():
            return value.strip()

    message = (
        "ERROR: no HubSpot token found in env. Run through `bash ./scripts/op_run.sh ...` "
        "so 1Password-backed tokens are injected."
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)


class HubSpotClient:
    def __init__(self, token: str, base_url: str = BASE_URL) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.ssl_context = ssl.create_default_context()

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        encoded_params = urllib.parse.urlencode(params or {}, doseq=True)
        url = f"{self.base_url}{path}"
        if encoded_params:
            url = f"{url}?{encoded_params}"

        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        backoff = INITIAL_BACKOFF_SECONDS
        for attempt in range(1, MAX_RETRIES + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
            try:
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=60) as resp:
                    raw = resp.read()
                    if not raw:
                        return {}
                    return json.loads(raw)
            except urllib.error.HTTPError as exc:
                body_text = exc.read().decode("utf-8", errors="replace")
                if exc.code in RETRY_STATUS_CODES and attempt < MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise RuntimeError(f"{method.upper()} {path} -> {exc.code}: {body_text}") from exc
            except OSError as exc:
                if attempt < MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise RuntimeError(f"{method.upper()} {path} failed: {exc}") from exc

        raise RuntimeError(f"{method.upper()} {path} exceeded retry budget")

    def search_records(
        self,
        object_type: str,
        *,
        properties: Sequence[str] | None = None,
        after: str | None = None,
        filter_groups: Sequence[dict[str, Any]] | None = None,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"limit": limit}
        if properties is not None:
            body["properties"] = list(properties)
        if filter_groups:
            body["filterGroups"] = list(filter_groups)
        if after:
            body["after"] = after
        return self.request_json("POST", f"/crm/objects/{OBJECTS_API_VERSION}/{object_type}/search", body=body)

    def count_records(self, object_type: str) -> int:
        response = self.search_records(object_type, properties=(), limit=1)
        return int(response.get("total", 0))

    def iter_record_ids(self, object_type: str) -> Iterator[str]:
        after: str | None = None
        while True:
            response = self.search_records(object_type, properties=(), after=after)
            for result in response.get("results", []):
                record_id = result.get("id")
                if record_id:
                    yield str(record_id)
            after = response.get("paging", {}).get("next", {}).get("after")
            if not after:
                return

    def iter_records(self, object_type: str, property_names: Sequence[str]) -> Iterator[dict[str, Any]]:
        after: str | None = None
        requested = list(property_names)
        while True:
            response = self.search_records(object_type, properties=requested, after=after)
            for result in response.get("results", []):
                yield result
            after = response.get("paging", {}).get("next", {}).get("after")
            if not after:
                return

    def get_properties(self, object_type: str) -> list[dict[str, Any]]:
        after: str | None = None
        results: list[dict[str, Any]] = []
        while True:
            params: dict[str, Any] = {"limit": 500}
            if after:
                params["after"] = after
            response = self.request_json("GET", f"/crm/v3/properties/{object_type}", params=params)
            results.extend(response.get("results", []))
            after = response.get("paging", {}).get("next", {}).get("after")
            if not after:
                return results

    def list_custom_objects(self) -> list[ObjectDescriptor]:
        try:
            response = self.request_json("GET", "/crm/v3/schemas")
        except RuntimeError:
            return []

        results: list[ObjectDescriptor] = []
        for item in response.get("results", []):
            labels = item.get("labels", {}) or {}
            label = labels.get("plural") or labels.get("singular") or item.get("name") or item.get("objectTypeId")
            object_type = item.get("objectTypeId") or item.get("fullyQualifiedName") or item.get("name")
            if not object_type:
                continue
            associated_objects = tuple(
                normalize_object_type(str(value)).object_type
                for value in item.get("associatedObjects", []) or []
            )
            aliases = _dedupe(
                (
                    str(object_type),
                    str(item.get("fullyQualifiedName", "")),
                    str(item.get("name", "")),
                    str(labels.get("singular", "")),
                    str(labels.get("plural", "")),
                )
            )
            results.append(
                ObjectDescriptor(
                    object_type=str(object_type),
                    label=str(label),
                    aliases=aliases,
                    associated_objects=associated_objects,
                )
            )
        return results

    def get_association_labels(self, from_object_type: str, to_object_type: str) -> list[dict[str, Any]]:
        try:
            response = self.request_json(
                "GET",
                f"/crm/associations/{ASSOCIATIONS_API_VERSION}/{from_object_type}/{to_object_type}/labels",
            )
        except RuntimeError:
            return []
        return response.get("results", [])

    def discover_association_targets(
        self,
        object_type: str,
        custom_objects: Sequence[ObjectDescriptor | dict[str, Any]] | None = None,
    ) -> list[ObjectDescriptor]:
        source = normalize_object_type(object_type, custom_objects)
        custom_descriptors = [_descriptor_from_mapping(item) for item in (custom_objects or ())]
        candidates: list[ObjectDescriptor] = list(STANDARD_OBJECTS) + custom_descriptors

        if source.associated_objects:
            allowed = set(source.associated_objects)
            candidates = [item for item in candidates if item.object_type in allowed or item.object_type == source.object_type]

        seen: set[str] = set()
        discovered: list[ObjectDescriptor] = []
        for candidate in candidates:
            if candidate.object_type in seen:
                continue
            seen.add(candidate.object_type)
            labels = self.get_association_labels(source.object_type, candidate.object_type)
            if labels:
                discovered.append(candidate)
        discovered.sort(key=lambda item: item.label.lower())
        return discovered

    def get_record_ids_with_associations(
        self,
        from_object_type: str,
        to_object_type: str,
        record_ids: Sequence[str] | Iterable[str],
    ) -> set[str]:
        ids = [str(record_id) for record_id in record_ids]
        if not ids:
            return set()

        associated: set[str] = set()
        for offset in range(0, len(ids), ASSOCIATION_BATCH_SIZE):
            chunk = ids[offset : offset + ASSOCIATION_BATCH_SIZE]
            body = {"inputs": [{"id": record_id} for record_id in chunk]}
            try:
                response = self.request_json(
                    "POST",
                    f"/crm/associations/{ASSOCIATIONS_API_VERSION}/{from_object_type}/{to_object_type}/batch/read",
                    body=body,
                )
            except RuntimeError:
                return set()

            for result in response.get("results", []):
                if result.get("to"):
                    from_id = result.get("from", {}).get("id")
                    if from_id:
                        associated.add(str(from_id))
        return associated

    def count_property_usage(self, object_type: str, property_names: Sequence[str]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for property_name in property_names:
            filters = [{"filters": [{"propertyName": property_name, "operator": "HAS_PROPERTY"}]}]
            response = self.search_records(object_type, properties=(), filter_groups=filters, limit=1)
            counts[property_name] = int(response.get("total", 0))
        return counts


def _summary_row(
    descriptor: ObjectDescriptor,
    metric_name: str,
    value: int,
    *,
    notes: str = "",
) -> dict[str, str]:
    return {
        "row_type": "summary",
        "object_type": descriptor.object_type,
        "object_label": descriptor.label,
        "metric_name": metric_name,
        "related_object_type": "",
        "related_object_label": "",
        "value": str(value),
        "notes": notes,
    }


def _association_rows(
    descriptor: ObjectDescriptor,
    target: ObjectDescriptor,
    with_count: int,
    without_count: int,
) -> list[dict[str, str]]:
    return [
        {
            "row_type": "association",
            "object_type": descriptor.object_type,
            "object_label": descriptor.label,
            "metric_name": "records_with_relationship",
            "related_object_type": target.object_type,
            "related_object_label": target.label,
            "value": str(with_count),
            "notes": "",
        },
        {
            "row_type": "association",
            "object_type": descriptor.object_type,
            "object_label": descriptor.label,
            "metric_name": "records_without_relationship",
            "related_object_type": target.object_type,
            "related_object_label": target.label,
            "value": str(without_count),
            "notes": "",
        },
    ]


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def create_snapshot_report(
    object_input: str,
    *,
    client: HubSpotClient | Any | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    now: dt.datetime | None = None,
) -> Path:
    hubspot = client or HubSpotClient(get_token())
    custom_objects = [_descriptor_from_mapping(item) for item in hubspot.list_custom_objects()]
    descriptor = normalize_object_type(object_input, custom_objects)

    record_count = hubspot.count_records(descriptor.object_type)
    record_ids = list(hubspot.iter_record_ids(descriptor.object_type))

    properties = [item for item in hubspot.get_properties(descriptor.object_type) if not item.get("archived", False)]
    custom_properties = [item for item in properties if not bool(item.get("hubspotDefined", False))]
    property_names = [item["name"] for item in custom_properties]
    usage_counts = hubspot.count_property_usage(descriptor.object_type, property_names) if property_names else {}
    custom_used_count = sum(1 for value in usage_counts.values() if value > 0)
    custom_unused_count = len(custom_properties) - custom_used_count

    targets = [_descriptor_from_mapping(item) for item in hubspot.discover_association_targets(descriptor.object_type, custom_objects)]
    any_relationship_ids: set[str] = set()
    association_rows: list[dict[str, str]] = []
    for target in targets:
        related_ids = set(hubspot.get_record_ids_with_associations(descriptor.object_type, target.object_type, record_ids))
        any_relationship_ids.update(related_ids)
        with_count = len(related_ids)
        without_count = max(record_count - with_count, 0)
        association_rows.extend(_association_rows(descriptor, target, with_count, without_count))

    summary_rows = [
        _summary_row(descriptor, "record_count", record_count, notes="Non-archived records only"),
        _summary_row(descriptor, "records_with_any_relationship", len(any_relationship_ids)),
        _summary_row(descriptor, "records_without_any_relationship", max(record_count - len(any_relationship_ids), 0)),
        _summary_row(descriptor, "custom_property_count", len(custom_properties)),
        _summary_row(
            descriptor,
            "custom_property_used_count",
            custom_used_count,
            notes="Used means at least one non-archived record has a value",
        ),
        _summary_row(
            descriptor,
            "custom_property_unused_count",
            custom_unused_count,
            notes="Unused means zero non-archived records currently have a value",
        ),
    ]

    timestamp = _timestamp_label(now)
    output_path = Path(output_dir) / f"{_safe_slug(descriptor.object_type)}_snapshot_{timestamp}.csv"
    fieldnames = (
        "row_type",
        "object_type",
        "object_label",
        "metric_name",
        "related_object_type",
        "related_object_label",
        "value",
        "notes",
    )
    return _write_csv(output_path, [*summary_rows, *association_rows], fieldnames)


def create_property_export(
    object_input: str,
    *,
    client: HubSpotClient | Any | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    now: dt.datetime | None = None,
) -> Path:
    hubspot = client or HubSpotClient(get_token())
    custom_objects = [_descriptor_from_mapping(item) for item in hubspot.list_custom_objects()]
    descriptor = normalize_object_type(object_input, custom_objects)

    properties = [item for item in hubspot.get_properties(descriptor.object_type) if not item.get("archived", False)]
    usage_counts = hubspot.count_property_usage(descriptor.object_type, [item["name"] for item in properties]) if properties else {}

    rows: list[dict[str, Any]] = []
    for item in properties:
        name = item["name"]
        populated_record_count = int(usage_counts.get(name, 0))
        rows.append(
            {
                "object_type": descriptor.object_type,
                "object_label": descriptor.label,
                "property_name": name,
                "property_label": item.get("label", name),
                "property_group": item.get("groupName", ""),
                "property_type": item.get("type", ""),
                "field_type": item.get("fieldType", ""),
                "is_custom": str(not bool(item.get("hubspotDefined", False))).lower(),
                "used_in_records": str(populated_record_count > 0).lower(),
                "populated_record_count": str(populated_record_count),
                "form_field": str(bool(item.get("formField", False))).lower(),
                "hidden": str(bool(item.get("hidden", False))).lower(),
                "archived": str(bool(item.get("archived", False))).lower(),
            }
        )

    timestamp = _timestamp_label(now)
    output_path = Path(output_dir) / f"{_safe_slug(descriptor.object_type)}_properties_{timestamp}.csv"
    fieldnames = (
        "object_type",
        "object_label",
        "property_name",
        "property_label",
        "property_group",
        "property_type",
        "field_type",
        "is_custom",
        "used_in_records",
        "populated_record_count",
        "form_field",
        "hidden",
        "archived",
    )
    return _write_csv(output_path, rows, fieldnames)


def create_crm_export(
    object_input: str,
    *,
    client: HubSpotClient | Any | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    now: dt.datetime | None = None,
) -> Path:
    hubspot = client or HubSpotClient(get_token())
    custom_objects = [_descriptor_from_mapping(item) for item in hubspot.list_custom_objects()]
    descriptor = normalize_object_type(object_input, custom_objects)

    properties = [item for item in hubspot.get_properties(descriptor.object_type) if not item.get("archived", False)]
    property_names = [item["name"] for item in properties]

    rows: list[dict[str, Any]] = []
    for record in hubspot.iter_records(descriptor.object_type, property_names):
        record_properties = record.get("properties", {}) or {}
        row: dict[str, Any] = {"record_id": str(record.get("id", ""))}
        for property_name in property_names:
            row[property_name] = record_properties.get(property_name, "")
        rows.append(row)

    timestamp = _timestamp_label(now)
    output_path = Path(output_dir) / f"{_safe_slug(descriptor.object_type)}_records_{timestamp}.csv"
    fieldnames = ("record_id", *property_names)
    return _write_csv(output_path, rows, fieldnames)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HubSpot object snapshot and export workflows.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where CSV files will be written.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot = subparsers.add_parser("snapshot", help="Create a snapshot CSV for an object.")
    snapshot.add_argument("object", help="HubSpot object type, e.g. contacts or companies.")

    exportcrm = subparsers.add_parser("exportcrm", help="Export CRM records for an object to CSV.")
    exportcrm.add_argument("object", help="HubSpot object type, e.g. contacts or orders.")

    exportprop = subparsers.add_parser("exportprop", help="Export object properties to CSV.")
    exportprop.add_argument("object", help="HubSpot object type, e.g. contacts or orders.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = HubSpotClient(get_token())
    output_dir = Path(args.output_dir)

    if args.command == "snapshot":
        output_path = create_snapshot_report(args.object, client=client, output_dir=output_dir)
    elif args.command == "exportcrm":
        output_path = create_crm_export(args.object, client=client, output_dir=output_dir)
    elif args.command == "exportprop":
        output_path = create_property_export(args.object, client=client, output_dir=output_dir)
    else:
        parser.error(f"Unsupported command: {args.command}")
        return 2

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
