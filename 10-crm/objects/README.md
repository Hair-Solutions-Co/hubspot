# Objects

This folder owns direct record-level operations for standard and custom CRM objects.

## Power

- Create, retrieve, search, update, upsert, and archive records.
- Work across contacts, companies, deals, leads, tickets, quotes, invoices, subscriptions, orders, products, line items, and custom objects.

## Core Calls

- `GET /crm/v3/objects/{objectType}`
- `GET /crm/v3/objects/{objectType}/{recordId}`
- `POST /crm/v3/objects/{objectType}`
- `POST /crm/v3/objects/{objectType}/batch/read`
- `POST /crm/v3/objects/{objectType}/search`
- `PATCH /crm/v3/objects/{objectType}/{recordId}`
- `POST /crm/v3/objects/{objectType}/batch/update`
- `POST /crm/v3/objects/{objectType}/batch/upsert`
- `DELETE /crm/v3/objects/{objectType}/{recordId}`

## Notes

- Most object families share the same contract.
- Substitute object names such as `contacts`, `deals`, `tickets`, `quotes`, `invoices`, `orders`, or object type IDs like `0-54` for marketing events.

