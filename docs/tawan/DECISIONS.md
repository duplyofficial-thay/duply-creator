# Tawan Decision Log

This log records approved product and architecture decisions. New entries append; changed decisions are marked superseded rather than silently rewritten.

## 2026-08-18 - One Tawan product, isolated Store Workspaces

Tawan is one shared commerce product supporting many stores. Each store is a separately provisioned Tawan Instance/Duple with a unique `duple_id`, isolated schema, role, Customer Memory, Store Knowledge, configuration, staff access, and Channel mapping. Instances reuse a shared Tawan archetype implementation instead of forking code. This preserves Duply's current one-Duple/one-schema convention and strongest isolation control.

## 2026-08-18 - No cross-store Customer profile

The same natural person is a separate Customer relationship in every Store Workspace. Tawan will not match or share Customer Memory across stores based on name, phone, email, LINE identity, or inferred similarity. Cross-store insight is limited to approved anonymous aggregates.

## 2026-08-18 - Shared commerce core with optional business modules

Customer, memory, Sales Journey, Task, Approval, payment, Campaign, audit, and analytics concepts are shared. Retail, restaurant, booking, wholesale, construction, rental, and future business behaviour extend the common Transaction model. This avoids both duplicated foundations and one universal workflow full of irrelevant fields.

## 2026-08-18 - Structured memory instead of indefinite transcript retention

Tawan preserves structured Customer Memory, Interaction Events, Sales Journeys, Tasks, and outcomes. Raw conversation content is encrypted and retained only for a short justified period. This supports continuity and analytics while reducing privacy and breach exposure.

## 2026-08-18 - Knowledge is staged before publication

The ingestion agent creates Knowledge Candidates with provenance, confidence, validity, and conflicts. Staff may review and recommend, but permanent Store Knowledge never becomes customer-facing until the Store Owner approves it. This preserves the rule that Tawan must not invent or silently change store facts.

## 2026-08-18 - Human authority for material commercial action

Tawan may propose and staff may prepare work, but the Store Owner gives final approval for exceptional prices, Campaign commercial terms, permanent Store Knowledge, uncertain Phase 1 payments, and other material changes. The model has no direct database write authority.

## 2026-08-18 - Price precedence is deterministic

Applicable price order is customer-specific approval, Campaign, Customer Tier, quantity or wholesale, then standard price. Every non-standard price is scoped, time-bound, attributable, and auditable. Customer Tier alone does not grant a discount.

## 2026-08-18 - Phase 1 payment review is manual

Tawan may generate a PromptPay QR, receive a slip, extract candidate fields, detect duplicates, and create a Task. AI does not mark payment paid in Phase 1. This keeps the initial transaction flow useful without treating unverified media and vision output as financial authority.

## 2026-08-18 - LINE first through a shared channel interface

LINE OA is the first complete Channel. Core commerce records preserve Channel and external identity fields, while Channel-specific payloads remain inside adapters. Future Channels are added only through official or otherwise authorized capabilities and may expose different features.

## 2026-08-18 - Action-first dashboard

The Store Owner's first view prioritizes unresolved work, approvals, high-value opportunities, payment review, low stock, upcoming Bookings, and overdue follow-up. Analytics supports action instead of replacing the operational queue.

## 2026-08-18 - Hourly operations analytics and daily close

Operational state remains real time. Dashboard aggregates refresh hourly, daily close finalizes store-local business totals, and advanced models run daily or weekly. This balances usefulness, stability, and cost.

## 2026-08-18 - Standard and higher-tier analytics

All paying stores receive operational commerce measures in Phase 1. Higher-tier intelligence is post-Phase-1 work requiring separate product approval and may add segmentation, lifetime value, cohorts, churn, affinity, demand forecasting, attribution, anomaly detection, and Anonymous Benchmarks. Predictions remain recommendations and expose evidence, confidence, and insufficient-data states.

## 2026-08-18 - Assisted B2B onboarding and no permanent free tier

Duply onboards stores using their existing materials or guided templates. Qualified customers may receive a standard introductory first-month offer. Custom identity, branding, workflows, migration, and white-label work are separately scoped B2B engagements.

## 2026-08-18 - Existing store-controlled outputs are not a paid export lock

Ordinary departure export includes existing Customer, memory, tier, Sales Journey, Transaction, Task, consent, Campaign, Catalog, and approved knowledge records. Duply may charge for newly commissioned BI, data cleaning, migration assistance, consulting, and proprietary Anonymous Benchmarks. Thai counsel must approve final contract and rights language.

## 2026-08-18 - Store normally controls Customer processing

The store normally acts as controller for its Customer purposes and Duply as processor under documented instructions. Duply is a separate controller for narrow independently chosen purposes such as billing, account administration, platform security, or approved identifiable telemetry. Actual conduct, not labels, determines the legal role.

## 2026-08-18 - Five demos, one complete vertical first

Fashion is the first production-complete module. Restaurant/bakery, beauty salon, wholesale, and construction use realistic synthetic scenarios to test the shared model before their modules become production-complete. This tests breadth without claiming five simultaneous production systems.

## 2026-08-18 - Phase transition requires an end-to-end proof

Phase 2 may begin after a realistic Customer question progresses through accurate response, Order, payment-review Task, staff action, and completion, and an independent security review confirms no cross-store leakage. Blocked private-platform or legal work remains explicitly incomplete.
