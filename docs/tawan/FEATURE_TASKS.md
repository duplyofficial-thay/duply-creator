# Tawan Feature-Card Completion Checklists

**Status:** Approved planning checklist for `TWN-01` through `TWN-12`.

**How to use this document:** A card is complete only when every applicable checkbox is evidenced in its design/specification document and the Store Owner/product owner approves that document. These are documentation tasks, not permission to implement, connect a live Channel, process real customer data, or incur paid API costs.

**Required close-out on every card:** The completed feature document must include its own acceptance criteria, explicit out-of-scope boundary, dependencies/cross-references, named decision owner, and approval evidence. Shared contracts have one canonical home: Store Context/Channel authorization is owned by TWN-04; reply-time structured capture is owned by TWN-06; other cards reference rather than redefine them.

## TWN-01 — Tawan Product Direction

- [x] Write the one-sentence Tawan promise: a LINE-first business assistant for Thai SMEs and solo entrepreneurs selling physical retail items by the piece. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Define the Phase 1 result: assisted onboarding, merchant-owned LINE OA, Store Brain, safe customer sales/admin support, action-first dashboard, and daily digest. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Define Phase 2: demand-proven integrations, owner-approved Pro campaigns, segmentation, and advanced insights. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Define Phase 3: mature multi-channel operations, recurring billing, advanced intelligence, and optional merchant showcase/brand-ambassador programme. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Confirm Pilot, Standard, and Pro boundaries; distinguish merchant subscription payments from customer Order payments. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Record the free 30-day/ten-merchant pilot target, Standard payment-link conversion for continuing merchants, and all success measures. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Record the out-of-scope list so no one assumes marketplace, campaigns, or multi-channel work is Phase 1. Evidence: `TWN-01_PRODUCT_DIRECTION.md`.
- [x] Obtain product-owner approval of the roadmap and terms used in all later cards. Evidence: `TWN-01_PRODUCT_DIRECTION.md` and `DECISIONS.md` (2026-09-10).

## TWN-02 — Tawan Official

- [x] Map the prospective merchant journey from first LINE message to pilot request, including FAQs Tawan can answer and cases that must go to the Duply team. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §§1–2.
- [x] Define the qualification information Tawan Official collects before a pilot: business type, owner contact, current sales channel, store size, source of catalog/stock data, and main pain point. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §3.
- [x] Define the assisted onboarding status stages and the plain-Thai messages sent at each stage. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §§2–3.
- [x] Specify exactly when a team member must verify or intervene; Tawan Official must never activate an unreviewed Store Workspace. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §4.
- [x] Define the support journey for existing Store Owners and Staff: how they ask operational questions, report a problem, and receive escalation status. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §4.
- [x] Define the post-pilot conversion journey: Standard offer, payment-link handoff, payment follow-up, and outcome recording. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §5.
- [x] Keep customer Order/PromptPay handling explicitly outside Tawan Official merchant-billing messages. Evidence: `TWN-02_TAWAN_OFFICIAL.md` §5.
- [x] Obtain product-owner approval of the Tawan Official conversation map. Evidence: `TWN-02_TAWAN_OFFICIAL.md` approval section and `DECISIONS.md` (2026-09-11).

## TWN-03 — Merchant Onboarding

- [x] Create the mandatory onboarding checklist: owner/business details, brand voice, operating hours, staff, policies, consent settings, catalog/prices/variants/stock source, and merchant LINE OA. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §§1–2.
- [x] Define optional data sources for Phase 1: templates, CSV, Google Sheets, approved uploads, and approved-domain website imports. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §5.
- [x] Define input quality rules: required fields, data owner, missing-data path, update frequency, and a test-data option. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §§2,5.
- [x] Define protected-source rules: allowed file types/sizes, malware scan, protected storage, approved URL/domain allowlist, and no public file path. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §5.
- [x] Define draft, review, needs-owner-decision, test-ready, and live-ready onboarding states. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §6.
- [x] Require Store Owner approval of published Store Knowledge and a successful test conversation before activation. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §7.
- [x] Require versioned acceptance of counsel-approved service terms, controller/processor terms, and privacy notices before activation. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §§2,7.
- [x] Confirm manual fulfilment/delivery/return work is sufficient at launch; detailed shipping setup is later work. Evidence: `TWN-03_MERCHANT_ONBOARDING.md` §8.

## TWN-04 — Store Workspace and Access

- [x] Reconcile the contradictory existing tenancy designs and select one verified Store Workspace isolation model before implementation starts. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §§1,4,11.
- [x] Define how a verified Store Context is resolved for every management and customer operation. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §3.
- [x] Define the canonical roles: `platform_admin`, `store_owner`, `workspace_admin`, `store_staff`, and `customer`; store staff are capability-based. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §5.
- [x] Define Store Staff Capabilities, including sales, fulfilment, marketing, knowledge editor, manager, and payment review; state what remains Owner-only. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §5.
- [x] Define the mapping/retirement plan for legacy role names such as owner and employee. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §6.
- [x] Define time-limited, reason-coded, auditable Platform Administrator support access. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §10.
- [x] State and test the non-negotiable rule: no role, Channel, model, prompt, or client parameter may cross Store Workspace boundaries. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §§3–4,7,11.
- [x] Publish Store Context/Channel authorization as the canonical contract that TWN-06, TWN-07, TWN-09, and TWN-11 must reference. Evidence: `TWN-04_STORE_WORKSPACE_ACCESS.md` §§3,7.
- [ ] Obtain architecture/security owner approval of the chosen boundary. Evidence target: `TWN-04_STORE_WORKSPACE_ACCESS.md` §§4,11; pending architecture/security sign-off and verified negative isolation tests.

## TWN-05 — Tawan Store Brain

- [x] Separate the definitions and allowed uses of Store Knowledge, Knowledge Source, Knowledge Candidate, published knowledge, and Customer Memory. Evidence: `TWN-05_STORE_BRAIN.md` §1.
- [x] Define source metadata: uploader, source/version, checksum, approved domain, sensitivity, retention, provenance, and effective/expiry date. Evidence: `TWN-05_STORE_BRAIN.md` §§2,4.
- [x] Define the extraction/review journey: uploaded, extracting, needs review, approved/rejected, published, corrected, superseded, or expired. Evidence: `TWN-05_STORE_BRAIN.md` §3.
- [x] Define conflict handling for catalog, price, stock, policy, delivery, promotion, and payment facts. Evidence: `TWN-05_STORE_BRAIN.md` §5.
- [x] State which facts need immediate Owner approval and which low-risk updates may use a periodic review digest. Evidence: `TWN-05_STORE_BRAIN.md` §6.
- [x] Define what Tawan may use in a customer reply: approved/current facts only; raw uploads and unapproved candidates never become promises. Evidence: `TWN-05_STORE_BRAIN.md` §8.
- [x] Define the stale/missing/conflicting-fact response: create accountable work and say Tawan is checking. Evidence: `TWN-05_STORE_BRAIN.md §§5,8`.
- [x] Obtain Store Owner and product-owner approval of the Store Brain lifecycle. Evidence: `TWN-05_STORE_BRAIN.md §10` and `DECISIONS.md` (2026-09-15).

## TWN-06 — Customer Sales Assistant

- [x] Define the customer-facing persona: warm, consultative, merchant-brand-aligned, clear, and never inventing facts. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §1.
- [x] Define the supported Phase 1 customer intents: product search, variant/colour/size question, stock/price/promotion question, comparison, order intent, payment question, tracking question, cancellation request, and human help. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §2.
- [x] Define the answer rules for approved/current facts, missing/stale/conflicting facts, uncertainty, and prohibited promises. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §3.
- [x] Define in-conversation alternatives: relevant colour, size, and product suggestions only while a customer is actively shopping. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §§4–5.
- [x] Define escalation triggers, Store Staff takeover, owner-only commercial exceptions, and the customer-facing waiting message. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §§6–7.
- [x] Define reply-time structured capture: Interaction Event, Sales Journey, next action, Task/Approval, and eligible Customer Memory candidate. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §8.
- [x] Define retry/idempotency expectations so Channel retries cannot duplicate sales work. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §9.
- [x] Publish reply-time structured capture as the canonical contract that TWN-07 and TWN-10 must reference. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §§8,11.
- [x] Approve representative Thai conversation examples before implementation. Evidence: `TWN-06_CUSTOMER_SALES_ASSISTANT.md` §10 and `DECISIONS.md` (2026-09-16).

## TWN-07 — Orders and Store Operations

- [x] Define the retail Order lifecycle from customer confirmation through completed, cancelled, returned, or expired outcome, including stock/fulfilment failure states. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §1.
- [x] Define authoritative price and stock sources, revalidation at confirmation, recurring availability-to-sell profile, reservation duration, and safe expiry/release behavior. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §§2–4.
- [x] Define configured PromptPay QR presentation and the boundary between customer payment and merchant subscription billing. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §5.
- [x] Define protected payment-slip intake, OCR/AI candidate extraction, manual review, owner-only paid/rejected decision, and customer update messages. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §§5–6,9.
- [x] Define duplicate payment controls: exact evidence, normalized fingerprint, bank reference, unresolvable conflict, reason-coded false-positive handling, immediate notification, and audit evidence. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §6.
- [x] Define Tasks for fulfilment, delivery, tracking, returns, cancellation requests, stock issue, payment review, customer follow-up, SLAs, and duration tracking. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §§7–9.
- [x] Define cancellation authority: Tawan can request and prepare; authorized human approves the completed action; no automated refund/cancellation in Phase 1. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §8.
- [x] Explicitly prohibit autonomous exceptional prices, discounts, and price changes; every exception follows the Approval workflow. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §§8,10.
- [x] Approve an end-to-end example covering Order, recurring overnight allowance, reservation, payment review, fulfilment, stock issue, and return/cancellation. Evidence: `TWN-07_ORDERS_STORE_OPERATIONS.md` §10 and `DECISIONS.md` (2026-09-16).

## TWN-08 — Customer Memory and Consent

- [x] Define the personal-data categories for operational service, structured Customer Memory, direct marketing, security/audit, and anonymous aggregate analysis. Evidence: purpose map and field boundaries in `TWN-08_CUSTOMER_MEMORY_CONSENT.md`.
- [x] Define memory fields and metadata: source, confidence, confirmation, first/last observed, effective/expiry, correction, dispute, and deletion status. Evidence: Customer Memory contract.
- [x] Confirm Customer Memory is Store Workspace-local: no global profile, cross-store matching, or identifiable cross-store reuse. Evidence: workspace-local contract and negative-test gate.
- [x] Write the layered Thai privacy experience: short notice, full notice, service explanation, optional durable-memory choice, and separate marketing choice. Evidence: approved Thai baseline copy; counsel gate recorded.
- [x] Define consent evidence: Store Workspace, Customer, purpose, Channel, wording version, timestamp, actor, withdrawal, and suppression result. Evidence: consent and suppression schema requirements.
- [x] Define STOP and equivalent Thai opt-out language; confirm it immediately suppresses marketing without reducing normal service. Evidence: `STOP`, `ยกเลิก`, and `ไม่รับข่าวสาร` behavior.
- [x] Define customer-rights workflow: identity-verification strength, authorized requester, Store Owner approval, minimised/redacted export scope, deadline, legal hold, and auditable completion. Evidence: rights workflow and escalation gates.
- [x] Define retention/deletion rules separately for raw chat, memory, Order/payment evidence, consent/audit history, vectors/caches/logs/backups, and anonymous aggregates. Evidence: retention table and deletion propagation requirement.
- [x] Require raw chat to be encrypted, short-lived, and excluded from durable behaviour after its purpose/retention period ends. Evidence: 30-day default and deletion propagation/negative tests.
- [x] State that sensitive traits are not stored/inferred/segmented by default; define Store Owner evidence-backed Customer Tier assignment/override with audit history; and confirm a Tier never alone authorizes a discount. Evidence: sensitive-data and Tier rules.
- [ ] Obtain Thai counsel sign-off before real customer data is admitted. The required gate is specified and approved by the Product Owner on 2026-09-17, but actual counsel evidence is still pending before production/customer-data use.

## TWN-09 — Admin Dashboard

- [x] Define the action-first home view: low stock first, then morning confirmation, orders/payments, customers/follow-up, tasks/approvals, Catalog/Store Brain, and Settings/Access. Evidence: `TWN-09_ADMIN_DASHBOARD.md` home-view contract.
- [x] Define authorized screens for Customers, Customer Memory/consent, Sales Journeys, Transactions, Tasks, Approvals, Catalog, Store Brain, and settings. Evidence: screen/action matrix.
- [x] Define what each role/Capability can see, change, approve, export, or only prepare. Evidence: Owner/Staff matrix and backend authorization gate.
- [x] Define the dashboard's real-time operational state, hourly aggregates, and store-local business-day display. Evidence: freshness, timezone, and aggregation rules.
- [x] Define empty, loading, error, stale-data, and insufficient-data states in plain Thai. Evidence: state behavior and Thai example copy.
- [x] Define audit evidence for owner decisions, staff action, exports, deletion, and support access. Evidence: audit fields, 30-day investigation minimum, and minimisation rule.
- [x] Ensure dashboard views lead to accountable actions, not charts with no next step. Evidence: next-action requirement and traceable Task/Order/Approval record.
- [x] Approve wireframes or representative screen requirements before implementation. Evidence: Phase 1 wireframe requirements approved by Product Owner 2026-09-17.

## TWN-10 — AI Workflow and Daily Insights

- [x] Define the real-time reply workflow and the structured data captured on each inbound customer event. Evidence: event fields, focused-question behavior, confirmation, confidence, and source references in `TWN-10_AI_WORKFLOW_DAILY_INSIGHTS.md`.
- [x] Define real-time reply handling, hourly refresh, daily close, weekly review, and the boundary between Phase 1 and Pro work using the Store Workspace timezone and business date. Evidence: operating cadence and phase boundary.
- [x] Define the daily plain-Thai LINE owner digest: sales/orders, inventory risk, unresolved questions, leads/follow-ups, payment/cancellation work, preference/demand signals, and up to three recommended actions. Evidence: Duply + authenticated management LINE digest and Thai sample.
- [x] Define what evidence, confidence, explanation, model/rule version, and expiry a recommendation must show. Evidence: recommendation contract and accept/dismiss/snooze behavior.
- [x] Define “insufficient data” behaviour so Tawan never creates unsupported insights. Evidence: explicit `ข้อมูลยังไม่เพียงพอ` rules and approved sample.
- [x] Define approval boundaries: Tawan recommends; owner/staff take accountable commercial action. Evidence: payment/refund/commercial-state negative tests and authorization boundaries.
- [x] Keep segmentation, proactive campaigns, LTV, churn, demand forecasting, and advanced intelligence explicitly Pro/post-Phase-1. Evidence: phase boundary and out-of-scope list.
- [x] Approve one sample daily digest and one sample insufficient-data digest. Evidence: two approved Thai samples; Product Owner approved 2026-09-17.

## TWN-11 — Channels and Integrations

- [x] Define the distinction between Tawan Official management Channel and a merchant's customer-facing LINE OA. Evidence: website, management/sales AI, customer Channel, and cross-channel authorization boundary in `TWN-11_CHANNELS_INTEGRATIONS.md`.
- [x] Define the common Channel Adapter contract: identity, messages, media, delivery status, consent, capabilities, error handling, and Store Context resolution. Evidence: versioned adapter contract and server-derived Store Context.
- [x] Confirm LINE OA is the only complete customer Channel in Phase 1. Evidence: explicit Phase 1 boundary and out-of-scope connector list.
- [x] Define manual/template/CSV/Google Sheets as Phase 1 data-input paths. Evidence: validated Owner-approved Google Drive/API source path included.
- [x] Create a Phase 2 connector-selection scorecard: merchant demand, API authorization, reliability, security, cost, maintenance, and measurable business value. Evidence: scored criteria and approval gates.
- [x] List later candidates without committing to build them: POS, Shopee, Lazada, TikTok Shop, Facebook, Instagram, and Discord. Evidence: candidate list and no-build promise for Phase 1.
- [x] Define Tawan Official Instagram as Tawan product marketing first; merchant showcase requires a separate opt-in commercial agreement. Evidence: partner approval, agreement, identity, usage, and withdrawal rules.
- [x] Obtain product/technical approval before committing to any non-LINE integration. Evidence: scorecard, threat/risk review, rollback plan, scope copy, pilot evidence, and approval gate; Product Owner approved 2026-09-18.

## TWN-12 — Pilot, Safety, and Launch Gate

- [x] Define the free pilot cohort planned for ten Thai retailers selling physical items by the piece, 30-day duration, support ownership, onboarding schedule, and Standard payment-link exit/conversion path; fashion/accessories may be a representative scenario, not a cohort restriction. Evidence: pilot charter, support ownership, sandbox-payment boundary, and provisional conversion decision.
- [x] Define the primary synthetic rehearsal: Tawan Official onboarding; approved and rejected Knowledge Candidates; owner approval; synthetic merchant LINE conversation; safe missing/conflicting-fact escalation; memory refusal and STOP; Order/reservation expiry; PromptPay/payment review; duplicate-payment conflict; human work; dashboard; and daily digest. Evidence: rehearsal matrix.
- [x] Define the required safety evidence: negative cross-store tests at Channel, retrieval/vector/cache, tools, analytics, staff, export, and support boundaries; authorization/idempotency; payment safety; consent/rights; export/deletion; recovery; incident response; and cost-ledger evidence. Evidence: pre-production security, privacy, reliability, and cost gates.
- [x] Define pre-production legal evidence: Thai counsel-approved notices, lawful bases, controller/processor agreement, retention schedule, marketing rules, international-transfer arrangements, and export terms. Evidence: legal release checklist; actual counsel approval remains a launch gate.
- [x] Define security/reliability evidence: credential rotation, RLS/tenant isolation, runtime contract verification, recovery/restore exercise, incident detection/containment/escalation rehearsal, and independent review. Evidence: security/reliability checklist and severity pause rules.
- [x] Define measurable pilot acceptance: 10-merchant recruitment target; 80% onboarding completion; 14 consecutive useful daily summaries for every active merchant; 85% routine replies without correction; two hours saved weekly per merchant; zero leakage/unauthorized action; and 50% paid conversion. Evidence: metric definitions, denominators, survey rubric, source events, and weekly report.
- [x] Define a documented Phase 2 go/no-go decision that uses pilot evidence to choose integrations and Pro work. Evidence: Go/Hold/No-go record and evidence categories.
- [ ] Obtain product, security, operations, and Thai legal approval before any real customer-data activation. The approval gate, owners, synthetic pre-gate boundary, sandbox payment contract, and independent-review requirement are defined; actual signed approvals remain pending.
