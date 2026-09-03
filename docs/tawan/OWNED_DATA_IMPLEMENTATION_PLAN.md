# Tawan Owned Data Implementation Plan

**Status:** Proposed for local Supabase implementation

**Updated:** 2026-09-03

This plan moves Tawan's product data model into the creator-kit migration
layer. It assumes one provisioned Postgres schema per Store Workspace. The
same Tawan code can serve many stores, but no store table is shared across
schemas.

## Data Layers

| Layer | Purpose | Main tables | Retention rule |
|---|---|---|---|
| Identity | Store setup, customers, LINE identity | `store_settings`, `customers`, `channel_identities` | Keep while account/customer relationship is active, subject to rights requests |
| Memory and rights | Preferences, tiers, consent, Thai privacy requests | `customer_memories`, `customer_tiers`, `consent_records`, `data_subject_requests` | Store-specific; inferred memory expires sooner; deletion is auditable |
| Reply progress | Durable outcome of each reply without indefinite transcript storage | `interaction_events`, `sales_journeys`, `journey_interests` | Structured records retained by approved purpose |
| Human work | Tasks, approvals, status history | `tasks`, `task_status_history`, `approvals` | Keep while operational/legal evidence is required |
| Commerce | Products, variants, stock, prices, orders, payment and fulfilment | `catalog_*`, `inventory_*`, `price_rules`, `transactions`, `transaction_lines`, `stock_reservations`, `payments`, `payment_evidence` | Financial/order evidence follows legal and store retention policy |
| Knowledge | Store materials and owner-approved facts | `knowledge_sources`, `knowledge_candidates`, existing `knowledge_entries` | Raw sources expire by policy; published facts require provenance and approval |
| Analytics and control | Operational metrics, audit, future de-identified analysis | `analytics_events`, `daily_store_metrics`, `audit_events` | Aggregates remain store-scoped unless explicitly approved and de-identified |

## Execution Order

1. Apply the existing creator-kit schema template to a disposable store schema.
2. Apply migration `0010` and verify the migration planner output.
3. Apply migration `0020` in a disposable Postgres/Supabase environment.
4. Seed synthetic fashion, food, beauty, service, wholesale, and construction stores.
5. Test reply-time capture with one idempotency key and a repeated webhook event.
6. Test a full fashion journey: customer question, interest, order, reservation, payment-review Task, owner decision, fulfilment, and completion.
7. Test schema isolation with two database roles and negative cross-store queries.
8. Add LINE adapter calls only after the inbound/outbound webhook contract is verified.
9. Add hourly aggregate refresh and daily close after operational state is working.
10. Add Pro Campaign tables and delivery only after the Phase 2 product gate; Standard does not send proactive campaigns.

## Card Mapping

| Cards | Work owned in this plan | Current state |
|---|---|---|
| `TWN-0202` | Reversible migration planner and SQL migrations | Local Review |
| `TWN-0203` | Disposable Postgres/Supabase apply, rollback, recreate | Needs environment |
| `TWN-0204` | Synthetic multi-business fixtures | Local Review |
| `TWN-0205` | Registration and migration replay checks | Local partial Review |
| `TWN-0206` | Native role/schema isolation and secret checks | Needs database roles |
| `TWN-0301` to `TWN-0314` | Store settings, roles, audit, access, and security wiring | Depends on platform/runtime auth contract |
| `TWN-0401` to `TWN-0412` | Knowledge source, approval, memory, retention, and OCR wiring | Schema foundation ready; adapters and legal policy remain |
| `TWN-0501` to `TWN-0512` | Reply-time events, journeys, tasks, approvals, tiers, notifications | Schema foundation ready; runtime command contract remains |
| `TWN-0601` to `TWN-0617` | Catalog through payment and LINE journey | Schema foundation ready; deterministic services and LINE contract remain |
| `TWN-0701` onward | Dashboard and operational analytics | Requires dashboard repository and API boundary |
| Pro Campaign cards | Campaign approval, consent, delivery, attribution, BI | Intentionally later and Pro-only |

## What We Can Own

We can own the SQL schema, migration files, deterministic domain services,
fixtures, local tests, and Tawan-specific LINE adapter code. We should not
copy or replace Duply's central webhook router, authentication, queue, secret
manager, or deployment service until we have confirmed how Tawan is invoked.

The GitHub scaffold currently has LINE Flex/card and reply configuration
placeholders, but it does not contain the webhook transport itself. The
transport can remain in Duply while it calls Tawan's store-scoped handlers.
