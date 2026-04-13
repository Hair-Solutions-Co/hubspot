# Imports Exports

This folder owns bulk CRM data movement.

## Power

- Import records into HubSpot from CSV or spreadsheet sources.
- Map columns to object properties and association keys.
- Export CRM data for downstream analysis or migration.

## Core Calls

- `POST /crm/v3/imports`
- `GET /crm/v3/imports/{importId}`
- `GET /crm/v3/imports`
- `POST /crm/v3/exports/export/async`
- `GET /crm/v3/exports/export/async/tasks/{taskId}/status`

## Notes

- Imports are the correct surface for large structured loads.
- Record-by-record writes belong under `objects/` or `object-sync/`.
- Local agent workflows live in `scripts/hubspot_object_reports.py`.
- Project slash commands `/snapshot`, `/exportcrm`, and `/exportprop` write CSV files to `10-crm/imports-exports/exports/`.
- Run secret-bearing exports through `bash ./scripts/op_run.sh ...` or the package shortcuts in `package.json`.

## Reference

- `https://developers.hubspot.com/docs/api-reference/legacy/crm/imports/guide`
