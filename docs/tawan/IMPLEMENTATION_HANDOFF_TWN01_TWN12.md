# Tawan implementation handoff — TWN-01 through TWN-12

**Audience:** Duply.official / implementation team  
**Source:** `FEATURE_TASKS.md`, `FEATURE_MAP.md`, `DECISIONS.md`, and TWN-01–TWN-12 specifications  
**Planning baseline:** 2026-09-18  
**Important:** This is a planning-only development handoff, not production-data
approval or activation authorization.

The formal requirements and acceptance matrix are in
`TAWAN_IMPLEMENTATION_SPEC_REQUIREMENTS.md`; use that document for
implementation tickets, API/data contracts, test evidence, and release status.
The Supabase table/column contract and tenancy reconciliation are in
`SUPABASE_SCHEMA_REQUIREMENTS.md`; do not apply the draft migrations until the
TWN-04 data-model decision and RLS evidence are approved.

## How to use this handoff

Implement in dependency order. Each work item must link code, migration,
configuration, test evidence, and a short demo result. Do not infer permission
from a hidden UI button: backend authorization, Store Context, RLS, idempotency,
consent, and audit checks are the enforcement layer.

### Release blockers that remain open

1. **TWN-04:** architecture/security owner approval of the tenancy boundary and
   verified negative cross-workspace isolation tests.
2. **TWN-08:** Thai counsel approval of notices, lawful bases, controller/
   processor terms, retention, rights, transfers, breach handling, and sensitive
   data policy.
3. **TWN-12:** named Security, Operations, Thai counsel, and Incident Commander
   contacts plus signed product/security/operations/legal release evidence.

No real customer data, live merchant LINE activation, production payment, or
Phase 2 connector is authorized until these blockers are attached to the release
record.

## Workstream A — foundation and tenancy (TWN-01–TWN-04)

- Create the canonical Store Workspace model with immutable
  `store_workspace_id`, server-derived Store Context, workspace-scoped indexes,
  caches, foreign keys, and audit identity.
- Implement roles `platform_admin`, `store_owner`, `workspace_admin`,
  `store_staff`, and `customer`; grant explicit Capabilities rather than broad
  staff access.
- Separate Tawan Official management Channel from merchant customer LINE OA;
  bind management LINE only through signed webhook plus authenticated Owner
  linking; reject ambiguous, duplicate, revoked, or unlinked bindings.
- Enable RLS and least-privilege grants on every exposed table. Add negative
  tests for table reads/writes, views/functions, Storage, vectors, caches,
  analytics, exports, support access, and direct API paths.
- Implement the entitlement state machine: `active` → `payment_due` → `past_due`
  → `grace_period` → `suspended` → `closed` as provider status/time rules
  require, with idempotent audited transitions and Store Workspace timezone
  `paid_through` calculation. At paid-through end, stop new service but preserve
  read-only rights/records under retention policy; reactivation requires valid
  entitlement and Owner approval; closure never silently deletes data.
- Deny workspace-admin, staff, and platform-admin attempts to perform Owner-only
  actions: final payment, sensitive export/deletion approval, subscription,
  Duply settings, discounts/exceptions, management-Channel binding,
  administrator appointment/removal, ownership transfer, legal/retention
  settings, workspace closure, and reactivation.
- Keep onboarding/activation evidence, Owner approvals, verification gates, and
  support access reason-coded and auditable.

**Exit evidence:** migrations/schema review, RLS policy tests, role/capability
matrix, Channel-binding tests, entitlement transition tests, Owner-only denial
tests, and architecture/security sign-off.

## Workstream B — Store Brain and customer conversation (TWN-05–TWN-06)

- Ingest Owner-approved sources with provenance, checksum/version, sensitivity,
  expiry, conflict, malware, and prompt-injection checks.
- Keep raw uploads, published Store Knowledge, Knowledge Candidates, and
  Customer Memory separate. Only approved published facts enter customer replies.
- Implement natural Thai seller voice, focused questions, fact confirmation,
  safe “checking” responses, owner takeover/pause/resume, and idempotent LINE
  webhook handling.
- Build wishlist/restock requests and dashboard signals without proactive
  campaigns in Phase 1.

**Exit evidence:** synthetic conversations for approved/rejected/stale/conflicting
facts, owner takeover, memory refusal, STOP, restock, and replay/idempotency.

## Workstream C — Orders, stock, payment, and daily operations (TWN-07–TWN-09)

- Implement stock limits, overnight allowance, reservation expiry, waitlist,
  Morning Confirmation, order state/timing, and source-specific evidence.
- Payment slips/OCR are candidates only. Staff may inspect/prepare; only the
  Store Owner finalizes Phase 1 paid/rejected status.
- Refunds/cancellations are requests completed by an authorized human. Use
  idempotency keys, amount/exception limits, confirmation, and audit evidence.
- Build the Thai-first Duply dashboard with English option: Low Stock, Morning
  Confirmation, Orders/Payments, Customers/Follow-up, Tasks/Approvals,
  Catalog/Store Brain, Settings/Access.
- Enforce workspace_admin/staff boundaries server-side; Owner-only controls
  include final payment, deletion/export approval, subscription, Duply settings,
  discounts, and exceptions.
- Add authenticated management-LINE quick actions; customer LINE OA must never
  invoke management operations.

**Exit evidence:** state-machine tests, duplicate-payment tests, refund safety,
dashboard capability tests, stale/error states, timezone/business-day tests,
and audit records with actor, previous/new value, reason, and result.

## Workstream D — privacy, memory, AI workflow (TWN-08–TWN-10)

- Implement purpose-separated operational data, optional Store Workspace-local
  Customer Memory, marketing suppression, security/audit, and anonymous
  aggregates.
- Store source interaction IDs with minimised/redacted excerpts or hashes, not
  durable raw transcripts. Propagate correction/deletion/withdrawal through
  vectors, prompts, caches, queues, exports, dashboards, and training inputs.
- Implement Thai layered notices, versioned consent evidence, STOP/ยกเลิก/
  ไม่รับข่าวสาร, rights intake/verification/approval, retention jobs, legal
  holds, and redacted/time-limited exports.
- Capture meaningful conversation fields in real time with confidence,
  confirmation, source, model/rule version, and idempotency.
- Produce hourly refresh, store-local daily close, weekly review, and a daily
  Thai digest in Duply and authenticated management LINE with no more than three
  capability-filtered recommendations.
- Show `ข้อมูลยังไม่เพียงพอ` when evidence is missing; never rank by sensitive
  traits, hidden spending scores, unauthorized memory, or cross-customer value.

**Exit evidence:** consent/withdrawal/deletion tests, rights workflow tests,
redaction/retention tests, deleted-memory non-reappearance tests, digest samples,
insufficient-data samples, and recommendation expiry/dismissal tests.

## Workstream E — channels and integrations (TWN-11)

- Implement the versioned Channel Adapter contract: identity, Store Context,
  messages/media, delivery, consent, Capabilities, errors, rate limits,
  credentials, idempotency, pause/disconnect, audit, and deletion propagation.
- Phase 1 inputs: manual/templates/CSV/Sheets and Owner-selected Google Drive/API.
  Each new Drive-folder file is quarantined, scanned, validated, and approved
  before retrieval.
- Maintain one combined operational view while preserving source-specific stock,
  order, price, timestamp, reservation, and conflict state.
- No connector scope may finalize payment, approve refunds, alter prices/
  discounts, change subscriptions, or bypass Owner approval.
- Future candidates: Shopee, Facebook, TikTok, Instagram, Lazada. Score demand,
  authorization, reliability, security, cost, maintenance, and measurable value
  before any build. Tawan Official Instagram needs partner opt-in agreement.

**Exit evidence:** adapter contract tests, source reconciliation tests, Drive
quarantine tests, scope/reauthorization tests, pause/disconnect tests, and
product/technical/security approval for any connector.

## Workstream F — pilot and launch gate (TWN-12)

- Build a non-production pilot harness for ten planned Thai retailers, synthetic
  identities/messages, and a 30-day free pilot.
- Use separate test OA, credentials, provider sandbox/non-live PromptPay,
  synthetic IDs/slips, and hard rejection of live QR/callbacks, production
  writes, paid status, refunds, accounting, and real-money requests.
- Automate the rehearsal matrix: onboarding, knowledge approval/rejection,
  missing facts, memory refusal, STOP, expiry, duplicate payment, stock issue,
  dashboard/digest, rights/deletion, recovery, and incident pause/resume.
- Implement severity handling: Critical pause + 15-minute Security/Product Owner
  notification; High stop within one hour + Store Owner/Product Owner approval;
  explicit Incident Commander and evidence custody.
- Produce weekly pilot metrics with defined denominators/rubrics and cost-ledger
  records. Keep Product, Security, Operations, Thai counsel, and independent
  reviewer sign-offs as release artifacts.

**Exit evidence:** sandbox negative tests, synthetic-only proof, recovery/restore,
incident rehearsal, cost ledger, independent review, signed release approvals,
and Go/Hold/No-go decision.

## Definition of done for every implementation card

1. Code/configuration is linked to the relevant TWN spec and Trello card.
2. Positive and negative authorization tests pass, including direct API paths.
3. Idempotency/replay, stale/error, audit, privacy/retention, and failure paths
   are tested where applicable.
4. Evidence includes a reproducible command or test output and a short demo.
5. No real customer data or live money is used without the TWN-04/TWN-08/TWN-12
   release approvals.
