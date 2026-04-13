# OAuth Apps

Use this folder for installable HubSpot apps that need account-by-account authorization.

## Power

- Request required, conditionally required, and optional scopes.
- Run the OAuth authorization-code flow with refresh tokens.
- Support app settings pages, webhooks, UI extensions, app cards, custom workflow actions, and project-based features.

## Common Calls

- `GET /oauth/authorize` - start install/consent.
- `POST /oauth/v1/token` - exchange code or refresh token.
- Then call granted HubSpot APIs with the resulting bearer token.

## Local Commands

- `hs auth`
- `hs init`
- `hs project create`
- `hs project upload`
- `hs project deploy`

## References

- `https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview`
- `https://developers.hubspot.com/docs/api/working-with-oauth`

