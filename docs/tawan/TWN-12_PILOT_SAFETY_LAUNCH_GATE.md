# TWN-12 — Pilot, Safety, and Launch Gate

**Status:** Approved planning baseline (2026-09-18); release gates remain open
**Phase:** Phase 1 pilot and decision gate
**Depends on:** TWN-01 through TWN-11

## Pilot charter

The pilot plans for ten Thai retailers selling physical products by the piece,
free for 30 days. Fashion/accessories may be a representative scenario, not a
recruitment restriction. The Product Owner is the primary pilot owner; the
Duply.official teammate assists only when assigned. Each merchant gets a named
onboarding/support owner, an onboarding schedule, issue triage, monitoring, and
a feedback survey for both Owner and staff.

There is no cashback or testing-payment route involving real customer money. A
clearly labelled sandbox/synthetic payment test verifies the payment workflow,
duplicate handling, evidence capture, and failure messages without production
Orders, refunds, accounting, or customer funds. Standard payment-link conversion
is evaluated only after pilot evidence and a separate Product Owner decision.

## Standard validation journey

1. Tawan Official explains the service and guides merchant onboarding.
2. The Store Owner supplies and approves Store Knowledge, policies, catalog,
   stock limits, Capabilities, consent settings, and LINE OA binding.
3. Duply runs a safe synthetic conversation and activation checks.
4. A synthetic/test identity uses test messages through a non-production
   Channel. Before release gates pass, no real LINE user ID, customer message,
   PII, Order, or production Channel activation is permitted.
5. The rehearsal covers stock, Order/reservation expiry, sandbox PromptPay/payment
   review, duplicate-payment conflict, human work, dashboard update, and daily
   digest.
6. Owner and staff review results, support issues, and feedback; no real-data
   activation occurs until every release gate passes. Any later real-data
   activation requires the signed release gates below.

## Sandbox payment contract

The payment rehearsal uses a separate non-production environment, test LINE OA,
test-only provider credentials, synthetic payee/account/reference data, and
non-live PromptPay destinations or a provider sandbox. Production PromptPay QR,
merchant bank details, live callbacks, payment credentials, ledger writes,
production Orders, refunds, accounting, and customer money requests are hard
blocked by configuration and authorization checks. Negative tests must prove
live credentials and live QR are rejected, production writes are rejected,
replayed test events are idempotent, and sandbox evidence cannot mark a
production Order paid. Any accidental real-money signal immediately pauses the
test and escalates as Critical.

## Synthetic rehearsal matrix

The primary rehearsal must include both success and failure paths:

- approved and rejected Knowledge Candidates, conflict, stale fact, and Owner
  approval;
- missing/conflicting product or stock facts, focused question, safe escalation,
  and no invented answer;
- customer refusal of durable memory and `STOP`/Thai marketing suppression;
- Order reservation expiry, stock unavailable after payment, and human remedy;
- sandbox PromptPay evidence review, duplicate fingerprint/conflict, and replay;
- dashboard queues, audit record, daily digest, insufficient-data state, and
  Owner/Staff Capability boundaries;
- export/deletion request, support access, incident pause, recovery, and resume.

## Required evidence before real customer data

### Security and isolation

- credential rotation and secret inventory;
- Supabase RLS/tenant isolation, Store Context, Channel separation, and negative
  tests across Channel, retrieval/vector/cache, tools, analytics, staff,
  exports, and support boundaries;
- runtime contract verification, authorization/idempotency/replay tests, and
  no payment/refund/discount bypass;
- private storage, signed-URL expiry, deletion propagation, and no raw-secret
  exposure.

### Privacy, legal, and rights

- Thai counsel-approved privacy notices, lawful bases, controller/processor
  agreement, retention schedule, marketing rules, international-transfer
  arrangements, rights/export terms, and breach process;
- consent, STOP, memory withdrawal, access/correction/deletion/restriction,
  legal-hold, minimised export, and audit evidence;
- no real customer data before the counsel and security gates are signed.

### Reliability, operations, and cost

- recovery/restore exercise with evidence of RPO/RTO assumptions;
- incident detection, containment, credential rotation, escalation, and resume
  rehearsal with severity ownership;
- support runbook, monitoring, stale/error behavior, and independent review;
- every paid model/API/provider call recorded in the project cost ledger at the
  moment it succeeds, with pilot cost per merchant reported.

## Incident severity and pause rules

| Severity | Examples | Required response |
| --- | --- | --- |
| Critical | cross-store leak, unauthorized commercial action, secret exposure, payment corruption | Incident Commander pauses affected merchant/workflow immediately; preserve evidence, notify Product Owner and Security within 15 minutes, assess Store Owner/customer/regulator communication with counsel, rotate/isolate, and require Product Owner + Security reactivation |
| High | repeated wrong reply, unauthorized scope, duplicate action, material stale stock | Operations lead stops affected automation within 1 hour, creates remediation, notifies Store Owner/Product Owner, and requires Store Owner + Product Owner approval and retest before resume |
| Medium | workflow defect or missed digest without data exposure | Track owner/due date, correct during pilot, regression test |
| Low | wording, usability, non-blocking report issue | Backlog and review in weekly report |

## Pilot reporting and acceptance

Weekly reports cover onboarding progress, daily-summary usefulness, reply
corrections, stock/order/payment issues, support time, incidents, staff/Owner
feedback, cost, and proposed changes. The recruitment/planning target is ten
merchants; actual cohort size is reported separately. Initial targets are
provisional and may be revised only through an evidence-based Product Owner
decision:

- 10-merchant recruitment/planning target;
- 80% onboarding completion;
- 14 consecutive useful daily summaries for every active merchant;
- 85% routine replies without correction;
- two hours saved per merchant each week;
- zero cross-store leaks or unauthorized commercial actions;
- 50% paid conversion after the free pilot.

Measurement definitions: an active merchant has completed activation and used the
service at least once in the reporting period; a useful daily summary passes an
Owner rubric for accuracy, actionable next step, freshness, and no unsupported
claim; a routine reply is a supported FAQ/product/status reply; correction means
Owner/staff edits or rejects the response within the review window. Denominators,
exclusions, source event IDs, survey responses, and weekly reporting windows are
recorded. Time saved uses a weekly Owner/staff survey with a fixed baseline
question and sampled task-duration evidence.

Any zero-leakage, unauthorized-action, legal, or security gate failure blocks
real-data activation regardless of other metrics.

## Phase 2 go/no-go

At pilot close, the Product Owner reviews the evidence with an independent
reviewer who is not responsible for implementation, pilot support, or the
recommendation itself. The reviewer identity, conflict check, evidence reviewed,
and sign-off are recorded before a Go decision. The decision record must cover
safety/security,
merchant/customer satisfaction, digest usefulness, reply accuracy, time saved,
payment/order reliability, support workload, paid conversion, connector demand,
and Pro feature demand. It selects one outcome:

- **Go:** named Phase 2 connector/Pro work, owner, budget, risks, and acceptance
  criteria;
- **Hold:** extend pilot or fix named gaps with a new review date;
- **No-go:** stop or redesign the affected scope with evidence and rationale.

No Phase 2/3 feature or connector launches before this decision and its release
gates are recorded.

## Approval owners

Product Owner (you): pilot scope, acceptance changes, final go/no-go.  
Store Owner: merchant-specific data, policies, Capabilities, and activation.  
Duply.official: assigned support and technical coordination; not the independent
go/no-go reviewer.  
Security lead (named before activation): isolation, runtime, incident, recovery,
and credential evidence.  
Operations lead (named before activation): support, monitoring, cost, and weekly
reporting.  
Thai counsel/contact (named before activation): legal/privacy artifacts and
real-data release approval.  
Incident Commander (named per incident): declares severity, owns evidence
custody, coordinates notifications, and proposes reactivation. Missing owners
block activation; role assignments and contact details are stored in the release
record.

## Out of scope

Automatic real-money refunds, cashback, production payment testing with customer
funds, silent real-data activation, Phase 2/3 launch before go/no-go, and any
waiver of consumer, privacy, security, or Owner-approval requirements.
