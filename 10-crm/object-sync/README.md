# Object Sync

This folder is for bi-directional or one-way record synchronization patterns between HubSpot CRM and external systems.

## Power

- Pull record snapshots from HubSpot.
- Push creates, updates, upserts, and soft deletes.
- Mirror associations alongside record state.
- Store local sync state, checkpoints, and dedupe keys.

## Core Calls

- `GET /crm/v3/objects/{objectType}`
- `GET /crm/v3/objects/{objectType}/{id}`
- `POST /crm/v3/objects/{objectType}/search`
- `POST /crm/v3/objects/{objectType}`
- `PATCH /crm/v3/objects/{objectType}/{id}`
- `POST /crm/v3/objects/{objectType}/batch/update`
- `POST /crm/v3/objects/{objectType}/batch/archive`

## Local Example

- `npm run dev`
- `npm run build`
- `npm run db-init`
- `npm run db-seed`
- `npm run test`

