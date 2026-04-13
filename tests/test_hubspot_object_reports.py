import csv
import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import hubspot_object_reports as subject  # noqa: E402


class FakeClient:
    def __init__(self) -> None:
        self.custom_objects = []
        self.properties = {
            "contacts": [
                {
                    "name": "firstname",
                    "label": "First name",
                    "type": "string",
                    "fieldType": "text",
                    "groupName": "contactinformation",
                    "hubspotDefined": True,
                    "archived": False,
                },
                {
                    "name": "favorite_color",
                    "label": "Favorite Color",
                    "type": "string",
                    "fieldType": "text",
                    "groupName": "custom",
                    "hubspotDefined": False,
                    "archived": False,
                },
                {
                    "name": "hair_system_status",
                    "label": "Hair System Status",
                    "type": "enumeration",
                    "fieldType": "select",
                    "groupName": "custom",
                    "hubspotDefined": False,
                    "archived": False,
                },
            ]
        }
        self.record_count = {"contacts": 3}
        self.record_ids = {"contacts": ["101", "102", "103"]}
        self.association_targets = {
            "contacts": [
                {"object_type": "companies", "label": "Companies"},
                {"object_type": "deals", "label": "Deals"},
            ]
        }
        self.association_counts = {
            ("contacts", "companies"): 2,
            ("contacts", "deals"): 1,
        }
        self.association_record_ids = {
            ("contacts", "companies"): {"101", "102"},
            ("contacts", "deals"): {"102"},
        }
        self.property_usage = {
            ("contacts", "firstname"): 2,
            ("contacts", "favorite_color"): 2,
            ("contacts", "hair_system_status"): 0,
        }
        self.records = {
            "contacts": [
                {
                    "id": "101",
                    "properties": {
                        "firstname": "Ana",
                        "favorite_color": "Blue",
                        "hair_system_status": "",
                    },
                },
                {
                    "id": "102",
                    "properties": {
                        "firstname": "Ben",
                        "favorite_color": "",
                        "hair_system_status": "active",
                    },
                },
            ]
        }

    def list_custom_objects(self):
        return self.custom_objects

    def get_properties(self, object_type):
        return self.properties[object_type]

    def count_records(self, object_type):
        return self.record_count[object_type]

    def iter_record_ids(self, object_type):
        yield from self.record_ids[object_type]

    def discover_association_targets(self, object_type, custom_objects=None):
        del custom_objects
        return self.association_targets[object_type]

    def get_record_ids_with_associations(self, from_object_type, to_object_type, record_ids):
        self.assert_record_ids(record_ids)
        return self.association_record_ids[(from_object_type, to_object_type)]

    def count_property_usage(self, object_type, property_names):
        return {
            name: self.property_usage[(object_type, name)]
            for name in property_names
        }

    def iter_records(self, object_type, property_names):
        del property_names
        yield from self.records[object_type]

    def assert_record_ids(self, record_ids):
        if list(record_ids) != self.record_ids["contacts"]:
            raise AssertionError(f"unexpected record ids: {record_ids}")


class HubSpotObjectReportsTests(unittest.TestCase):
    def test_normalize_object_type_maps_common_aliases(self):
        self.assertEqual(subject.normalize_object_type("contact").object_type, "contacts")
        self.assertEqual(subject.normalize_object_type("Company").object_type, "companies")
        self.assertEqual(subject.normalize_object_type("line items").object_type, "line_items")

    def test_create_snapshot_report_writes_summary_and_association_rows(self):
        client = FakeClient()
        now = dt.datetime(2026, 4, 10, 15, 45, 0, tzinfo=dt.timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = subject.create_snapshot_report(
                "contacts",
                client=client,
                output_dir=Path(tmpdir),
                now=now,
            )

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.name, "contacts_snapshot_20260410T154500Z.csv")

            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        metrics = {
            (row["row_type"], row["metric_name"], row["related_object_type"]): row["value"]
            for row in rows
        }
        self.assertEqual(metrics[("summary", "record_count", "")], "3")
        self.assertEqual(metrics[("summary", "records_with_any_relationship", "")], "2")
        self.assertEqual(metrics[("summary", "records_without_any_relationship", "")], "1")
        self.assertEqual(metrics[("summary", "custom_property_count", "")], "2")
        self.assertEqual(metrics[("summary", "custom_property_used_count", "")], "1")
        self.assertEqual(metrics[("summary", "custom_property_unused_count", "")], "1")
        self.assertEqual(metrics[("association", "records_with_relationship", "companies")], "2")
        self.assertEqual(metrics[("association", "records_without_relationship", "companies")], "1")
        self.assertEqual(metrics[("association", "records_with_relationship", "deals")], "1")
        self.assertEqual(metrics[("association", "records_without_relationship", "deals")], "2")

    def test_create_property_export_includes_usage_counts(self):
        client = FakeClient()
        now = dt.datetime(2026, 4, 10, 15, 45, 0, tzinfo=dt.timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = subject.create_property_export(
                "contacts",
                client=client,
                output_dir=Path(tmpdir),
                now=now,
            )

            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        by_name = {row["property_name"]: row for row in rows}
        self.assertEqual(output_path.name, "contacts_properties_20260410T154500Z.csv")
        self.assertEqual(by_name["favorite_color"]["is_custom"], "true")
        self.assertEqual(by_name["favorite_color"]["used_in_records"], "true")
        self.assertEqual(by_name["favorite_color"]["populated_record_count"], "2")
        self.assertEqual(by_name["hair_system_status"]["used_in_records"], "false")
        self.assertEqual(by_name["hair_system_status"]["populated_record_count"], "0")
        self.assertEqual(by_name["firstname"]["is_custom"], "false")

    def test_create_crm_export_includes_all_property_columns(self):
        client = FakeClient()
        now = dt.datetime(2026, 4, 10, 15, 45, 0, tzinfo=dt.timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = subject.create_crm_export(
                "contacts",
                client=client,
                output_dir=Path(tmpdir),
                now=now,
            )

            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(output_path.name, "contacts_records_20260410T154500Z.csv")
        self.assertEqual(rows[0]["record_id"], "101")
        self.assertEqual(rows[0]["firstname"], "Ana")
        self.assertEqual(rows[0]["favorite_color"], "Blue")
        self.assertEqual(rows[1]["record_id"], "102")
        self.assertEqual(rows[1]["hair_system_status"], "active")


if __name__ == "__main__":
    unittest.main()
