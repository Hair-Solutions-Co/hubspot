#!/usr/bin/env bash
# weekly_schema_pull.sh — Pulls CRM schemas, auto-commits, and pushes.
#
# Called by launchd (co.hairsolutions.hubspot.weekly-schema) or manually:
#   bash ./scripts/weekly_schema_pull.sh
set -euo pipefail

HUBSPOT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HUBSPOT_ROOT"

LOG_FILE="/tmp/hubspot-weekly-schema.log"
exec >> "$LOG_FILE" 2>&1
echo "=== $(date -Iseconds) weekly_schema_pull start ==="

bash ./scripts/op_run.sh python3 scripts/crm_schema_pull.py

if git diff --quiet HEAD && git diff --cached --quiet; then
  echo "No schema changes detected."
else
  git add 10-crm/schemas/ config/
  git commit -m "weekly: schema pull $(date +%F)" || true
  git push origin main || echo "WARN: push failed — will retry next run"
fi

echo "=== $(date -Iseconds) weekly_schema_pull done ==="
