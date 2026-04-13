# Hair Solutions Design Manager Workspace

This directory is a workspace for the HubSpot customer portal program. It is not a single Next.js app root.

The canonical deliverable lives in `customer-portal/theme/` as a HubSpot CMS theme. The old Next.js application under `customer-portal/app/` and its supporting `components/`, `lib/`, and `prisma/` sources are archived legacy scaffolding kept only behind explicit `legacy:*` commands.

## Workspace Layout

- `customer-portal/theme/`: HubSpot CMS theme source uploaded to Design Manager
- `customer-portal/data/`: CRM property and HubDB model definitions, seeds, and schema registry
- `customer-portal/ops/`: automation, release, HubSpot sync, and GitHub export scripts
- `customer-portal/scripts/`: repo-local build, upload, and issue-sync helpers
- `customer-portal/app/`, `customer-portal/components/`, `customer-portal/lib/`, `customer-portal/prisma/`: archived Next.js customer portal sources kept for reference / controlled legacy access
- `customer-portal/docs/`: implementation plan, handoff docs, known issues, and agent prompts; legacy deploy artifacts archived under `docs/archive/`
- `../../hubspot.code-workspace` (repo root): primary multi-root workspace (tasks use `hubspot/` as cwd)
- `customer-portal.code-workspace`: VS Code workspace rooted in Design Manager only (relative paths like `customer-portal/app`)

## How To Work Here

- For HubSpot theme work, work in `customer-portal/theme/`
- For CRM properties and HubDB sync definitions, work in `customer-portal/data/`
- For scripted operations, use `customer-portal/ops/scripts/`
- For the archived Next app, use `npm run legacy:* --prefix customer-portal` only when intentionally reviving or auditing it

## Common Commands

From this workspace root:

```bash
npm run dev          # prints CMS guidance
npm run build        # CMS theme validation
npm run lint         # CMS theme validation
npm run portal:verify
npm run legacy:dev
npm run legacy:typecheck
```

The default wrappers delegate into the `customer-portal/` repo root and follow the CMS-only workflow. `legacy:*` wrappers are the only entrypoint for the archived Next app.

From the archived app path directly:

```bash
cd customer-portal
npm run legacy:dev
npm run legacy:build
npm run legacy:lint
npm run legacy:typecheck
```

## Secrets

Do not read or edit `.env` directly. For commands that need HubSpot or other secrets, use the local wrapper:

```bash
bash customer-portal/ops/scripts/op_env.sh <command>
```

`op_env.sh` forwards to `hubspot/scripts/op_run.sh` and **changes directory to this Design Manager root** before running `<command>`, so paths stay the same as in these docs even though `op_run` starts from `hubspot/`. From **`hubspot/`** you can also run the same script by absolute path under the repo, e.g. `bash 99-development/design-manager/customer-portal/ops/scripts/op_env.sh npm run portal:hubspot-props`.

## HubSpot Design Manager (official link)

| What | Value |
|------|--------|
| **This workspace** | `99-development/design-manager/` — canonical clone for the customer portal program |
| **Theme on disk** | `customer-portal/theme/` (edit here; flat `modules/*.module` layout) |
| **Design Manager path (CLI)** | **`customer-portal`** — use `hs list` at the account root to confirm |
| **Theme label** (`theme.json`) | `Hair Solutions Customer Portal` (UI may show a similar name such as “hair solutions portal”) |
| **Upload / publish** | `npm run portal:ship` or `bash customer-portal/ops/scripts/portal_task_complete.sh "msg"` — destination `$HUBSPOT_THEME_DEST` (default **`customer-portal`**). Uploads use **`-m publish`** by default (not `hs theme …`; there is no `hs theme publish`). Draft only: `HUBSPOT_CMS_PUBLISH_MODE=draft`. |
| **Pull for comparison** | `npm run portal:fetch` — writes `customer-portal/.hubspot-theme-fetch/` (gitignored). HubSpot’s copy may differ in folder shape (`_locales`, nested module dirs) while file contents stay equivalent. |
| **Live dev upload** | From `customer-portal/theme/`: `hs watch . customer-portal` (optional `--initial-upload`) |

Auth uses the HubSpot CLI default account (`hs accounts list`; config in `~/.hscli/config.yml`). Do not commit `hubspot.config.yml`.

## Canonical References

- `docs/design-manager/HUBSPOT_AGENT_CHEATSHEET.md` (CLI paths, upload/fetch/watch, account)
- `customer-portal/docs/HANDOFF_PROMPT.md`
- `customer-portal/docs/IMPLEMENTATION_PLAN_SUBAGENTS.md`
- `customer-portal/docs/KNOWN_ISSUES.md`
- `customer-portal/data/SCHEMA_REGISTRY.md`
