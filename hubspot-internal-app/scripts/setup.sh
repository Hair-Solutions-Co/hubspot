#!/usr/bin/env bash
# setup.sh — bootstrap the HubSpot Internal Integrations project
# Usage: bash scripts/setup.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[setup]${NC} $*"; }
warn()    { echo -e "${YELLOW}[warn]${NC}  $*"; }
abort()   { echo -e "${RED}[error]${NC} $*"; exit 1; }

# ── 1. Check Node.js ───────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
  abort "Node.js is not installed. Install via https://nodejs.org or nvm."
fi
info "Node.js $(node -v) found."

# ── 2. Install / upgrade HubSpot CLI ──────────────────────────────────────────
if ! command -v hs &>/dev/null; then
  info "Installing @hubspot/cli globally..."
  npm install -g @hubspot/cli
else
  info "HubSpot CLI already installed: $(hs --version 2>/dev/null || echo 'version unknown')"
  warn "Run 'npm install -g @hubspot/cli@latest' to upgrade."
fi

# ── 3. Check for .env file ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  warn ".env not found. Creating from .env.example..."
  cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
  warn "Fill in $PROJECT_ROOT/.env before running the OAuth flow."
else
  info ".env found."
fi

# ── 4. HubSpot account auth ────────────────────────────────────────────────────
info "────────────────────────────────────────────────────────────"
info "Next step: authenticate with your HubSpot account."
info ""
info "  hs account auth"
info ""
info "This will open a browser window and store credentials in ~/.hubspot/"
info "────────────────────────────────────────────────────────────"

read -rp "Run 'hs account auth' now? [y/N] " run_auth
if [[ "$run_auth" =~ ^[Yy]$ ]]; then
  hs account auth
fi

# ── 5. Upload the app project ──────────────────────────────────────────────────
info "────────────────────────────────────────────────────────────"
info "To upload and deploy the project to HubSpot, run:"
info ""
info "  cd $PROJECT_ROOT"
info "  hs project upload"
info "  hs project deploy"
info ""
info "The first upload creates the app in the developer portal."
info "────────────────────────────────────────────────────────────"

info "Setup complete."
