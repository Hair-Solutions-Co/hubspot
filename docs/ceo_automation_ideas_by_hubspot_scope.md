# CEO automation ideas by HubSpot API scope

Generated against **161 scopes** on your current private-app token (`hubspot:token:scopes`). Each scope lists up to **three** script or workflow-style automations relevant to **daily CEO operations** (revenue, CX, risk, visibility—not exhaustive engineering tasks).

---

### account-info.security.read
- Weekly email summarizing account security posture flags for board / insurance questionnaires.
- Alert if SSO or 2FA policy changes vs your documented baseline.
- Audit trail export before high-stakes fundraising or acquisition diligence.

### accounting
- Nightly sync of HubSpot commerce/accounting-related records to your finance model (CSV → Sheets / BI).
- Exception report: orders/invoices out of sync with expected states.
- Month-end checklist automation: reconcile open balances against CRM pipeline stages.

### actions
- Inventory of custom workflow actions so you know what can break when you change stacks.
- Doc generator: map each action to owner and business purpose (governance).
- Pre-deploy diff when `hs project upload` changes action URLs.

### analytics.behavioral_events.send
- Server-side events for “CEO cares” milestones (consult booked, deposit paid) into HubSpot for attribution.
- Funnel QA: verify events fire on key storefront / portal paths.
- Cross-check event volume vs Shopify orders for a sanity dashboard.

### automation
- Catalog of active workflows with last-modified and owner (change-risk radar).
- “Freeze window” report before Black Friday: flag workflows touching discounts or inventory.
- Dry-run impact: count records that would enter a workflow if you toggled a enroll trigger.

### automation.sequences.enrollments.write
- Safe bulk enroll for a vetted list after campaign approval (with human gate in the script).
- Re-enroll stalled prospects who replied positively in inbox.
- Rollback helper: remove enrollments for a mistaken CSV upload.

### automation.sequences.read
- Morning digest: open sequence performance (reply/book rates) by sequence name.
- Compare sequence metrics week-over-week for leadership standup slides.
- Detect sequences with zero sends (broken enrollment or bad filters).

### behavioral_events.event_definitions.read_write
- Versioned definitions doc in-repo when you add new “hair journey” events.
- Lint: event names follow `namespace/object/action` convention.
- Alert if a definition is deprecated but still referenced in frontend code.

### business-intelligence
- Scheduled PDF/Slides-friendly metrics export for investor updates.
- Cross-object KPI sheet: deals + service tickets + NPS proxy fields.
- Anomaly detection: sudden drop in pipeline creation vs trailing average.

### cms.domains.read
- Domain SSL/expiry calendar pulled into a CEO calendar feed.
- List of connected domains for brand/compliance reviews.
- Pre-launch checklist: domain + redirect verification before a campaign.

### cms.domains.write
- Scripted staging domain attach for a new microsite (with approval token in CI).
- Rollback script after a bad DNS cutover.
- Audit log of domain changes monthly.

### cms.knowledge_base.articles.publish
- Publish queue: draft → review → publish with Slack approval for sensitive medical claims.
- Bulk unpublish outdated articles after product SKU changes.
- SEO sweep: flag articles without required disclaimers.

### cms.knowledge_base.articles.read
- Weekly “top articles by views” for CX prioritization.
- Export KB to offline PDF for legal review.
- Find articles linking to deprecated product URLs.

### cms.knowledge_base.articles.write
- AI-assisted draft pipeline with human medical review gate (your policy).
- Bulk update CTAs when a promo ends.
- Translation workflow stub (export strings → re-import).

### cms.knowledge_base.settings.read
- Snapshot KB settings before portal migration.
- Compare prod vs sandbox KB configuration.
- Settings change log for IT governance.

### cms.knowledge_base.settings.write
- Scripted enable/disable of customer-facing KB modules during incidents.
- Align KB categories with CRM ticket categories (naming sync).
- Rollback settings to last known-good JSON snapshot.

### cms.membership.access_groups.read
- Map membership tiers to customer segments for executive reporting.
- Audit who can see premium KB content.
- Identify orphaned access groups after org changes.

### cms.membership.access_groups.write
- Provision access when a customer hits “VIP” deal stage (with manual override file).
- Revoke access on chargeback or subscription cancel (paired with Shopify).
- Quarterly access review export for compliance.

### collector.graphql_query.execute
- Custom executive dashboard queries (deals + tickets + commerce) in one GraphQL doc.
- Data quality query: contacts missing critical fields for routing.
- Nightly cache of heavy queries to Sheets for mobile-friendly viewing.

### collector.graphql_schema.read
- Schema explorer markdown for your internal data council.
- Detect breaking schema changes after HubSpot updates.
- Validate that required fields exist before deploying a new workflow.

### communication_preferences.read
- Suppression report: opted-out channels by segment (SMS vs email).
- Pre-campaign audience estimate excluding unsubscribed contacts.
- Compliance evidence export for CAN-SPAM / CASL audits.

### communication_preferences.read_write
- Bulk fix communication preferences after a mistaken send (with legal sign-off).
- Sync preferences from Shopify customer marketing consent where allowed.
- Reconciliation job if signup forms diverged from CRM reality.

### communication_preferences.write
- Single-purpose script to set preferences from a signed customer service ticket outcome.
- Emergency global pause helper template (use rarely; CEO-approved).
- Preference migration when rebranding sender domains.

### content
- Asset inventory: landing pages + emails referencing outdated pricing.
- Content freshness score for leadership review.
- Link checker across HubSpot-hosted content.

### conversations.custom_channels.read
- Daily volume by custom channel (Concierge vs SMS) for capacity planning.
- SLA report for first-response time by channel.
- Escalation heatmap: which topics route to humans most.

### conversations.custom_channels.write
- Channel routing experiment: A/B route rules with measured outcomes.
- Temporary routing change during staffing shortages (time-boxed).
- Channel disable/enable runbook as scripts + checklist.

### conversations.read
- CEO digest: threads tagged “VIP,” “legal,” or “refund” in the last 24h.
- Queue depth alert if backlog exceeds threshold.
- Export conversations for training new CX leads.

### conversations.visitor_identification.tokens.create
- Tie anonymous chat to known contact after Shopify login (identity stitching).
- Fraud reduction: rate-limit token creation per IP.
- Measure identification success rate vs traffic.

### conversations.write
- Approved macro sender: post internal notes from Slack to a thread (careful governance).
- Escalation note template injection for sensitive cases.
- Close-loop tagging after resolution for analytics.

### crm.export
- Scheduled full-funnel export for backup / data warehouse landing zone.
- Object-specific export before a major property migration.
- GDPR-oriented export for a single data subject request (paired with legal process).

### crm.extensions_calling_transcripts.read
- Call transcript search for “competitor mentions” or “pricing objections.”
- Coaching pack: last 5 calls for a rep flagged by low win rate.
- Compliance sample: random call review for script adherence.

### crm.extensions_calling_transcripts.write
- Annotate or attach corrected transcript metadata after manual review (if your stack uses it).
- Redaction workflow integration stub (partner-dependent).
- Sync transcript availability flags to a custom “ready for QA” property.

### crm.import
- Bulk import cleaned partner lists after trade shows (dedupe rules in script).
- Re-import corrected CSV after a bad merge (with dry-run counts).
- Staging import to a “review” list before promotion to active segments.

### crm.lists.read
- Morning “lists touching revenue” snapshot: size and last-updated.
- Detect static lists that haven’t changed in 90 days (stale audiences).
- Cross-check list membership vs deal stage for campaign readiness.

### crm.lists.write
- Add contacts to a “CEO follow-up” list from a Google Sheet approval column.
- Remove churned customers from nurture lists automatically.
- Sync list membership from Shopify tags (one-way or bidirectional with care).

### crm.objects.appointments.read
- Executive calendar of high-value consultations booked this week.
- No-show risk list based on prior behavior properties.
- Utilization report for stylists / consultants if modeled as appointments.

### crm.objects.appointments.sensitive.read.v2
- Restricted weekly digest for leadership only (PII-minimized outputs).
- Secure audit log of who exported sensitive appointment fields.
- Pair with legal: retention policy enforcement reports.

### crm.objects.appointments.write
- Reschedule automation after shipping delays (customer comms + appointment update).
- Block double-booking checks before confirming VIP slots.
- Post-appointment satisfaction task creation.

### crm.objects.carts.read
- Abandoned cart rescue list for high-AOV contacts (CEO-approved discount rules).
- Cart value distribution for weekly revenue standup.
- Identify carts stuck on payment step (UX triage).

### crm.objects.carts.write
- Cart cleanup after order completion or cancel (hygiene).
- Apply loyalty credits via scripted cart adjustments (finance-approved).
- Emergency cart flag for suspected fraud (hold + notify).

### crm.objects.commercepayments.read
- Daily successful payment volume vs Shopify cash for reconciliation.
- Failed payment follow-up queue for CX.
- Payment method mix trends for leadership.

### crm.objects.commercepayments.write
- Refund orchestration script with dual approval for above-threshold amounts.
- Mark payment records after external processor webhooks.
- Correct mis-tagged payments after manual review.

### crm.objects.companies.highly_sensitive.read.v2
- Board-pack extracts with strict field allowlists and redaction.
- Secure pipeline by parent account for enterprise prospects.
- DLP-style logging when highly sensitive company fields are accessed.

### crm.objects.companies.read
- Top accounts by revenue, open tickets, and last touch (single view).
- Territory coverage map for partner/distributor accounts.
- Duplicate company detection report for MDM cleanup.

### crm.objects.companies.sensitive.read.v2
- Finance-sensitive fields only in closed finance Slack channel summaries.
- Credit-limit review queue for wholesale accounts.
- Segregated export for accountants (field-scoped).

### crm.objects.companies.write
- Bulk industry tagging from enrichment vendor CSV.
- Parent/child company linking after M&A of a salon group.
- Normalize billing addresses before tax season.

### crm.objects.contacts.highly_sensitive.read.v2
- Minimal necessary exports for legal holds with hash audit.
- VIP identification for white-glove routing without exposing full PII in logs.
- Secure “single customer view” for escalations only.

### crm.objects.contacts.read
- Daily new contacts from key sources with dedupe score.
- Lifecycle stage distribution for marketing–sales alignment meetings.
- Contact health score recompute inputs (engagement + orders + tickets).

### crm.objects.contacts.sensitive.read.v2
- Medical or sensitive note fields only for clinical/partner workflows (governance).
- Restricted cohort analysis for retention programs.
- Compliance-friendly extracts with field-level justification metadata.

### crm.objects.contacts.write
- Bulk update lifecycle stage from spreadsheet after event attendance.
- Tag contacts from webinar CSV with consent timestamp.
- Merge helper dry-run before human-approved merges.

### crm.objects.courses.read
- Training completion funnel for internal or partner education programs.
- Certificate earned → badge on partner record.
- Identify drop-off lessons for content improvements.

### crm.objects.courses.write
- Auto-enroll new hires in onboarding course objects when hired in HubSpot.
- Reset progress when role changes.
- Sync completion to badges visible to sales managers.

### crm.objects.custom.highly_sensitive.read.v2
- Controlled exports of sensitive custom objects (e.g., clinical notes IDs).
- Executive KPIs built only on aggregated custom object metrics when possible.
- Access reviews for who can query sensitive custom objects.

### crm.objects.custom.read
- Nightly custom object row counts per type (data quality).
- Join custom “hair system” objects to contacts for CX context panel.
- Pipeline of custom objects driving executive dashboards.

### crm.objects.custom.sensitive.read.v2
- Tiered reporting: aggregate metrics without row-level sensitive fields.
- Redacted samples for QA training.
- Alert on unusual spikes in sensitive custom record creation.

### crm.objects.custom.write
- Bulk update custom object stages after factory status change from ERP.
- Create custom object rows from Shopify metafields nightly.
- Backfill historical custom objects from legacy CSV.

### crm.objects.deals.highly_sensitive.read.v2
- Board-level pipeline with deal splits and discount sensitivity hidden in sub-reports.
- M&A data room exports with field allowlists.
- Restricted win/loss analysis including margin fields.

### crm.objects.deals.read
- Weekly pipeline by stage with aging and forecast category.
- Deal slippage report: pushed close dates.
- Source attribution rollup for marketing ROI reviews.

### crm.objects.deals.sensitive.read.v2
- Margin-aware forecast for inner leadership circle only.
- Discount approval queue sorted by impact.
- Competitive intel fields surfaced only to sales leadership.

### crm.objects.deals.write
- Auto-create follow-up tasks when deal stage changes to “proposal sent.”
- Bulk stage moves after a process change (with safeguards).
- Stamp “last CEO touch” property when you log an executive meeting.

### crm.objects.feedback_submissions.read
- NPS/CSAT theme extraction via export to review weekly.
- Route negative feedback to `#cx-escalations` with context.
- Product roadmap input: top requested improvements from feedback.

### crm.objects.forecasts.read
- Forecast vs actual monthly rollup for board slides.
- Team-level forecast accuracy scoring.
- Scenario sheet: forecast if top 10 deals close next week.

### crm.objects.goals.read
- OKR-style visibility: goals vs actuals for revenue and retention.
- Flag teams with goals far off track mid-quarter.
- Historical goal attainment for bonus planning.

### crm.objects.goals.write
- Quarterly goal reset templates from a canonical Sheet.
- Adjust targets after major market events (documented script + approval).
- Sync goal definitions to all-hands slides automatically.

### crm.objects.invoices.read
- DSO (days sales outstanding) trend for finance standups.
- Invoice dispute list cross-referenced with tickets.
- Cash timing forecast from open invoices.

### crm.objects.invoices.write
- Mark invoices paid from accounting system webhook.
- Issue credit memo workflow stub (paired with finance policy).
- Reconcile invoice totals vs line items nightly.

### crm.objects.leads.read
- Lead response time SLA by source (ads vs organic).
- Conversion rate from lead → MQL → SQL for weekly marketing review.
- Geographic heatmap of inbound leads.

### crm.objects.leads.write
- Round-robin assignment rules audit + fix script.
- Bulk disqualify leads matching competitor domains.
- Reassign leads when a rep leaves (with activity notes).

### crm.objects.line_items.read
- Average order composition (units, addons) for merchandising.
- Discount line detection report for margin protection.
- Bundle performance: which line item SKUs attach most often.

### crm.objects.line_items.write
- Correct line items after a catalog SKU migration.
- Apply promotional line items in bulk for approved B2B quotes.
- Sync line items from Shopify order webhook for parity checks.

### crm.objects.listings.read
- Marketplace or partner listing performance if you use listings objects.
- Availability vs pipeline for partner inventory coordination.
- Stale listing alerts.

### crm.objects.listings.write
- Bulk publish/unpublish listings during stockouts.
- Price sync from master sheet after leadership approval.
- Seasonal listing refresh automation.

### crm.objects.marketing_events.read
- Event ROI: registrations, attendance, influenced revenue.
- Compare webinar vs in-person event efficiency.
- List of attendees for executive thank-you notes.

### crm.objects.marketing_events.write
- Create events from a canonical marketing calendar CSV.
- Update attendance status from check-in app export.
- Close out events and trigger nurture workflows.

### crm.objects.orders.read
- Daily GMV and unfulfilled order backlog for CEO morning brief.
- Orders at risk (payment pending + high value).
- Shopify ↔ HubSpot order parity exceptions.

### crm.objects.orders.write
- Update order status from warehouse system events.
- Flag high-risk orders for manual review.
- Create order records from approved quotes (controlled).

### crm.objects.owners.read
- Coverage report: accounts per rep for capacity balancing.
- Identify orphaned records with no owner.
- Owner performance fair comparisons (normalized pipeline).

### crm.objects.partner-clients.read
- Partner-sourced revenue roll-up for channel strategy.
- Partner health score inputs (tickets, repeat orders).
- Top partners for executive QBRs.

### crm.objects.partner-clients.write
- Onboard new partner locations with templated records.
- Offboard partners with data hygiene scripts.
- Sync tier changes after quarterly reviews.

### crm.objects.partner-services.read
- Catalog of partner services offered vs attach rate.
- Margin by partner service line.
- Underperforming services flagged for sunsetting.

### crm.objects.partner-services.write
- Update service catalogs after training certifications.
- Bulk price adjustments on partner services (approved).
- Map new factory capabilities to partner service entries.

### crm.objects.products.read
- Product mix trends tied to campaigns.
- Identify products with high return rates (joined with tickets).
- SKU master vs CRM product sync audit.

### crm.objects.products.write
- Bulk activate/deactivate SKUs after inventory changes.
- Update product descriptions for regulatory text changes.
- Seasonal product sort order for quoting tools.

### crm.objects.projects.read
- Implementation project status for enterprise or B2B2C rollouts.
- Milestone delay alerts for customer onboarding projects.
- Resource load across project managers.

### crm.objects.projects.write
- Advance project stages when Shopify fulfillment hits milestones.
- Create projects automatically from high-value deals won.
- Close projects and trigger CSAT surveys.

### crm.objects.quotes.read
- Quote win rate and average discount by rep.
- Quotes expiring in 48h for proactive follow-up.
- Compare quote versions for negotiation insights.

### crm.objects.quotes.write
- Regenerate quotes after price list updates (with customer comms template).
- Approve-discount workflow integration (threshold-based).
- Mark quotes superseded when a new order is placed.

### crm.objects.services.read
- Attach rate for service plans to core product sales.
- Service revenue vs product revenue trends.
- Identify services with low margin (if modeled).

### crm.objects.services.write
- Update service SKUs after packaging changes.
- Bundle services to quotes for VIP programs.
- Archive deprecated services across open quotes (careful).

### crm.objects.subscriptions.read
- MRR/ARR movement summary for CEO + finance.
- Churn risk list from subscription fields + ticket sentiment.
- Trial-to-paid conversion by cohort.

### crm.objects.subscriptions.write
- Pause/resume subscriptions per policy after payment issues.
- Apply plan changes after customer success review.
- Align subscription status with Shopify subscription webhooks.

### crm.objects.users.read
- Seat usage vs paid HubSpot seats for cost control.
- Admin user change log for security reviews.
- Deprovision checklist when someone offboards.

### crm.objects.users.write
- Provision users from HRIS CSV (IT-approved).
- Role changes after promotions.
- Disable users on termination day (paired with IT).

### crm.pipelines.orders.read
- Pipeline-specific velocity for commerce orders if used.
- Bottleneck stage identification for fulfillment ops.
- Executive view of stuck orders by pipeline.

### crm.pipelines.orders.write
- Rebalance automation when a stage is deprecated.
- Bulk move orders after workflow redesign (with safeguards).
- Mirror ERP stage changes into HubSpot for visibility.

### crm.schemas.appointments.read
- Document custom appointment properties for CX training.
- Detect schema drift between sandboxes.
- Validate required fields before go-live of scheduling changes.

### crm.schemas.appointments.write
- Add new properties for “consultation outcome” with governance PR in git.
- Deprecate unused appointment fields after audit.
- Clone schema patterns from sandbox to prod via controlled migration.

### crm.schemas.carts.read
- Inventory of cart properties used in integrations.
- Schema diff after HubSpot product updates.
- Field usage report: which automations reference which cart properties.

### crm.schemas.carts.write
- Add cart properties for new payment experiments (feature-flagged).
- Align cart field names with Shopify line item metadata mapping.
- Archive experimental cart fields after test conclusion.

### crm.schemas.commercepayments.read
- Map payment properties to finance reporting fields.
- Compliance checklist: which PII sits on payment objects.
- Schema documentation for auditors.

### crm.schemas.commercepayments.write
- Add properties for processor IDs and reconciliation keys.
- Tighten field-level permissions recommendations (process).
- Versioned migration plan for payment schema changes.

### crm.schemas.companies.read
- Company property hygiene score for ABM readiness.
- Required-field gaps before outbound campaigns.
- Merge readiness: which fields block auto-merge.

### crm.schemas.companies.write
- Add “strategic account tier” property with approval workflow.
- Deprecate duplicate industry picklists.
- Introduce parent-account rollup fields for reporting.

### crm.schemas.contacts.read
- Contact property catalog for AI tools and agents (what’s safe to expose).
- Consent field audit for marketing compliance.
- Identify unused contact properties to archive.

### crm.schemas.contacts.write
- Add lifecycle fields for new product lines.
- Standardize phone/email field usage across teams.
- Create “CEO priority” boolean with strict usage policy.

### crm.schemas.courses.read
- Training field taxonomy for partner certification levels.
- Schema for course objects aligned to LMS if integrated.
- Validate completion fields before reporting.

### crm.schemas.courses.write
- Extend course schema for new curriculum releases.
- Add quiz score fields for compliance training.
- Deprecate legacy course properties.

### crm.schemas.custom.read
- Catalog custom objects for data council: owners, PII level, purpose.
- Impact analysis before deleting a custom property.
- Map custom objects to executive KPIs.

### crm.schemas.custom.write
- Versioned creation of new custom objects for “partner tier” programs.
- Add properties for manufacturing milestones if tracked in CRM.
- Consolidate redundant custom objects after M&A.

### crm.schemas.deals.read
- Deal property governance: required fields per stage.
- Forecast category field usage audit.
- Competitive field adoption metrics.

### crm.schemas.deals.write
- Add “competitor” picklist values after market research.
- Stage-gate required properties for revenue recognition alignment.
- Introduce executive sponsor field for whale deals.

### crm.schemas.forecasts.read
- Understand forecast fields for board reporting accuracy.
- Schema alignment between HubSpot and FP&A model.
- Field lineage documentation.

### crm.schemas.invoices.read
- Invoice property set for reconciliation automation design.
- Tax field audit before multi-jurisdiction expansion.
- Match invoice schema to accounting export.

### crm.schemas.invoices.write
- Add properties for payment processor references.
- Introduce dispute status fields for CX workflows.
- Schema migration after tax engine change.

### crm.schemas.line_items.read
- Line item property usage for discount governance.
- Map line items to COGS categories for margin reporting.
- Identify unused line item fields.

### crm.schemas.line_items.write
- Add bundle component fields for configurators.
- Add regulatory labeling fields for medical-adjacent products (process-driven).
- Deprecate legacy SKU fields post-migration.

### crm.schemas.listings.read
- Listing schema for marketplace strategy documentation.
- Field gaps vs what merchandising needs on site.
- Compare listing schema across portals if multiple.

### crm.schemas.listings.write
- Expand listing schema for new distribution channel.
- Add compliance fields for regional listings.
- Normalize listing attributes after taxonomy project.

### crm.schemas.orders.read
- Order schema alignment with Shopify order metafields.
- SLA fields for shipping promises on order objects.
- Data dictionary for ops leadership.

### crm.schemas.orders.write
- Add “VIP handling” flags on orders for CX prioritization.
- Introduce return reason codes standardized across systems.
- Schema updates for new warehouse integration.

### crm.schemas.projects.read
- Project schema review before CS handoff process change.
- Executive rollup fields for project profitability if tracked.
- Stage definitions for onboarding projects.

### crm.schemas.projects.write
- Add milestone properties tied to factory timelines.
- Introduce risk flag fields for at-risk implementations.
- Deprecate unused project stages after process simplification.

### crm.schemas.quotes.read
- Quote schema for CPQ governance and approval matrices.
- Validity/expiration field usage audit.
- Map quote fields to contract review checklist.

### crm.schemas.quotes.write
- Add approval threshold fields for discounting.
- Terms & conditions version field for legal control.
- Schema for multi-currency quotes if expanding.

### crm.schemas.services.read
- Service catalog schema for attach-rate analytics readiness.
- Warranty field planning on service objects.
- Compare service schema vs Shopify service products.

### crm.schemas.services.write
- Add SLA tier properties for premium support SKUs.
- Introduce geo-specific service availability fields.
- Consolidate overlapping service definitions.

### crm.schemas.subscriptions.read
- Subscription schema for finance-recognized revenue fields.
- Pause reason taxonomy before self-serve pause flows.
- Churn reason field governance.

### crm.schemas.subscriptions.write
- Add fields for “save offer” outcomes.
- Introduce upgrade path tracking properties.
- Align subscription schema with billing system IDs.

### ctas.read
- CTA performance by page for conversion reviews.
- Find broken CTAs after URL migrations.
- Executive summary: top CTAs driving qualified leads.

### data_integration.data_source.file.read
- Ingest CSV snapshots from warehouse for hybrid reporting.
- Compare file snapshots day-over-day for drift detection.
- Feed CEO metrics from governed file extracts.

### data_integration.data_source.file.write
- Push cleaned segments back as files for other teams (with ACLs).
- Upload reconciliation files after finance close.
- Scheduled file drops for partner systems.

### e-commerce
- Cross-channel commerce health: orders, carts, payments in one daily brief.
- Promo abuse monitoring (velocity, duplicate addresses).
- Inventory risk signals tied to commerce objects.

### external_integrations.forms.access
- Audit third-party forms feeding HubSpot for GDPR consent alignment.
- Map each form to owner and intended use case.
- Disable abandoned integration forms after migration.

### files
- Inventory marketing assets for brand consistency reviews.
- Find outdated PDFs linked in sales emails.
- Storage cost / large-file report for housekeeping.

### files.ui_hidden.read
- Discover hidden system files referenced in integrations (governance).
- Audit before portal migration.
- Document which automations rely on hidden assets.

### forms
- Form conversion rate leaderboard for landing pages.
- Field-level drop-off analysis export.
- Pre-submit spam pattern detection.

### forms-uploaded-files
- Aggregate uploads linked to support cases for QA sampling.
- Virus-scan workflow hook (partner process) if applicable.
- Retention policy for uploaded attachments.

### hubdb
- Merchandising tables driving CMS (if used): version and diff.
- HubDB → CRM sync for store locator or partner data.
- Backup HubDB tables before schema edits.

### integration-sync
- Integration health dashboard: sync errors, backlog, retries.
- CEO alert on sync paused >1 hour for revenue-critical objects.
- Change log when integration mappings update.

### integrations.zoom-app.playbooks.read
- Pull Zoom playbook usage into sales coaching metrics.
- Compare playbook usage vs win rates.
- Identify unused playbooks to deprecate.

### marketing.campaigns.read
- Campaign ROI summary for weekly leadership sync.
- Compare channel performance (email vs social vs paid).
- Campaigns with declining engagement trend alerts.

### marketing.campaigns.revenue.read
- Tie campaigns to influenced revenue for board metrics.
- CAC sensitivity by campaign cohort.
- Executive “money slide” export for investor meetings.

### marketing.campaigns.write
- Create campaigns from a structured editorial calendar CSV.
- Pause all non-essential campaigns during crisis comms (governance).
- Clone winning campaign structures for new regions.

### mcp.users.read
- Audit which internal users can use MCP-style integrations (if applicable to your setup).
- Map MCP users to least-privilege roles.
- Monthly access review for AI tool users.

### media_bridge.read
- Inventory media assets bridged into HubSpot for creative reviews.
- Performance of creative variants linked to deals.
- Rights/expiry tracking for licensed imagery.

### media_bridge.write
- Push approved creative batches after brand review.
- Tag media with campaign IDs for attribution.
- Archive outdated creative linked to old promos.

### oauth
- Token lifecycle monitoring for customer-facing OAuth apps (expiry, refresh failures).
- Security review checklist before expanding OAuth scopes.
- Incident runbook: revoke tokens for compromised app.

### record_images.signed_urls.read
- Secure image access for VIP galleries or custom hair photos (process-heavy).
- Audit who generates signed URLs and how often.
- Link signed URL usage to support cases.

### sales-email-read
- Digest of sales email engagement on key accounts.
- Template effectiveness ranking for leadership.
- Compliance sampling of outbound sequences.

### scheduler.meetings.meeting-link.read
- No-show rate by meeting type for CX optimization.
- Round-robin fairness report for sales meetings.
- CEO office hours booking analytics.

### settings.billing.write
- Scripted invoice details updates only in controlled CI (rare; finance-owned).
- Seat purchase simulation before scaling team (with guardrails).
- Post-contract seat adjustment automation (CFO-approved).

### settings.currencies.read
- Multi-currency reporting readiness check before new market launch.
- FX impact narrative for board (paired with finance data).
- Detect stale currency settings before big quotes.

### settings.currencies.write
- Update base reporting currency after entity restructuring (extremely rare; multi-signoff).
- Add new market currency after banking setup.
- Align CRM currencies with Shopify markets configuration.

### settings.security.security_health.read
- Weekly security posture one-pager for CEO.
- Track remediation items after pen tests.
- Compare settings vs CIS-style checklist (manual + scripted hints).

### settings.users.read
- Seat utilization and role distribution for budget planning.
- Shadow admin detection (unexpected super admins).
- Quarterly access certification export.

### settings.users.teams.read
- Team structure for routing and forecasting by pod.
- Identify teams with no manager assigned.
- Capacity model inputs for hiring plan.

### settings.users.teams.write
- Restructure teams after reorg (scripted with HR approval).
- Align team names with GTM motion changes.
- Archive empty teams after consolidation.

### settings.users.write
- Offboarding automation: deactivate users on last day (IT partnership).
- Role changes after promotions (bulk update).
- Freeze changes during audit windows (policy flag).

### social
- Social post performance tied to CRM campaigns if integrated.
- Brand mention triage list for leadership.
- UGC permission tracking for marketing reuse.

### tax_rates.read
- Tax configuration sanity check before big promotions.
- Compare tax rates vs Shopify for a jurisdiction launch.
- Executive summary of tax exposure by region (with finance).

### tickets
- Ticket backlog and SLA breach daily brief for Service leadership.
- Escalation queue for “VIP” or “legal” tags.
- Root-cause tagging trends for product quality reviews.

### timeline
- Executive timeline digest: key customer events yesterday on top accounts.
- Detect negative event clusters before churn.
- Feed timeline highlights to weekly all-hands narrative.

---

## Note on scope count

Your token currently lists **161** scopes (not 150). If HubSpot adds or removes scopes later, re-run:

`npm run hubspot:token:scopes`

and diff this document against the new list.
