# Associations Sync

This folder owns relationship synchronization between HubSpot records and external systems.

## Power

- Read available association labels and type IDs.
- Create or remove record relationships.
- Persist association mapping logic outside raw sync transport code.

## Core Calls

- `GET /crm/v4/associations/{fromObjectType}/{toObjectType}/labels`
- `PUT /crm/v3/objects/{objectType}/{fromRecordId}/associations/{toObjectType}/{toRecordId}/{associationTypeId}`
- `DELETE /crm/v3/objects/{objectType}/{fromRecordId}/associations/{toObjectType}/{toRecordId}/{associationTypeId}`

## Local Example

- `npm run dev`
- `npm run build`
- `npm run db-init`
- `npm run seed`
- `npm run test`

