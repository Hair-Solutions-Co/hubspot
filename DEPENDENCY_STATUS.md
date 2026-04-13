# HubSpot Dependency Status

This file tracks the install state of dependency-bearing projects under `hubspot/`.

## Installable Projects

| Path | Type | Install Method | Status | Notes |
|---|---|---|---|---|
| `99-development/hubspot-ui-cards` | HubSpot project | `hs project install-deps` | Partially prepared | The actual local JS package lives at `src/app/cards`. Dependencies there are installed. Preferred command remains `hs project install-deps`. |
| `99-development/example-apps/crm-object-sync` | OAuth + Prisma example server | `npm install` | Installed | Requires PostgreSQL and secret-bearing env injection before use. |
| `99-development/example-apps/property-mapping-client` | React example client | `npm install` | Installed | Ready for local front-end work. |
| `99-development/example-apps/property-mapping-server` | OAuth + Prisma example server | `npm install` | Installed | Requires PostgreSQL and secret-bearing env injection before use. |
| `99-development/example-apps/associations-sync-server` | OAuth + Prisma example server | `npm install` | Installed | Requires PostgreSQL and secret-bearing env injection before use. |

## Non-Package HubSpot Surfaces

| Path | Type | Status | Notes |
|---|---|---|---|
| `20-marketing/programmable-emails` | HubSpot project assets | No package install required | Managed as HubSpot modules/templates plus a Python helper script. |

## External repositories

| Repository | Local path (after clone) | Notes |
|---|---|---|
| Design Manager / customer portal (separate Git repo) | `99-development/design-manager/` | Next.js app: `customer-portal/app/` (`npm install` there). Theme build CI runs in that repo’s `.github/workflows/`. Secrets: `hubspot/.env` via `./scripts/op_run.sh` when running portal scripts from a combined checkout. |

## Current Installation State

The install commands have already been run manually for every valid dependency-bearing project listed above.

## Structural Notes

- There are no remaining broken HubSpot project boundaries in this tree.
- The numbered prefixes are intentional and define the stable visual and cognitive order of the workspace.
- Development surfaces that older notes may call `development/` or `00-platform/30-development/` now live under `99-development/` at the HubSpot repo root (sorts last).
- `60-service/`, `80-automation/`, and `90-reporting/` were added so the folder structure now matches the real HubSpot operational domains more closely.
