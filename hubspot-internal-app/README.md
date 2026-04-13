# HSC Internal Integrations — HubSpot App

> A production-ready HubSpot public app that acts as the integration layer between HubSpot and Hair Solutions Co.'s external tools: **Shopify**, **ClickUp**, **Notion**, and **Cloudinary**.

This app now lives inside the `hairsolutionsco/integrations` monorepo at `apps/hubspot-internal-app`.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Install the HubSpot CLI](#install-the-hubspot-cli)
4. [Authenticate with HubSpot](#authenticate-with-hubspot)
5. [Environment Setup](#environment-setup)
6. [Upload and Deploy](#upload-and-deploy)
7. [Install the App on Your Portal](#install-the-app-on-your-portal)
8. [Test the OAuth Flow Locally](#test-the-oauth-flow-locally)
9. [Scopes Reference](#scopes-reference)
10. [Adding Future Connectors](#adding-future-connectors)

---

## Project Structure

```
hubspot-internal-app/
├── package.json                    # Workspace package manifest
├── hsproject.json                  # HubSpot CLI project config (platformVersion 2025.2)
├── src/
│   └── app/
│       └── app-hsmeta.json         # App config: OAuth auth, scopes, permitted URLs
├── docs/
│   └── hubspot/
│       └── SCOPES.md               # Why each scope group exists
├── scripts/
│   └── setup.sh                    # Bootstrap: install CLI, auth, upload guidance
├── .env.example                    # All required env variable placeholders
├── .gitignore
└── README.md
```

---

## Prerequisites

- **Node.js** ≥ 18 (managed via [nvm](https://github.com/nvm-sh/nvm))
- A **HubSpot Developer account** (free — create one at https://app.hubspot.com/signup-hubspot/developers)
- A **HubSpot Developer Portal** (different from your regular portal — used to register apps)

---

## Install the HubSpot CLI

```bash
npm install -g @hubspot/cli
```

Verify the install:
```bash
hs --version
```

---

## Authenticate with HubSpot

Authenticate the CLI against your developer portal:

```bash
hs account auth
```

This opens a browser window. Log in with your HubSpot credentials. The CLI stores tokens under `~/.hubspot/`.

To confirm which account is active:
```bash
hs accounts list
```

To switch default account:
```bash
hs accounts use <accountName>
```

---

## Environment Setup

1. Use `.env.example` in this folder as the variable-name reference only.
2. Store the real values in 1Password Desktop Environments for the repo root environment.
3. Inject secrets at runtime with `op run --env-file .env.op --env-file .env -- <command>` from the repo root.

HubSpot variables used by this app:
- `HUBSPOT_PORTAL_ID` — your developer portal ID (visible in the URL at `app.hubspot.com`)
- `HUBSPOT_CLIENT_ID` and `HUBSPOT_CLIENT_SECRET` — generated after the first `hs project upload`
- `HUBSPOT_ACCESS_TOKEN` — standard private app / personal access token for normal CRM integrations
- `HUBSPOT_SERVICE_KEY` — separate broad-scope service key for admin-style automation
- `HUBSPOT_DEVELOPER_API_KEY` — developer account API key for developer-portal-only workflows

Do not commit secrets and do not create a local `.env` in this workspace.

---

## Upload and Deploy

From the project root:

```bash
cd hubspot-internal-app

# Push the project config to HubSpot
hs project upload

# Deploy the uploaded build
hs project deploy
```

On first upload, HubSpot creates the app in your developer portal. After upload:

1. Go to your [HubSpot Developer Portal → Apps](https://app.hubspot.com/developer)
2. Open **HSC Internal Integrations**
3. Go to **Auth** tab — copy `Client ID` and `Client Secret` into 1Password Desktop Environments under `HUBSPOT_CLIENT_ID` and `HUBSPOT_CLIENT_SECRET`

---

## Install the App on Your Portal

Once uploaded, install the app on your production HubSpot portal to grant it the OAuth scopes:

1. In your developer portal, open **HSC Internal Integrations → Auth**
2. Click **Install URL (OAuth)**
3. Open the generated URL in a browser
4. Select your **production portal** and click **Connect app**
5. Review and accept the requested scopes
6. You will be redirected to `http://localhost:3000/oauth/callback` (or your production domain) — exchange the `code` parameter for tokens using the standard HubSpot OAuth token endpoint:
   ```
   POST https://api.hubapi.com/oauth/v1/token
   ```
   Store the returned `access_token` and `refresh_token` in your secrets manager / 1Password environment.

---

## Test the OAuth Flow Locally

1. Start your local server on port 3000 (however you run your integration backend)
2. Make sure `APP_BASE_URL=http://localhost:3000` is present in the injected environment
3. Visit the OAuth install URL (from the developer portal) and complete the flow
4. Confirm the callback is hit and tokens are received

---

## Scopes Reference

All scope decisions are documented in [docs/hubspot/SCOPES.md](docs/hubspot/SCOPES.md).

That file explains:
- Which scope group each scope belongs to (CRM, e-commerce, media, automation, pipeline)
- Why it's present
- Whether it's `required` or `optional`
- Which scopes still need verification before promoting to required

### Adding New Scopes

1. Open `src/app/app-hsmeta.json`
2. Add the scope string to `requiredScopes` or `optionalScopes`
3. Run `hs project upload && hs project deploy`
4. Re-install the app on your portal (HubSpot will prompt for re-auth if required scopes changed)
5. Document the change in `docs/hubspot/SCOPES.md`

---

## Adding Future Connectors

The project is structured for modular expansion. Suggested layout as connectors are added:

```
src/
└── app/
    ├── app-hsmeta.json
    └── connectors/
        ├── shopify/
        ├── clickup/
        ├── notion/
        └── cloudinary/
```

Each connector will:
- Add its own scope requirements to `app-hsmeta.json` (optional until activated)
- Add its permitted API domain to `permittedUrls.fetch` in `app-hsmeta.json`
- Add its credentials to `.env.example`
- Document its scope needs in `docs/hubspot/SCOPES.md`

---

## Useful CLI Commands

| Command | What it does |
|---------|-------------|
| `npm run setup` | Bootstrap local CLI auth and env scaffolding |
| `hs project upload` | Push config changes to HubSpot |
| `hs project deploy` | Deploy the latest upload |
| `hs accounts list` | Show authenticated accounts |
| `hs account auth` | Authenticate a new account |
| `hs project logs` | View recent project logs |
| `hs --help` | Full CLI reference |

---

## Security Notes

- This is a **private distribution** app — it won't appear on the HubSpot Marketplace
- Access tokens expire after ~30 minutes; use the refresh token to renew them
- Validate `x-hubspot-signature` v2 on every incoming webhook request
- Never log or expose `HUBSPOT_CLIENT_SECRET`, private-app tokens, service keys, or developer API keys
