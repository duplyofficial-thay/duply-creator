# TWN-03 — Merchant Onboarding

**Status:** Approved planning specification; pilot verification is low-friction and stronger identity checks are risk-triggered (2026-09-14)

**Decision owner:** Store Owner/product owner (Arriyathanasak, `arriyathanasak@gmail.com`).

**Purpose:** Define the assisted onboarding checklist and review gates for a Thai retail merchant using Tawan. This document is a design and engineering handoff. Approval does not authorize production LINE connection, real customer data, payment-provider spend, passport/national-ID collection, or schema migration.

## 1. Pilot boundary and ownership

Phase 1 onboarding targets Thai small-to-medium social-commerce merchants selling physical retail products by piece. The merchant's Duply account is the starting identity. Duply owns platform identity, entitlement, legal/compliance review, and final activation. Tawan owns the guided checklist, draft progress, safe explanations, and task creation. The Store Owner approves Store Knowledge, policies, consent acknowledgements, staff access, and the test conversation.

The pilot uses low-friction verification:

- verified Duply account, email, phone, and linked LINE identity;
- store/business name, owner name, contact details, and owner-authority declaration;
- no passport or national-ID document for ordinary onboarding;
- an auditable verification result and source, not a copy of identity documents.

This is not zero verification. It is a deliberately limited pilot verification tier. Stronger verification is a later risk-triggered path owned by Duply.

## 2. Required checklist

| Area | Required minimum | Owner / evidence | Blocks readiness when |
|---|---|---|---|
| Duply identity | Duply account ID, Store Workspace ID, verified email/phone, linked LINE identity, account status | Duply service | Identity is inactive, conflicting, or unresolved |
| Owner authority | Full name, store/business name, contact route, country, authority declaration | Store Owner + Duply | Authority is unclear or contradictory |
| Pilot verification | `verified`, `needs_review`, or `restricted` result; source, timestamp, rule/reviewer version | Duply | Result is missing or review remains open |
| Brand voice | Fixed choices for tone, formality, greeting, customer reference, and prohibited style | Store Owner | No safe default or an unsafe free-form instruction is supplied |
| Operating hours | Store timezone (Asia/Bangkok default), business days, hours, temporary closure note, owner contact window | Store Owner | Timezone or emergency contact route is missing |
| Staff | Name, LINE user ID, proposed role/Capability, owner approval, status | Store Owner | A staff member is granted access before approval |
| Policies | Payment methods, delivery area/method, estimated delivery time, returns/exchanges, cancellation, warranty if applicable, human-support hours | Store Owner; supporting source optional | A customer-facing answer would be unsafe or misleading |
| Consent/legal | Versioned service terms, controller/processor terms, privacy notice, source permission, publication responsibility, authority confirmation | Store Owner; legal versions owned by Duply | Required version is not accepted |
| Catalog | Product name, SKU/unique ID, unit, price, stock/availability, variants when relevant, description, update source | Store Owner / source record | Required facts conflict or cannot be traced |
| Stock operations | Who updates stock, update frequency, stale-data response, and approved source | Store Owner | Tawan would need to promise unknown availability |
| Merchant LINE OA | Approved connection, channel identity/store association, webhook/reply test | Duply/Channel Adapter | Channel is unverified or test fails |
| Fulfilment | Manual fulfilment owner, delivery/tracking route, return/cancellation handoff | Store Owner | No accountable manual path exists |

Tawan asks one plain-Thai question at a time, accepts “ยังไม่แน่ใจ”, saves partial answers, and shows an editable summary before submission. Required fields are marked separately from optional fields. A merchant may pause and resume without silently submitting an incomplete checklist.

## 3. Constrained brand voice

Beginner merchants choose from safe, fixed values rather than writing a system prompt:

| Category | Allowed pilot choices |
|---|---|
| Tone | friendly, professional, warm, concise, playful |
| Formality | casual, balanced, formal |
| Greeting | short, welcoming, brand-style |
| Customer reference | ลูกค้า, คุณลูกค้า, one owner-approved term |
| Prohibited style | pressure, exaggerated claims, unsupported promises, abusive language |

Tawan preserves the global rule “never invent store facts”. Free-form persona prompts, autonomous style rules, and sensitive-trait targeting are out of scope. An owner can change a choice only through a versioned review; the previous value remains in audit history.

## 4. Identity, risk, and illegal-use handling

### 4.1 Tier 1 — standard pilot verification

Continue onboarding only when the Duply account, email, phone, LINE identity, store details, and owner-authority declaration are consistent; no duplicate-account, impersonation, payment, security, or prohibited-product signal is open; and the requested capabilities fit the normal retail pilot.

### 4.2 Tier 2 — enhanced Duply review

Pause activation and create a Duply review task for identity/ownership mismatch, unusual duplicate-account patterns, inconsistent payment/subscription details, copied or incomplete business information, potentially restricted products or claims, repeated onboarding bypass attempts, serious complaints, or a trusted platform/payment/security signal.

Tawan must not accuse the merchant, request an ID in LINE, or decide that conduct is illegal. It explains that the request needs review and shows the case status.

### 4.3 Tier 3 — strong verification or restriction

Only an authorised Duply reviewer may request national ID/passport evidence through a secure Duply verification provider or vault when Tier 2 evidence remains unresolved, a payment/compliance provider requires it, counsel confirms the legal basis, impersonation/fraud evidence is strong, or access to a higher-risk capability requires it.

Identity documents are never ordinary Store Knowledge, customer data, prompts, or model input. Tawan consumes only a result such as `verified`, `rejected`, `expired`, or `needs_review`, plus source, timestamp, reviewer/rule version, and reason code.

Potential fraud or illegal selling is first signalled to Duply. Duply confirms, restricts, or suspends the account and handles any lawful authority request. No automatic police disclosure or accusation is made by Tawan.

### 4.4 Protection requirements

- Collect only the minimum evidence needed for the approved purpose.
- Show purpose, legal basis, access scope, retention period, and correction/deletion route before collection.
- Use secure upload/identity-provider flow; never accept ID in LINE chat or ordinary email attachment.
- Encrypt in transit and at rest; keep the document in a restricted compliance vault separate from Store Workspace data.
- Restrict access to named Duply compliance/security roles and log every view, export, decision, and deletion.
- Retain only for the approved legal/compliance period; delete unused or failed documents and record the deletion unless a legal hold applies.
- Use pseudonymised verification references in Tawan and Store Workspace records.

## 5. Data sources and input quality

Phase 1 supports guided templates, CSV, Google Sheets, approved document/image uploads, and approved-domain website imports. A source record stores uploader, source type, source/version, checksum or equivalent fingerprint, approved domain where relevant, sensitivity, retention, provenance, and effective/expiry dates.

The onboarding UI also provides an isolated **test-data mode**. A merchant may rehearse the checklist and test conversation with clearly labelled synthetic/sample products, prices, stock, and policies before connecting a live source. Test data is stored in a separate test context, is never shown to real customers, cannot be published as live Store Knowledge, and is deleted or reset when the merchant switches to live setup. The test mode does not bypass owner approval, legal acknowledgements, LINE verification, or activation gates.

The initial protected-source allowlist is CSV, XLSX, PDF, PNG, and JPEG. The engineering handoff must set a per-file limit of 10 MB and a total onboarding upload limit of 50 MB, with the values configurable before launch. Unsupported formats, oversized files, encrypted archives, and failed scans are rejected with a plain-Thai explanation and a Duply support route; the owner may provide a supported replacement rather than bypassing the checks.

Every upload or import first passes file/type/size checks, malware scanning, protected storage, and prompt-injection/data-exfiltration controls. Website fetching is limited to an owner-approved domain allowlist. There is no public file path and no unrestricted web crawl.

Extracted facts remain draft Knowledge Candidates. They carry confidence, warnings, conflicts, source location, effective date, and expiry. They are never customer-facing promises until the Store Owner approves the resulting Store Knowledge. Price, stock, payment, delivery, return, and policy conflicts block readiness or create an owner decision task.

The owner must state who owns each source and how often it is updated. If a source is stale, missing, or contradictory, Tawan says it is checking and does not promise availability, price, delivery, or policy.

## 6. Onboarding state machine

`draft → owner_review → needs_owner_decision → test_ready → live_ready`

The state may exit to `paused`, `rejected`, `restricted`, or `closed`. `owner_review` means all required fields have a draft value and the owner can edit the summary. `needs_owner_decision` means a conflict, missing policy, risk signal, or source-quality issue requires an accountable decision. `test_ready` means required data and legal acknowledgements are present, Store Knowledge is approved, the merchant LINE OA is verified, and a safe test conversation can run. `live_ready` means the test passed and Duply's activation gate is satisfied.

Tawan can move a draft forward only when the responsible owner/action is recorded. It cannot bypass risk review, Store Owner approval, legal acceptance, or the successful test conversation.

## 7. Approval and activation gates

Before `test_ready`, the system must have:

1. Duply identity and Store Workspace resolved.
2. Owner authority and pilot verification result recorded.
3. Required checklist fields complete or explicitly marked not applicable.
4. Staff access approved or no staff invited.
5. Policies and fulfilment path recorded.
6. Versioned terms, privacy notice, controller/processor terms, source permission, and publication responsibility accepted.
7. Catalog/stock facts traceable to an approved source with no unresolved blocking conflict.
8. Merchant LINE OA connected and testable.
9. Store Knowledge approved by the Store Owner.

Before `live_ready`, the system must also record a successful test conversation, safe missing/stale-fact behaviour, audit evidence for every gate, and Duply's final activation decision. Routine pilot activation may be automated only when deterministic checks pass; risk exceptions and low-confidence evidence require human Duply review.

## 8. 24-hour support and manual operations

Tawan remains available 24 hours. The store's operating hours control customer-facing expectations, not whether Tawan can receive a merchant issue. Outside store hours, Tawan contacts the owner only for urgent security, suspected illegal use, payment risk, service outage, or customer-harm cases; routine messages follow configured quiet hours.

Manual fulfilment is sufficient for the pilot. The checklist records fulfilment owner, delivery method/area, tracking route, returns, cancellations, and support hours. POS, warehouse, courier, automatic shipping, and other connectors are not required by TWN-03.

Payment methods may include PromptPay QR and bank transfer/manual slip review for the merchant's own customer-facing store checkout. These are Store Workspace payment settings and never determine Tawan/Duply merchant subscription entitlement. Card/Stripe is recorded as planned/not enabled until Duply activates it. Tawan must not display an unavailable payment method to a customer.

“Tawan remains available 24 hours” means automated intake, saved-progress, and status display are available continuously. Human review and replies follow configured Duply/store support hours and published service levels, except that urgent security, suspected illegal use, payment-risk, outage, or customer-harm cases follow the urgent escalation policy.

## 9. Acceptance criteria and out of scope

TWN-03 is accepted only when all eight task rows are evidenced here, the Duply team reviews feasibility/UX, the Store Owner approves the onboarding checklist and gates, and approval is recorded with a date. No implementation, live LINE connection, real customer-data admission, paid provider activation, or ID-document collection starts from this document alone.

Out of scope: mandatory passport/national-ID collection for ordinary pilot merchants; automatic legal conclusions; automatic authority disclosure; public web crawling; autonomous Knowledge publication; autonomous activation without all gates and Duply's activation decision; automatic fulfilment/shipping; POS/marketplace connectors; free-form system prompts; and final Standard/Pro pricing.

## Approval evidence

- Product owner approved the TWN-03 decision rounds, including low-friction pilot verification and risk-triggered stronger verification, on 2026-09-14.
- Duply team feasibility, security/privacy, and UX review remains required before coding.
- Thai counsel must approve final privacy notices, controller/processor terms, identity-verification wording, retention schedule, and authority-disclosure procedure before production use.
