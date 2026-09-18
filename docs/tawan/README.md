# Tawan documentation index and implementation summary

**Product:** Tawan, Duply's LINE-first commerce assistant for Thai small and
medium social-commerce merchants.  
**Product Owner:** Arriyathanasak / Tawan owner  
**Implementation contact:** Duply.official  
**Planning baseline:** 2026-09-18  
**Repository:** `duplyofficial-thay/duply-creator`

## Current status

TWN-01 through TWN-12 have approved planning documentation. The implementation
handoff and Supabase table/column contract are complete and pushed to GitHub.
This is not production activation approval. The system must remain synthetic-
data/test-Channel/sandbox-payment only until the open release gates are signed.

The latest repository commit is `ff33433` (`docs(tawan): define Supabase
schema requirements`).

## Read these first

1. [TAWAN_IMPLEMENTATION_SPEC_REQUIREMENTS.md](TAWAN_IMPLEMENTATION_SPEC_REQUIREMENTS.md) — functional requirements FR-001–FR-008, non-functional requirements, evidence matrix, implementation order, and definition of done.
2. [SUPABASE_SCHEMA_REQUIREMENTS.md](SUPABASE_SCHEMA_REQUIREMENTS.md) — proposed tables, columns, keys, tenancy decision, RLS requirements, and migration gaps.
3. [IMPLEMENTATION_HANDOFF_TWN01_TWN12.md](IMPLEMENTATION_HANDOFF_TWN01_TWN12.md) — workstreams for Duply.official, exit evidence, and release blockers.
4. [FEATURE_TASKS.md](FEATURE_TASKS.md) — card-by-card completion checklist and the three intentionally open approval cards.
5. [DECISIONS.md](DECISIONS.md) — approved product decisions and unresolved Supabase tenancy reconciliation.

## Product summary

Tawan helps Thai merchants using LINE OA respond consistently, capture customer
and order details correctly, and produce clear daily follow-up actions. It may
prepare work and recommendations, but the Store Owner retains authority over
money, refunds, discounts, exceptions, subscriptions, sensitive exports, and
workspace closure.

Phase 1 is LINE-first and supports retail products sold by the piece. It
includes assisted onboarding, Store Brain, safe customer replies, stock and
order support, payment-review preparation, staff tasks, dashboard actions,
daily digest, consent/rights controls, and a free 30-day pilot planned for up
to ten Thai retailers. Phase 2/Pro work is demand-led integrations, campaigns,
segmentation, forecasting, and advanced intelligence. Future channels include
Shopee, Facebook, TikTok, Instagram, and Lazada, but they are not Phase 1 build
commitments.

## Feature documents

| Feature | Document | Implementation meaning |
| --- | --- | --- |
| TWN-01 | [Product Direction](TWN-01_PRODUCT_DIRECTION.md) | Promise, Phase 1/2/3 boundaries, Pilot/Standard/Pro, scope exclusions |
| TWN-02 | [Tawan Official](TWN-02_TAWAN_OFFICIAL.md) | Merchant qualification, onboarding, support, payment-link handoff |
| TWN-03 | [Merchant Onboarding](TWN-03_MERCHANT_ONBOARDING.md) | Checklist, source intake, validation, Owner approval, activation states |
| TWN-04 | [Store Workspace and Access](TWN-04_STORE_WORKSPACE_ACCESS.md) | Store Context, roles, capabilities, Channel separation, isolation |
| TWN-05 | [Store Brain](TWN-05_STORE_BRAIN.md) | Sources, candidates, approval, conflicts, stale facts, publication |
| TWN-06 | [Customer Sales Assistant](TWN-06_CUSTOMER_SALES_ASSISTANT.md) | Thai seller voice, safe answers, takeover, structured capture, idempotency |
| TWN-07 | [Orders and Store Operations](TWN-07_ORDERS_STORE_OPERATIONS.md) | Stock limits, reservations, payment review, fulfilment, returns, refunds |
| TWN-08 | [Customer Memory and Consent](TWN-08_CUSTOMER_MEMORY_CONSENT.md) | Workspace-local memory, consent, STOP, rights, retention, deletion |
| TWN-09 | [Admin Dashboard](TWN-09_ADMIN_DASHBOARD.md) | Low stock first, morning confirmation, orders/payments, tasks, access |
| TWN-10 | [AI Workflow and Daily Insights](TWN-10_AI_WORKFLOW_DAILY_INSIGHTS.md) | Real-time capture, daily digest, recommendations, insufficient-data behavior |
| TWN-11 | [Channels and Integrations](TWN-11_CHANNELS_INTEGRATIONS.md) | Tawan Official vs merchant LINE, adapter contract, imports, future connectors |
| TWN-12 | [Pilot Safety and Launch Gate](TWN-12_PILOT_SAFETY_LAUNCH_GATE.md) | Synthetic pilot, sandbox payment, safety evidence, incident response, Go/Hold/No-go |

## Supporting documents

- [REQUIREMENTS.md](REQUIREMENTS.md) — complete product baseline: roles,
  journeys, pricing, memory, dashboard, analytics, modules, and safeguards.
- [DESIGN.md](DESIGN.md) — Phase 1 commerce model, architecture, agents, and
  tool packs.
- [REFERENCE.md](REFERENCE.md) — entity model, lifecycles, data layers, and
  invariants.
- [TESTING.md](TESTING.md) — current test commands and verification scope.
- [PHASE_1_PILOT_SPEC.md](PHASE_1_PILOT_SPEC.md) — pilot-specific requirements.

## Open gates before real activation

1. **TWN-04 architecture/security:** approve the final tenancy model and attach
   negative cross-workspace and cross-Channel isolation tests.
2. **TWN-08 Thai counsel:** approve Thai notices, lawful bases, controller/
   processor terms, retention, rights, transfers, breach handling, and exports.
3. **TWN-12 release:** name Security, Operations, Thai counsel, and Incident
   Commander; attach signed product/security/operations/legal evidence and an
   independent review.

No real customer data, live merchant LINE, production payment, refund, or
Phase 2 connector is authorized before these gates are attached.

## Supabase warning

The existing SQL drafts are useful but not approved production migrations. They
use a per-Duple schema model, omit the full `store_workspace_id` contract, and
do not yet provide verified RLS. The team must explicitly approve either the
per-Duple model with evidence or a shared schema with workspace-scoped rows.
The detailed table/column contract and migration gap list are in
[SUPABASE_SCHEMA_REQUIREMENTS.md](SUPABASE_SCHEMA_REQUIREMENTS.md).
