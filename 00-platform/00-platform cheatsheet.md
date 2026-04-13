# 00-platform — Cheatsheet

## Mental model

This folder is operational infrastructure, not a business domain. It answers: *how do I authenticate, deploy, and expose HubSpot capabilities to agents?*

## Auth decision tree

```
Need to distribute to multiple accounts?
  → OAuth app (oauth-apps/)
  
Internal automation, REST only, no install flow?
  → Service key (service-keys/)
  
Legacy internal token, or intentionally isolated?
  → Private app (private-apps/)  ← avoid for new work
```

| Type | Location | Use when | Can't do |
|------|----------|----------|----------|
| OAuth app | `00-auth/oauth-apps/` | Public apps, refresh tokens, webhooks, UI extensions, workflow actions, marketplace | Nothing — full platform |
| Service key | `00-auth/service-keys/` | Internal sync jobs, cron automation, migrations, reporting pulls, admin scripts | Webhooks, UI extensions, marketplace |
| Private app | `00-auth/private-apps/` | Legacy scripts that predate service keys | Full app-platform features |

**Current setup:** all scripts use a service key injected via `scripts/op_run.sh` as `HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN`. The customer portal uses OAuth (HubSpot UI Extensions project).

## op_run.sh token flow (canonical)

1. `scripts/op_run.sh` loads `.env.op` (non-secret config) + `.env` (real tokens via 1Password)
2. Remaps legacy names → `HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN` before unsetting them
3. Python `get_token()` reads `HUBSPOT_PRIVATE_APP__OPS__ACCESS_TOKEN` first

Legacy env var names that get remapped: `HUBSPOT_TOKEN`, `HUBSPOT_SERVICE_KEY`. Both are unset after remapping.

## CLI commands reference

```bash
# Auth
hs auth                   # authenticate the CLI
hs account list           # list connected accounts
hs account use <name>     # switch active account
hs account info           # show current account

# Projects (UI Extensions / HubSpot projects)
hs project create         # scaffold a new project
hs project add            # add a component to a project
hs project upload         # upload project to HubSpot
hs project deploy         # deploy uploaded project
hs project watch          # live sync during development
hs project dev            # local dev server
hs project logs           # view project logs
hs project list-builds    # list build history
hs project download       # pull project from HubSpot
hs project install-deps   # install project dependencies

# CMS / Design Manager
hs watch                  # watch local → HubSpot file sync
hs upload                 # one-shot upload
hs fetch                  # pull from HubSpot
hs hubdb                  # HubDB table management
hs theme                  # theme management
hs filemanager            # file manager operations
hs function               # serverless functions (we do not use these)
hs logs                   # general logs
hs doctor                 # diagnose CLI setup issues
hs init                   # initialize project config
```

**Portal ship command:** `npm run portal:ship` from `99-development/design-manager/` (calls `hs project upload` internally).

## MCP wrapper rules (20-mcp/)

- MCP wraps HubSpot API calls for agent consumption — it does not own auth or schema
- Scope ownership stays in domain folders (`10-crm/`, `20-marketing/`, etc.)
- MCP exposes composite actions: don't expose raw CRUD — wrap meaningful operations
- Agent Tool outputs must be strings — no arrays or objects returned from tool handlers
- No HubSpot serverless Functions — use external `actionUrl` endpoints (Cloudflare Workers)

## What not to do

- Do not put business domain logic in `00-platform/` — it belongs in the numbered domain folders
- Do not create new private apps — use service keys for new REST-only automation
- Do not skip `op_run.sh` for script execution — secrets must come from 1Password injection
- Do not add MCP servers to this workspace unless they materially reduce manual HubSpot work
