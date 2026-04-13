# Data Integration

Owns bulk or pipeline-driven movement of HubSpot data across systems.

## Power

- Import and export CRM records.
- Coordinate sync contracts with external systems.
- Keep transport rules separate from CRM schema definitions.

## Common Calls

- `POST /crm/v3/imports`
- `GET /crm/v3/imports/{importId}`
- `POST /crm/v3/exports/export/async`
- `GET /crm/v3/exports/export/async/tasks/{taskId}/status`

