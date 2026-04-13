# Private Apps

Use this folder only for legacy or intentionally isolated internal tokens.

## Power

- Static bearer-token access to HubSpot APIs.
- Good for simple internal scripts when you do not need install flow or app-platform features.

## Caution

- Do not mix private-app assumptions into `oauth-apps/` or `service-keys/`.
- Prefer `service-keys/` for new REST-only admin automation on the new platform.

## Common Calls

- Same HubSpot REST calls as the granted scopes allow.
- Typical usage is direct bearer-token calls from scripts or backend services.

## References

- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview`
- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/scopes`

