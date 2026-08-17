# Tawan Product Specification

**Status:** Approved product baseline

**Approved:** 2026-08-18

**Source of truth:** This document and the linked Tawan documents in this directory

**Product owner:** [arriyathanasak@gmail.com](mailto:arriyathanasak@gmail.com)

## 1. Product Definition

Tawan is Duply's commerce AI operating agent. It helps a business answer customers, preserve structured sales progress, complete transactions, coordinate staff work, remember permitted customer preferences, run approved promotions, and learn from reviewed store knowledge.

One shared Tawan product supports many businesses. Each business receives a separately provisioned Tawan Instance with a unique `duple_id` and one isolated Store Workspace. Shared commerce code and configuration patterns are reused; operational data, credentials, schemas, channel identities, and customer records are not shared.

Tawan is the standard product identity. A customer may contract directly with Duply for a custom name, persona, branding, or workflow. That custom identity remains a Tawan commerce implementation internally.

## 2. Product Principles

1. **Never invent store facts.** Price, stock, discount, delivery, availability, payment, policy, and project estimates must come from approved data or an authorized person.
2. **Structured progress over transcript hoarding.** Tawan preserves Sales Journeys, Interaction Events, Customer Memory, Tasks, and outcomes. Raw messages have a short justified retention period.
3. **One product, isolated stores.** Shared behaviour must never create shared operational or customer data.
4. **Human authority over commercial risk.** Owners approve campaigns, permanent knowledge, exceptional prices, uncertain payments, and material commercial changes.
5. **Useful breadth through modules.** A shared commerce core supports optional modules instead of one table or workflow pretending every business is identical.
6. **LINE first, channel-neutral core.** LINE OA is the first complete Channel Adapter. Other channels are added only through authorized capabilities.
7. **Analytics must earn trust.** Recommendations show supporting data and confidence. Tawan says when evidence is insufficient.

## 3. Users And Roles

Canonical role identifiers are `platform_admin`, `store_owner`, `store_staff`, and `customer`. Existing Duply role labels require an explicit migration or compatibility mapping.

### Platform Administrator

- Manages platform operations across Store Workspaces.
- Uses time-limited, reason-coded, audited support access.
- Does not act as a Store Owner by default.

### Store Owner

- Configures business rules, staff access, Customer Tier rules, price authority, campaigns, retention, closing time, and notifications.
- Approves permanent Store Knowledge and high-risk changes.
- Can assign a Customer Tier or customer-specific price manually with an audit record.
- Resolves probable duplicate-payment fingerprint false positives with a recorded reason; cannot override reuse of a confirmed bank transaction reference.
- Chooses retention settings only within platform limits approved for the applicable legal purpose; cannot shorten a statutory minimum, extend raw-message storage beyond the platform maximum, or remove a valid legal hold.

### Store Staff

Store Staff receive individual capabilities rather than universal access:

- `manager`
- `sales`
- `fulfilment`
- `marketing`
- `knowledge_editor`
- `payment_review`

`knowledge_editor` may prepare and review Knowledge Candidates but cannot publish permanent Store Knowledge. `payment_review` may inspect evidence and recommend a decision, but the Store Owner makes the final Phase 1 payment decision.

### Customer

- Receives service within one Store Workspace.
- Can ask what Tawan remembers, correct information, request deletion where applicable, and stop marketing.
- Is not linked across stores merely because a name, phone number, or preference appears similar.

## 4. Core Customer Journey

1. A Customer contacts the store through LINE OA.
2. Tawan resolves the Store Workspace and Customer identity before loading data.
3. Tawan answers from approved Store Knowledge and operational facts.
4. Tawan records structured progress, relevant Interaction Events, and permitted Customer Memory.
5. A Sales Journey is created or advanced when there is commercial intent.
6. Tawan creates a Transaction when the Customer commits to a supported business outcome.
7. Tawan applies the authorized price precedence and revalidates availability.
8. Stock or capacity is reserved for the Store Workspace's configured expiry period, normally 30-60 minutes for retail Orders.
9. Tawan generates a PromptPay QR where configured and records the submitted slip.
10. Phase 1 routes payment slips to manual review. It does not auto-approve payment.
11. Staff complete fulfilment or delivery work through Tasks and Transaction status changes.
12. The completed outcome feeds Store Analytics and eligible Customer Memory.

## 5. Sales Journey And Tasking

### Sales Journey states

The initial common states are:

`interested -> comparing -> awaiting_decision -> transacting -> completed`

Terminal or alternate outcomes include `abandoned`, `lost`, and `cancelled`. Business modules may add detail without changing the common reporting meaning.

### Task states

`new -> assigned -> in_progress -> waiting_customer | waiting_owner -> resolved`

Terminal outcomes also include `cancelled` and `expired`.

### Initial Task types

- `answer_needed`
- `discount_approval`
- `payment_review`
- `stock_issue`
- `order_follow_up`
- `delivery_issue`
- `knowledge_approval`
- `vip_attention`

Each Task records Store Workspace, Customer where applicable, related Sales Journey or Transaction, priority, assignee, due time, status history, and resolution.

## 6. Customer Memory And Tiers

Customer Memory stores structured information, not an undifferentiated transcript. Every memory records:

- source: Customer statement, imported record, staff entry, or AI inference;
- confidence;
- first and last observed dates;
- confirmation date and actor;
- effective and expiry dates where relevant;
- current status and correction history.

Customer Tiers support Standard, Regular, VIP, Wholesale, or store-defined equivalents. A transparent rule may use completed spend, transaction count, purchase frequency, or wholesale status. Tawan can recommend changes; Store Owners can approve or override them manually.

Customer Tier alone does not authorize a discount. Price authority remains explicit.

## 7. Pricing And Negotiation

Applicable prices follow this precedence:

1. owner-approved customer-specific price;
2. active Campaign price;
3. Customer Tier price;
4. quantity or wholesale price;
5. standard price.

Every non-standard price records authorizer, reason, scope, Customer where applicable, product or service, quantity conditions, effective time, and expiry.

When a Customer requests an unauthorized exception, Tawan creates a `discount_approval` Task and says it is checking. Tawan makes no promise before approval.

## 8. Store Knowledge And Onboarding

Duply provides assisted onboarding. A store may supply spreadsheets, CSV, PDFs, Word documents, images, text, website pages, catalogs, menus, policy documents, price lists, or structured exports. Website imports are limited to store-approved domains.

The ingestion workflow is:

`uploaded -> extracting -> needs_review -> approved -> published`

The ingestion agent creates Knowledge Candidates with source, confidence, extracted fields, warnings, conflicts, effective dates, and expiry dates. Knowledge editors may prepare recommendations, but the Store Owner approves publication of permanent Store Knowledge. The system never silently publishes or overwrites price, stock, payment, or policy information.

Businesses without existing data receive guided templates for catalog or service data, policies, payment, staff, operating hours, consent settings, and channel setup. Direct POS and business-system integrations are later work.

Critical changes require immediate approval. Tawan also prepares a daily change digest. The Store Owner chooses weekly or monthly confirmation for lower-risk knowledge.

## 9. Campaigns And Proactive Sales

Marketing permission is tracked per Store Workspace, Customer, purpose, and Channel. Buying from one store or consenting on one Channel does not authorize another store or Channel.

Campaign workflow:

`drafted_by_tawan -> owner_review -> approved -> scheduled -> sending -> completed -> analysed`

The Store Owner approves products or services, prices and discounts, dates, eligibility, contact limits, and audience rules. Tawan may select eligible Customers and personalize wording within those approved constraints.

Each store configures weekly limits, quiet hours, cooldowns, and suppression rules. `STOP` and equivalent Thai opt-out requests take effect immediately.

## 10. Dashboard

The dashboard contains:

- **Overview:** urgent approvals, unanswered Customers, high-value opportunities, payment reviews, low stock, upcoming Bookings, overdue follow-ups, and concise performance measures.
- **Customers:** profile, Customer Memory, confidence, Customer Tier, consent, Sales Journeys, Transactions, Tasks, Campaign history, staff notes, correction, and deletion controls.
- **Sales Journeys:** progress, products or services discussed, next action, value, and outcome.
- **Transactions:** shared view with module-specific names and status.
- **Tasks:** queue, assignment, priority, due time, escalation, and history.
- **Catalog/Services:** approved commercial facts and availability.
- **Campaigns:** approval, scheduling, delivery, suppression, and results.
- **Tawan Brain:** uploads, Knowledge Candidates, conflicts, approvals, sources, and review digest.
- **Analytics:** operational and subscription-tier reporting.
- **Settings:** business, staff capabilities, payment, Channels, retention, notifications, consent, and closing schedule.

Operational records update in real time. Dashboard aggregates refresh hourly. Daily close finalizes store-local daily totals. Advanced models refresh daily or weekly.

## 11. Analytics And Subscription Tiers

### Standard operational analytics

- revenue and Transaction count;
- units sold and average Transaction value;
- refunds and cancellations;
- views, interest, checkout, purchase, and drop-off funnel;
- repeat-customer rate;
- unresolved Sales Journeys and response completion;
- human escalation and response time;
- top products, services, and stock movement;
- Campaign-attributed Transactions;
- staff workload.

### Higher-tier intelligence

Higher-tier intelligence is post-Phase-1 work and requires separate product approval after the Phase 1 transition gate.

- customer segmentation and RFM;
- customer lifetime value and cohort retention;
- churn risk and next-best offer;
- product affinity and market-basket analysis;
- demand forecasting;
- promotion effectiveness and discount leakage;
- Campaign attribution and anomaly alerts;
- Anonymous Benchmarks across participating stores.

Predictions are recommendations, not authority. Tawan displays evidence, confidence, and insufficient-data states. Commercial actions still require the appropriate human approval.

## 12. Business Modules And Demos

The shared core supports business modules. Initial fictional demos are:

1. **Fashion and accessories:** variants, stock, delivery, and returns. This is the first complete end-to-end module.
2. **Restaurant or bakery:** modifiers, preparation, collection, and delivery slots.
3. **Beauty salon:** services, staff calendars, capacity, and Bookings.
4. **Wholesale supplier:** Quotations, quantity prices, approvals, and repeat Orders.
5. **Construction contractor and materials supplier:** leads, site visits, bills of quantities, Quotations, Projects, milestones, change orders, materials, deposits, and progress payments.

The latter four first validate the shared model with realistic synthetic scenarios. They become production-complete incrementally after the core model survives those tests.

## 13. Commercial Offering

- No permanent free tier.
- Assisted sales and onboarding.
- A standard introductory first-month offer after a qualified Customer sees the product's value.
- Final pricing follows a documented cost model covering AI, messaging, support, storage, and onboarding.
- Standard plans use the Tawan identity.
- Custom identity, branding, workflow, migration, and white-label work are direct B2B engagements.
- Custom pricing, setup fees, recurring service, ownership, and support terms are negotiated case by case; no default buyout or recurring structure is promised by this specification.

## 14. Phase 1 Acceptance

Phase 1 delivers:

- the shared multi-store model with isolated Store Workspaces;
- assisted onboarding and knowledge ingestion review;
- role and capability controls;
- Customer Memory, Sales Journeys, Tasks, Customer Tiers, and approvals;
- retail catalog, variants, stock, Orders, expiry, PromptPay QR, and manual payment review;
- action-first dashboard and operational analytics;
- complete fashion demo and validation scenarios for four other businesses;
- LINE OA integration with Channel fields preserved for future adapters;
- consent, export, audit, retention, and security controls.

Phase 1 excludes automatic payment approval, autonomous price or Campaign changes, production-complete secondary modules, unrestricted cross-store analytics, and additional Channels.

Phase 2 may start after one realistic journey completes from Customer question through accurate answer, Order, payment-review Task, staff action, and completed outcome, with an independent security review confirming no cross-store leakage.

## 15. Launch Gates

Real customer data must not enter production until:

- Duply platform dependencies in [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) are complete;
- isolation, authorization, idempotency, payment, consent, export, deletion, and recovery tests pass;
- an independent engineering and security review has no unresolved release-blocking findings;
- Thai counsel approves the privacy notice, controller/processor allocation, data-processing agreement, retention schedule, marketing basis, international transfers, and export terms;
- operational cost tracking is active for every paid API call.

## Related Documents

- [Domain language](../../CONTEXT.md)
- [Architecture](ARCHITECTURE.md)
- [Data model](DATA_MODEL.md)
- [Security and privacy](SECURITY.md)
- [Decision log](DECISIONS.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Thai PDPA research](../research/2026-08-17-thailand-pdpa-tawan-data.md)
