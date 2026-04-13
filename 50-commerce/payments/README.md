# Payments

Owns payment-record retrieval and payment-adjacent integrations.

**Scope note:** The internal app manifest (`hubspot-internal-app/src/app/app-hsmeta.json`) does **not** list `crm.objects.commercepayments.read` (or related payment scopes). Confirm required scopes in [HubSpot commerce/payments API docs](https://developers.hubspot.com/docs/api/crm/commerce-extensions) and add them to the app before relying on payment-object endpoints.

## Power

- Read payment records tied to commerce activity.
- Use with orders, invoices, subscriptions, and taxes when building a full commerce view.

## Common Calls

- `GET /crm/v3/objects/payments`
- `GET /crm/v3/objects/payments/{paymentId}`
- `POST /crm/v3/objects/payments/search`

