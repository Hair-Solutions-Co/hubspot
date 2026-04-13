# HubDB

Owns HubDB tables and rows.

## Power

- Create and manage tables.
- Create, update, publish, or delete rows.
- Use HubDB as content backing storage for CMS assets and portals.

## Common Calls

- `GET /cms/v3/hubdb/tables`
- `GET /cms/v3/hubdb/tables/{tableIdOrName}`
- `POST /cms/v3/hubdb/tables`
- `PATCH /cms/v3/hubdb/tables/{tableIdOrName}`
- `GET /cms/v3/hubdb/tables/{tableIdOrName}/rows`
- `POST /cms/v3/hubdb/tables/{tableIdOrName}/rows`
- `PATCH /cms/v3/hubdb/tables/{tableIdOrName}/rows/{rowId}`
- `DELETE /cms/v3/hubdb/tables/{tableIdOrName}/rows/{rowId}`
- `POST /cms/v3/hubdb/tables/{tableIdOrName}/draft/publish`

