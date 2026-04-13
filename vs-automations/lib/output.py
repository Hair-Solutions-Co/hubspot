"""
automations/lib/output.py
=========================
Timestamped output writers for CSV, JSON, and Markdown.

Usage:
    from lib.output import OutputWriter
    w = OutputWriter("schema-drift-audit")
    w.write_csv("drift_report", rows, fieldnames)
    w.write_json("raw_data", {})
    w.write_markdown("summary", "# Header\n...")
"""
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Sequence

# Outputs land in automations/../outputs/<automation_name>/<timestamp>/
_BASE_DIR = Path(__file__).parent.parent.parent
OUTPUTS_DIR = _BASE_DIR / "outputs"


class OutputWriter:
    """Write timestamped files to outputs/<automation_name>/<timestamp>/."""

    def __init__(self, automation_name: str, *, now: dt.datetime | None = None) -> None:
        self.automation_name = automation_name
        self._now = now or dt.datetime.now(dt.timezone.utc)
        self._ts = self._now.strftime("%Y%m%dT%H%M%SZ")
        self.run_dir = OUTPUTS_DIR / automation_name / self._ts
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def path(self, filename: str) -> Path:
        return self.run_dir / filename

    def write_csv(
        self,
        stem: str,
        rows: Sequence[dict[str, Any]],
        fieldnames: Sequence[str] | None = None,
    ) -> Path:
        if not rows:
            fields = list(fieldnames or [])
        else:
            fields = list(fieldnames or rows[0].keys())
        out = self.run_dir / f"{stem}.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        return out

    def write_json(self, stem: str, data: Any) -> Path:
        out = self.run_dir / f"{stem}.json"
        out.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")
        return out

    def write_markdown(self, stem: str, content: str) -> Path:
        out = self.run_dir / f"{stem}.md"
        out.write_text(content, encoding="utf-8")
        return out

    def timestamp(self) -> str:
        return self._ts

    def date_str(self) -> str:
        return self._now.strftime("%Y-%m-%d")
