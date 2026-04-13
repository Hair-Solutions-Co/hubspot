# Copilot Instructions — HubSpot

- `hubspot/` is the canonical env boundary for HubSpot work.
- Read `hubspot/AGENTS.md` first.
- Use `hubspot/.env.op` and `hubspot/.env`.
- Prefer `bash ./scripts/op_run.sh <command>` for secret-bearing commands.
- Do not fall back to the engineering-root `.env` unless the local wrapper does it in legacy mode.
