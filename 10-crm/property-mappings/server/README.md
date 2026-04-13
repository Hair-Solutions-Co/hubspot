# Property Mappings Server

This folder is for backend services that read property metadata, persist mappings, and expose mapping APIs.

## Power

- Read HubSpot property metadata.
- Persist external-to-HubSpot mapping tables.
- Validate mappings before write jobs run.

## Common Calls

- `GET /crm/v3/properties/{objectType}`
- `GET /crm/v3/properties/{objectType}/{propertyName}`
- `POST /crm/v3/properties/{objectType}` when creating missing fields

## Local Commands

- `npm run dev`
- `npm run build`
- `npm run db-init`
- `npm run seed`
- `npm test`

