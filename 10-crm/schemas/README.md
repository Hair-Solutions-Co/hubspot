# Schemas

This folder owns property, pipeline, and object-model structure rather than record data.

## Power

- Create and update CRM properties.
- Manage custom object definitions and property groups.
- Read schema metadata needed by sync, validation, and UI layers.

## Core Calls

- `GET /crm/v3/properties/{objectType}`
- `GET /crm/v3/properties/{objectType}/{propertyName}`
- `POST /crm/v3/properties/{objectType}`
- `PATCH /crm/v3/properties/{objectType}/{propertyName}`
- `DELETE /crm/v3/properties/{objectType}/{propertyName}`
- `GET /crm/v3/schemas`
- `POST /crm/v3/schemas`
- `PATCH /crm/v3/schemas/{objectTypeId}`

## Notes

- Schema work is high-impact because it affects downstream imports, UI, workflows, and sync jobs.

