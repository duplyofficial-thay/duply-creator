# Tawan implementation specification and requirements

**Document ID:** TAWAN-IMPL-001  
**Version:** 1.0 planning baseline  
**Date:** 2026-09-18  
**Implementer:** Duply.official  
**Product Owner:** Arriyathanasak / Tawan owner  
**Status:** Ready for development planning; not production approval

## 1. Purpose and source of truth

This document translates TWN-01 through TWN-12 into buildable requirements.
Feature behavior remains authoritative in the linked TWN specifications; this
document defines implementation order, contracts, acceptance evidence, and
release controls.

Required reading:

- `docs/tawan/IMPLEMENTATION_HANDOFF_TWN01_TWN12.md`
- `docs/tawan/FEATURE_MAP.md`, `FEATURE_TASKS.md`, and `DECISIONS.md`
- `TWN-01_PRODUCT_DIRECTION.md` through `TWN-12_PILOT_SAFETY_LAUNCH_GATE.md`

## 2. Non-negotiable release boundary

Until all release evidence is attached, the system must use synthetic identities,
test messages, non-production Channels, and sandbox payment data only. It must
reject live PromptPay QR/bank details, production payment credentials, live
callbacks, production database writes, real Orders, refunds, accounting writes,
and real customer-data activation.

Open approvals:

| Gate | Required evidence | Owner |
| --- | --- | --- |
| Architecture/security | Tenancy choice, RLS/context review, negative isolation tests | Named Security/Architecture lead |
| Privacy/legal | Thai notices, lawful bases, controller/processor terms, retention, rights, transfers, breach, exports | Named Thai counsel/contact |
| Operations | Support runbook, monitoring, cost, recovery, incident rehearsal | Named Operations lead |
| Product/release | Pilot scope, acceptance metrics, Go/Hold/No-go | Product Owner |
| Incident readiness | Incident Commander, evidence custody, notification and reactivation policy | Named Incident Commander |

Missing names or signatures block activation.

## 3. Functional requirements

### FR-001 — Store Workspace and access (TWN-04)

- Every merchant-owned record has immutable `store_workspace_id`.
- Store Context is derived server-side from authenticated membership/Channel;
  client input and model output cannot select a workspace.
- Roles are `platform_admin`, `store_owner`, `workspace_admin`, `store_staff`,
  and `customer`; staff receive explicit Capabilities.
- Owner-only actions include final Phase 1 payment decision, sensitive export/
  deletion approval, subscription, Duply settings, discounts, exceptions,
  ownership transfer, legal/retention settings, management-Channel binding,
  appointing/removing administrators, workspace closure, and reactivation.
- Entitlement states are `active`, `payment_due`, `past_due`, `grace_period`,
  `suspended`, and `closed`. Transitions are provider-status/time driven,
  idempotent, audited, and calculate `paid_through` in the Store Workspace
  timezone. At paid-through end, new service stops; read-only records, rights,
  exports, and support remain governed by policy. Reactivation requires valid
  entitlement and Owner approval; closure is explicit and never silently
  deletes records.

### FR-002 — Channel separation (TWN-02, TWN-04, TWN-11)

- Tawan Official and merchant customer LINE OA use distinct Channel types,
  credentials, webhook routes, permissions, and audit events.
- Customer LINE OA cannot invoke management operations; management LINE requires
  signed event, Owner-linked membership, workspace binding, Capability, state,
  confirmation, and idempotency checks.
- LINE OA is the only complete customer Channel in Phase 1.

### FR-003 — Store Brain and safe replies (TWN-05, TWN-06)

- Sources require provenance, checksum/version, sensitivity, expiry, validation,
  malware scan, prompt-injection scan, and Owner approval before publication.
- Raw upload, Knowledge Candidate, published Store Knowledge, and Customer
  Memory are separate records.
- Tawan asks one focused question, confirms important facts, says it is checking
  when uncertain, and creates human work instead of inventing facts.
- Owner takeover/pause/resume and idempotent webhook processing are required.

### FR-004 — Orders, stock, payment, and refunds (TWN-07)

- Revalidate price/stock, reserve with expiry, track state duration, and create
  waitlist/demand work when unavailable.
- OCR/payment extraction creates a candidate only. Staff may inspect/prepare;
  only Store Owner finalizes paid/rejected status.
- Refund/cancellation is a request completed by an authorized human with
  idempotency key, reason, amount/exception boundary, confirmation, and audit.
- Duplicate payment evidence creates review; it never auto-approves or rejects.

### FR-005 — Customer Memory, consent, and rights (TWN-08)

- Separate operational service, optional Store Workspace-local memory, marketing,
  security/audit, and anonymous aggregate purposes.
- Events store source interaction ID plus minimised/redacted excerpt/hash, not a
  durable raw transcript. Withdrawal/deletion propagates to derived copies.
- Record versioned notices/consent, STOP equivalents, identity verification,
  rights intake, approval, redacted export, legal hold, retention, and deletion.
- Sensitive traits and hidden customer-value profiling are prohibited by default.

### FR-006 — Dashboard and AI workflow (TWN-09, TWN-10)

- Dashboard order: Low Stock; Morning Confirmation; Orders/Payments;
  Customers/Follow-up; Tasks/Approvals; Catalog/Store Brain; Settings/Access.
- Thai-first with English option; store-selected timezone; explicit loading,
  empty, stale, error, and insufficient-data states.
- Real-time structured capture, hourly refresh, store-local daily close, weekly
  review, and daily digest in Duply plus authenticated management LINE.
- Digest contains no more than three Capability-filtered recommendations with
  evidence, confidence, explanation, model/rule version, assignee, expiry, and
  accept/dismiss/snooze audit.
- `ข้อมูลยังไม่เพียงพอ` blocks unsupported insight; ranking cannot use sensitive
  traits, hidden spending scores, unauthorized memory, or cross-customer value.

### FR-007 — Adapters and imports (TWN-11)

- Versioned adapter contract covers identity, Store Context, text/media,
  delivery, consent, Capabilities, errors, rate limits, credentials,
  idempotency, pause/disconnect, audit, and deletion propagation.
- Phase 1 imports are manual/templates/CSV/Sheets and Owner-approved Drive/API.
  Every newly added Drive-folder file is quarantined, scanned, validated, and
  approved before retrieval.
- Unified views preserve per-source stock/order/price/timestamp/conflict data.
- No connector scope can finalize payment, approve refunds, alter price/discount,
  change subscription, or bypass Owner approval.

### FR-008 — Pilot and launch gate (TWN-12)

- Non-production pilot harness: ten planned Thai retailers, synthetic identities,
  30 days, support/feedback, and weekly evidence.
- Sandbox payment uses separate test OA/environment/credentials, synthetic IDs,
  non-live destination, hard production-write rejection, and replay tests.
- Critical issue: pause immediately, notify Product Owner/Security within 15
  minutes, preserve evidence, isolate, and require Product Owner + Security to
  reactivate. High issue: stop within one hour and require Store Owner + Product
  Owner approval and retest.
- Phase 2 outcome is Product Owner-owned Go/Hold/No-go with independent review.

## 4. Data and event contract

Every operational event includes: `event_id`, `store_workspace_id`, source
Channel, actor/member, Capability, entity type/id, action, previous/new state,
source interaction ID, confidence, confirmation state, model/rule version,
idempotency key, local/UTC timestamps, reason, consent/purpose reference, and
retention/deletion class. Secrets, raw payment credentials, and durable raw
transcripts are prohibited.

## 5. Non-functional requirements

- **Isolation:** RLS and backend authorization on every read/write; negative
  tests across UI, LINE, views/functions, Storage, vectors, analytics, exports,
  support, and direct API.
- **Reliability:** idempotent retries, replay protection, explicit stale/error
  states, pause/disconnect, recovery/restore evidence, and no silent financial
  retries.
- **Privacy:** purpose/audience/consent/retention on each data class; redaction,
  deletion propagation, legal holds, and time-limited exports.
- **Auditability:** append-only/tamper-evident action trail where practical;
  actor, Capability, before/after, reason, result, and evidence reference.
- **Observability:** alerts for isolation failure, unauthorized scope, payment
  conflict, stale data, provider failure, cost anomaly, and incident severity.
- **Cost:** log every paid model/API/provider call at success time; report cost per
  pilot merchant weekly.
- **Localization:** Thai-first copy with English option; store-local dates,
  cutoffs, business date, and safe customer wording.

## 6. Test and evidence matrix

| Area | Required proof |
| --- | --- |
| Tenant/Channel | Cross-workspace and cross-Channel negative tests through UI, LINE, and API |
| Authorization | Owner/admin/staff/customer capability matrix; final-payment/refund/discount denial |
| Idempotency | Webhook replay, duplicate payment, repeated refund request, connector retry |
| Privacy | Consent/STOP/withdrawal, rights verification, redacted export, deletion propagation |
| AI safety | Missing/conflicting fact, insufficient data, stale source, prompt injection, no guessing |
| Payments | Sandbox-only credentials/QR/callback, production-write rejection, paid-state denial |
| Operations | Morning Confirmation, timezone, stale/error states, incident pause/resume |
| Recovery | Restore exercise, secret rotation, disconnect/reauthorize, evidence custody |
| Pilot | Weekly metrics, survey rubric, cost ledger, independent review, Go/Hold/No-go |

## 7. Implementation sequence and Trello evidence

Implement in this order: TWN-04 foundation → TWN-05/06 knowledge/replies →
TWN-07/09 orders/dashboard → TWN-08/10 privacy/workflow → TWN-11 adapters →
TWN-12 pilot gate. Every implementation card must contain:

1. linked source spec and code/configuration;
2. migration/API/config notes;
3. positive and negative test output;
4. security/privacy/audit evidence;
5. short demo or reproducible command;
6. explicit status: Ready, Blocked, In Review, or Done.

## 8. Definition of done

Development is not complete when the UI renders. It is complete only when the
specified behavior works through UI, management LINE, backend, and direct API;
negative tests prove forbidden actions fail; evidence is reproducible; and the
relevant release gate is signed. Real customer data and live money remain blocked
until TWN-04, TWN-08, and TWN-12 approvals are attached.
