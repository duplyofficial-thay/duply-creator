# Tawan Continuity Snapshot

**Snapshot date:** 2026-08-18

**Authority:** Orientation only. Current Git state and the canonical Tawan documents override this snapshot.

## Repository

- Canonical remote: `https://github.com/duplyofficial-thay/duply-creator.git`
- Canonical checkout on the owner's Mac: `~/Documents/06_Code/Projects/Duply/duply-creator`
- Stale duplicate: `~/Documents/06_Code/Projects/Solo/duply-creator`; inspect only, never edit
- Approved product baseline commit: `66b3fd1` (`docs(tawan): establish approved product blueprint`)
- Pro-only Campaign decision commit: `38b2422` (`docs(tawan): reserve campaigns for pro tier`)
- Production implementation status at this snapshot: not started

Always verify the branch, latest commit, remotes, and working tree. Local approved commits may be ahead of GitHub until the product owner authorizes a push.

## Product Baseline

Tawan is Duply's LINE-first commerce AI product. Shared code supports many businesses, but each store receives a separately provisioned Tawan Instance/Duple with an isolated schema, database role, Channel identity, Store Knowledge, Customer Memory, operational data, and credentials.

The first complete demo is fashion and accessories. Restaurant/bakery, beauty salon, wholesale, and construction are synthetic validation scenarios before they become complete modules. The common model covers Customer, Sales Journey, Task, Approval, Transaction, payment, memory, consent, analytics, and optional business modules.

Tawan answers only from approved Store Knowledge and authorized operational facts. It records structured progress and permitted Customer Memory instead of keeping raw transcripts indefinitely. Knowledge publication, exceptional prices, and uncertain Phase 1 payments remain under Store Owner authority.

## Subscription Boundary

Standard includes customer service, commerce operations, Customer Memory, Sales Journeys, Tasks, Transactions, consent and objections, the action-first dashboard, and store-scoped operational analytics.

Pro adds outbound Campaign drafting, owner approval, audience selection, scheduling, delivery, suppression, personalization, results, attribution, segmentation, lifetime value, cohorts, churn, affinity, forecasting, promotion analysis, anomaly detection, and approved Anonymous Benchmarks. Pro Campaigns and intelligence are post-Phase-1 work; Standard must not expose Campaign execution controls.

Custom identity, branding, workflows, migration, and white-label service are separately scoped B2B engagements. There is no permanent free tier.

## Phase 1 Gate

Phase 1 must prove one realistic journey:

`Customer question -> approved product answer -> Order -> PromptPay QR -> payment-review Task -> Store Owner payment decision -> staff fulfilment -> completed Order`

The gate also requires an independent security review confirming no cross-store leakage. AI payment auto-approval, outbound Campaign execution, additional Channels, and production-complete secondary business modules are outside Phase 1.

## Current Blockers

Before production implementation, obtain read-only access and verify ownership and contracts for:

- the private Duply agent/runtime repository;
- the Supabase and migration environment, possibly owned in `duply-astro`;
- the Store Owner/Staff dashboard repository and deployment target;
- LINE webhook, media, identity, and delivery interfaces;
- tool registry, authentication, queue, cache, storage, backup, and cost-ledger interfaces;
- Thai counsel approval for controller/processor roles, privacy notice, marketing basis, retention, international transfers, exports, and incident handling.

Do not invent missing platform contracts from the public creator kit.

## Immediate Next Milestone

Perform the read-only discovery milestone in `docs/tawan/IMPLEMENTATION_PLAN.md`. Reconcile the approved target against Duply's real runtime and schema conventions. Return a dependency map, contradiction list, proposed test harness, migration foundation, and smallest implementation change for owner approval.

## Canonical Record Map

- `CLAUDE.md`: repo entry point, session workflow, Trello boards, and required language and domain terms
- `docs/tawan/DECISIONS.md`: approved decision history
- `docs/tawan/PRODUCT_SPEC.md`: product behaviour, tiers, and acceptance
- `docs/tawan/ARCHITECTURE.md`: boundaries, isolation, flows, and dependencies
- `docs/tawan/DATA_MODEL.md`: entities, lifecycle, and invariants
- `docs/tawan/SECURITY.md`: threats, privacy, marketing, retention, and launch blockers
- `docs/tawan/IMPLEMENTATION_PLAN.md`: ordered milestones and verification
- `docs/research/2026-08-17-thailand-pdpa-tawan-data.md`: legal research starting point, not legal advice
- `docs/tawan/COMMERCE_DESIGN.md`: current Phase 1 commerce design (v3, multi-tenant single-schema) — **not** superseded; it replaced the earlier per-store-Duple assumption
- `docs/tawan/CURRENT_TASK_STATUS.md`: live task status by state; read before assuming what is done
- `docs/tawan/PHASE_1_ROADBLOCKS.md`: what Duply platform must supply before blocked cards can move
- `docs/tawan/README.md`: index of every Tawan document, categorised

The long planning conversation was normalized into these records so future agents do not need the original account or chat history.
