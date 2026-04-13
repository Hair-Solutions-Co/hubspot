# GraphQL

Owns HubSpot GraphQL query and schema introspection surfaces.

**Not in HSC Internal Integrations manifest:** `hubspot-internal-app/src/app/app-hsmeta.json` does **not** include `collector.graphql_query.execute` or `collector.graphql_schema.read`. Add those scopes to the app (or use another credential) before calling the collector GraphQL API.

## Power

- Execute GraphQL queries against HubSpot-supported collectors.
- Perform schema introspection for query planning and portal-aware CMS work.

## Common Calls

- `POST /collector/graphql`

