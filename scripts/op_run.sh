#!/usr/bin/env bash
# Run a command with 1Password-injected env (.env.op + .env). HubSpot cwd is the repo root.
#
#   bash ./scripts/op_run.sh python3 ./scripts/hubspot_object_reports.py snapshot contacts
#   npm run hubspot:snapshot:contacts
#   npm run hubspot:snapshot -- companies   # pass object type after --
#
set -euo pipefail

HUBSPOT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENGINEERING_ROOT="$(cd "$HUBSPOT_ROOT/.." && pwd)"
ENV_OP_ROOT="$HUBSPOT_ROOT"
ENV_SECRET_ROOT="$HUBSPOT_ROOT"

if [[ ! -e "$ENV_SECRET_ROOT/.env" && -e "$ENGINEERING_ROOT/.env" ]]; then
  ENV_SECRET_ROOT="$ENGINEERING_ROOT"
fi

if ! command -v op >/dev/null 2>&1; then
  echo "op_run: install 1Password CLI (https://developer.1password.com/docs/cli/)" >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "usage: op_run.sh <command> [args...]" >&2
  exit 1
fi

OP_ARGS=(run)
if [[ -e "$ENV_OP_ROOT/.env.op" ]]; then
  OP_ARGS+=(--env-file "$ENV_OP_ROOT/.env.op")
fi

if [[ -e "$ENV_SECRET_ROOT/.env" ]]; then
  OP_ARGS+=(--env-file "$ENV_SECRET_ROOT/.env")
else
  echo "op_run: missing $ENV_SECRET_ROOT/.env (mount the HubSpot 1Password Environment at hubspot/.env; engineering-root fallback is legacy only)" >&2
  exit 1
fi

export HUBSPOT_ROOT
export HUBSPOT_ENV_ROOT="$ENV_SECRET_ROOT"

OP_ARGS+=(--)
cd "$HUBSPOT_ROOT"
exec op "${OP_ARGS[@]}" bash -c '
  # Prefer HUBSPOT_SERVICE_KEY (broad private-app PAT) when present; then narrow fallbacks.
  unset HUBSPOT_CREDENTIAL_SOURCE || true
  if [[ -n "${HUBSPOT_SERVICE_KEY:-}" ]]; then
    export HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN="$HUBSPOT_SERVICE_KEY"
    export HUBSPOT_CREDENTIAL_SOURCE="HUBSPOT_SERVICE_KEY"
  elif [[ -n "${HUBSPOT_TOKEN:-}" && -z "${HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN:-}" ]]; then
    export HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN="$HUBSPOT_TOKEN"
    export HUBSPOT_CREDENTIAL_SOURCE="HUBSPOT_TOKEN"
  elif [[ -n "${HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN:-}" ]]; then
    export HUBSPOT_CREDENTIAL_SOURCE="HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN"
  fi

  if [[ -n "${HUBSPOT_APP_CLIENT_SECRET:-}" && -z "${HUBSPOT_APP__CUSTOMER_PORTAL__CLIENT_SECRET:-}" ]]; then
    export HUBSPOT_APP__CUSTOMER_PORTAL__CLIENT_SECRET="$HUBSPOT_APP_CLIENT_SECRET"
  fi

  unset HUBSPOT_PORTAL_ID
  unset HUBSPOT_APP_ID
  unset HUBSPOT_CLIENT_ID
  unset HUBSPOT_CLIENT_SECRET
  unset HUBSPOT_REDIRECT_URL
  unset HUBSPOT_PRIVATE_APP_ACCESS_TOKEN
  unset HUBSPOT_SERVICE_KEY
  unset HUBSPOT_STATIC_TOKEN
  unset HUBSPOT_ACCESS_TOKEN
  unset HUBSPOT_PERSONAL_ACCESS_KEY
  unset HUBSPOT_TOKEN
  unset HUBSPOT_APP_CLIENT_SECRET

  exec "$@"
' bash "$@"
