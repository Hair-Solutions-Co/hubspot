# Programmable Emails — Implementation Plan

**Project:** Hair Solutions Co. Programmable Email System
**Platform:** HubSpot Marketing Hub Professional
**Date:** 2026-04-07
**Status:** Planning

---

## Executive Summary

Build a programmable email system that delivers 41 lifecycle emails across 8 customer journeys, plus a 10-asset consultation/active-sales email library migrated from the legacy OHHS archive.

The system has two independent tracks:

- **Track A — Lifecycle Journeys (J1-J8 + Dunning):** 39 emails, 7 programmable, 13 workflow-triggered, 16 standard, 3 redesign-required
- **Track B — Consultation & Active Sales:** 10 core assets migrated from the OHHS archive, delivered as sales templates and workflow-triggered sends

Both tracks share a common property layer and follow a single architectural rule:

> Workflows and precomputed CRM properties own all business logic. Email templates only render what is already resolved.

---

## What Already Exists

### CRM Properties (confirmed live in HubSpot)

**Contact properties confirmed:**
- `hsc_customer_class`, `hsc_experience_level`, `hsc_relationship_state`
- `hsc_primary_goal`, `hsc_preferred_channel`, `hsc_reengagement_priority`
- `hsc_base_preference`, `hsc_density_preference`, `hsc_attachment_preference`, `hsc_hair_type_preference`
- `hsc_last_known_system_family`, `hsc_next_action_date`
- `hsc_customer_health_score`, `hsc_risk_band`, `hsc_reorder_readiness`

**Deal properties confirmed:**
- `hsc_deal_type`, `hsc_quote_status`, `hsc_quote_version`
- `hsc_payment_path`, `hsc_spec_lock_status`
- `hsc_confirm_factory_order_placed`, `hsc_reengagement_eligible_on`
- `hsc_lost_reason_primary`, `hsc_lost_reason_secondary`, `hsc_exception_flag`

**Ticket properties confirmed:**
- `hsc_inquiry_type`, `hsc_qualification_state`, `hsc_spec_readiness`
- `hsc_primary_blocker`, `hsc_next_action_type`, `hsc_next_action_date`
- `hsc_route_decision`, `hsc_escalation_level`, `hsc_relationship_state`

### Email Campaign Pipeline (10-marketing/email/)

- 63 emails live in HubSpot (41 lifecycle + 22 campaign calendar)
- YAML-spec build pipeline: `specs → HTML → validator → HubSpot push`
- 20 active lists defined (need manual HubSpot creation)
- 11 workflows documented (need configuration)
- Contact scoring scripts ready

### What Does NOT Exist Yet

- Programmable email modules (HubL conditional blocks)
- Coded email templates for programmable content
- Order/subscription mirror properties on contacts
- Reorder-timing computation workflows
- Consultation recap sales templates
- Quote-context deal properties for consultation tokens

---

## Architecture

### Platform Constraints (Marketing Hub Pro)

| Allowed | Not Allowed |
|---------|-------------|
| Contact, company, product CRM data in programmable emails | HubDB lookups in email |
| `{% if %}` / `{% elif %}` / `{% else %}` conditional blocks | Custom objects in email HubL |
| `personalization_token()`, `crm_object()`, `crm_objects()` | A/B testing on programmable emails |
| `crm_associations()` on standard objects | Real-time subscription math in templates |
| Coded email templates with `isEnabledForEmailV3Rendering` | Complex multi-object joins |

### Email Classification System

| Class | Count | Meaning |
|-------|-------|---------|
| `S` Standard | 16 | Contact tokens + static content, drag-and-drop |
| `W` Workflow | 13 | Event-triggered, deal/order context, simple body |
| `P` Programmable | 7 | Conditional HubL rendering adds real value |
| `R` Redesign | 3 | Blocked until precomputed property fields exist |

### Template Tiers

```
Tier 1: Standard Marketing Templates
  └── Drag-and-drop or coded, no CRM HubL lookups
  └── J1-E1/E2/E4/E5, all J2, J5-E4, J6-E1/E3/E4, J7-E1/E3/E4

Tier 2: Programmable Modules (4 reusable blocks)
  └── hsc_goal_based_recommendation_block
  └── hsc_base_type_guidance_block
  └── hsc_lifespan_next_step_block
  └── hsc_customer_snapshot_block

Tier 3: Workflow-Triggered Operational Templates
  └── Order confirmation, shipping, arrival, payment, renewal
  └── Consultation follow-up (day 90, close-loop)
```

---

## Property Gap Analysis

### Contact Properties — Must Create

#### Order / Reorder Summary
| Property | Type | Purpose |
|----------|------|---------|
| `hsc_last_order_date` | date | Last completed order date |
| `hsc_last_order_id` | string | External order reference |
| `hsc_last_order_value` | number | Last order total |
| `hsc_predicted_reorder_date` | date | Computed by base-type wear schedule |
| `hsc_reorder_window_open` | boolean | True when reorder window is active |
| `hsc_reorder_message_angle` | enumeration | Which reorder messaging variant to use |
| `hsc_total_orders_lifetime` | number | Lifetime order count |
| `hsc_total_orders_last_12m` | number | Rolling 12-month order count |

#### Subscription Summary
| Property | Type | Purpose |
|----------|------|---------|
| `hsc_subscription_status` | enumeration | active / paused / expired / cancelled |
| `hsc_subscription_eligible` | boolean | Meets criteria for plan offer |
| `hsc_subscription_renewal_date` | date | Next renewal date |
| `hsc_subscription_plan_name` | string | Plan tier label |
| `hsc_subscription_plan_amount` | number | Monthly/annual amount |
| `hsc_subscription_deliveries_last_12m` | number | Deliveries in trailing 12m |
| `hsc_subscription_payment_link` | string | Self-service payment update URL |
| `hsc_subscription_last4` | string | Last 4 digits of payment method |

#### Commercial Summary (for Redesign-Required emails)
| Property | Type | Purpose |
|----------|------|---------|
| `hsc_estimated_annual_spend_individual` | number | What they spend buying individually |
| `hsc_estimated_annual_spend_plan` | number | What they would spend on a plan |
| `hsc_estimated_plan_savings` | number | Individual minus plan |
| `hsc_customer_milestone_summary` | string | Pre-rendered milestone text |
| `hsc_anniversary_type` | enumeration | first_purchase / fitting / birthday |
| `hsc_vip_reward_choice` | string | Selected VIP reward |
| `hsc_specs_locked` | boolean | True when specs are finalized |
| `hsc_last_spec_summary` | string | Human-readable spec snapshot |

#### Consultation Context
| Property | Type | Purpose |
|----------|------|---------|
| `hsc_nearest_partner_location` | string | Nearest affiliated stylist/location |
| `hsc_has_local_partner` | boolean | Whether a nearby partner exists |
| `hsc_current_system_user` | boolean | Already wears a system |
| `hsc_preferred_language` | enumeration | en / fr / pt / es |

### Deal Properties — Must Create

#### Quote Context (for Consultation Recap Tokens)
| Property | Type | Purpose |
|----------|------|---------|
| `hsc_recommended_path` | enumeration | standard / remote_fitting / salon_partner |
| `hsc_quote_currency` | enumeration | USD / CAD / EUR / GBP |
| `hsc_quote_base_price` | number | Quoted unit price |
| `hsc_quote_shipping_price` | number | Shipping cost in customer currency |
| `hsc_quote_template_shipping_price` | number | Template kit shipping cost |
| `hsc_quote_down_payment` | number | Down payment amount |
| `hsc_quote_consultation_fee` | number | Consultation fee (if applicable) |
| `hsc_quote_fitting_fee_estimate` | number | Estimated fitting service cost |
| `hsc_quote_maintenance_fee_estimate` | number | Estimated maintenance service cost |
| `hsc_quote_base_type` | enumeration | lace / skin / mono / hybrid / frontal |
| `hsc_quote_density_percent` | number | Quoted density |
| `hsc_quote_hair_type` | enumeration | remy / virgin / synthetic / blend |
| `hsc_quote_plan_3_monthly_price` | number | 3-unit plan monthly price |
| `hsc_quote_plan_4_monthly_price` | number | 4-unit plan monthly price |
| `hsc_quote_plan_6_monthly_price` | number | 6-unit plan monthly price |

### Ticket Properties — Must Create

| Property | Type | Purpose |
|----------|------|---------|
| `hsc_consultation_completed_at` | datetime | Timestamp of completed consultation |
| `hsc_consultation_variant` | enumeration | standard / no_local / current_user / front_partial |

---

## Programmable Modules (4 Reusable Blocks)

### Module 1: `hsc_goal_based_recommendation_block`

**Used in:** J1-E3
**Input:** `contact.hsc_primary_goal`
**Logic:**

```hubl
{%- if contact.hsc_primary_goal == "realism" -%}
  {# Lace-forward recommendation content #}
{%- elif contact.hsc_primary_goal == "durability" -%}
  {# Skin/mono recommendation content #}
{%- elif contact.hsc_primary_goal == "active_lifestyle" -%}
  {# Hybrid/sport-rated recommendation content #}
{%- else -%}
  {# General overview of all base types #}
{%- endif -%}
```

### Module 2: `hsc_base_type_guidance_block`

**Used in:** J3-E2, J3-E7, J4-E2, J5-E2, J7-E2
**Input:** `contact.hsc_base_preference` or `deal.hsc_quote_base_type`
**Logic:** Renders base-type-specific preparation, removal, styling, and reorder guidance. This is the most-reused programmable module.

```hubl
{%- set base = contact.hsc_base_preference -%}
{%- if base == "french_lace" or base == "swiss_lace" -%}
  {# Lace-specific care, removal, and longevity guidance #}
{%- elif base == "thin_skin" or base == "poly" -%}
  {# Skin-specific care, removal, and longevity guidance #}
{%- elif base == "mono" -%}
  {# Mono-specific guidance #}
{%- elif base == "hybrid" -%}
  {# Hybrid-specific guidance #}
{%- else -%}
  {# Generic guidance #}
{%- endif -%}
```

### Module 3: `hsc_lifespan_next_step_block`

**Used in:** J3-E8, J4-E2
**Input:** `contact.hsc_last_known_system_family`, `contact.hsc_predicted_reorder_date`, `contact.hsc_density_preference`
**Logic:** Shows lifespan timeline, reorder timing, and next-step recommendation based on current system state.

### Module 4: `hsc_customer_snapshot_block`

**Used in:** J5-E1 (redesigned), J8-E1 (redesigned)
**Input:** Precomputed summary fields on contact
**Logic:** Renders a customer success summary (orders, milestones, spec history) from pre-resolved contact properties. No real-time CRM lookups.

---

## Build Phases

### Phase 0: Foundation Audit

**Goal:** Confirm current state and close gaps before building.

| Task | Details |
|------|---------|
| 0.1 | Audit live `hsc_` contact properties against the gap list above. Identify which already exist, which need creation |
| 0.2 | Audit live `hsc_` deal properties against the quote-context gap list |
| 0.3 | Audit live `hsc_` ticket properties — confirm `hsc_consultation_completed_at` and `hsc_consultation_variant` are missing |
| 0.4 | Verify enum values for existing properties: `hsc_customer_class`, `hsc_experience_level`, `hsc_primary_goal`, `hsc_base_preference` — ensure they match the values assumed by the programmable module logic |
| 0.5 | Confirm which of the 63 existing emails in HubSpot overlap with J1-J8 journey emails |
| 0.6 | Inventory existing workflows from `WORKFLOW_DEPLOYMENT_GUIDE.md` and map to journey workflow groups |

**Output:** `audit-report.md` with exact create/update/skip decisions for every property and every existing email asset.

**Blocked by:** Nothing. Can start immediately.

---

### Phase 1: Property Layer

**Goal:** Create all missing CRM properties needed by the email system.

| Task | Object | Count | Details |
|------|--------|-------|---------|
| 1.1 | Contact | ~16 | Order/reorder summary, subscription summary, commercial summary, consultation context |
| 1.2 | Deal | ~15 | Quote context properties for consultation recap tokens |
| 1.3 | Ticket | 2 | `hsc_consultation_completed_at`, `hsc_consultation_variant` |
| 1.4 | Validation | — | Run `search_properties` for each new property to confirm creation |

**Implementation:** Script in `scripts/create_email_properties.py` using HubSpot API. Group all email-related properties under a dedicated property group (`Email System Properties` or similar).

**Blocked by:** Phase 0 audit (to avoid creating duplicates).

---

### Phase 2: Workflow Helper Computation

**Goal:** Build the precomputation workflows that resolve business logic into contact properties before email send.

| Task | Computation | Source | Target Property |
|------|-------------|--------|-----------------|
| 2.1 | Predicted reorder date | Base type wear schedule + last order date | `hsc_predicted_reorder_date` |
| 2.2 | Reorder window open | Current date vs predicted reorder date | `hsc_reorder_window_open` |
| 2.3 | Total orders (12m) | Order association count, trailing 12 months | `hsc_total_orders_last_12m` |
| 2.4 | Total orders (lifetime) | Order association count, all time | `hsc_total_orders_lifetime` |
| 2.5 | Subscription eligibility | 3+ orders in 12m AND no active subscription | `hsc_subscription_eligible` |
| 2.6 | Estimated plan savings | Individual spend vs plan pricing | `hsc_estimated_plan_savings` |
| 2.7 | Subscription mirror | Shopify subscription data → contact properties | `hsc_subscription_status`, `hsc_subscription_renewal_date`, etc. |
| 2.8 | Customer milestone summary | Order history + anniversary logic | `hsc_customer_milestone_summary` |

**Implementation options:**
- HubSpot Operations Hub workflows (copy/compute actions)
- External Cloudflare Worker triggered by deal/order webhooks
- Scheduled sync script for batch computation

**Blocked by:** Phase 1 (properties must exist before workflows can write to them).

---

### Phase 3: Template System

**Goal:** Build the base layout, 4 programmable modules, and all email templates.

#### 3.1 Base Layout

Create a single coded email base template in HubSpot Design Manager:
- Hair Solutions brand header
- Responsive single-column body area with module drop zones
- Footer with CAN-SPAM compliance, unsubscribe, social links
- `isEnabledForEmailV3Rendering: true` for programmable modules

#### 3.2 Programmable Modules

| Module | Priority | Complexity |
|--------|----------|------------|
| `hsc_goal_based_recommendation_block` | High | Low — single property branch |
| `hsc_base_type_guidance_block` | High | Medium — multiple base types, reused in 5 emails |
| `hsc_lifespan_next_step_block` | Medium | Medium — multiple property inputs |
| `hsc_customer_snapshot_block` | Low | High — depends on Phase 2 precomputation |

Build in HubSpot Design Manager as coded modules. Each module:
- Lives in `@hubspot/programmable-emails/modules/`
- Has a `module.html` (HubL), `module.css`, and `meta.json`
- Accepts field inputs from the parent template
- Falls back gracefully when property values are empty

#### 3.3 Standard Templates

Build as drag-and-drop or simple coded templates using the base layout. No HubL CRM functions needed.

#### 3.4 Workflow-Triggered Templates

Build as automation emails in HubSpot. Simpler than programmable — triggered by workflows, use standard tokens.

**Blocked by:** Phase 1 (properties), Phase 2 (for snapshot module only).

---

### Phase 4: Journey Rollout

**Rollout order (revenue impact descending):**

#### Wave 1: Revenue-Critical (Weeks 1-3)

**Journey 3 — New Customer Onboarding (8 emails)**

| Email | Class | Module Used | Trigger |
|-------|-------|-------------|---------|
| J3-E1 Order Confirmation | W | — | Deal closed won |
| J3-E2 Preparation Guide | P | `hsc_base_type_guidance_block` | Day 2-3 post order |
| J3-E3 Shipping Notification | W | — | Fulfillment shipped |
| J3-E4 Arrival Check-In | W | — | Day 1 post expected delivery |
| J3-E5 Maintenance Week 1 | W | — | Day 3 post delivery confirmation |
| J3-E6 Maintenance Week 2 | W | — | Day 7 post delivery |
| J3-E7 Styling and Removal | P | `hsc_base_type_guidance_block` | Day 14 post delivery |
| J3-E8 Review & Next Steps | P | `hsc_lifespan_next_step_block` | Day 21 post delivery |

**Workflow group:** First-order onboarding sequence. Branch on shipment, arrival issue, engagement.

#### Wave 2: Lead Conversion (Weeks 3-4)

**Journey 1 — Initial Arrival & Discovery (5 emails)**

| Email | Class | Module Used | Trigger |
|-------|-------|-------------|---------|
| J1-E1 Welcome & Resource Delivery | S | — | Quiz / lead magnet submission |
| J1-E2 Brand Story | S | — | Day 2 after E1 |
| J1-E3 Base Types Educational | P | `hsc_goal_based_recommendation_block` | Day 4 after E1 |
| J1-E4 Social Proof Wall | S | — | Day 7 after E1 |
| J1-E5 Consultation Invitation | S | — | Day 10 after E1 |

**Workflow group:** Lead nurture → routes to active qualification on engagement.

#### Wave 3: Retention & Recovery (Weeks 4-5)

**Journey 7 — Win-Back (4 emails)**

| Email | Class | Module Used | Trigger |
|-------|-------|-------------|---------|
| J7-E1 Human Note | S | — | 90d inactivity |
| J7-E2 What's New | P | `hsc_base_type_guidance_block` | Day 7 after E1 |
| J7-E3 Specific Offer | S | — | Day 14 after E1 |
| J7-E4 Sunset Notice | S | — | Day 21 after E1 |

**Journey 4 — Second Purchase Momentum (3 emails)**

| Email | Class | Module Used | Trigger |
|-------|-------|-------------|---------|
| J4-E1 Mid-Cycle Care Check | W | — | 45d post shipment (base-adjusted) |
| J4-E2 Replacement Nudge | P | `hsc_base_type_guidance_block` + `hsc_lifespan_next_step_block` | 15d before predicted wear-out |
| J4-E3 Loyalty Hook | W | — | No engagement after E2 |

#### Wave 4: Top-of-Funnel (Week 5)

**Journey 2 — Newsletter Nurture (5 emails)**

All standard marketing emails. No programmable content. Fast to build, easy to test and iterate.

#### Wave 5: Commerce & Subscription (Weeks 6-8)

**Journey 8 — Annual Renewal (4 emails)**

| Email | Class | Notes |
|-------|-------|-------|
| J8-E1 30-Day Success Snapshot | R | Requires Phase 2 subscription mirror + `hsc_customer_snapshot_block` |
| J8-E2 14-Day Heads-Up | W | Standard workflow |
| J8-E3 7-Day Urgency | W | Standard workflow |
| J8-E4 Final Confirmation | W | Standard workflow |

**Journey 6 — Subscription Ascension (4 emails)**

| Email | Class | Notes |
|-------|-------|-------|
| J6-E1 Loyalty Acknowledgment | S | Standard |
| J6-E2 Math of Value | R | Requires Phase 2 savings computation |
| J6-E3 Peace of Mind | S | Standard |
| J6-E4 VIP Offer | S | Standard |

**Dunning (2 emails)** — Workflow-triggered, no programmable content.

#### Wave 6: Elite (Week 8+)

**Journey 5 — Multi-Purchase Elite Clienteling (4 emails)**

| Email | Class | Notes |
|-------|-------|-------|
| J5-E1 Annual Recap | R | Requires Phase 2 milestone computation + `hsc_customer_snapshot_block` |
| J5-E2 Artisan Update | P | `hsc_base_type_guidance_block` |
| J5-E3 Birthday/Anniversary | W | Date-triggered |
| J5-E4 VIP Maintenance Check-In | S | Plain text |

---

### Phase 5: Consultation Email Library (Track B)

**Goal:** Migrate the legacy OHHS consultation archive into a modern HubSpot sales email system.

**This is a separate track from lifecycle journeys.** It runs in parallel after Phase 1 deal properties are created.

#### 5.1 Core Consultation Recap (4 variants)

| Asset | Variant | Delivery Surface |
|-------|---------|-----------------|
| `consultation_recap_standard` | Standard path, local partner available | Sales template / SEND_EMAIL |
| `consultation_recap_no_local_partner` | No nearby affiliated location | Sales template / SEND_EMAIL |
| `consultation_recap_current_system_user` | Already wears a system | Sales template / SEND_EMAIL |
| `consultation_recap_front_partial` | Special base case | Sales template / SEND_EMAIL |

**Token normalization:** Replace all legacy `company.*` pricing tokens with deal-level quote properties:
- `{{ company.unit_base_cost }}` → `{{ deal.hsc_quote_base_price }}`
- `{{ company.shipping___usd }}` → `{{ deal.hsc_quote_shipping_price }}`
- `{{ company.n3_units_monthly___usd }}` → `{{ deal.hsc_quote_plan_3_monthly_price }}`
- Currency selection driven by `{{ deal.hsc_quote_currency }}` (single template, not 4 currency variants)

#### 5.2 Follow-Up Ladder (6 assets)

| Asset | Timing | Surface |
|-------|--------|---------|
| `consultation_followup_day_5` | 5d after recap, no reply | Sales template / SEND_EMAIL |
| `consultation_followup_day_10` | 10d after recap, no reply | Sales template / SEND_EMAIL |
| `consultation_followup_day_90` | 90d / reengagement eligible | Workflow-triggered |
| `consultation_followup_final_close_loop` | 10d after 90d followup | Workflow-triggered |
| `consultation_followup_day_5_current_system_user` | 5d, experienced user variant | Sales template / SEND_EMAIL |
| `consultation_followup_day_10_current_system_user` | 10d, experienced user variant | Sales template / SEND_EMAIL |

#### 5.3 Consultation Workflow Integration

```
Consultation completed (ticket stage = Recommendation Active)
  → hsc_consultation_completed_at set
  → Variant selected (standard / no_local / current_user / front_partial)
  → Recap email sent (manual via sales template or app card)
  → If no reply after 5d → followup_day_5
  → If no reply after 10d → followup_day_10
  → If deferred / no decision → qualification state = deferred
  → When reengagement_eligible_on reached → followup_day_90
  → If no reply → followup_final_close_loop
```

---

## Workflow Architecture

### Group 1: Lead & Nurture

| Workflow | Journeys | Trigger |
|----------|----------|---------|
| Initial Arrival Sequence | J1 | Quiz/lead magnet submission |
| Newsletter Nurture | J2 | Newsletter opt-in |
| J1→Qualification Router | — | Consultation CTA engagement |
| J1→J2 Fallback | — | No engagement after J1-E5 |

### Group 2: First-Order Onboarding

| Workflow | Journeys | Trigger |
|----------|----------|---------|
| Onboarding Sequence | J3 | Deal closed won (first order) |
| Shipment Branch | J3 | Fulfillment status change |
| Delivery Follow-Up | J3 | Expected delivery date reached |
| Post-Delivery Education | J3 E5-E8 | Delivery confirmation + time delays |

### Group 3: Reorder & Reengagement

| Workflow | Journeys | Trigger |
|----------|----------|---------|
| Reorder Timing | J4 | `hsc_predicted_reorder_date` approaching |
| Win-Back Sequence | J7 | 90d inactivity + not suppressed |
| Suppression & Cooldown | — | Sunset reached or manual suppress |

### Group 4: High-Value & Subscription

| Workflow | Journeys | Trigger |
|----------|----------|---------|
| Subscription Ascension | J6 | 3 orders in 12m + not subscribed |
| Renewal Sequence | J8 | 30d before `hsc_subscription_renewal_date` |
| Dunning Sequence | Dunning | Payment failure event |
| VIP/Elite Touches | J5 | Order count >= 3, anniversary dates |

### Group 5: Consultation & Active Sales

| Workflow | Assets | Trigger |
|----------|--------|---------|
| Consultation Recap Router | Recap variants | `hsc_consultation_completed_at` set |
| Consultation Follow-Up | Day 5/10 | Time after recap, no reply |
| Deferred Reengagement | Day 90 / Close-loop | `hsc_reengagement_eligible_on` reached |

### Cross-Journey Routing Rules

| Event | Route To |
|-------|----------|
| J1 contact engages consultation CTA | Active qualification → Deal pipeline |
| J1 no engagement after E5 | J2 Newsletter Nurture |
| J3 completes → reorder date approaches | J4 Second Purchase |
| J4 no engagement | J7 Win-Back (90d inactivity) |
| J4 second order placed | J3 abbreviated repeat OR J5 if 3+ orders |
| J5 qualifies (3+ orders / 12m) | J6 Subscription Ascension |
| J6 activates subscription | J8 Annual Renewal cycle |
| J6 declines | Continue J5 Elite Clienteling |
| J7 reactivates | J4 or J5 based on order count |
| J7 sunset reached | Suppress 60d, newsletter-only |
| J8 payment fails | Dunning sequence |
| J8 cancels | J7 Win-Back (subscription-aware) |

---

## Master Email Classification Table

| Journey | Email | Class | Module | Trigger | Status |
|---------|-------|-------|--------|---------|--------|
| J1 | E1 Welcome | S | — | Quiz/form | Ready |
| J1 | E2 Brand Story | S | — | Day 2 | Ready |
| J1 | E3 Base Types | P | goal_recommendation | Day 4 | Ready |
| J1 | E4 Social Proof | S | — | Day 7 | Ready |
| J1 | E5 Consultation Invite | S | — | Day 10 | Ready |
| J2 | E1 Newsletter Welcome | S | — | Newsletter opt-in | Ready |
| J2 | E2 How Systems Work | S | — | Day 3 | Ready |
| J2 | E3 Style Inspiration | S | — | Day 7 | Ready |
| J2 | E4 Maintenance Tips | S | — | Day 14 | Ready |
| J2 | E5 Soft Consult Invite | S | — | Day 21 | Ready |
| J3 | E1 Order Confirmation | W | — | Deal closed won | Ready |
| J3 | E2 Prep Guide | P | base_type_guidance | Day 2-3 | Ready |
| J3 | E3 Shipping | W | — | Shipped | Ready |
| J3 | E4 Arrival Check-In | W | — | +1d delivery | Ready |
| J3 | E5 Maintenance Wk 1 | W | — | +3d delivery | Ready |
| J3 | E6 Maintenance Wk 2 | W | — | +7d delivery | Ready |
| J3 | E7 Styling/Removal | P | base_type_guidance | +14d delivery | Ready |
| J3 | E8 Review & Next | P | lifespan_next_step | +21d delivery | Ready |
| J4 | E1 Mid-Cycle Care | W | — | 45d post ship | Ready |
| J4 | E2 Replacement Nudge | P | base_type + lifespan | -15d reorder | Ready |
| J4 | E3 Loyalty Hook | W | — | No engagement | Ready |
| J5 | E1 Annual Recap | R | customer_snapshot | Anniversary | Blocked (Phase 2) |
| J5 | E2 Artisan Update | P | base_type_guidance | Quarterly | Ready |
| J5 | E3 Birthday/Anniversary | W | — | Date trigger | Ready |
| J5 | E4 VIP Check-In | S | — | Bi-annual | Ready |
| J6 | E1 Loyalty Ack | S | — | 3 orders/12m | Ready |
| J6 | E2 Math of Value | R | — | Day 3 after E1 | Blocked (Phase 2) |
| J6 | E3 Peace of Mind | S | — | Day 5 after E1 | Ready |
| J6 | E4 VIP Offer | S | — | Day 7 after E1 | Ready |
| J7 | E1 Human Note | S | — | 90d inactive | Ready |
| J7 | E2 What's New | P | base_type_guidance | +7d | Ready |
| J7 | E3 Specific Offer | S | — | +14d | Ready |
| J7 | E4 Sunset Notice | S | — | +21d | Ready |
| J8 | E1 Success Snapshot | R | customer_snapshot | -30d renewal | Blocked (Phase 2) |
| J8 | E2 14d Heads-Up | W | — | -14d renewal | Ready |
| J8 | E3 7d Urgency | W | — | -7d renewal | Ready |
| J8 | E4 Final Confirm | W | — | -1d renewal | Ready |
| Dunning | D1 Payment Failed | W | — | Payment failure | Ready |
| Dunning | D2 Grace Period | W | — | 48h unresolved | Ready |

---

## File Structure

```
programmable-emails/
├── PLAN.md                          ← This file
├── CLAUDE.md                        ← Agent instructions for this project
├── audit-report.md                  ← Phase 0 output (to be created)
│
├── scripts/
│   ├── create_email_properties.py   ← Phase 1: Create missing CRM properties
│   ├── audit_properties.py          ← Phase 0: Audit existing vs required
│   └── validate_enum_values.py      ← Phase 0: Confirm enum option alignment
│
├── modules/                         ← Phase 3: HubL programmable module source
│   ├── hsc_goal_based_recommendation_block/
│   │   ├── module.html
│   │   ├── module.css
│   │   └── meta.json
│   ├── hsc_base_type_guidance_block/
│   │   ├── module.html
│   │   ├── module.css
│   │   └── meta.json
│   ├── hsc_lifespan_next_step_block/
│   │   ├── module.html
│   │   ├── module.css
│   │   └── meta.json
│   └── hsc_customer_snapshot_block/
│       ├── module.html
│       ├── module.css
│       └── meta.json
│
├── templates/                       ← Phase 3: Email template source
│   ├── base-layout.html             ← Shared coded email layout
│   ├── programmable/                ← P-class email templates
│   ├── standard/                    ← S-class email templates
│   └── workflow/                    ← W-class email templates
│
├── consultation/                    ← Phase 5: Track B consultation library
│   ├── recaps/
│   │   ├── standard.md
│   │   ├── no_local_partner.md
│   │   ├── current_system_user.md
│   │   └── front_partial.md
│   ├── followups/
│   │   ├── day_5.md
│   │   ├── day_10.md
│   │   ├── day_90.md
│   │   ├── final_close_loop.md
│   │   ├── day_5_current_user.md
│   │   └── day_10_current_user.md
│   └── token_mapping.md            ← Legacy → modern token normalization
│
└── workflows/                       ← Phase 4: Workflow specs
    ├── group1_lead_nurture.md
    ├── group2_onboarding.md
    ├── group3_reorder_reengagement.md
    ├── group4_subscription_renewal.md
    └── group5_consultation_sales.md
```

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Overusing programmable rendering | Slow sends, no A/B testing, reliability issues | Only 7 of 39 emails use HubL conditionals |
| Simulating Enterprise patterns on Pro | Implementation debt, fragile lookups | All business logic precomputed into properties, not computed in templates |
| Mixing workflow logic with template logic | Hard to debug, split ownership | Strict rule: workflows compute, templates render |
| Subscription data not reliably mirrored | J6-E2, J8-E1 blocked | Phase 2 builds the mirror; J6-E2 and J8-E1 deferred until mirror is stable |
| Legacy token model copied directly | Brittle multi-currency pricing | Normalize to deal-level quote properties with single `hsc_quote_currency` selector |
| Consultation recaps over-automated | Lose founder-led personal touch | Day 5/10 follow-ups stay as sales templates (manual send), only day 90+ goes to workflow |

---

## Quick Reference: Immediate Wins

These 4 programmable modules can be built right now with existing properties:

1. **J1-E3** — `hsc_goal_based_recommendation_block` using `contact.hsc_primary_goal` (exists)
2. **J3-E2** — `hsc_base_type_guidance_block` using `contact.hsc_base_preference` (exists)
3. **J7-E2** — `hsc_base_type_guidance_block` using `contact.hsc_base_preference` (exists)
4. **J4-E2** — `hsc_base_type_guidance_block` + timing from `contact.hsc_reorder_readiness` (exists)

These 6 consultation assets can start after Phase 1 deal properties:

1. `consultation_recap_standard`
2. `consultation_recap_no_local_partner`
3. `consultation_followup_day_5`
4. `consultation_followup_day_10`
5. `consultation_followup_day_90`
6. `consultation_followup_final_close_loop`

---

## Source Documents

- [Programmable Email Synthesis and Implementation Plan](../../06_knowledge/00-master-vault/30-sales/programmable-email-synthesis-and-implementation-plan.md)
- [Consultation Email Library and Migration Plan](../../06_knowledge/00-master-vault/30-sales/consultation-email-library-and-migration-plan.md)
- [HubSpot Email Template Source Index](../../06_knowledge/00-master-vault/30-sales/hubspot-email-template-source-index.md)
- [Email Journey Implementation Summary](../../06_knowledge/00-master-vault/30-sales/sales-communication-and-personas/email-journeys/email-journey-implementation-summary.md)
- [Email Journey Token Reference](../../06_knowledge/00-master-vault/30-sales/sales-communication-and-personas/email-journeys/email-journey-token-reference.md)
- [Email Campaign Pipeline Summary](../../10-marketing/email/PIPELINE_SUMMARY.md)
