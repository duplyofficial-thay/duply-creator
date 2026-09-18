# Tawan Feature Map — Active Documentation Plan

**Status:** Approved by product owner on 2026-09-09.

**Purpose:** This is the active, intentionally small planning board for Tawan. A `TWN-01` through `TWN-12` card represents one product feature area and completes when its design, specification, requirements, acceptance criteria, and out-of-scope boundary are approved. It is **not** an implementation task or a promise that code will be started.

**Completion checklists:** `FEATURE_TASKS.md` is the authoritative detailed task list for every feature card.

**Historical cards:** Existing long-form `TWN-*` engineering cards remain historical evidence/backlog. They are not the active Phase 1 delivery plan and are not renumbered or deleted by this feature map.

## Working Rules

- Use the two-digit feature identifier in conversations, Trello, design documents, and later implementation work.
- Do not create code-level subcards while a feature is still in this documentation stage.
- Each feature document uses the canonical Duply/Tawan glossary: Tawan Instance, Store Workspace, Store Context, Store Knowledge, Customer Memory, Sales Journey, Transaction, Task, Approval, Channel, and Capability.
- `TWN-01` is the product compass; `TWN-12` is the final pilot/launch gate. The middle cards can be researched and drafted in parallel, but their final approval follows the listed dependencies.
- No real customer data, production Channel, paid integration, or production activation is permitted merely because a feature specification is complete.

## Card List

### TWN-01 — Tawan Product Direction

**Phase:** All phases

**Depends on:** None

**Complete when:** `TWN-01_PRODUCT_DIRECTION.md` defines Tawan's target customer, problem, value proposition, three phases, Standard/Pro boundary, pilot commercial model, success metrics, explicit out-of-scope list, and product-owner approval evidence.

**Requirements to settle:**

- Phase 1 is a LINE-first, assisted business-assistant pilot for Thai SMEs and solo entrepreneurs selling physical retail items by the piece. Fashion/accessories remain representative scenarios, not a recruitment restriction.
- Phase 2 introduces demand-proven integrations and owner-approved Pro campaigns/intelligence.
- Phase 3 addresses mature multi-channel operations, recurring billing, advanced intelligence, and optional merchant showcase/brand-ambassador work.
- The first pilot is free for 30 days and planned for ten merchants, with the cohort reassessed from recruitment evidence; Standard payment-link conversion is considered only after pilot feedback and product-owner review.
- Pilot success has measurable onboarding, daily-summary, reply-quality, time-saved, safety, and conversion targets.

**Out of scope:** Detailed engineering architecture, a public marketplace, and individual third-party connector implementation.

### TWN-02 — Tawan Official

**Phase:** 1

**Depends on:** TWN-01

**Complete when:** `TWN-02_TAWAN_OFFICIAL.md` explains and product-owner approval covers the complete management-plane journey: discovery, feature questions, assisted pilot registration, support, onboarding status, deterministic team intervention/activation, post-pilot conversion, and merchant subscription entitlement/cancellation.

**Requirements to settle:**

- Tawan Official is Duply's management Channel, not the shared identity seen by a merchant's customers.
- Prospective merchants can understand Tawan, request a pilot, and be guided to the next onboarding action in plain Thai.
- Tawan Official records onboarding progress, escalates uncertainty to the Duply team, and distinguishes merchant subscription billing from a customer's Order payment; Duply owns payment-provider status and Tawan consumes status only.
- Activation is Duply-gated and audited: routine paid activations may run automatically only after every deterministic verification gate passes; human review is required for exceptions, low-confidence evidence, or failed gates. Self-service chat never bypasses the gates or activates an unreviewed store.

**Out of scope:** Customer commerce conversations and automated recurring billing.

### TWN-03 — Merchant Onboarding

**Phase:** 1

**Depends on:** TWN-01, TWN-02

**Complete when:** `TWN-03_MERCHANT_ONBOARDING.md` lists the required inputs, low-friction pilot verification and risk-triggered strong verification, review points, responsible role, protected-source rules, activation criteria, and test conversation, with product-owner approval evidence.

**Requirements to settle:**

- Capture business/owner details, brand voice, operating hours, staff Capabilities, store policies, consent settings, catalog/price/variant/stock source, and own LINE OA connection.
- Accept guided templates, CSV, Google Sheets, approved uploads, and approved-domain website imports.
- Before activation, record the Store Owner's versioned acceptance of the final service terms, controller/processor agreement, and applicable privacy notices approved by Thai counsel.
- Keep the Store Workspace in draft until the Store Owner approves Store Knowledge and a safe test conversation succeeds.
- Do not require detailed shipping configuration at initial setup; require a manual path for fulfilment/delivery/returns instead.
- Provide an isolated synthetic/test-data mode and an initial protected-source allowlist with configurable per-file and total-upload limits; test data can never become live Store Knowledge.
- Pilot onboarding uses Duply account/email/phone/LINE verification and owner authority declaration; passport/national-ID collection is not ordinary onboarding. Strong verification is requested only by an authorised Duply reviewer for a documented risk, provider/legal requirement, or higher-risk capability.
- Automated intake/status availability is continuous, while human response follows configured support hours and urgent-incident policy.
- Potential fraud or illegal selling is signalled to Duply first; Tawan does not accuse, disclose to authorities, or suspend without Duply's confirmed decision.

**Out of scope:** Marketplace/POS connector setup and autonomous activation without all required gates and Duply's activation decision.

### TWN-04 — Store Workspace and Access

**Phase:** 1

**Depends on:** TWN-01

**Complete when:** `TWN-04_STORE_WORKSPACE_ACCESS.md` defines and product-owner approval covers the canonical Store Workspace isolation model, server-derived Store Context, RLS/member-scoped access, roles, Capabilities, support access, Channel separation, subscription suspension/reactivation, and the required negative isolation tests.

**Requirements to settle:**

- Every merchant has isolated customers, Channel mapping, credentials, Store Knowledge, settings, operations, and analytics.
- Every data action derives a verified Store Context; a model, customer message, or client request cannot select another store.
- Canonical roles are `platform_admin`, `store_owner`, `workspace_admin`, `store_staff`, and `customer`; `store_staff` receives explicit Capabilities rather than universal access.
- Platform support access is exceptional, time-limited, reason-coded, and audited.
- The document explicitly selects one tenancy model; architecture/security verification, RLS/context tests, and the correct current payment semantics (Store Owner review, never model/OCR auto-payment completion) remain implementation gates.
- Tawan uses one shared `tawan_ai` schema with workspace-scoped rows, but this is not implementation-ready without RLS, transaction-local server-derived context, workspace-scoped foreign keys/indexes/caches, private object storage, and cross-workspace negative tests.
- Expired subscription suspends service without deleting data; restricted read-only status and reactivation use the same Store Workspace after a new entitlement is confirmed.

**Out of scope:** Building the authorization system or provisioning a production workspace; production activation before RLS/context verification and architecture/security approval.

### TWN-05 — Tawan Store Brain

**Phase:** 1

**Depends on:** TWN-03, TWN-04

**Complete when:** `TWN-05_STORE_BRAIN.md` explains how Store Knowledge is supplied, validated, approved, updated, expired, and used safely in customer replies, with product-owner and Store Owner approval evidence.

**Requirements to settle:**

- Separate Store Knowledge from raw uploads and Customer Memory.
- Store sources carry provenance, checksum, uploader, sensitivity, retention, approved domain where relevant, and source version.
- Website fetching is restricted to approved domains; uploaded materials have defined type/size limits, malware scanning, protected storage, and no public access path.
- Extracted facts become Knowledge Candidates with confidence, conflict, validity, and expiry information.
- Only Store Owner-approved published knowledge can be used as a durable customer-facing fact.
- Price, stock, promotion, availability, payment, and policy facts never come from unreviewed material or model invention.
- Separate Customer Memory from Store Knowledge; retain only consented, purpose-limited summaries and never use raw merchant/customer data for general model training.
- Enforce approved/current retrieval at database, vector, prompt, tool, cache, queue, export, and reply-validation layers.
- Every fact has an explicit audience (`customer_visible`, `merchant_internal`, `support_only`, or `restricted`); sensitivity and approval never override audience restrictions.

**Out of scope:** General web crawling, autonomous knowledge publication, and cross-store knowledge sharing.

### TWN-06 — Customer Sales Assistant

**Phase:** 1

**Depends on:** TWN-04, TWN-05

**Complete when:** `TWN-06_CUSTOMER_SALES_ASSISTANT.md` defines Tawan's brand-safe sales behavior in a merchant's own LINE OA, including structured capture, idempotency, owner takeover, wishlist flow, and approved Thai examples.

**Requirements to settle:**

- Answer product, colour, size, price, promotion, and availability questions from current approved facts.
- Offer relevant alternatives while a customer is actively shopping, without proactive marketing in Phase 1.
- When facts are missing, stale, low-confidence, or conflicting, say that Tawan is checking and create accountable human work rather than guessing.
- Record Sales Journey and Interaction Event progress in the reply flow, with idempotency for Channel retries.
- Use the merchant's approved brand voice while preserving the Tawan principle: never invent store facts.
- Tawan may sound like a cute, humble Thai part-time shop assistant but truthfully identifies herself as an AI assistant when relevant.
- Phase 1 supports consented restock wishlists and Owner-approved transactional notices; Pro/later forecasting, campaigns, and multi-channel outreach remain out of scope.
- Owner takeover stops automated replies and queued sends; resume re-reads authorized summaries and current facts before continuing on new messages.

**Out of scope:** Outbound campaigns, cross-Channel customer profiling, and autonomous commercial exceptions.

### TWN-07 — Orders and Store Operations

**Phase:** 1

**Depends on:** TWN-04, TWN-05, TWN-06

**Complete when:** `TWN-07_ORDERS_STORE_OPERATIONS.md` defines the safe Order-to-outcome workflow for the piece-based physical-retail pilot, including recurring overnight availability, demand requests, payment evidence, incidents, and human authority.

**Requirements to settle:**

- Revalidate price and stock when a customer confirms an Order; reserve stock for a defined expiry period.
- Present a configured PromptPay QR where enabled and retain payment slips as protected evidence.
- OCR/AI may extract payment candidates but never marks payment paid; only the Store Owner gives the final Phase 1 decision.
- Block duplicate exact payment evidence or bank references; owner review of a probable fingerprint false positive is reason-coded and auditable.
- Track fulfilment, delivery, return, cancellation-request, and handover Tasks. Cancellation is requested by Tawan but completed by authorized human approval.
- A recurring availability-to-sell profile enables 24-hour automation with caps, safety buffers, expiry, morning digest, and Owner emergency pause.
- When capacity is full or stale, Tawan creates a consented Request/Waitlist rather than an Order or payment request; Owner dashboards show demand without hidden customer scoring.
- Merchant source accuracy and fulfilment responsibility are explicit, while Duply/Tawan remains accountable for platform, authorization, duplicate-action, and security defects; final terms require legal review.

**Out of scope:** Refund automation, automatic cancellation, automatic payment approval, or autonomous discounts/price changes.

### TWN-08 — Customer Memory and Consent

**Phase:** 1

**Depends on:** TWN-04

**Complete when:** `TWN-08_CUSTOMER_MEMORY_CONSENT.md` defines purpose-separated Customer Memory, Thai layered privacy and consent, rights, retention/deletion, security controls, and pre-launch legal/security gates.

**Requirements to settle:**

- Customer Memory remains local to one Store Workspace and identifies source, confidence, confirmation, validity, expiry, correction, dispute, consent, and deletion history.
- Routine service data, durable preference memory, and direct marketing are separate documented purposes.
- A short Thai notice links to a full privacy notice; durable preference memory and marketing are separate voluntary choices with versioned evidence.
- STOP immediately suppresses marketing for that Store Workspace, customer, purpose, and Channel without affecting normal service.
- Verified customers can request access, applicable portability export, correction, restriction, deletion, and objection handling.
- A rights request defines risk-based identity verification, allowed requester/Store Owner approvals, minimised/redacted scope, legal hold, one-business-day acknowledgement, 30-calendar-day target, and auditable completion evidence before an export is released.
- Sensitive traits are not retained as memory, inferred, segmented, or used for recommendations/marketing by default.
- Only the Store Owner may assign or override a transparent Customer Tier; evidence, reason, actor, timestamp, expiry, visibility, correction/appeal, and audit history are required. A Tier alone never authorizes a discount. Automated Tier recommendations remain outside this documentation-first Phase 1 scope.
- RLS, private Storage, LINE signature verification, deletion propagation, incident response, and negative isolation tests are implementation gates.
- Durable-memory withdrawal immediately suppresses retrieval and derived copies; retention is bounded/configurable, deletion jobs emit verification evidence, and anonymous aggregates require a minimum cohort of 10 plus re-identification testing and rare-pattern suppression.

**Out of scope:** Cross-store identifiable analytics, routine passport/national-ID collection, autonomous legal/discount decisions, and final legal advice; Thai counsel approves final legal artifacts before launch.

### TWN-09 — Admin Dashboard

**Phase:** 1

**Depends on:** TWN-04, TWN-07, TWN-08

**Complete when:** `TWN-09_ADMIN_DASHBOARD.md` defines the action-first views, Store Owner/Staff Capabilities, store-local timing, LINE quick actions, audit evidence, and Phase 1 wireframe requirements.

**Requirements to settle:**

- Prioritise low stock, Morning Confirmation, Orders/Payments, Customers/Follow-up, Tasks/Approvals, Catalog/Store Brain, and Settings/Access; high-value opportunities, payment review, urgent approvals, unanswered customers, and overdue follow-up remain accountable queues.
- Define the permitted views for Customer, Sales Journey, Transaction, Task, Approval, Catalog, Store Knowledge, consent, and settings.
- Reflect individual Capability boundaries and make material actions auditable; `workspace_admin` cannot self-grant or approve final Phase 1 payment, and Owner-only controls include payment final decision, deletion, subscriptions, Duply settings, discounts, exports, and exceptions.
- Keep analytics useful for action rather than hiding urgent work behind charts.
- Use store-selected country/timezone, explicit freshness, Thai-first labels with English option, and authenticated management-LINE quick actions backed by Duply evidence; customer-facing LINE OA cannot invoke management actions.

**Out of scope:** Advanced Pro campaigns, external marketplace control panels, autonomous discounts, cross-store staff views, and custom BI projects.

### TWN-10 — AI Workflow and Daily Insights

**Phase:** 1 to 2

**Depends on:** TWN-05, TWN-07, TWN-08, TWN-09

**Complete when:** `TWN-10_AI_WORKFLOW_DAILY_INSIGHTS.md` defines real-time capture, hourly/daily/weekly cadence, Thai owner digests, evidence-backed recommendations, insufficient-data behavior, approval boundaries, and Pro limits.

**Requirements to settle:**

- Customer reply orchestration captures meaningful structured progress immediately, confirms important facts, and asks focused questions without repeating known information; it does not wait for a nightly summariser. Source references are minimised/redacted and inherit TWN-08 purpose, audience, consent, retention, and deletion rules.
- Store operational state is current where possible; dashboard aggregates refresh hourly; daily close finalises store-local totals.
- The daily plain-Thai owner digest includes sales/orders, stock risks, unresolved questions, leads/follow-ups, payment/cancellation work, demand signals, and up to three evidence-backed actions.
- Recommendations expose evidence, confidence, explanation, model/rule version, assignee, expiry, and insufficient-data state; they do not make commercial decisions, are idempotent/auditable, are capability-filtered/redacted, and never rank by sensitive traits or hidden customer value.
- Segmentation, proactive campaigns, customer lifetime value, churn, demand forecasting, and advanced intelligence are Pro/post-Phase-1 only.

**Out of scope:** Background actions that alter a store's commercial state without owner authority, proactive campaigns, segmentation, LTV, churn, forecasting, and advanced intelligence.

### TWN-11 — Channels and Integrations

**Phase:** 1 to 3

**Depends on:** TWN-01, TWN-04

**Complete when:** `TWN-11_CHANNELS_INTEGRATIONS.md` defines the Phase 1 LINE boundary, common adapter contract, source-separated unified view, approved input paths, connector scorecard, and product/technical approval gate.

**Requirements to settle:**

- A merchant's own LINE OA is the first complete customer Channel; Tawan Official is management/sales administration in Phase 1, and Duply website remains the authenticated management surface. Future connector selling is a separately approved Channel capability.
- The shared Channel interface preserves the possibility of Sheets/POS, Shopee, Lazada, TikTok, Facebook, Instagram, and Discord without assuming identical features or authorization; source records remain separate in one operational view.
- Phase 1 uses manual inputs, templates, CSV, Sheets, and Owner-approved Google Drive/API sources before marketplace/POS integrations; each new Drive file is quarantined and approved before retrieval.
- Pilot demand, API legality/capability, security, cost, and value determine the first Phase 2 connector.
- Tawan Official Instagram initially markets Tawan/Duply and approved current partners; merchant showcases need explicit partner opt-in and a separate commercial agreement.

**Out of scope:** Implementing any post-LINE connector in Phase 1 or bypassing Store Context, privacy, payment, or Owner approval boundaries.

### TWN-12 — Pilot, Safety, and Launch Gate

**Phase:** 1

**Depends on:** TWN-01 through TWN-11

**Complete when:** `TWN-12_PILOT_SAFETY_LAUNCH_GATE.md` defines the pilot journey, synthetic payment rehearsal, evidence, accountable owners, provisional acceptance targets, legal/security release criteria, incident pause rules, and Phase 2 go/no-go decision.

**Requirements to settle:**

- Pilot cohort: planned for ten Thai retailers selling physical items by the piece, free for 30 days and reassessed from recruitment evidence; sandbox payment testing is separate from real customer funds, and Standard payment-link conversion is considered after pilot feedback and product-owner review. Fashion/accessories may be a representative scenario, not a cohort restriction.
- Primary validation seam: Tawan Official onboarding through owner-approved activation, synthetic merchant LINE customer conversation before release, safe Order/payment/human work, dashboard update, and daily digest.
- Acceptance targets: ten-merchant recruitment target; 80% onboarding completion, 14 consecutive useful daily summaries for active merchants, 85% routine replies without correction, two hours saved per merchant each week, zero cross-store leaks/unapproved commercial actions, and 50% paid conversion, with defined denominators/rubrics and weekly evidence.
- No real customer data before credential rotation, tenant isolation/RLS, runtime verification, cost tracking, Thai counsel review, rights/retention controls, recovery/restore exercise, incident-response rehearsal, independent security review, named approval owners, and signed evidence. Pre-gate conversations use synthetic identities/messages only; missing Security, Operations, counsel, or Incident Commander assignments block activation.
- The Phase 2 decision uses the evidence from the pilot rather than assumptions about integrations or Pro features; the reviewer must be independent from implementation/support and recorded before Go.

**Out of scope:** Real-money payment testing/cashback, silent activation, or launching Phase 2 or Phase 3 features before this gate passes.
