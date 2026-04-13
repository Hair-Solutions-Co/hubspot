"""
automations/lib/log.py
======================
Minimal structured logger for automations.
Prints timestamped lines with automation name prefix to stdout/stderr.
"""
from __future__ import annotations

import datetime as dt
import sys


class AutomationLogger:
    def __init__(self, name: str) -> None:
        self.name = name

    def _ts(self) -> str:
        return dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")

    def info(self, msg: str) -> None:
        print(f"[{self._ts()}] [{self.name}] {msg}", flush=True)

    def warn(self, msg: str) -> None:
        print(f"[{self._ts()}] [{self.name}] WARN  {msg}", flush=True)

    def error(self, msg: str) -> None:
        print(f"[{self._ts()}] [{self.name}] ERROR {msg}", file=sys.stderr, flush=True)

    def section(self, title: str) -> None:
        bar = "─" * 60
        print(f"\n{bar}\n  {self.name} │ {title}\n{bar}", flush=True)

    def result(self, label: str, value: Any) -> None:  # type: ignore[name-defined]
        print(f"  → {label}: {value}", flush=True)


# Allow `from lib.log import AutomationLogger` or bare import for type hints
from typing import Any  # noqa: E402 — needed for result() above
