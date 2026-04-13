# Programmable Emails — Agent Instructions

## What This Project Is

HubSpot programmable email system for Hair Solutions Co. Two tracks:

- **Track A:** 39 lifecycle emails across 8 customer journeys (J1-J8 + dunning)
- **Track B:** 10 consultation/active-sales email assets migrated from legacy OHHS archive

## Platform

- HubSpot Marketing Hub Professional (NOT Enterprise)
- No HubDB or custom objects in email HubL
- No A/B testing on programmable emails
- CRM data available: contacts, companies, products (standard objects only)

## Key Files

- `PLAN.md` — Complete implementation plan with phases, property gaps, module specs, rollout order
- `audit-report.md` — Phase 0 output (property audit results)
- `modules/` — HubL programmable module source code
- `templates/` — Email template source (base layout + per-class templates)
- `consultation/` — Track B consultation library (recaps, follow-ups, token mapping)
- `scripts/` — Property creation, audit, and validation scripts
- `workflows/` — Workflow specification documents

## Architecture Rules

1. **Workflows compute, templates render.** Never compute business logic inside email HubL.
2. **Precompute everything.** Order counts, reorder timing, subscription state, savings math — all resolved into contact/deal properties before the email sends.
3. **Only 7 of 39 emails are programmable.** The rest are standard or workflow-triggered. Do not over-engineer.
4. **4 reusable modules, not 7 unique templates.** The programmable modules are shared across emails.
5. **Consultation recaps are sales templates, not marketing emails.** Day 5/10 follow-ups stay manual. Only day 90+ goes to workflow automation.

## CRM Properties

Many `hsc_` properties already exist. Before creating any property, search HubSpot first using `search_properties` to avoid duplicates. See PLAN.md "Property Gap Analysis" for the complete list of what exists vs what must be created.

## HubSpot Skills Available

Use these skills when working on this project:
- `hubspot-developer` — Agent Tools, coded modules, Design Manager, hsmeta.json
- `hubspot-crm-model` — Objects, properties, pipelines
- `hubspot-business-ops` — Automation strategy, workflows, customer journey
- `hubspot-how-to` — Step-by-step HubSpot UI tasks
- `hubspot-ai-expert` — Breeze, Agent Tools, Custom Channels (not directly relevant here but available)

## Existing Infrastructure

- 63 emails already live in HubSpot (built via YAML pipeline in `10-marketing/email/`)
- 20 active lists defined but need manual HubSpot creation
- 11 workflows documented but need configuration
- Contact scoring scripts ready in `10-marketing/email/scripts/`

## HubL Conventions

- Whitespace control: `{%- -%}` always
- Token defaults: `{{ contact.firstname | default("there") }}` for names
- Empty-value strategy: use workflow enrollment filters, not template defaults, when missing data means the email should not send
- Module fields: every module must fall back gracefully when input properties are empty
