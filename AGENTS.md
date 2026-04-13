# HubSpot Workspace — Agent Contract

This folder is the default env and tooling boundary for HubSpot work inside `00_engineering/`.

## Boundary Rule

- Treat `hubspot/` as the canonical secret boundary for the full HubSpot subtree.
- Use `hubspot/.env.op` for non-secret defaults.
- Use `hubspot/.env` for 1Password-backed secret injection.
- Subprojects under `hubspot/` should inherit this boundary unless they publish a stricter local wrapper.

## 1Password Rule

- Never read or print `.env` directly.
- Prefer process injection:
  - `bash ./scripts/op_run.sh <command>`
  - equivalent raw form: `op run --env-file .env.op --env-file .env -- <command>`
- If `hubspot/.env` does not exist yet, the wrapper temporarily falls back to `../.env` so existing work keeps running while the 1Password link is moved down to this folder.

## VS Code Rule

- Daily entry point: `hubspot.code-workspace` at this repo root (multi-root HubSpot + Design Manager + portal folders). **Design Manager is a separate Git repo** — clone it into `99-development/design-manager/` so workspace folders resolve. Narrower window: open `customer-portal.code-workspace` from that checkout.
- Keep the global VS Code MCP baseline lean. HubSpot-specific MCP belongs in this workspace only.
- Do not add extra workspace MCP servers unless they materially reduce manual HubSpot work.

## MCP Rule

- Global/user MCP baseline should stay minimal.
- The HubSpot workspace MCP file is limited to low-noise docs support.
- Do not wire stale or repo-external HubSpot API MCP servers into this workspace.
- **Cursor-integrated browser:** Use the **`cursor-ide-browser`** MCP to drive **HubSpot’s web UI** when the task requires navigation, filters, workflows, settings, or other **browser-only** work. Follow [.cursor/rules/hubspot-browser-automation.mdc](.cursor/rules/hubspot-browser-automation.mdc) and [docs/hubspot-browser-playbook.md](docs/hubspot-browser-playbook.md). This does not replace Private Apps/APIs for bulk or auditable automation—see “API vs browser” in that rule.

## HubSpot API vs browser (routing)

- **Prefer Private App / REST / GraphQL / Python scripts** (`bash ./scripts/op_run.sh …`) for bulk operations, imports, scheduled jobs, and anything that must be **repeatable and auditable**.
- **Use `hs` CLI** for developer project lifecycle in this repo: [`hubspot-internal-app/package.json`](hubspot-internal-app/package.json) (`hs:upload`, `hs:deploy`, `hs:logs`).
- **Use the browser MCP** for UI-only configuration, visual verification, sequences/workflows where you need the **exact UI path**, or when **no API** fits. Never put tokens in chat; use 1Password-injected env only.

## HubSpot browser automation — session safety

- The user **logs in manually** in the browser tab (password, SSO, **2FA**). The agent must **never** ask for passwords or MFA codes in chat.
- On **captcha**, **forced 2FA**, **session expired**, or **iframe**-blocked UI: stop, describe the blocker, and hand off to the user or switch to API/CLI.
- **Destructive** actions (delete, merge, mass enroll, editing live workflows): require **explicit user confirmation** in the instruction (e.g. approval line or clear intent). If missing, ask once before executing.

## High-Use Paths

- `99-development/design-manager/customer-portal/app/` (path exists after cloning the Design Manager repository)
- `99-development/hubspot-ui-cards/`
- `20-marketing/programmable-emails/`

## Default Agent Behavior

1. Read this file, `README.md`, and the nearest local README in the active subfolder.
2. Use `bash ./scripts/op_run.sh` for secret-bearing commands.
3. Keep secrets in 1Password-backed env injection only.
4. Prefer the tasks in `hubspot.code-workspace` before inventing new one-off shell commands.