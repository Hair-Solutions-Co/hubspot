# Service Keys

Use this folder for internal system-to-system HubSpot automation that is REST-only.

## Power

- Grant selected HubSpot scopes from the normal scope catalog.
- Authenticate server jobs without an end-user OAuth install flow.
- Best for connectors, sync jobs, migrations, reporting pulls, and admin automation.

## Limits

- No full app-platform behavior such as webhooks or UI extensions.
- Treat this as REST automation only.

## Common Calls

- Service keys do not introduce new endpoint families.
- They authorize normal HubSpot REST endpoints such as:
  - `GET /crm/v3/objects/...`
  - `POST /crm/v3/objects/...`
  - `GET /marketing/campaigns/...`
  - `POST /files/v3/files`

## References

- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys`
- `https://developers.hubspot.com/changelog/service-keys`

