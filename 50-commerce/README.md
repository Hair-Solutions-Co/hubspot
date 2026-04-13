# Commerce

This folder owns HubSpot commerce objects and payment-adjacent data surfaces.

**Scope source of truth:** `hubspot-internal-app/src/app/app-hsmeta.json` (HSC Internal Integrations).

## Scopes in the internal app manifest

- `e-commerce`
- `accounting`
- `crm.objects.quotes.*`, `line_items.*`, `products.*`, `orders.*`, `carts.*`, `invoices.*`, `subscriptions.*`
- `crm.pipelines.orders.read`, `crm.pipelines.orders.write`
- Commerce-aligned **schema read** scopes for `line_items`, `quotes`, `orders`, `carts`, `subscriptions`, `invoices` (see manifest)

`crm.objects.commercepayments.read` and `tax_rates.read` are **not** on the internal app manifest. Payment-object and tax API work may need additional scopes—add them to the app before treating those endpoints as authorized.

