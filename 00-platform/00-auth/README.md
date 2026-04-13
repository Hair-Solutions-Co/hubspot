# Auth

This folder separates HubSpot auth by installation and capability model.

## Boundaries

- `oauth-apps/` - installable apps, refresh tokens, webhooks, app features, workflow extensions.
- `service-keys/` - REST-only system-to-system automation.
- `private-apps/` - legacy or isolated internal tokens kept separate from the new platform model.

## Power

- Controls which scopes can be granted.
- Determines whether the integration can use REST only or full app-platform features.
- Determines whether auth is per account install or internal account key.

## References

- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview`
- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/scopes`
- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys`

