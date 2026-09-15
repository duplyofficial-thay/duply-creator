# TWN-05 — Tawan Store Brain

**Status:** Approved planning specification; product-owner approval recorded 2026-09-15. Production implementation remains gated by Duply/security/privacy review and the TWN-04 isolation gate.

**Purpose:** Define how merchant information becomes safe, current, workspace-scoped knowledge that Tawan may use in customer conversations, while keeping raw sources, unresolved candidates, and Customer Memory separate.

## 1. Canonical definitions and boundaries

| Concept | Meaning | May reach a customer reply? |
|---|---|---|
| Store Knowledge | Approved, workspace-scoped facts about one merchant/store | Yes, only while current and entitled |
| Knowledge Source | Original upload, sheet, template, or approved-domain import | No; source material is not a promise |
| Knowledge Candidate | Extracted/proposed fact awaiting validation or approval | No |
| Published Knowledge | Owner-approved version released for retrieval | Yes, subject to freshness and scope |
| Customer Memory | Consent-eligible summary about one customer and their service history/preferences | Only for that same workspace/customer and only for its allowed purpose |

Raw uploads, rejected candidates, expired facts, credentials, secrets, payment evidence, identity documents, and restricted-sensitive material never become ordinary retrieval context. Customer Memory is not Store Knowledge and must not silently change a product, price, policy, or payment fact.

## 2. Phase 1 source contract

Supported sources are guided templates, CSV/XLSX, Google Sheets, protected document/image uploads, and owner-approved-domain website imports. General web crawling, arbitrary URLs, and cross-store reuse are out of scope.

Each source records:

- workspace and source owner/uploader;
- source type, URI/reference, approved domain where relevant, and source/version;
- checksum/content fingerprint and provenance;
- sensitivity class and retention policy;
- created, effective, reviewed, and expiry timestamps;
- extraction status, trust level, and review decision;
- superseded/replacement relationship and reason for change.

Each fact also has an explicit audience/visibility: `customer_visible`,
`merchant_internal`, `support_only`, or `restricted`. Sensitivity alone is not
an authorization decision. Merchant-confidential, customer-personal, and
restricted-sensitive facts default to non-customer-visible even when approved.

Trust levels are `owner_approved`, `merchant_submitted`, `approved_domain_import`, `staff_submitted`, `system_sync`, and `unverified`.

| Trust state | May create candidate? | May support durable fact? | May be customer-visible? |
|---|---:|---:|---:|
| `owner_approved` | Yes | Yes | Only when `customer_visible` and current |
| `system_sync` | Yes | After configured validation and Owner policy | Only after approval and visibility mapping |
| `merchant_submitted` | Yes | After Owner review | After Owner publication |
| `approved_domain_import` | Yes | After Owner review | After Owner publication |
| `staff_submitted` | Yes | After Owner review | After Owner publication |
| `unverified` or unknown | Quarantine only | No | No |

Classifier confidence falling below policy thresholds lowers trust and removes
the candidate from retrieval until re-reviewed.

Protected-source rules from TWN-03 still apply: allowlisted file types, 10 MB per-file and 50 MB total pilot limits, malware scanning, prompt-injection/data-exfiltration controls, private object storage, approved-domain allowlist, and no public file path. Source and object access must use the TWN-04 server-derived Store Context and RLS boundary.

## 3. Knowledge lifecycle

The lifecycle is:

`uploaded → extracting → needs_review → approved → published → corrected/superseded → expired`

`rejected` is an auditable terminal review outcome for a candidate; it is never retrievable. A source may be paused or quarantined when scanning, provenance, permissions, or extraction safety checks fail.

Every transition records actor, workspace, timestamp, source/version, audience,
reason, previous state, new state, and resulting task/approval. The original
source and rejected candidate remain immutable audit evidence subject to
retention policy. A correction creates a new version rather than mutating
history.

Only the `store_owner` can publish or unpublish any customer-visible knowledge,
including low-risk digest items. `workspace_admin` and the `knowledge_editor`
capability may prepare, classify, and propose candidates but cannot self-grant
publication authority. Digest approval is versioned, audited, supports rollback,
and cannot change commercial, legal, payment, stock, eligibility, or
customer-rights facts.

## 4. Version, freshness, retention, and sensitivity

Every published fact has a version, checksum/provenance, effective date, expiry date or review cadence, and superseded-by link. Retrieval excludes expired or superseded versions immediately, even if audit retention keeps them.

Sensitivity classes are:

- `public_store_info`: ordinary brand and product description;
- `merchant_confidential`: internal pricing, stock, supplier, and operating details;
- `customer_personal`: consented customer preferences and service history;
- `restricted_sensitive`: identity documents, payment evidence, credentials, legal or fraud material.

Restricted-sensitive data is never included in normal model context or vector retrieval. When a source or memory expires, retrieval stops immediately; the minimum required audit metadata is retained under policy, and deletion/anonymisation requests follow the merchant privacy process. Publication, correction, supersession, expiry, deletion, and entitlement suspension invalidate vector entries, caches, queued prompts, exports, and derived indexes within 60 seconds; the invalidation event is audited and tested.

Freshness is fact-specific. Price, stock, promotion, and payment instructions are short-lived and revalidated near use. Brand description and general policy may have longer review periods, but every source declares its review cadence and stale behavior.

## 5. Authority and conflict handling

The default authority order is:

1. current Owner-approved Published Knowledge;
2. current owner-approved catalog/price/stock system;
3. recently reviewed merchant source;
4. older or lower-confidence source;
5. unresolved conflict, which is not usable as a promise.

Fact-specific rules are mandatory:

- **Price/stock:** revalidate the current merchant source at confirmation; never infer availability.
- **Promotion:** require owner approval, eligibility, effective dates, and expiry.
- **Payment:** use only configured official instructions; never infer bank details or payment completion.
- **Policy/delivery/returns:** use the latest owner-approved version and its effective date.
- **Any unresolved conflict:** block the promise, say Tawan is checking, and create accountable work.

## 6. Approval rules and review digest

Immediate `store_owner` approval is required for price, stock, promotion, payment instructions, delivery promises, return/refund policy, legal terms, customer eligibility, and any fact that changes money or customer rights.

A periodic review digest may cover only low-risk descriptive corrections, duplicate cleanup, formatting, and non-commercial wording. The digest cannot publish high-impact facts. Each digest item includes source, proposed change, confidence, affected facts, and approve/reject action.

Rejection or correction requires a reason code/note. The candidate remains immutable for audit, the corrected version is separately versioned, and the rejected version is excluded from retrieval.

## 7. Customer Memory

Customer Memory is a short, purpose-limited, workspace-scoped summary such as a product preference, size/colour interest, prior issue, or follow-up request. It is created only when useful, non-sensitive, correctly linked to the customer/workspace, and covered by the merchant consent/privacy terms.

Low-risk preferences may be proposed or retained automatically under policy. Sensitive, ambiguous, financial, identity, complaint, or legal information remains pending or is deleted unless an authorised human approves it. Store only the summary, source interaction reference, consent basis, retention/expiry, and deletion status—not secrets, payment credentials, identity documents, or unrestricted raw transcripts.

When a customer requests correction or deletion, the memory is immediately excluded from retrieval, marked pending deletion, and then deleted or anonymised according to policy. The deletion workflow invalidates its vector entries, caches, queued prompts, exports, summaries, and derived indexes; it records completion and any retry/failure. TWN-08 owns the canonical consent, marketing-purpose separation, rights handling, and retention rules. Deleted memory is not used for training.

No raw merchant or customer data is used to improve the general Tawan model. Only explicitly approved, de-identified, aggregated patterns may be considered, after Duply product, privacy, security, and legal approval. A minimum cohort size, aggregation threshold, re-identification test, and rare-pattern/small-store suppression are required; reconstruction of one store or customer is prohibited.

## 8. Safe retrieval and customer reply contract

The rule “approved/current, customer-visible facts only” is enforced at every layer: database query, vector retrieval, prompt assembly, tool/action input, cache, queue, export, and final reply validation. The prompt is never the sole protection. A `merchant_internal`, `support_only`, or `restricted` fact must be blocked from a customer Channel even when it is approved and current.

Tawan must not guess. For missing, stale, low-confidence, expired, or conflicting facts, it says it is checking, creates a Task/Approval with source, issue type, severity, owner capability, due time, and customer-facing status, and offers a safe next step. High-impact issues block promises immediately; low-risk issues may wait for a review digest.

## 9. Audit and acceptance tests

Audit events cover upload, extraction, candidate creation, approval, rejection, publication, correction, supersession, expiry, retrieval, memory creation/deletion, conflict resolution, export, and break-glass access. Each event records actor, workspace, source/version, timestamp, reason, and result.

Before implementation approval, tests must prove that:

- raw, unapproved, rejected, expired, and conflicting facts cannot reach customer replies;
- merchant-internal, support-only, customer-personal, and restricted facts cannot reach a customer reply;
- owner approval gates work and non-owner roles cannot self-publish high-impact facts;
- workspace isolation holds across rows, joins, vectors, prompts, tools, caches, queues, exports, and object storage;
- source versions, provenance, freshness, and conflict reasons are visible;
- Customer Memory consent, retention, correction, and deletion work;
- deletion invalidates vectors, caches, queues, exports, summaries, and derived indexes within the 60-second maximum;
- low-risk digest publication still requires Owner approval and supports rollback;
- trust-level changes and unknown/low-confidence sources default to non-retrievable;
- representative Thai stale/conflict conversations create safe Tasks rather than invented promises;
- TWN-04 subscription suspension and Store Context rules still apply.

## 10. Approval and out-of-scope boundary

TWN-05 is complete when all eight checklist tasks are evidenced here, the product owner approves the behavior, the Store Owner approves the merchant-facing lifecycle, and independent Duply/security/privacy review records its findings and gates.

Out of scope: general web crawling, autonomous knowledge publication, cross-store knowledge sharing, automatic payment completion, unrestricted transcript training, and production activation before TWN-04 isolation/security approval.

**Dependencies:** TWN-03 protected-source/onboarding rules; TWN-04 Store Context, RLS, roles, Channel, storage, entitlement, and audit contracts. TWN-06 must reference this document for customer reply behavior rather than redefining Store Brain semantics.
