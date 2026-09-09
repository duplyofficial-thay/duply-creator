# Tawan Feature Map — Active Documentation Plan

**Status:** Approved by product owner on 2026-09-09.

**Purpose:** This is the active, intentionally small planning board for Tawan. A `TWN-01` through `TWN-12` card represents one product feature area and completes when its design, specification, requirements, acceptance criteria, and out-of-scope boundary are approved. It is **not** an implementation task or a promise that code will be started.

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

**Complete when:** A product direction document defines Tawan's target customer, problem, value proposition, three phases, Standard/Pro boundary, pilot commercial model, success metrics, and explicit out-of-scope list.

**Requirements to settle:**

- Phase 1 is a LINE-first, assisted business-assistant pilot for Thai fashion/accessories SMEs and solo entrepreneurs.
- Phase 2 introduces demand-proven integrations and owner-approved Pro campaigns/intelligence.
- Phase 3 addresses mature multi-channel operations, recurring billing, advanced intelligence, and optional merchant showcase/brand-ambassador work.
- The first pilot is free for 30 days, limited to ten merchants, with Standard available by payment link after the pilot.
- Pilot success has measurable onboarding, daily-summary, reply-quality, time-saved, safety, and conversion targets.

**Out of scope:** Detailed engineering architecture, a public marketplace, and individual third-party connector implementation.

### TWN-02 — Tawan Official

**Phase:** 1

**Depends on:** TWN-01

**Complete when:** A requirements document explains the complete management-plane journey: discovery, feature questions, assisted pilot registration, support, onboarding status, team intervention, and later merchant subscription billing.

**Requirements to settle:**

- Tawan Official is Duply's management Channel, not the shared identity seen by a merchant's customers.
- Prospective merchants can understand Tawan, request a pilot, and be guided to the next onboarding action in plain Thai.
- Tawan Official records onboarding progress, escalates uncertainty to the Duply team, and distinguishes merchant subscription billing from a customer's Order payment.
- Activation is team-verified; self-service chat never activates an unreviewed store.

**Out of scope:** Customer commerce conversations and automated recurring billing.

### TWN-03 — Merchant Onboarding

**Phase:** 1

**Depends on:** TWN-01, TWN-02

**Complete when:** An assisted onboarding specification lists the required inputs, review points, responsible role, activation criteria, and test conversation.

**Requirements to settle:**

- Capture business/owner details, brand voice, operating hours, staff Capabilities, store policies, consent settings, catalog/price/variant/stock source, and own LINE OA connection.
- Accept guided templates, CSV, Google Sheets, approved uploads, and approved-domain website imports.
- Before activation, record the Store Owner's versioned acceptance of the final service terms, controller/processor agreement, and applicable privacy notices approved by Thai counsel.
- Keep the Store Workspace in draft until the Store Owner approves Store Knowledge and a safe test conversation succeeds.
- Do not require detailed shipping configuration at initial setup; require a manual path for fulfilment/delivery/returns instead.

**Out of scope:** Marketplace/POS connector setup and automatic store activation.

### TWN-04 — Store Workspace and Access

**Phase:** 1

**Depends on:** TWN-01

**Complete when:** A design/requirements document defines Store Workspace isolation, Store Context, canonical roles, Capabilities, support access, and the resolution of the conflicting existing tenancy designs.

**Requirements to settle:**

- Every merchant has isolated customers, Channel mapping, credentials, Store Knowledge, settings, operations, and analytics.
- Every data action derives a verified Store Context; a model, customer message, or client request cannot select another store.
- Canonical roles are `platform_admin`, `store_owner`, `store_staff`, and `customer`; staff receive explicit Capabilities rather than universal access.
- Platform support access is exceptional, time-limited, reason-coded, and audited.
- The document explicitly selects and verifies one tenancy model before implementation, including the correct current payment semantics: Store Owner review, never model/OCR auto-payment completion.

**Out of scope:** Building the authorization system or provisioning a production workspace.

### TWN-05 — Tawan Store Brain

**Phase:** 1

**Depends on:** TWN-03, TWN-04

**Complete when:** A requirements document explains how Store Knowledge is supplied, validated, approved, updated, expired, and used safely in customer replies.

**Requirements to settle:**

- Separate Store Knowledge from raw uploads and Customer Memory.
- Store sources carry provenance, checksum, uploader, sensitivity, retention, approved domain where relevant, and source version.
- Website fetching is restricted to approved domains; uploaded materials have defined type/size limits, malware scanning, protected storage, and no public access path.
- Extracted facts become Knowledge Candidates with confidence, conflict, validity, and expiry information.
- Only Store Owner-approved published knowledge can be used as a durable customer-facing fact.
- Price, stock, promotion, availability, payment, and policy facts never come from unreviewed material or model invention.

**Out of scope:** General web crawling, autonomous knowledge publication, and cross-store knowledge sharing.

### TWN-06 — Customer Sales Assistant

**Phase:** 1

**Depends on:** TWN-04, TWN-05

**Complete when:** A customer-conversation specification defines Tawan's brand-safe sales behaviour in a merchant's own LINE OA.

**Requirements to settle:**

- Answer product, colour, size, price, promotion, and availability questions from current approved facts.
- Offer relevant alternatives while a customer is actively shopping, without proactive marketing in Phase 1.
- When facts are missing, stale, low-confidence, or conflicting, say that Tawan is checking and create accountable human work rather than guessing.
- Record Sales Journey and Interaction Event progress in the reply flow, with idempotency for Channel retries.
- Use the merchant's approved brand voice while preserving the Tawan principle: never invent store facts.

**Out of scope:** Outbound campaigns, cross-Channel customer profiling, and autonomous commercial exceptions.

### TWN-07 — Orders and Store Operations

**Phase:** 1

**Depends on:** TWN-04, TWN-05, TWN-06

**Complete when:** A retail-operation specification defines the safe Order-to-outcome workflow for the fashion/accessories pilot.

**Requirements to settle:**

- Revalidate price and stock when a customer confirms an Order; reserve stock for a defined expiry period.
- Present a configured PromptPay QR where enabled and retain payment slips as protected evidence.
- OCR/AI may extract payment candidates but never marks payment paid; only the Store Owner gives the final Phase 1 decision.
- Block duplicate exact payment evidence or bank references; owner review of a probable fingerprint false positive is reason-coded and auditable.
- Track fulfilment, delivery, return, cancellation-request, and handover Tasks. Cancellation is requested by Tawan but completed by authorized human approval.

**Out of scope:** Refund automation, automatic cancellation, automatic payment approval, or autonomous discounts/price changes.

### TWN-08 — Customer Memory and Consent

**Phase:** 1

**Depends on:** TWN-04

**Complete when:** A privacy-first Customer Memory and consent specification defines what can be retained, why, for how long, and how a customer controls it.

**Requirements to settle:**

- Customer Memory remains local to one Store Workspace and identifies source, confidence, confirmation, validity, expiry, and correction history.
- Routine service data, durable preference memory, and direct marketing are separate documented purposes.
- A short Thai notice links to a full privacy notice; durable preference memory and marketing are separate voluntary choices with versioned evidence.
- STOP immediately suppresses marketing for that Store Workspace, customer, purpose, and Channel without affecting normal service.
- Verified customers can request access, applicable portability export, correction, restriction, deletion, and objection handling.
- A rights request defines identity verification strength, allowed requester/Store Owner approvals, minimised/redacted scope, response deadline, and auditable completion evidence before an export is released.
- Sensitive traits are not retained as memory, inferred, segmented, or used for recommendations/marketing by default.
- A Store Owner may assign or override a transparent Customer Tier with evidence and audit history; a Tier alone never authorizes a discount. Automated Tier recommendations remain outside this documentation-first Phase 1 scope.

**Out of scope:** Cross-store identifiable analytics and final legal advice; Thai counsel approves final legal artifacts before launch.

### TWN-09 — Admin Dashboard

**Phase:** 1

**Depends on:** TWN-04, TWN-07, TWN-08

**Complete when:** A dashboard requirements document defines the action-first views for Store Owner and Store Staff.

**Requirements to settle:**

- Prioritise unresolved Tasks and Approvals, unanswered customers, high-value opportunities, payment review, low stock, and overdue follow-up.
- Define the permitted views for Customer, Sales Journey, Transaction, Task, Approval, Catalog, Store Knowledge, consent, and settings.
- Reflect individual Capability boundaries and make material actions auditable.
- Keep analytics useful for action rather than hiding urgent work behind charts.

**Out of scope:** Advanced Pro campaigns, external marketplace control panels, and custom BI projects.

### TWN-10 — AI Workflow and Daily Insights

**Phase:** 1 to 2

**Depends on:** TWN-05, TWN-07, TWN-09

**Complete when:** A workflow document defines what happens in real time, hourly, daily, weekly, and only in Pro.

**Requirements to settle:**

- Customer reply orchestration captures structured progress immediately; it does not wait for a nightly summariser.
- Store operational state is current where possible; dashboard aggregates refresh hourly; daily close finalises store-local totals.
- The daily plain-Thai owner digest includes sales/orders, stock risks, unresolved questions, leads/follow-ups, payment/cancellation work, demand signals, and up to three evidence-backed actions.
- Recommendations expose evidence, confidence, expiry, and insufficient-data state; they do not make commercial decisions.
- Segmentation, proactive campaigns, customer lifetime value, churn, demand forecasting, and advanced intelligence are Pro/post-Phase-1 only.

**Out of scope:** Background actions that alter a store's commercial state without owner authority.

### TWN-11 — Channels and Integrations

**Phase:** 1 to 3

**Depends on:** TWN-01, TWN-04

**Complete when:** A Channel/integration strategy identifies the Phase 1 LINE boundary and an evidence-led process for later connectors.

**Requirements to settle:**

- A merchant's own LINE OA is the first complete customer Channel; Tawan Official remains the merchant-management Channel.
- The shared Channel interface preserves the possibility of Sheets/POS, Shopee, Lazada, TikTok Shop, Facebook, Instagram, and Discord without assuming identical features or authorization.
- Phase 1 uses manual inputs, templates, CSV, and Sheets before marketplace/POS integrations.
- Pilot demand, API legality/capability, security, cost, and value determine the first Phase 2 connector.
- Tawan Official Instagram initially markets Tawan itself; merchant showcases need an explicit opt-in commercial agreement in a later phase.

**Out of scope:** Implementing any post-LINE connector in Phase 1.

### TWN-12 — Pilot, Safety, and Launch Gate

**Phase:** 1

**Depends on:** TWN-01 through TWN-11

**Complete when:** A pilot and launch-gate specification defines the test journey, evidence, accountable owners, acceptance targets, legal/security release criteria, and Phase 2 go/no-go decision.

**Requirements to settle:**

- Pilot cohort: ten fashion/accessories merchants, free for 30 days, then Standard payment link for merchants who continue.
- Primary validation seam: Tawan Official onboarding through owner-approved activation, merchant LINE customer conversation, safe Order/payment/human work, dashboard update, and daily digest.
- Acceptance targets: 80% onboarding completion, 14 consecutive useful daily summaries for active merchants, 85% routine replies without correction, two hours saved per merchant each week, zero cross-store leaks/unapproved commercial actions, and 50% paid conversion.
- No real customer data before credential rotation, tenant isolation/RLS, runtime verification, cost tracking, Thai counsel review, rights/retention controls, recovery/restore exercise, incident-response rehearsal, and independent security review.
- The Phase 2 decision uses the evidence from the pilot rather than assumptions about integrations or Pro features.

**Out of scope:** Launching Phase 2 or Phase 3 features before this gate passes.
