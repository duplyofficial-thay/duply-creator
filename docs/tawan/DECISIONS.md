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

## 2026-09-03 - Reply flow captures structured data inline

Tawan no longer uses a separate post-conversation Noter step as the default path. The customer reply orchestration step now produces both the customer-facing response and the structured internal capture for that inbound event: Interaction Events, Sales Journey updates, Tasks, Approval requests, Order changes, and Customer Memory candidates as applicable.

Structured capture must run under the verified Store Context and deterministic command validation. Writes need idempotency keys tied to the inbound channel event and reply attempt so retries cannot duplicate Tasks, Orders, or memory candidates. Permanent Store Knowledge still requires Store Owner approval, Customer Memory still needs source and confidence metadata, and raw message retention remains short.

## 2026-09-03 - Selective integration of GitHub Tawan scaffold

The GitHub scaffold/provisioning commit is integrated selectively into the
canonical creator-kit checkout. Approved Tawan documentation, tests, and
decision history remain authoritative locally. Remote deletion of those docs
and tests is not accepted as part of the integration. Card rendering, data
fetching, and reach hooks remain stubs until the Duply runtime contracts are
verified.

## 2026-09-03 - Close operational data-model gaps from team review

The team review identified pilot-critical gaps around staff takeover, outbound
message evidence, usage cost, order amendments, shipping/COD/returns, schema
drift, branch hours, scheduled-job evidence, entitlements, tax foundations,
and cross-border processing records. These are now represented in the
store-scoped `0030_tawan_operational_safety` migration and absorbed into `REFERENCE.md`. Cross-store payment-slip fingerprinting and
Thai legal treatment of external AI transfers remain explicit platform/legal
decisions; they are not enabled implicitly by the store schema.

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

## 2026-08-18 - Campaign activity is Pro-only

Outbound Campaign drafting, scheduling, delivery, personalization, attribution, and Campaign intelligence are Pro-tier capabilities delivered after the Phase 1 transition gate. Standard plans retain customer-service messaging, store- and Channel-specific consent and objection records, and operational commerce analytics, but do not execute proactive Campaigns. This decision supersedes the earlier implementation-plan placement of Campaign execution alongside Phase 1 Standard analytics.

## 2026-08-20 - Initial Tawan test toolchain

The initial `TWN-0201` test baseline uses Python's standard-library `unittest` runner plus `compileall` so a clean local checkout can produce unit and syntax evidence without downloading packages. Real provisioning still requires `PyYAML`, and database/LINE/Supabase tests remain blocked until Duply confirms the private runtime and verification environment.

## 2026-09-04 - Trello is the active task board

The team will plan and execute Duply/Tawan work in the [Duple - Tawan Trello
board](https://trello.com/b/HUbjHwDh/duple-tawan) inside the Duply workspace.
Stable `TWN-*` identifiers remain the join key to the Git task manifest and
evidence. Trello lists are the operational status; when a destination board has
fewer lists than the canonical manifest, the original status remains explicit
in the card description. Notion is retained as historical reference and is not
updated as a parallel active board.

## 2026-09-09 - Tawan restarts planning with twelve feature specifications

The product owner approved a clean, documentation-first feature map: `TWN-01`
through `TWN-12`. Each card completes when its design, specification,
requirements, acceptance criteria, and out-of-scope boundary are approved; it
does not authorise implementation. The map covers product direction, Tawan
Official, merchant onboarding, Store Workspace/access, Store Brain, customer
sales, store operations, Customer Memory/consent, dashboard, AI workflow,
Channels/integrations, and pilot/safety/launch gate. Earlier long-form
engineering `TWN-*` cards remain historical evidence/backlog and are not
deleted or renumbered. The active feature map is `FEATURE_MAP.md`; the approved
Phase 1 product detail is `PHASE_1_PILOT_SPEC.md`.

## 2026-09-10 - TWN-01 product direction approved

The product owner approved the complete TWN-01 roadmap and its eight
requirement rows. Tawan is a LINE-first sales-administration partner for Thai
SMEs and solo entrepreneurs selling physical retail items by the piece. It
helps teams respond consistently, capture customer and Order details, and act
on daily follow-ups while humans retain authority over money and exceptions.

The Phase 1 pilot is free for 30 days and planned for ten merchants, subject
to recruitment evidence. It includes assisted onboarding, a merchant-owned
LINE OA, Store Brain, safe sales/admin support, an action-first dashboard, and
a daily digest. Tawan Official manages Tawan subscription billing after the
pilot; it never owns or autonomously decides a merchant customer's Order
payment. Standard price and Pro entitlements remain deliberately open until
pilot feedback, survey results, willingness-to-pay, and purchasing-power
evidence are reviewed. Pro is a future higher-paid tier for special advanced
capabilities, with no entitlement or price promised in Phase 1.

Phase 2 is demand-proven integrations plus owner-approved Pro campaigns,
segmentation, and advanced insights. Phase 3 is mature multichannel
operations, recurring billing, advanced intelligence, and optional merchant
showcase/brand-ambassador work. Marketplace, multichannel connectors,
campaigns, autonomous commercial actions, cross-store identifiable data use,
and real customer data before the legal/security/runtime launch gates are
explicitly out of scope. The detailed source of truth is
`TWN-01_PRODUCT_DIRECTION.md`.

## 2026-09-03 - Approved additive schema applied to Supabase

With explicit owner approval, the up sections of migrations `0010`, `0020`,
and `0030` were applied to project `fpjevusrpausqunjhubk`, schema `tawan_ai`,
through the signed-in Supabase SQL Editor. The transaction completed
successfully. Verification found 59 tables total: 12 expected Tawan table
checks plus the 12 existing platform tables, with 96 indexes. Existing
platform tables and data were preserved. The migration was executed without
RLS after Supabase presented its warning; RLS policies and runtime authorization
are a required follow-up before customer data is exposed.

## 2026-09-11 - TWN-02 Tawan Official management-plane contract approved

Tawan Official is Duply's management Channel for discovery, plain-Thai
qualification, onboarding coordination, support, and merchant subscription
status. Duply's main platform is the discovery surface; a merchant then
connects to Tawan Official and says “Hi”. The merchant's own LINE OA remains
the customer-facing sales Channel. An immutable `handoff_id` joins Duply and
Tawan records; Tawan reads only approved fields through a controlled service or
approved view, never unrestricted database data, secrets, prompts, customer
conversations, Store Knowledge, Orders, or payment evidence.

The approved journey is `discovered → handoff_pending → connected →
acknowledgement_pending → pilot_request_draft → team_review →
needs_merchant_input → approved_for_onboarding → onboarding_in_progress →
activation_pending → activated`, with explicit escalation, ineligible,
withdrawn, and closed exits. Six qualification fields are required; partial
answers are saved and reviewed before submission. Duply owns queue identity,
subscription/payment-process status, and paid-through time. Tawan owns detailed
Store Workspace onboarding after handoff. Activation may be deterministic for
the regular paid path only when payment, qualification, workspace, merchant
LINE OA, legal/privacy acknowledgement, Store Knowledge approval, test
conversation, and no-exception gates all pass; otherwise a named team queue
must intervene.

The free 30-day pilot has no cashback/refund system route. Post-pilot Standard
conversion hands to a Duply-owned PromptPay or online provider such as Stripe;
price and Pro entitlements remain open pending pilot survey and purchasing
power evidence. Subscription state is tracked per merchant/Store Workspace,
stays active through the paid-through day, and closes at end of day in the
merchant timezone after cancellation with no automatic refund. Customer Order
PromptPay and payment slips remain outside Tawan Official merchant billing.
The implementation-ready conversation map and acceptance criteria are
`TWN-02_TAWAN_OFFICIAL.md`; TWN-04 must still resolve the existing tenancy
model conflict before production implementation.

## 2026-09-14 - TWN-03 merchant onboarding contract approved

The product owner approved the TWN-03 onboarding checklist and gates. Phase 1
targets Thai small-to-medium social-commerce merchants selling physical retail
products by piece. Onboarding is assisted, one question at a time, with partial
save, editable summary, owner approval, and explicit test-ready/live-ready
states. Required inputs cover Duply identity, owner authority, constrained brand
voice, timezone and operating hours, staff, store policies, consent/legal
acknowledgements, catalog/price/variant/stock source, merchant LINE OA, and a
manual fulfilment path.

Pilot identity verification is intentionally low-friction: verified Duply
account, email, phone, linked LINE identity, consistent store details, and an
owner-authority declaration. Passport or national-ID documents are not required
for ordinary pilot onboarding. Tier 2 signals pause activation and create a
Duply review. Only an authorised Duply reviewer may request strong identity
verification through a secure provider/vault for confirmed risk, provider/legal
requirements, or higher-risk capability. Tawan records the verification result
and audit metadata, not identity documents. Potential fraud or illegal selling
is signalled to Duply; Duply confirms, restricts, or suspends and manages lawful
authority requests.

Approved sources are guided templates, CSV, Google Sheets, protected uploads,
and owner-approved-domain website imports. Malware/file checks, protected
storage, prompt-injection/data-exfiltration controls, provenance, checksum,
confidence, conflicts, effective/expiry dates, and no public file path are
required. Extracted facts remain Knowledge Candidates until the Store Owner
approves published Store Knowledge. Before live-ready, legal acknowledgements,
merchant LINE OA verification, approved Store Knowledge, a successful test
conversation, and Duply's activation decision are required. Manual
fulfilment/delivery/returns are sufficient for the pilot; POS, courier, and
automatic shipping integrations remain out of scope.

The detailed source of truth is `TWN-03_MERCHANT_ONBOARDING.md`. Duply team
feasibility, security/privacy, UX, and Thai-counsel review remain gates before
production implementation or any passport/national-ID collection.

## 2026-09-14 - TWN-04 Store Workspace and access contract approved

The product owner selected one shared `tawan_ai` schema with many Store
Workspaces and mandatory workspace scope on every store-owned row. This choice
is valid only with database-enforced RLS, server-derived transaction-local Store
Context, workspace-scoped foreign keys/indexes/caches/queues/exports, private
object storage, atomic quota accounting, and negative cross-workspace tests.
The client, model, tool, URL, message, stale session, retry, webhook, or
background job may never choose or change `store_workspace_id`.

Customer operational records use shared workspace-scoped relational tables;
documents, images, slips, and other binary data use private workspace-bound
object storage. The starting Store Knowledge quota is 1 GB per workspace with
70/85/100% warnings and atomic reserve/release accounting. Signed URLs are
short-lived and issued only after authorization; upload, read, download,
replacement, deletion, expiry, and quota decisions are audited.

The canonical access model is exactly one primary `store_owner`, optional
`workspace_admin`, and capability-based `store_staff` (`manager`, `sales`,
`fulfilment`, `marketing`, `knowledge_editor`, `payment_review`). Owner-only
actions include owner/admin grants, sensitive capability changes, management
Channel binding, Store Knowledge publication, final Phase 1 payment decisions,
legal/retention changes, ownership transfer, and workspace closure/reactivation.
Legacy `owner` maps to `store_owner`; `employee` maps to `store_staff`; unknown
or conflicting labels receive no elevated access.

Tawan Official management LINE and the merchant customer-facing LINE OA are
separate security domains. Each management LINE ID requires signed-event
verification and explicit Owner approval, with immediate revocation and
idempotency/replay protection. Retrieval, vectors, prompts, tools, caches,
logs, queues, and exports carry the same server-derived workspace scope.

Membership and subscription are separate. After the paid-through day, the
workspace becomes `suspended`: new customer replies, API/tool actions,
onboarding/knowledge changes, outbound sends, Orders, and payment operations
stop; retained records remain under their own retention schedules. Expired
owners/admins receive restricted read-only status/reactivation information.
Reactivation restores the same workspace and memberships after entitlement and
safety checks; it never creates a duplicate workspace or silently restores
revoked access.

The implementation gate is architecture/security approval plus negative tests
for RLS, Store Context, object storage, quotas, roles, Channels, AI layers,
suspension/reactivation, and break-glass support. TWN-04-T01 through T08 are
design-complete; TWN-04-T09 remains pending until that evidence exists. The
detailed source of truth is `TWN-04_STORE_WORKSPACE_ACCESS.md`.

## 2026-09-15 - TWN-05 Store Brain lifecycle approved

The product owner approved the Store Brain contract. Store Knowledge, Knowledge
Source, Knowledge Candidate, Published Knowledge, and Customer Memory remain
separate concepts. Only current, workspace-scoped, Owner-approved Published
Knowledge may support a customer promise. Sources carry uploader, version,
checksum, provenance, sensitivity, retention, trust, effective/expiry, and
review metadata. The lifecycle is uploaded, extracting, needs review, approved
or rejected, published, corrected/superseded, and expired.

Price, stock, promotion, payment, delivery, return/refund, legal, and customer
rights facts require immediate Owner approval. Low-risk descriptive cleanup may
use a periodic review digest. Missing, stale, expired, low-confidence, or
conflicting facts block promises, tell the customer Tawan is checking, and
create accountable Task/Approval work. Retrieval enforcement applies to the
database, vectors, prompts, tools, caches, queues, exports, object storage, and
final reply validation.

Customer Memory is limited to consented, purpose-bound summaries with retention,
correction, deletion, and audit controls. Restricted-sensitive data and raw
merchant/customer data are excluded from normal model context and general
training; only approved de-identified aggregates may be considered. TWN-05 is
design-complete for planning, but production implementation still requires
TWN-04 isolation/security approval plus Duply/security/privacy review and the
specified acceptance tests. The detailed source of truth is
`TWN-05_STORE_BRAIN.md`.

The independent review added mandatory safeguards before Trello close-out:
explicit audience visibility separate from sensitivity, Owner approval even for
low-risk review-digest publication, trust-to-authorization mapping, 60-second
invalidation of vectors/caches/queues/exports/derived indexes, TWN-08 consent
and rights propagation for Customer Memory, and Duply product/privacy/security/
legal approval plus minimum-cohort and re-identification controls for any
approved aggregate improvement data.

## 2026-09-16 - TWN-06 Customer Sales Assistant approved

The product owner approved the TWN-06 customer-assistant contract. Tawan uses a
natural, cute, humble Thai part-time-assistant voice but truthfully identifies
herself as an AI assistant when relevant. She supports Phase 1 product,
variant, stock, price, promotion, comparison, order-intent, payment-question,
tracking, cancellation-request, and human-help intents using only current,
approved, customer-visible facts.

Missing, stale, low-confidence, expired, conflicting, internal, or restricted
facts trigger a concise Thai “I will check with the owner” response, accountable
Task/Approval work, and no guessing. Relevant alternatives are offered only
while actively shopping. Out-of-stock requests may create an explicitly
consented, 90-day configurable wishlist with Owner-entered restock date/range,
dashboard demand analysis, and Owner-approved transactional notification;
forecasting, campaigns, and multi-channel outreach remain Pro/later scope.

Owner takeover immediately stops automated replies and queued sends. Resume
requires confirmation, re-reads authorized summaries and current Store Brain
facts, and continues only on new messages. Interaction Events, Sales Journey,
Tasks/Approvals, wishlist, feedback, and eligible Customer Memory records are
structured and idempotent; LINE retries cannot duplicate operational work.
Representative Thai examples and pilot metrics are required before
implementation. The detailed source of truth is
`TWN-06_CUSTOMER_SALES_ASSISTANT.md`; production remains gated by TWN-04,
TWN-05, TWN-07, TWN-08, and independent security/privacy review.

On 2026-09-16 the product owner approved the representative Thai dialogue
baseline in `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §10 for planning. The baseline
also records the Store Owner approval responsibility: each merchant Store Owner
must approve the brand-specific wording and examples before that merchant's
activation. Any wording change requires a new dated review record.

## 2026-09-16 - TWN-07 Orders and Store Operations approved

The product owner approved the TWN-07 Order contract. Phase 1 uses an Order
state machine with explicit stock, fulfilment, payment-review, cancellation,
return, expiry, and incident outcomes. A recurring availability-to-sell profile
supports 24-hour automation: the Owner configures product limits, safety buffer,
payment deadline, fulfilment promise, active schedule, blackout periods, and
responsible capability. Allowance warnings occur at 70% and 90%; 100% stops
automatic acceptance. Morning digests report overnight work and delays.

When capacity is full or stale, Tawan creates a Request/Waitlist rather than an
Order or payment request. Customer consent, first-requested priority, 90-day
configurable expiry, Owner demand dashboard, and new payment deadline on later
availability are required. PromptPay customer payment remains separate from
Duply subscription billing. Slips are protected evidence; OCR/AI extracts
candidates only. Only the Store Owner makes the final Phase 1 paid/rejected
decision; `payment_review` inspects and recommends only.

Duplicate signals immediately notify the store and create reason-coded review
work. Every state and queue duration is tracked. Store-side no-stock or
non-fulfilment incidents preserve immutable evidence, notify the Store Owner and
Duply where appropriate, and trigger customer-safe remedies; repeated abuse can
suspend new paid Orders. Tawan may prepare cancellation/return work but cannot
complete refunds, cancellations, payment approval, discounts, or exceptional
prices autonomously. The detailed source of truth is
`TWN-07_ORDERS_STORE_OPERATIONS.md`; implementation remains gated by
TWN-04/TWN-05/TWN-06/TWN-08 and legal/security review.

The planning end-to-end baseline was approved on 2026-09-16. Each merchant
Store Owner must approve the store-specific availability profile, payment
wording, terms, and customer messages before activation. Only the Store Owner
can finalize a Phase 1 paid/rejected payment decision; `payment_review` can
inspect and recommend only. Availability uses store-local period identifiers,
atomic reservation/release, safety buffers, and Owner-approved renewal windows;
hard expiry never renews silently. Duplicate matching is Store Workspace-local.

## 2026-09-17 - TWN-08 Customer Memory and Consent approved

The Product Owner approved the TWN-08 documentation baseline. Tawan separates
operational service, optional durable Customer Memory, direct marketing,
security/audit, and anonymous aggregate analysis. Memory is Store Workspace-local
with source, confidence, confirmation, validity, expiry, correction/dispute and
deletion evidence; no global profile or identifiable cross-store reuse is allowed.

The Thai customer experience is layered. Durable memory and marketing are
separate voluntary choices with versioned evidence. `STOP`, `ยกเลิก`, and
`ไม่รับข่าวสาร` immediately suppress marketing without disabling ordinary service.
Rights requests use risk-based identity verification, minimised/redacted exports,
Store Owner/Duply privacy approval, legal holds, and auditable completion. They
are acknowledged within one business day and target completion within 30 calendar
days (or a counsel-configured shorter period). Durable-memory withdrawal
immediately suppresses retrieval and derived copies. Raw chat is short-lived;
each data class has bounded/configurable retention and deletion-job evidence.

The merchant is the primary controller for customer/order data; Duply/Tawan is
the processor, while Duply independently controls platform, billing, fraud,
security, and audit data. Sensitive traits are not stored or inferred by default.
A transparent evidence-backed Customer Tier never alone authorizes a discount.
Thai counsel must approve notices, legal bases, consent, contracts, providers,
retention, rights, breach handling, and sensitive-data policy before real data;
the actual sign-off remains pending. Duply security must approve RLS/Storage/
LINE signature controls and negative tests. Anonymous aggregates require a
minimum cohort of 10, rare-pattern suppression, and re-identification testing.
The detailed source of truth is `TWN-08_CUSTOMER_MEMORY_CONSENT.md`.

## 2026-09-17 - TWN-09 Admin Dashboard approved

The Product Owner approved the Phase 1 dashboard baseline. The dashboard is
store-scoped, Thai-first with a user-selectable English option, and available in
Duply with selected LINE alerts/quick actions. The daily order is Low Stock,
Morning Confirmation, Orders and Payments, Customers and Follow-up, Tasks and
Approvals, Catalog/Store Brain, and Settings/Access.

Store Staff can see permitted operational detail and handle assigned stock,
payment-review preparation, customer-contact, refund-request preparation, and
restock work. Only the Store Owner makes the final Phase 1 paid/rejected payment
decision; staff and workspace admins may inspect and recommend only. Refunds are
prepared in an idempotent workflow and completed only by an authorized human.
The Store Owner controls Capabilities and remains the only authority for customer deletion, subscription
changes, Duply settings, discounts, exports, and exceptions. Staff never see
another Store Workspace. Overnight paid work must appear in the daily Morning
Confirmation routine with a recorded outcome.

All material actions record actor, Capability, time, previous/new values, reason,
and result. Operational logs are retained for at least 30 days for investigation,
subject to TWN-08 retention approval. Store timezone drives cutoffs and business
days; stale, empty, error, and insufficient-data states provide plain Thai next
steps. The detailed source of truth is `TWN-09_ADMIN_DASHBOARD.md`.
