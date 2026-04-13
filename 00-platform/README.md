# Platform

This folder groups the operational surfaces that make HubSpot usable as a platform, not as a business domain.

## Subfolders

- `00-auth/` - installation and token model boundaries.
- `10-cli/` - local `hs` command surface and workflow notes.
- `20-mcp/` - agent and MCP wrappers over HubSpot capabilities.

HubSpot-native **development** build surfaces (Design Manager, UI extension cards, example apps) live at the HubSpot repo root in **`99-development/`** (last in the numbered map, aligned with HubSpot’s Development area).

## Rule

- Keep platform mechanics here.
- Keep CRM, marketing, content, sales, commerce, service, and data work in their numbered domain folders.
