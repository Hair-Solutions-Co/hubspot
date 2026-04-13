# 95-breeze Cheatsheet

## What Lives Where

Breeze spans three folders. Don't confuse them:

| What | Where | Why |
|------|-------|-----|
| Breeze Agent Tool **code** | `99-development/hubspot-ui-cards/` | Deployed via `hs project upload` |
| Breeze Agent Tool **contracts** (specs) | `95-breeze/app-features/` | Document what each tool does, inputs/outputs |
| Knowledge base **articles** | `60-service/knowledge-base/articles/` | Content the Breeze agent reads |
| Customer Agent **system prompt** | `95-breeze/app-features/system-prompt.md` | The agent's personality + instructions |
| Custom Channel API **config** | `99-development/` or `98-integrations/` | The Hair Concierge integration point |

---

## Breeze Customer Agent — How It Works

The Breeze Customer Agent (your AI support agent) reads from three sources:
1. **Knowledge Base articles** → `60-service/knowledge-base/articles/` (write here, push to HubSpot KB)
2. **CRM context** → Contact + ticket + deal properties fetched at runtime
3. **Agent Tools** → Custom actions the agent can call (look up spec, check order, etc.)

**This folder (`95-breeze/`) documents the agent's design. The actual KB content and tool code live elsewhere.**

---

## Agent Tool Contracts (Document Here)

Every custom Agent Tool gets a spec file in `95-breeze/app-features/tools/`. This documents what the tool does so you can build and maintain it:

```markdown
## Tool: GetCustomerSpec

**Purpose:** Retrieve the locked spec for a customer's current hair system

**Trigger phrases:** "what's my current spec", "pull my specs", "show my system details"

**HubSpot data read:**
- Contact: `hsc_last_known_system_family`, `hsc_base_preference`, `hsc_density_preference`,
  `hsc_hair_type_preference`, `hsc_specs_locked`
- Associated object: Hair System Specs (hsc_ custom object if exists)

**Output to agent:** String — formatted spec summary
  Example: "Your current system: Swiss Lace | 80% density | Indian hair | Specs locked ✓"

**Code location:** `99-development/hubspot-ui-cards/src/app/tools/get-customer-spec.js`

**Status:** planned | built | deployed
```

---

## Known Agent Tools to Build

Based on the sales vault and portal design, these are the highest-value tools for the Hair Concierge:

| Tool | What it does | Priority |
|------|-------------|----------|
| `GetCustomerSpec` | Return locked spec summary for a contact | High |
| `GetReorderWindow` | Check if `hsc_reorder_window_open` = true, return timing | High |
| `GetOpenTickets` | Return open tickets for this contact | High |
| `LookupProduct` | Return product details from HubDB | Medium |
| `GetSubscriptionStatus` | Return `hsc_subscription_status` + renewal date | Medium |
| `CreateTicket` | Create a service ticket from chat | Medium |
| `GetOrderHistory` | Return recent orders from deals | Low |
| `CalculateReorderDate` | Compute reorder date from base type + last order | Low |

---

## System Prompt (Document Here)

Write your Breeze Customer Agent system prompt in `95-breeze/app-features/system-prompt.md`. This is the agent's operating instructions.

Key things to include in the prompt:
- Tone (from `06_knowledge/obsidian-vault/30-sales/sales-tone-guide.md` — credible, supportive, commercial, unhurried)
- What the agent can and can't do
- When to escalate to a human
- How to handle sensitive topics (financial disputes, chargebacks, crisis-era orders)
- Suppression rule: if contact risk band = Critical → don't engage, route to founder

---

## No Dedicated API Scope

Breeze/AI features are **not enumerated as separate API scopes**. The agent operates through:
- HubSpot's Custom Channels API (Hair Concierge integration)
- Standard CRM API (for reading/writing contact + ticket data)
- Agent Tools (deployed via HubSpot project, called by Breeze at runtime)

There is no `breeze.*` scope to request. Configure Breeze in HubSpot Settings → Breeze Customer Agent.

---

## Folder Layout to Build

```
95-breeze/
  app-features/
    system-prompt.md              ← Agent operating instructions
    tools/
      get-customer-spec.md        ← Tool contract
      get-reorder-window.md
      get-open-tickets.md
      lookup-product.md
      get-subscription-status.md
      create-ticket.md
    knowledge-base-index.md       ← What KB articles exist + their purpose
```

---

## What NOT to Do

- Don't put Agent Tool **code** here — it lives in `99-development/hubspot-ui-cards/`
- Don't put KB **article content** here — it lives in `60-service/knowledge-base/articles/`
- Don't configure Breeze via API — use HubSpot Settings UI
- Don't give the agent write access to deals or contact properties without explicit tool contracts reviewed first
