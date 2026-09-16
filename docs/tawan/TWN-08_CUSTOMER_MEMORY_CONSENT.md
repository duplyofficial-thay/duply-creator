# TWN-08 — Customer Memory, Privacy, Consent, and Data Lifecycle

**Status:** Approved for documentation and implementation planning (2026-09-17)
**Phase:** 1, with legal/security gates before real customer data
**Owner:** Product Owner (Tawan/Duply)
**Depends on:** TWN-04 Workspace and access boundaries

## Outcome

Tawan may use the minimum data needed to provide store service, while durable
Customer Memory and direct marketing remain separate, transparent choices. All
data is scoped to a Store Workspace, evidence-backed, time-limited, auditable,
and removable. Tawan can classify and route a request; it cannot make a legal
determination or disclose a rights export without the approved workflow.

## Data-purpose map

| Purpose | Allowed data | Boundary and default |
| --- | --- | --- |
| Operational service | LINE identity, conversation context, customer/order details needed to answer and fulfil | Necessary for the requested service; Store Workspace only |
| Customer Memory | Short preference/service facts with source, confidence, confirmation, validity and expiry | Optional durable choice; no global profile or cross-store matching |
| Direct marketing | Contact/channel, campaign purpose, consent evidence and suppression state | Separate opt-in; STOP/Thai equivalent immediately suppresses it |
| Security, fraud, audit and legal hold | Access events, consent history, incident evidence, payment/order evidence where required | Restricted, append-only/tamper-evident where practical; never used as marketing memory |
| Anonymous aggregate analysis | De-identified counts/trends after re-identification testing | No direct or reasonably linkable identity; no secret credentials |

Sensitive traits are not collected, inferred, segmented, or used for targeting
by default. A Customer Tier is a transparent, evidence-backed operational label,
not a sensitive-trait proxy and never, by itself, authorizes a discount.

## Customer Memory contract

Each memory item is scoped by `store_workspace_id` and `customer_id` and records:

- `memory_type`, short summary, source interaction/event, and channel;
- confidence, confirmation state, first/last observed, effective-from and expiry;
- correction/dispute/deletion state, consent basis, creator, and audit timestamps.

Memory is never used to match or identify the same person across stores. A
correction or deletion request propagates to primary records, derived vectors,
prompt context, caches, queues, exports, dashboards, and future training inputs
where technically applicable. Training material is limited to rough anonymous
patterns; it must not contain credentials, payment secrets, identity evidence, or
re-identifiable customer details.

## Layered Thai privacy experience

The LINE flow must provide a short Thai notice, a link to the full privacy notice,
and a plain service explanation. Durable memory and marketing are separate,
optional choices. Approved baseline copy:

> ร้านใช้ข้อมูลที่จำเป็นเพื่อช่วยตอบคำถามและดูแลคำสั่งซื้อค่ะ การบันทึกความจำเพื่อช่วยบริการครั้งต่อไปและการรับข่าวสารการตลาดเป็นตัวเลือกแยกกัน อ่านรายละเอียดได้ที่ [ลิงก์] และเปลี่ยนแปลงตัวเลือกได้ทุกเมื่อค่ะ

Memory prompt:

> ต้องการให้ Tawan จำความชอบนี้ไว้ช่วยครั้งต่อไปไหมคะ? เลือก ‘ยินยอม’ หรือ ‘ไม่ต้องการ’ ได้ค่ะ การไม่ยินยอมไม่กระทบการใช้บริการปกตินะคะ

The final notice, purposes, lawful bases, controller/processor terms, transfers,
retention and rights wording require Thai counsel approval before launch.

## Consent and suppression evidence

Every choice records Store Workspace, Customer, purpose, Channel, exact wording
and version, timestamp, actor/source, consent state, withdrawal timestamp and
the resulting suppression action. `STOP`, `ยกเลิก`, `ไม่รับข่าวสาร`, and approved
equivalents immediately suppress marketing for that workspace/customer/purpose/
channel. Normal service, order support and safety messages continue unless the
customer separately restricts them.

## Rights workflow

Supported rights are access, copy/export where applicable, correction, deletion,
restriction/suppression, objection, consent withdrawal, and complaint/escalation.
Tawan classifies the request and creates auditable work; the Store Owner and
Duply privacy contact approve the response. Ordinary LINE chat does not request
passport or national ID. Low-risk requests use LINE identity plus a second
account detail; export, deletion, sensitive data, or suspected takeover require
stronger verification and Store Owner approval. Exports are minimised, redacted,
time-limited, and delivered only to the verified requester. The service
acknowledges a request within 1 business day and targets completion within 30
calendar days (or a shorter counsel-configured period), recording any lawful
extension, reason, owner, and customer notice. Legal hold pauses deletion only
for the documented records and reason.

Withdrawal of durable-memory consent immediately suppresses that memory from
retrieval, prompts, vectors, caches, queues, dashboards, exports, and future
training inputs, then deletes or anonymises it under the applicable retention or
legal-hold rule. A negative test must prove it cannot reappear in a later reply.

Customer Tier assignment and override are Store Owner-only actions. Each action
records actor, evidence source, reason, timestamp, previous/new value, expiry,
customer visibility, correction/appeal state, and audit history. Staff see only
the minimum permitted label; automation may recommend nothing in Phase 1.

Retention values are configurable per workspace only within Duply-approved
minimum/maximum bounds. A scheduled deletion job records its run, item count,
failure/retry, legal-hold exclusions, and verification result. Raw-chat default
is 30 days (maximum 90 without counsel approval); memory default is 12 months
since last relevant observation; transient vectors/caches/queues/exports are 24
hours or less unless an active workflow requires less; payment/order evidence,
consent/audit logs, backups, and legal holds use counsel-approved periods with
documented maximums.

Anonymous aggregate analysis requires a minimum cohort of 10, suppresses rare
patterns and small stores, passes a re-identification test, and prohibits
reconstructing a customer or store from multiple outputs.

## Retention and deletion defaults

| Data | Default | Deletion/suspension rule |
| --- | --- | --- |
| Raw chat/transient context | About 30 days | Delete after purpose unless active Order, dispute, legal hold, or security incident |
| Customer Memory | 12 months after last relevant observation | Individual expiry; delete/correct on approved request |
| Order/payment evidence | Counsel-approved accounting, dispute, and legal period | Restricted after fulfilment; legal hold wins |
| Consent and audit/security logs | Restricted, append-only/tamper-evident; counsel-approved period | Redact/minimise where possible; retain only the evidence needed |
| Vectors, caches, queues, exports | Short-lived and no longer than source purpose | Delete on source deletion/expiry and verify propagation |
| Anonymous aggregates | Only after de-identification and re-identification testing | Retain only while genuinely anonymous and useful |

Inactive or cancelled subscriptions stop service at the paid period end, but do
not silently delete the merchant's records. Re-activation requires an approved
status change; retention and rights continue to apply.

## Controller and processor model

The merchant is the primary controller for customer/order data. Duply/Tawan is
the processor/service provider for that workspace. Duply is an independent
controller for platform account, billing, fraud, security, and audit data. Any
external AI or analytics provider must be an approved processor under contract,
receive minimum necessary data, have no-training-by-default, and meet retention,
location, transfer, and deletion requirements. Thai counsel confirms the final
classification and legal bases.

## Security baseline and acceptance gates

1. Separate purpose, audience, sensitivity, retention, and access on every record.
2. Enable Supabase RLS and least-privilege grants on every exposed table; test
   select/insert/update/delete isolation. Service keys remain backend-only;
   views and functions are reviewed because they may bypass intended RLS.
3. Keep Storage buckets private with object RLS and short-lived signed URLs; do
   not mutate the managed Storage schema directly.
4. Verify the raw LINE webhook body with the channel-secret HMAC signature before
   parsing; process asynchronously and idempotently.
5. Detect, contain, preserve evidence, rotate credentials, assess risk, and
   execute counsel-approved regulator/customer notification for incidents.
6. Run negative tests for cross-workspace reads, cross-customer exports, deleted
   memory reappearance, stale signed URLs, webhook forgery, and replay.
7. Do not promise zero leakage; use defence in depth and document residual risk.

Before real customer data, Thai counsel must approve the privacy notice, lawful
bases, consent wording, controller/processor terms, provider/cross-border
processing, retention, rights workflow, breach plan, and sensitive-data policy.
Duply security must approve the technical controls and negative-test evidence.

## Out of scope for this milestone

- Passport/national-ID collection as routine LINE onboarding.
- Cross-store identity graphs, sensitive-trait segmentation, autonomous legal
  decisions, or automatic discounts.
- Automatic deletion of records under legal hold.
- Final legal advice; this document is an implementation baseline for counsel.

## Authoritative references

- Thai government PDPA resources: Department of Lands, FDA, and government
  retention guidance.
- Supabase RLS, API, and Storage security documentation.
- LINE Messaging API webhook signature and receiving-message guidance.
