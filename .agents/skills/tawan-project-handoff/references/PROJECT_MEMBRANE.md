# Tawan Project Membrane

**Updated:** 2026-09-10

**Purpose:** Durable context for any new Codex, Claude, teammate, or account
continuing the Tawan project. Read this reference before planning, answering
status questions, editing code, or touching the work board. It is a continuity
layer, not permission to make external changes.

## Authority And Working Systems

- Git and the canonical repository are the technical authority for what exists:
  `https://github.com/duplyofficial-thay/duply-creator`
- The canonical checkout is
  `/Users/zhg/Documents/06_Code/Projects/Duply/duply-creator`.
- Trello is the active planning and execution system:
  [Duple - Tawan](https://trello.com/b/HUbjHwDh/duple-tawan) in the Duply
  workspace.
- Notion is historical reference only. Do not create a parallel active board,
  update old Notion status, or treat a Notion mirror as newer than Git/Trello.
- Stable `TWN-*` identifiers join the Git manifest, Trello cards, source files,
  tests, and evidence. Never create a duplicate when an identifier already
  exists.
- This current context-capture request does not require a card report or card
  updates. Do not change Trello unless the user explicitly asks for board work.

## Repository State At This Snapshot

- Default branch: `main`.
- Canonical remote: `origin` at the GitHub URL above.
- Latest verified commit at snapshot time: `e6a0f13` (`docs(tawan): add
  feature completion checklists`). Re-check the full SHA before citing it as
  pushed evidence.
- The checkout may contain user-owned untracked `.claude/` and
  `marketing/` content. Preserve it; never delete or reset unrelated work.
- Before implementation, run `git status --short --branch`, `git remote -v`,
  `git branch -vv`, and a recent decorated log.

## Product Identity And Scope

Tawan is Duply's LINE-first commerce AI agent. One shared Tawan implementation
serves many stores. Each store has its own trusted Store Context, operational
records, Store Knowledge, Customer Memory, Channel identity, role membership,
and credentials. A store must never receive another store's product facts,
customer memory, price, stock, promotion, or operational output.

The first complete demo is fashion and accessories because it exercises
variants, sizes, colours, stock changes, promotions, shipping, returns, and
recommendations. Restaurant/bakery, beauty salon, wholesale, and construction
are synthetic validation scenarios before they become production-complete
modules. The shared model covers Customer, Sales Journey, Task, Approval,
Transaction, payment review, memory, consent, analytics, and optional business
modules.

Tawan must answer only from approved Store Knowledge and authorized operational
facts. It may propose an answer, a knowledge change, a customer preference, a
price exception, or a follow-up task; deterministic authorization and database
writes decide what is actually saved or sent.

## Canonical Architecture And Data Rules

- Current canonical commerce design is one shared `tawan_ai` schema with
  store-scoped rows and tenant isolation, not one new application per store.
  Do not revive the earlier per-store-schema assumption unless the decision log
  is intentionally changed.
- RLS and runtime authorization must enforce the store boundary on every new
  table. Platform-admin cross-store access is exceptional and must be logged.
- Roles are `platform_admin`, `store_owner`, `store_staff`, and `customer`.
  Store owners control permanent knowledge, exceptional commercial terms,
  marketing approval, and uncertain Phase 1 payment decisions.
- Customer memory records source, confidence, first seen, last seen, and
  confirmed-at. A direct customer statement is stronger evidence than an AI
  inference. Customers can ask what is remembered, correct it, delete it, or
  stop promotions.
- Consent is store-specific, purpose-specific, and Channel-specific. Buying
  from one store never authorizes marketing for another. `STOP` or unsubscribe
  suppresses outbound marketing immediately.
- Do not retain or expose raw conversation transcripts as the product memory by
  default. Save permitted structured progress, preferences, decisions, orders,
  tasks, and evidence with retention and deletion controls.
- Price and stock are never guessed. Price precedence is customer-specific
  approval, approved Campaign, Customer Tier, quantity/wholesale, then standard
  price. A Tier alone does not grant a discount.
- Payment Phase 1 is manual review: generate a real PromptPay QR, store the
  received slip safely, create a review Task, detect duplicates, and keep AI
  auto-approval disabled until media handling and duplicate protection are
  proven.
- Operational state is real time. Dashboard aggregates refresh hourly, daily
  close finalizes store-local totals, and advanced models refresh daily or
  weekly.

## Subscription And Commercial Boundaries

- Standard includes customer service, commerce operations, Customer Memory,
  Sales Journeys, Tasks, Transactions, consent/objection foundations, the
  action-first dashboard, and store-scoped operational analytics.
- Pro-only, post-Phase-1 capabilities include Campaign drafting, owner
  approval, audience selection, scheduling, delivery, suppression,
  personalization, results, attribution, segmentation, lifetime value,
  cohorts, churn, affinity, demand forecasting, promotion analysis, anomaly
  detection, and approved Anonymous Benchmarks.
- Standard must not expose Campaign execution controls. Tawan cannot change an
  approved Campaign's products, price, dates, audience rules, budget, or caps.
- Custom name, visual identity, vocabulary, workflows, migration, and full
  white-label work are special B2B engagements. Tawan remains the core product
  identity by default.
- There is no permanent free tier; an introductory first-month offer may be
  used for qualified customers.

## Phase 1 Exit Gate

Phase 1 is complete only after one realistic fashion journey is tested end to
end:

`Customer question -> approved product answer -> Order -> PromptPay QR -> payment-review Task -> Store Owner decision -> staff fulfilment -> completed Order`

The gate also requires an independent security review confirming no cross-store
data leakage. AI payment auto-approval, proactive Campaign execution, new
Channels, and production-complete secondary verticals remain outside this gate.

## Verified Implementation Evidence

- Migrations `0010`, `0020`, and `0030` were applied additively to Supabase
  project `fpjevusrpausqunjhubk`, schema `tawan_ai`, with owner approval.
- Read-only verification found 59 tables total, 12/12 expected new Tawan table
  checks, 12/12 pre-existing platform tables, and 96 indexes.
- Existing platform tables and data were preserved; no existing table
  definitions were changed.
- The repository test baseline has 21 passing unit tests and passing Python
  compilation checks.
- This evidence proves the repository and additive-schema milestone only. It
  does not prove production runtime, LINE webhook delivery, dashboard auth,
  backups, restore, deployment, or customer-data safety.

## Current Security And Platform Gates

The following are not safe to mark complete from local code alone:

- `TWN-0101`: Duply read-only access to runtime, data/Supabase, dashboard,
  LINE, and deployment surfaces.
- `TWN-0102` through `TWN-0107`: real platform contracts for Store Context,
  runtime dispatch, knowledge/memory, write infrastructure, LINE media and
  delivery, and migration/recovery/cost interfaces.
- `TWN-0108`: synthesis of those verified contracts.
- RLS policies and runtime authorization for all new `tawan_ai` tables.
- Rotation of any leaked database or service credentials. Never place secret
  values in Git, Trello, Notion, chat, logs, or examples.
- Thai counsel review of controller/processor roles, notices, lawful basis,
  marketing, retention, transfers, rights, exports, deletion, incidents, and
  subprocessors.

Until these gates close, do not use customer data, client keys, or production
LINE traffic with the new tables. Do not invent missing Duply contracts from
the public creator kit.

## Task Manifest And Trello State

The canonical manifest contains 149 Tawan cards. The latest Git roll-up records:

| Status | Count |
|---|---:|
| Done | 5 |
| Review | 15 |
| Ready | 1 |
| Blocked | 8 |
| Backlog | 120 |

The eight Duply Platform cards were copied to the main Trello board with their
individual descriptions, links, dependencies, acceptance criteria, and source
evidence. They map to the destination board's simpler lists as follows:

- `To Do` (2): repository-visibility decision; monthly retro and October
  re-plan.
- `Doing` (4): Duply read-only access; RLS policies; credential rotation;
  TWN-0104 through TWN-0107 interface contracts.
- `Done` (2): Git reconciliation; verified repository/schema baseline.

This is a partial board migration, not a claim that all 149 cards are already
in Trello. When migrating more cards, preserve the stable ID, use a unique
description, include dependencies and acceptance evidence, and map canonical
statuses explicitly when the board has fewer lists.

## Continuation Rules For Any New Chat

1. Read this membrane, then `references/HANDOFF.md` and the canonical Tawan
   documents: `CURRENT_TASK_STATUS.md`, `DECISIONS.md`, `PRODUCT_SPEC.md`,
   `ARCHITECTURE.md`, `DATA_MODEL.md`, `SECURITY.md`, and
   `IMPLEMENTATION_PLAN.md`.
2. Inspect current Git status, branch, remote, and recent commits. Treat
   uncommitted work as owned work in progress, not as disposable noise.
3. Use Trello for task planning/status and Git for technical truth. Do not use
   Notion as a second active tracker.
4. Before coding, state the smallest safe milestone, impacted files, evidence
   needed, and any Duply owner decision required.
5. Never hallucinate store facts, platform interfaces, permissions, price,
   stock, legal conclusions, or deployment results. Mark unknowns as blocked or
   needing verification.
6. After a real change, run relevant tests, perform an independent review,
   update the decision log and affected docs, show `git status` before commit,
   and leave unrelated changes untouched.

## Canonical Reading Map

- `docs/tawan/README.md`: document index and reading order
- `docs/tawan/CURRENT_TASK_STATUS.md`: current roll-up and blockers
- `docs/tawan/DECISIONS.md`: approved decisions, including Pro-only Campaigns
- `docs/tawan/PRODUCT_SPEC.md`: product behavior and tier boundaries
- `docs/tawan/ARCHITECTURE.md`: trust boundaries and flows
- `docs/tawan/DATA_MODEL.md`: entities, lifecycle, and invariants
- `docs/tawan/SECURITY.md`: threats, privacy, retention, and launch blockers
- `docs/tawan/IMPLEMENTATION_PLAN.md`: ordered milestones and verification
- `docs/tawan/TASK_BREAKDOWN.md`: all 149 task definitions and dependencies
- `docs/tawan/DATA_FLOW.md`: current database and application data flow
- `docs/research/2026-08-17-thailand-pdpa-tawan-data.md`: legal research
  starting point, not legal advice
