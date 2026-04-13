#!/usr/bin/env bash
# daily_snapshot.sh — Runs all daily HubSpot snapshots, auto-commits, and pushes.
#
# Called by launchd (co.hairsolutions.hubspot.daily-snapshot) or manually:
#   bash ./scripts/daily_snapshot.sh
#
# Decision 1.2: Auto-commit (Option A) — solo operator, zero-friction git history.
set -euo pipefail

HUBSPOT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HUBSPOT_ROOT"

LOG_FILE="/tmp/hubspot-daily-snapshot.log"
exec >> "$LOG_FILE" 2>&1
echo "=== $(date -Iseconds) daily_snapshot start ==="

# 1. CRM record counts + pipeline breakdowns
echo "[1/2] CRM daily snapshot..."
bash ./scripts/op_run.sh python3 scripts/crm_daily_snapshot.py

# 2. Open tickets snapshot
echo "[2/2] Open ticket snapshot..."
bash ./scripts/op_run.sh python3 scripts/open_ticket_snapshot.py

# 3. Auto-commit if there are changes
if git diff --quiet HEAD && git diff --cached --quiet; then
  echo "No changes to commit."
else
  git add \
    10-crm/imports-exports/snapshots/ \
    60-service/tickets/snapshots/ \
    config/
  git commit -m "daily: snapshot $(date +%F)" || true
  git push origin main || echo "WARN: push failed — will retry next run"
fi

echo "=== $(date -Iseconds) daily_snapshot done ==="
