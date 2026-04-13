# Property Audit Report

**Date:** 2026-04-07
**Phase:** Phase 0 — Foundation Audit
**Status:** Complete

---

## Summary

| Category | Count | Decision |
|----------|-------|----------|
| Contact properties confirmed existing | 15 | Keep / use as-is |
| Contact properties — create (Priority 1) | 8 | Create in Phase 1 |
| Contact properties — create (Priority 2) | 16 | Create in Phase 1 |
| Contact properties — native HubSpot substitute | 2 | Use native, skip custom |
| Deal properties — create (quote context) | 15 | Create in Phase 1 |
| Ticket properties — create | 2 | Create in Phase 1 |
| **Total to create** | **41** | |

---

## Section 1: Contact Properties

### 1.1 Confirmed Existing (KEEP)

These are live in HubSpot. No action needed.

| Property | Label | Type | Notes |
|----------|-------|------|-------|
| `hsc_customer_class` | HSC Customer Class | enumeration | Values: first_time_lead, returning_customer, active_customer, other |
| `hsc_experience_level` | HSC Experience Level | enumeration | Values: first_system, some_experience, experienced_wearer |
| `hsc_relationship_state` | HSC Relationship State | enumeration | Exists |
| `hsc_primary_goal` | HSC Primary Goal | enumeration | Values: realism, durability, easy_cleanup, fast_replacement, budget_control, help_deciding, issue_resolution |
| `hsc_preferred_channel` | HSC Preferred Channel | enumeration | Exists |
| `hsc_reengagement_priority` | HSC Reengagement Priority | enumeration | Exists |
| `hsc_base_preference` | HSC Base Preference | enumeration | Values: nano_skin, micro_skin, thin_skin, dura_skin, swiss_lace, french_lace, mono, hybrid, undecided |
| `hsc_density_preference` | HSC Density Preference | enumeration | Exists |
| `hsc_attachment_preference` | HSC Attachment Preference | enumeration | Exists |
| `hsc_hair_type_preference` | HSC Hair Type Preference | enumeration | Exists |
| `hsc_last_known_system_family` | HSC Last Known System Family | string | Exists |
| `hsc_next_action_date` | HSC Next Action Date | date | Exists |
| `hsc_customer_health_score` | HSC Customer Health Score | number | Exists |
| `hsc_risk_band` | HSC Risk Band | enumeration | Exists |
| `hsc_reorder_readiness` | HSC Reorder Readiness | enumeration | Values: active_now, 30_days, 60_days, 90+_days, unknown, not_applicable |

### 1.2 Native HubSpot Properties — Use Instead of Creating Custom (SKIP CUSTOM)

| Intended custom property | Use this native instead | Reason |
|--------------------------|------------------------|--------|
| `hsc_last_order_date` | `hs_recent_closed_order_date` | Auto-set by HubSpot, same data |
| `hsc_predicted_reorder_date` | `next_expected_reorder_date` | Already exists, same concept: "Projected next purchase date based on reorder cycle and last purchase" |
| `hsc_preferred_language` | `hs_language` | HubSpot native preferred language property |

**Additional existing properties that may eliminate other work:**
- `reorder_due_date` — "last_purchase_date + reorder_cycle_days" — can substitute for reorder window logic
- `reorder_cycle_days` — base-type wear schedule can be precomputed here
- `days_since_last_order` — useful in workflow enrollment filters
- `total_lifetime_spend` — tracks spend, not order count

### 1.3 Contact Properties to Create — Priority 1 (Required for "Ready" Emails)

These are needed immediately for modules and consultation track.

| Property | Label | Type | Options / Notes |
|----------|-------|------|-----------------|
| `hsc_reorder_window_open` | HSC Reorder Window Open | boolean | True when within reorder window; used in J4 enrollment |
| `hsc_reorder_message_angle` | HSC Reorder Message Angle | enumeration | Options: refresh / upgrade / loyalty / default |
| `hsc_total_orders_last_12m` | HSC Total Orders Last 12m | number | Rolling 12-month order count; used for J5/J6 eligibility |
| `hsc_total_orders_lifetime` | HSC Total Orders Lifetime | number | Lifetime order count; used for J5 elite routing |
| `hsc_last_order_value` | HSC Last Order Value | number | Last order total in USD; used in commercial summary |
| `hsc_current_system_user` | HSC Current System User | boolean | True if contact already wears a hair system |
| `hsc_has_local_partner` | HSC Has Local Partner | boolean | True if a nearby affiliated stylist/location exists |
| `hsc_nearest_partner_location` | HSC Nearest Partner Location | string | Name/city of nearest affiliated location |

### 1.4 Contact Properties to Create — Priority 2 (Required for Redesign-Required Emails)

These unblock J5-E1, J6-E2, and J8-E1. Create in Phase 1 so they're ready when Phase 2 computation workflows are built.

**Subscription mirror:**

| Property | Label | Type | Options / Notes |
|----------|-------|------|-----------------|
| `hsc_subscription_status` | HSC Subscription Status | enumeration | Options: active / paused / unpaid / expired / cancelled / none |
| `hsc_subscription_eligible` | HSC Subscription Eligible | boolean | True when meets criteria for plan offer |
| `hsc_subscription_renewal_date` | HSC Subscription Renewal Date | date | Next renewal date |
| `hsc_subscription_plan_name` | HSC Subscription Plan Name | string | e.g. "3-Unit Plan", "6-Unit Plan" |
| `hsc_subscription_plan_amount` | HSC Subscription Plan Amount | number | Recurring plan amount |
| `hsc_subscription_deliveries_last_12m` | HSC Subscription Deliveries Last 12m | number | Units delivered in trailing 12 months |
| `hsc_subscription_payment_link` | HSC Subscription Payment Link | string | Self-service payment update URL |
| `hsc_subscription_last4` | HSC Subscription Last 4 | string | Last 4 digits of payment card on file |

**Commercial summary:**

| Property | Label | Type | Notes |
|----------|-------|------|-------|
| `hsc_estimated_annual_spend_individual` | HSC Estimated Annual Spend (Individual) | number | What they spend buying individually (12m projection) |
| `hsc_estimated_annual_spend_plan` | HSC Estimated Annual Spend (Plan) | number | What a plan would cost them annually |
| `hsc_estimated_plan_savings` | HSC Estimated Plan Savings | number | Individual minus plan annual cost |
| `hsc_customer_milestone_summary` | HSC Customer Milestone Summary | string | Pre-rendered milestone text for J5-E1/J8-E1 |
| `hsc_anniversary_type` | HSC Anniversary Type | enumeration | Options: first_purchase / fitting / birthday |
| `hsc_vip_reward_choice` | HSC VIP Reward Choice | string | Selected VIP reward from J5-E3 |
| `hsc_specs_locked` | HSC Specs Locked | boolean | True when hair system specs are finalized on contact |
| `hsc_last_spec_summary` | HSC Last Spec Summary | string | Human-readable spec snapshot (base, density, hair type) |

---

## Section 2: Deal Properties

### 2.1 Confirmed Existing (KEEP)

| Property | Label | Notes |
|----------|-------|-------|
| `hsc_deal_type` | HSC Deal Type | Exists |
| `hsc_quote_status` | HSC Quote Status | Exists |
| `hsc_quote_version` | HSC Quote Version | Exists |
| `hsc_payment_path` | HSC Payment Path | Exists |
| `hsc_spec_lock_status` | HSC Spec Lock Status | Exists (deal-level spec lock) |
| `hsc_confirm_factory_order_placed` | HSC Confirm Factory Order Placed | Exists |
| `hsc_reengagement_eligible_on` | HSC Reengagement Eligible On | Exists |
| `hsc_lost_reason_primary` | HSC Lost Reason Primary | Exists |
| `hsc_lost_reason_secondary` | HSC Lost Reason Secondary | Exists |
| `hsc_exception_flag` | HSC Exception Flag | Exists |

### 2.2 Deal Properties to Create — Quote Context (for Consultation Recap Tokens)

All 15 are missing. Needed for Track B consultation email token normalization.

| Property | Label | Type | Notes |
|----------|-------|------|-------|
| `hsc_recommended_path` | HSC Recommended Path | enumeration | Options: standard / remote_fitting / salon_partner |
| `hsc_quote_currency` | HSC Quote Currency | enumeration | Options: USD / CAD / EUR / GBP |
| `hsc_quote_base_price` | HSC Quote Base Price | number | Unit price in customer currency |
| `hsc_quote_shipping_price` | HSC Quote Shipping Price | number | Shipping cost in customer currency |
| `hsc_quote_template_shipping_price` | HSC Quote Template Shipping Price | number | Template kit shipping cost |
| `hsc_quote_down_payment` | HSC Quote Down Payment | number | Down payment amount |
| `hsc_quote_consultation_fee` | HSC Quote Consultation Fee | number | Consultation fee (if applicable) |
| `hsc_quote_fitting_fee_estimate` | HSC Quote Fitting Fee Estimate | number | Estimated fitting service fee |
| `hsc_quote_maintenance_fee_estimate` | HSC Quote Maintenance Fee Estimate | number | Estimated maintenance service fee |
| `hsc_quote_base_type` | HSC Quote Base Type | enumeration | Options: nano_skin / micro_skin / thin_skin / dura_skin / swiss_lace / french_lace / mono / hybrid |
| `hsc_quote_density_percent` | HSC Quote Density % | number | Quoted density (e.g. 80, 100, 120) |
| `hsc_quote_hair_type` | HSC Quote Hair Type | enumeration | Options: remy / virgin / synthetic / blend |
| `hsc_quote_plan_3_monthly_price` | HSC Quote Plan 3 Monthly Price | number | 3-unit plan monthly price |
| `hsc_quote_plan_4_monthly_price` | HSC Quote Plan 4 Monthly Price | number | 4-unit plan monthly price |
| `hsc_quote_plan_6_monthly_price` | HSC Quote Plan 6 Monthly Price | number | 6-unit plan monthly price |

---

## Section 3: Ticket Properties

### 3.1 Confirmed Existing (KEEP)

| Property | Notes |
|----------|-------|
| `hsc_inquiry_type` | Exists |
| `hsc_qualification_state` | Exists |
| `hsc_spec_readiness` | Exists |
| `hsc_primary_blocker` | Exists |
| `hsc_next_action_type` | Exists |
| `hsc_next_action_date` | Exists |
| `hsc_route_decision` | Exists |
| `hsc_escalation_level` | Exists |
| `hsc_relationship_state` | Exists |

### 3.2 Ticket Properties to Create

| Property | Label | Type | Notes |
|----------|-------|------|-------|
| `hsc_consultation_completed_at` | HSC Consultation Completed At | datetime | Timestamp of consultation completion; triggers recap send |
| `hsc_consultation_variant` | HSC Consultation Variant | enumeration | Options: standard / no_local_partner / current_system_user / front_partial |

---

## Section 4: Enum Value Notes for Programmable Modules

These are the confirmed live enum values modules must use.

### `hsc_primary_goal` — Used in `hsc_goal_based_recommendation_block` (J1-E3)

| Value | Label | Module content direction |
|-------|-------|--------------------------|
| `realism` | Realism | French/Swiss lace recommendation |
| `durability` | Durability | Thin skin / dura skin / mono recommendation |
| `easy_cleanup` | Easy Cleanup | Nano/micro skin recommendation |
| `fast_replacement` | Fast Replacement | Premade skin/hybrid recommendation |
| `budget_control` | Budget Control | Plan value framing + affordable base options |
| `help_deciding` | Help Deciding | Comparison overview of all base types |
| `issue_resolution` | Issue Resolution | Route to consultation / support CTA |

**Note:** The plan referenced an `active_lifestyle` value that does not exist in the live CRM. Use `durability` or `fast_replacement` as the closest match for that intent. Do not add a conditional branch for `active_lifestyle`.

### `hsc_base_preference` — Used in `hsc_base_type_guidance_block` (J3-E2/E7, J4-E2, J5-E2, J7-E2)

Live values are more granular than the plan assumed. Group for HubL conditionals:

| Group | Values | Module content direction |
|-------|--------|--------------------------|
| Lace | `swiss_lace`, `french_lace` | Lace care, removal technique, replacement cycle |
| Skin (ultra-thin) | `nano_skin`, `micro_skin` | Ultra-thin skin care, poly tape removal, cycle |
| Skin (standard) | `thin_skin`, `dura_skin` | Standard skin care, solvent guide, cycle |
| Mono | `mono` | Mono care, brushing, perimeter tape |
| Hybrid | `hybrid` | Combined lace/skin zone care |
| Undecided | `undecided` | Generic overview + consultation CTA |

### `hsc_experience_level` — Used for conditional depth adjustment (multiple emails)

| Value | Module direction |
|-------|-----------------|
| `first_system` | Full explanation, no assumed knowledge |
| `some_experience` | Moderate depth, skip absolute basics |
| `experienced_wearer` | Condensed, peer-to-peer tone, skip basics entirely |

### `hsc_reorder_readiness` — Used in J4 workflow enrollment

| Value | Meaning |
|-------|---------|
| `active_now` | Window open — trigger J4-E2 immediately |
| `30_days` | 30 days out — trigger mid-cycle check J4-E1 |
| `60_days` | 60 days out — trigger J4-E1 |
| `90+_days` | Too early — no email |
| `unknown` | No data — suppress |
| `not_applicable` | Not a system wearer — suppress |

---

## Section 5: Decision Summary for Phase 1 Script

### Properties to create (41 total)

```
CONTACT (24):
  Priority 1 (8): hsc_reorder_window_open, hsc_reorder_message_angle,
    hsc_total_orders_last_12m, hsc_total_orders_lifetime, hsc_last_order_value,
    hsc_current_system_user, hsc_has_local_partner, hsc_nearest_partner_location

  Priority 2 - Subscription (8): hsc_subscription_status, hsc_subscription_eligible,
    hsc_subscription_renewal_date, hsc_subscription_plan_name,
    hsc_subscription_plan_amount, hsc_subscription_deliveries_last_12m,
    hsc_subscription_payment_link, hsc_subscription_last4

  Priority 2 - Commercial (8): hsc_estimated_annual_spend_individual,
    hsc_estimated_annual_spend_plan, hsc_estimated_plan_savings,
    hsc_customer_milestone_summary, hsc_anniversary_type, hsc_vip_reward_choice,
    hsc_specs_locked, hsc_last_spec_summary

DEAL (15):
  hsc_recommended_path, hsc_quote_currency, hsc_quote_base_price,
  hsc_quote_shipping_price, hsc_quote_template_shipping_price, hsc_quote_down_payment,
  hsc_quote_consultation_fee, hsc_quote_fitting_fee_estimate,
  hsc_quote_maintenance_fee_estimate, hsc_quote_base_type, hsc_quote_density_percent,
  hsc_quote_hair_type, hsc_quote_plan_3_monthly_price, hsc_quote_plan_4_monthly_price,
  hsc_quote_plan_6_monthly_price

TICKET (2):
  hsc_consultation_completed_at, hsc_consultation_variant
```

### Properties to skip (use native instead)

```
hsc_last_order_date        → use hs_recent_closed_order_date
hsc_predicted_reorder_date → use next_expected_reorder_date
hsc_preferred_language     → use hs_language
```

### Modules: enum value adjustments needed

- Remove `active_lifestyle` branch from goal recommendation module (value does not exist)
- Expand base type guidance module to handle all 8 base type values with grouping
