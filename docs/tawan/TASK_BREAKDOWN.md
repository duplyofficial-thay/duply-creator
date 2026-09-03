# Tawan Task Breakdown

**Status:** Canonical task manifest for Git and Notion synchronization

**Updated:** 2026-08-18

**Source:** Approved Tawan product, architecture, data, security, legal-research, decision, and implementation documents

## 1. How To Use This Manifest

- Keep each Task small enough for roughly one to two focused working days. Split a Task before implementation when verified private interfaces make it larger.
- Use the stable `TWN-*` identifier to update an existing Notion record. Never create a duplicate when the identifier already exists.
- Produce a dry-run mapping for legacy-title matches. Never merge, archive, or replace a human-maintained Notion record without explicit owner approval.
- Keep `Owner`, `Reviewer`, estimate, and due date `Unspecified` until a person accepts them. Do not infer assignments.
- A `Done` engineering Task requires a committed change and verification evidence. A Notion checkbox alone is not completion evidence.
- `Blocked` means an external dependency prevents responsible execution. Later milestones remain `Backlog`, not falsely blocked.
- Campaign execution and intelligence are Pro-only and post-Phase-1. Standard Tasks must not expose Campaign execution.

## 2. Notion Field Mapping

| Field | Rule |
|---|---|
| Task ID | Stable value from this manifest; use a title prefix if the database cannot add a property |
| Task | Use the action-oriented title below |
| Type | Epic, Task, Research, Decision, Review, or Bug |
| Status | Backlog, Ready, In Progress, Blocked, Review, or Done |
| Phase | Documentation, Discovery, Phase 1, Transition Gate, Phase 2, or Later |
| Plan | Shared, Standard, Pro, or Custom B2B |
| Area | Product, Platform, LINE, Data, Security, Dashboard, Analytics, Campaign, Legal, or Operations |
| Priority | Critical, High, Medium, or Low |
| Depends On | Stable Task IDs; preserve links when titles change |
| Acceptance | Required evidence before completion |
| Source | Commit-pinned Markdown link after the source commit reaches the canonical default branch |

## 3. Milestone 0 - Documentation And Handoff

**Epic:** Establish one approved source of truth and a safe human/AI handoff.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0001 | Reconcile the historical Notion draft against approved Git records | Review | Shared | Product | High | Review | - | Every stale tenancy, payment, Campaign, export, and implementation claim is mapped to its replacement or archive action |
| TWN-0002 | Maintain the canonical Tawan product and technical documents | Task | Shared | Product | Critical | Done | - | Product, architecture, data, security, decisions, and implementation documents are committed and internally consistent |
| TWN-0003 | Preserve Thai PDPA research and counsel questions | Research | Shared | Legal | High | Done | - | Research cites primary authorities and is clearly labelled as non-legal advice |
| TWN-0004 | Maintain the portable Tawan handoff skill | Task | Shared | Operations | High | Done | TWN-0002 | A fresh AI account reconstructs tier, status, blockers, and next milestone without chat history |
| TWN-0005 | Publish approved Tawan commits to the canonical GitHub default branch | Task | Shared | Operations | Critical | Blocked | Owner push approval | Full SHA is reachable from `origin` default branch and no unrelated files are pushed |
| TWN-0006 | Add verified Markdown source links to the Notion hub | Task | Shared | Operations | High | Blocked | TWN-0005 | Every required link opens in the intended friend/AI context and uses the full permanent SHA |
| TWN-0007 | Reconcile existing Tawan Board records by stable Task ID | Task | Shared | Operations | High | Blocked | Notion API/session access, TWN-0006 | Dry-run mapping is owner-approved before existing records are updated; no human record is merged or archived without explicit approval; comments are preserved |

## 4. Milestone 1 - Runtime And Data Discovery

**Epic:** Replace assumptions with verified Duply interfaces before production code.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0101 | Obtain read-only access to runtime, data, dashboard, and deployment repositories | Task | Shared | Operations | Critical | Ready | Human access grants | Repository names, owners, access limits, and contacts are recorded without exposing credentials |
| TWN-0102 | Verify LINE destination-to-Duple and Store Context resolution | Research | Shared | LINE | Critical | Blocked | TWN-0101 | Actual webhook path, identity inputs, failure behavior, and trusted boundary are documented |
| TWN-0103 | Verify archetype loading, agent dispatch, roles, and tool registry | Research | Shared | Platform | Critical | Blocked | TWN-0101 | Real interfaces and compatibility constraints for shared Tawan code are documented |
| TWN-0104 | Verify knowledge, vector, memory, and raw-message contracts | Research | Shared | Data | Critical | Blocked | TWN-0101 | Authoritative tables, retrieval filters, retention behavior, and store boundaries are documented |
| TWN-0105 | Verify command authorization, idempotency, cache, queue, and object storage | Research | Shared | Security | Critical | Blocked | TWN-0101 | Every write and shared subsystem has a verified tenancy and replay contract |
| TWN-0106 | Verify LINE media, Flex message, image validation, and delivery contracts | Research | Shared | LINE | High | Blocked | TWN-0101 | Inbound/outbound media interfaces, limits, storage, retry, and delivery results are documented |
| TWN-0107 | Verify migration, rollback, backup, restore, and cost-ledger interfaces | Research | Shared | Operations | Critical | Blocked | TWN-0101 | Owners, commands, environments, failure recovery, and paid-call logging contract are documented |
| TWN-0108 | Produce the repository map, contradiction report, and revised file-level plan | Review | Shared | Platform | Critical | Blocked | TWN-0102 through TWN-0107 | No private path is guessed; every dependency has an owner; product owner approves proposed platform changes |

## 5. Milestone 2 - Test Harness And Migration Foundation

**Epic:** Build repeatable local evidence before commerce implementation.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0201 | Select and document the repository test toolchain | Decision | Shared | Platform | Critical | Review | TWN-0108 | `python3 -m unittest discover -s tests -p "test_*.py"` and `PYTHONPYCACHEPREFIX=/tmp/duply-creator-pycache python3 -m compileall scripts duples` are documented in `docs/tawan/TESTING.md` and pass locally |
| TWN-0202 | Create a rollback-capable commerce migration runner and manifest | Task | Shared | Data | Critical | Review | TWN-0201 | Local manifest validates ordering, renders safe schema SQL, and plans apply/rollback; live execution awaits Duply's authoritative runner |
| TWN-0203 | Create a disposable Postgres verification environment | Task | Shared | Data | Critical | Backlog | TWN-0202 | A clean database can be created, migrated, rolled back, and recreated automatically |
| TWN-0204 | Create synthetic fixtures for two stores and five demo businesses | Task | Shared | Data | High | Review | TWN-0203 | Six isolated synthetic stores cover fashion, food, beauty, services, wholesale, and construction with no real credentials or personal data |
| TWN-0205 | Test archetype selection, registration validation, and migration replay | Task | Shared | Platform | Critical | Review | TWN-0202, TWN-0204 | Registration validation and migration plan/replay behavior are tested locally; database replay awaits Duply's disposable environment |
| TWN-0206 | Test schema-role isolation and secret/environment safeguards | Task | Shared | Security | Critical | Backlog | TWN-0203, TWN-0204 | Each synthetic role is denied access to the other schema and secret scans pass |
| TWN-0207 | Complete test and migration foundation exit review | Review | Shared | Operations | Critical | Backlog | TWN-0201 through TWN-0206 | Supported commands pass from a clean checkout; migration rollback, replay, fixtures, isolation, and regressions have evidence |

## 6. Milestone 3 - Store Workspace And Access Foundation

**Epic:** Enforce one isolated Tawan Instance per Store Workspace.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0301 | Implement Tawan registration and shared archetype configuration | Task | Standard | Platform | Critical | Backlog | TWN-0206 | Multiple Tawan Instances reuse shared code without sharing configuration or schema credentials |
| TWN-0302 | Implement trusted Store Resolver and Store Context propagation | Task | Standard | Platform | Critical | Backlog | TWN-0301 | Chat, tools, knowledge, memory, cache, queue, storage, and logs receive the verified Store Context |
| TWN-0303 | Provision one least-privilege schema role per Store Workspace | Task | Standard | Data | Critical | Backlog | TWN-0202, TWN-0301 | Native database permissions prevent cross-store reads and writes |
| TWN-0304 | Implement canonical roles and staff Capability grants | Task | Standard | Security | Critical | Backlog | TWN-0302 | `platform_admin`, `store_owner`, `store_staff`, and `customer` enforce the approved action matrix |
| TWN-0305 | Implement time-limited audited Platform Administrator support sessions | Task | Shared | Security | High | Backlog | TWN-0304 | Session records actor, reason, target, expiry, actions, and immediate revocation |
| TWN-0306 | Implement store settings and subscription entitlement boundaries | Task | Standard | Platform | High | Backlog | TWN-0304 | Timezone, currency, expiry, notifications, review cadence, and Standard/Pro gates validate server-side |
| TWN-0307 | Run cross-store adversarial tests through every implemented interface | Review | Shared | Security | Critical | Backlog | TWN-0302 through TWN-0306, TWN-0308 | Cross-store read, write, cache, vector, queue, object, and URL attempts fail with audit evidence |
| TWN-0308 | Implement append-only Audit Events and authorized inspection | Task | Shared | Security | Critical | Backlog | TWN-0302, TWN-0304 | Security and commercial actions record store, actor, reason, target, result, time, and correlation without mutable history |
| TWN-0309 | Implement staff and Platform Administrator MFA | Task | Shared | Security | Critical | Backlog | TWN-0105, TWN-0304 | Privileged sessions require supported MFA with recovery, revocation, and audit evidence |
| TWN-0310 | Implement webhook, authentication, and tool rate limits | Task | Shared | Security | High | Backlog | TWN-0105, TWN-0302 | Store/customer limits resist abuse without allowing one store to exhaust another store's capacity |
| TWN-0311 | Implement security monitoring and actionable alert delivery | Task | Shared | Operations | High | Backlog | TWN-0308, TWN-0310 | Cross-store denials, auth failures, unusual exports, queue failure, and payment conflicts alert an accountable owner |
| TWN-0312 | Implement periodic staff access and Capability review | Task | Standard | Security | High | Backlog | TWN-0304, TWN-0308 | Owners can review, revoke, and evidence current staff access on a configured cadence |
| TWN-0313 | Complete Store Workspace security exit review | Review | Shared | Security | Critical | Backlog | TWN-0302 through TWN-0312, TWN-0314 | Isolation, roles, audit, MFA, rate limits, monitoring, access review, and key handling pass before feature work begins |
| TWN-0314 | Implement encrypted secret and key lifecycle management | Task | Shared | Security | Critical | Backlog | TWN-0105, TWN-0302 | Secrets and keys are store/environment-scoped, encrypted, rotated, revocable, and absent from logs and exports |

## 7. Milestone 4 - Knowledge Ingestion And Customer Memory

**Epic:** Build reviewed Store Knowledge and privacy-aware Customer Memory.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0401 | Implement protected source upload and source registry | Task | Standard | Data | Critical | Backlog | TWN-0313 | Files are private, checksummed, store-scoped, bounded, scanned, and assigned retention classes |
| TWN-0402 | Implement approved-domain URL import with SSRF protection | Task | Standard | Security | High | Backlog | TWN-0401 | Redirects, private networks, size, timeout, and content type are safely controlled |
| TWN-0403 | Implement structured document parsers and Knowledge Candidate extraction | Task | Standard | Data | High | Backlog | TWN-0401 | Supported text, CSV, and spreadsheet fields include provenance, confidence, scope, validity, warnings, and conflicts |
| TWN-0404 | Implement candidate review, approval, publication, expiry, and supersession | Task | Standard | Platform | Critical | Backlog | TWN-0403 | Only the Store Owner publishes permanent knowledge; history remains auditable |
| TWN-0405 | Implement daily digest and configurable weekly/monthly knowledge review | Task | Standard | Operations | Medium | Backlog | TWN-0404 | Critical changes request immediate review; lower-risk changes follow owner cadence |
| TWN-0406 | Implement structured Customer Memory with source and confidence | Task | Standard | Data | Critical | Backlog | TWN-0313 | Explicit and inferred memory records source, dates, confidence, confirmation, version, validity, and correction history |
| TWN-0407 | Implement Customer memory view, correction, deletion, and retention | Task | Standard | Security | Critical | Backlog | TWN-0406 | Thai/plain-language requests work and deletion propagates subject to legal holds |
| TWN-0408 | Implement raw-message expiry and structured Interaction Events | Task | Standard | Data | Critical | Backlog | TWN-0313 | Raw content expires by policy while reply-time capture preserves required progress and outcome events as structured records |
| TWN-0409 | Test prompt injection, knowledge poisoning, stale facts, and cross-store retrieval | Review | Shared | Security | Critical | Backlog | TWN-0402, TWN-0404, TWN-0407, TWN-0408 | Untrusted content cannot publish, authorize tools, or retrieve another store's data |
| TWN-0410 | Create guided onboarding templates for stores without source data | Task | Standard | Product | Medium | Backlog | TWN-0403 | Catalog, policy, FAQ, service, shipping, and contact templates produce reviewable Knowledge Candidates |
| TWN-0411 | Implement bounded image/PDF OCR adapter | Task | Standard | Data | High | Backlog | TWN-0401, TWN-0403 | OCR enforces page/size limits and preserves page-level provenance, confidence, warnings, and failure evidence |
| TWN-0412 | Complete knowledge and memory exit review | Review | Standard | Security | Critical | Backlog | TWN-0401 through TWN-0411 | Upload, import, parsing, OCR, templates, approval, expiry, memory rights, retention, and poisoning tests pass |

## 8. Milestone 5 - Sales Journey, Tasking, And Approvals

**Epic:** Turn conversations into controlled progress and accountable human work.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0501 | Implement store-specific Customer identity and Sales Journey lifecycle | Task | Standard | Platform | Critical | Backlog | TWN-0313 | Journey states, outcomes, Channel identity, value, next action, and timestamps validate consistently |
| TWN-0502 | Implement Task lifecycle, assignment, due time, escalation, and history | Task | Standard | Platform | Critical | Backlog | TWN-0501 | Approved states and terminal outcomes are enforced and audited |
| TWN-0503 | Implement initial Task types and deterministic deduplication | Task | Standard | Platform | High | Backlog | TWN-0502 | Answer, discount, payment, stock, follow-up, delivery, knowledge, and VIP Tasks do not duplicate on retry |
| TWN-0504 | Implement Approval records and owner-only final authority | Task | Standard | Security | Critical | Backlog | TWN-0304, TWN-0502 | Knowledge, exceptional price, payment, staff, retention, and sensitive export approvals record scope and actor |
| TWN-0505 | Implement unauthorized-discount escalation without promise | Task | Standard | Platform | High | Backlog | TWN-0503, TWN-0504 | Tawan creates a waiting-owner Task and cannot communicate an unapproved commercial exception |
| TWN-0506 | Record structured Interaction Events and Task/Approval analytics events | Task | Standard | Analytics | Medium | Backlog | TWN-0501 through TWN-0504 | Meaningful progress is captured during reply orchestration and measurable without requiring indefinite transcripts |
| TWN-0507 | Test lifecycle authorization, retries, races, timeout, and revoked access | Review | Shared | Security | Critical | Backlog | TWN-0501 through TWN-0506 | Invalid transitions fail atomically and retries return the prior result |
| TWN-0508 | Implement store-defined Customer Tier rules and evidence | Task | Standard | Data | High | Backlog | TWN-0406, TWN-0501 | Tier calculations record store-local evidence, version, dates, confidence, and expiry without cross-store profiling |
| TWN-0509 | Implement owner Tier recommendation review and manual override | Task | Standard | Platform | High | Backlog | TWN-0508, TWN-0504 | Tawan recommends; owner can approve, reject, set, expire, or override a Tier with reason and audit history |
| TWN-0510 | Implement staff/owner notification policy and routing | Task | Standard | Operations | High | Backlog | TWN-0306, TWN-0502 | Dashboard and LINE destinations respect urgency, role, quiet hours, and critical escalation policy |
| TWN-0511 | Implement notification delivery results, retries, and deduplication | Task | Standard | Operations | High | Backlog | TWN-0510 | Retries do not duplicate alerts; failures and acknowledgements remain visible and actionable |
| TWN-0512 | Complete Journey, Task, Approval, Tier, and notification exit review | Review | Standard | Security | Critical | Backlog | TWN-0501 through TWN-0511 | Authorization, lifecycle, deduplication, escalation, owner authority, Tier, and delivery evidence pass |

## 9. Milestone 6 - Retail Commerce And Manual Payment

**Epic:** Complete the first fashion retail transaction safely.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0601 | Implement catalog items, variants, stock locations, and availability | Task | Standard | Data | Critical | Backlog | TWN-0313 | Size/color variants remain relational, stock cannot become negative, and store boundaries hold |
| TWN-0602 | Implement deterministic price precedence and auditable exceptions | Task | Standard | Platform | Critical | Backlog | TWN-0306, TWN-0504, TWN-0509 | Customer-specific, Campaign, Tier, quantity/wholesale, and standard prices resolve in approved order |
| TWN-0603 | Implement Order lifecycle and immutable confirmed line snapshots | Task | Standard | Platform | Critical | Backlog | TWN-0501, TWN-0601, TWN-0602 | State transitions are atomic and confirmed item/price snapshots do not silently change |
| TWN-0604 | Implement stock reservation, configurable expiry, and release | Task | Standard | Data | Critical | Backlog | TWN-0601, TWN-0603 | Concurrent reservations never oversell and expiry releases capacity exactly once |
| TWN-0605 | Implement PromptPay QR generation and protected payment evidence storage | Task | Standard | Platform | Critical | Backlog | TWN-0603 | QR uses configured merchant data; slips are private with short-lived authorized access |
| TWN-0606 | Implement payment extraction and duplicate-evidence blocking | Task | Standard | Security | Critical | Backlog | TWN-0605 | Hash, fingerprint, amount/time, and bank-reference conflicts block approval; confirmed bank references cannot be reused; only owner reason-coded resolution clears a false positive |
| TWN-0607 | Implement manual payment-review Task and owner decision | Task | Standard | Platform | Critical | Backlog | TWN-0503, TWN-0504, TWN-0606 | Staff may recommend; only Store Owner marks final Phase 1 paid/rejected state |
| TWN-0608 | Implement fulfilment, completion, refund, dispute, and failure handling | Task | Standard | Operations | High | Backlog | TWN-0603, TWN-0604, TWN-0607 | Delivery failure creates follow-up work; refund/dispute states remain distinct and auditable |
| TWN-0609 | Run the fashion LINE staging journey end to end | Review | Standard | LINE | Critical | Backlog | TWN-0409, TWN-0507, TWN-0608, TWN-0613 | Question, accurate answer, variant, Order, QR, slip, review, fulfilment, and completion succeed with synthetic data |
| TWN-0610 | Verify paid-call cost logging at response success time | Review | Shared | Operations | Critical | Backlog | TWN-0107, TWN-0609 | Every successful paid API call is ledgered before parsing and reconciles to the staging run |
| TWN-0611 | Implement LINE webhook verification, normalization, and idempotency | Task | Standard | LINE | Critical | Backlog | TWN-0106, TWN-0302, TWN-0310 | Invalid signatures fail; retries map to one store-scoped inbound event and one processing result |
| TWN-0612 | Implement LINE inbound text and protected media handling | Task | Standard | LINE | High | Backlog | TWN-0401, TWN-0611 | Text, images, and slips enforce type/size limits, private storage, retention, and Store Context |
| TWN-0613 | Implement LINE replies, Flex delivery, results, and retries | Task | Standard | LINE | Critical | Backlog | TWN-0511, TWN-0612, TWN-0616 | Customer replies and staff alerts record delivery state; retries are idempotent and failures create follow-up work |
| TWN-0614 | Implement store-scoped published-knowledge and Customer Memory retrieval | Task | Standard | Platform | Critical | Backlog | TWN-0412, TWN-0501 | Retrieval uses only current approved knowledge and permitted store-local memory with provenance and validity evidence |
| TWN-0615 | Implement response planning and deterministic command validation | Task | Standard | Platform | Critical | Backlog | TWN-0504, TWN-0603, TWN-0614 | One response plan contains the customer reply plus validated capture commands; model output cannot bypass authorization, price, stock, approval, idempotency, or command-schema validation |
| TWN-0616 | Implement no-answer and unsafe-action fail-to-human orchestration | Task | Standard | Platform | Critical | Backlog | TWN-0503, TWN-0615 | Unknown, conflicting, stale, unauthorized, or low-confidence cases ask safely or create one accountable Task without guessing |
| TWN-0617 | Complete retail commerce and LINE exit review | Review | Standard | Security | Critical | Backlog | TWN-0601 through TWN-0616 | Catalog, price, Order, reservation, payment, orchestration, LINE transport, full staging journey, and paid-call ledger pass |

## 10. Milestone 7 - Core Dashboard

**Epic:** Give owners and staff an action-first mobile and desktop workspace.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0701 | Verify dashboard repository, deployment target, and authentication | Research | Standard | Dashboard | Critical | Backlog | TWN-0108 | Ownership, stack, environment, session, and Store Context contract are documented |
| TWN-0702 | Implement subscription-aware navigation and action authorization | Task | Standard | Dashboard | Critical | Backlog | TWN-0304, TWN-0306, TWN-0701 | Standard cannot access Campaign controls; roles and Capabilities gate every action server-side |
| TWN-0703 | Build Overview and urgent-work queue | Task | Standard | Dashboard | High | Backlog | TWN-0507, TWN-0702 | Owner sees unanswered Customers, payment reviews, low stock, and overdue follow-up with stable loading states |
| TWN-0704 | Build Customer list, profile, Journey, and interaction history | Task | Standard | Dashboard | High | Backlog | TWN-0501, TWN-0702 | Authorized staff can find a store-local Customer and inspect Journey progress and structured history |
| TWN-0705 | Build Transaction and payment-review views | Task | Standard | Dashboard | Critical | Backlog | TWN-0608, TWN-0702 | Authorized staff inspect Transactions and evidence while owner-only payment decisions remain protected |
| TWN-0706 | Build Catalog and Service management views | Task | Standard | Dashboard | High | Backlog | TWN-0601, TWN-0702 | Authorized staff inspect and maintain store-scoped commercial facts without database access |
| TWN-0707 | Build Settings and staff-access views | Task | Standard | Dashboard | High | Backlog | TWN-0306, TWN-0312, TWN-0702 | Staff access, payment, Channel, retention, notifications, timezone, and closing schedule work |
| TWN-0708 | Validate responsive, accessible, empty, error, retry, and unauthorized states | Review | Standard | Dashboard | High | Backlog | TWN-0703 through TWN-0707, TWN-0709 through TWN-0712 | Phone and desktop screenshots plus browser tests cover critical owner/staff journeys |
| TWN-0709 | Build approval and sales-opportunity queues | Task | Standard | Dashboard | High | Backlog | TWN-0504, TWN-0509, TWN-0702 | Owner can act on knowledge, price, payment, Tier, staff, and high-value opportunity records |
| TWN-0710 | Build Customer Memory, Tier, and consent controls | Task | Standard | Dashboard | High | Backlog | TWN-0407, TWN-0509, TWN-0704 | Correction, deletion, consent, Tier review/override, and audit evidence are available |
| TWN-0711 | Build Task, assignment, escalation, and approval-history views | Task | Standard | Dashboard | High | Backlog | TWN-0507, TWN-0511, TWN-0702 | Staff work queues, notification results, overdue states, and owner decisions are inspectable |
| TWN-0712 | Build Tawan Brain candidate and digest review views | Task | Standard | Dashboard | High | Backlog | TWN-0405, TWN-0702 | Source conflicts, candidates, approval history, expiry, supersession, and review digest are inspectable |
| TWN-0713 | Complete Core Dashboard exit review | Review | Standard | Dashboard | Critical | Backlog | TWN-0701 through TWN-0712 | Role and entitlement tests plus phone/desktop evidence cover every Phase 1 owner/staff workflow |

## 11. Milestone 8 - Standard Analytics

**Epic:** Produce trusted store-local operational measures without Pro Campaign processing.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0801 | Define versioned commerce and service event taxonomy | Task | Standard | Analytics | High | Backlog | TWN-0506 | View, interest, checkout, purchase, refund, promotion, and module events have documented schemas |
| TWN-0802 | Implement store-scoped event ingestion and idempotency | Task | Standard | Analytics | Critical | Backlog | TWN-0307, TWN-0801 | Replays do not double-count and Customer-level events never cross stores |
| TWN-0803 | Implement hourly projections and store-local daily close | Task | Standard | Analytics | High | Backlog | TWN-0306, TWN-0802 | Provisional and finalized totals are distinguishable and timezone-correct |
| TWN-0804 | Implement revenue, units, and average-value measures | Task | Standard | Analytics | High | Backlog | TWN-0608, TWN-0802 | Measures reconcile to confirmed Transaction records and expose definitions |
| TWN-0805 | Implement commerce funnel and repeat-purchase measures | Task | Standard | Analytics | High | Backlog | TWN-0506, TWN-0802 | Metric definitions are inspectable and results reconcile to Interaction Events and Transactions |
| TWN-0806 | Test Standard entitlement, reconciliation, late events, and partial failures | Review | Standard | Analytics | Critical | Backlog | TWN-0803 through TWN-0805, TWN-0809 through TWN-0812 | Standard has no Campaign execution/attribution interface and analytics failure cannot block commerce |
| TWN-0807 | Build Standard operational analytics dashboard | Task | Standard | Dashboard | High | Backlog | TWN-0702, TWN-0804, TWN-0805 | Owners can inspect reconciled operational measures and definitions without Campaign controls or attribution |
| TWN-0808 | Complete Standard Analytics exit review | Review | Standard | Analytics | Critical | Backlog | TWN-0801 through TWN-0807, TWN-0809 through TWN-0812 | Event, projection, measure, reconciliation, entitlement, failure-isolation, and dashboard evidence pass |
| TWN-0809 | Implement refund and cancellation measures | Task | Standard | Analytics | High | Backlog | TWN-0608, TWN-0802 | Measures distinguish refund, dispute, failure, and cancellation states and reconcile to Transactions |
| TWN-0810 | Implement stock availability and movement measures | Task | Standard | Analytics | High | Backlog | TWN-0604, TWN-0802 | On-hand, reserved, available, released, and completed movements reconcile to inventory records |
| TWN-0811 | Implement response-time and escalation measures | Task | Standard | Analytics | High | Backlog | TWN-0506, TWN-0802 | Store-local definitions and results reconcile to Interaction, Task, and notification events |
| TWN-0812 | Implement unresolved-Journey and staff-workload measures | Task | Standard | Analytics | High | Backlog | TWN-0506, TWN-0802 | Open state, ageing, assignment, overdue work, and completion reconcile to Journey and Task records |

## 12. Milestone 9 - Multi-Business Validation

**Epic:** Prove the common model supports varied businesses without claiming production completeness.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-0901 | Validate restaurant modifiers, preparation, slots, and substitutions | Review | Standard | Product | Medium | Backlog | TWN-0609 | Synthetic scenario maps cleanly to shared entities plus a documented module extension |
| TWN-0902 | Validate beauty service duration, resources, booking, and no-show | Review | Standard | Product | Medium | Backlog | TWN-0609 | Capacity and booking states preserve shared Transaction invariants |
| TWN-0903 | Validate wholesale quotation, quantity price, validity, and Order conversion | Review | Standard | Product | Medium | Backlog | TWN-0609 | Versioned Quotation acceptance converts exactly once with approved price authority |
| TWN-0904 | Validate construction lead, quotation, project, milestone, change, and progress payment | Review | Standard | Product | High | Backlog | TWN-0609 | Project lifecycle supports BOQ, deposits, change orders, materials, receivables, and audit history |
| TWN-0905 | Review common-model pressure and document required extensions | Decision | Shared | Data | High | Backlog | TWN-0901 through TWN-0904 | No unrelated nullable fields or bypassed invariant remains; extensions are approved before implementation |

## 13. Milestone 10 - Compliance, Recovery, And Pilot Readiness

**Epic:** Satisfy legal, security, recovery, cost, and operational launch gates.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-1001 | Complete processing inventory and controller/processor role matrix | Task | Shared | Legal | Critical | Backlog | TWN-0108 | Each purpose records basis, data, recipients, retention, security, actual role, and unresolved allocation |
| TWN-1002 | Obtain Thai counsel approval for privacy, DPA, marketing, transfer, retention, and export terms | Review | Shared | Legal | Critical | Backlog | TWN-1001, TWN-1011 through TWN-1013, TWN-1017 through TWN-1021 | Written approval or required changes are recorded before real customer data |
| TWN-1003 | Implement verified rights-request intake and workflow routing | Task | Standard | Security | Critical | Backlog | TWN-0407, TWN-1001 | Identity verification, request type, deadlines, systems, decisions, and audit evidence are tracked |
| TWN-1004 | Implement ordinary store-data export and offboarding grace period | Task | Standard | Operations | High | Backlog | TWN-1001, TWN-1003 | Raw records, memory, Tiers, Journeys, Tasks, consent, approved knowledge, and stored customer outputs export without a paid lock; generated files expire safely |
| TWN-1005 | Implement retention schedules and legal holds | Task | Standard | Data | Critical | Backlog | TWN-0408, TWN-1001 | Platform bounds enforce approved minimums/maximums and holds record authority, scope, owner, expiry, and review |
| TWN-1006 | Rehearse backup restore, migration rollback, and credential rotation | Review | Shared | Operations | Critical | Backlog | TWN-0203, TWN-0107 | Recovery objectives are measured and failures have owners and runbooks |
| TWN-1007 | Test duplicate webhooks, partial failures, incident response, and breach timing | Review | Shared | Security | Critical | Backlog | TWN-0307, TWN-0507, TWN-0608 | Tabletop proves fast processor notice and supports the controller's 72-hour assessment deadline |
| TWN-1008 | Run dependency, secret, performance, and plan-cost reviews | Review | Shared | Operations | High | Backlog | TWN-0610, TWN-0708, TWN-0806, TWN-0807 | No critical/high finding remains and per-store/conversation cost is measured at proposed limits |
| TWN-1009 | Complete independent architecture, code, security, and specification review | Review | Shared | Security | Critical | Backlog | TWN-1002 through TWN-1008 | No unresolved release-blocking finding and all accepted risks have owners |
| TWN-1010 | Run pilot acceptance and obtain product/technical sign-off | Review | Standard | Operations | Critical | Backlog | TWN-0207, TWN-0313, TWN-0412, TWN-0512, TWN-0617, TWN-0713, TWN-0808, TWN-0905, TWN-1009, TWN-1014, TWN-1015, TWN-1022, TWN-1023 | All Phase 1 criteria pass with no unowned alert or manual step |
| TWN-1011 | Draft layered Thai privacy notices and consent/objection language | Task | Shared | Legal | Critical | Backlog | TWN-1001 | Customer, staff, owner, memory, payment, analytics, and marketing notices are purpose-specific and channel-appropriate |
| TWN-1012 | Create subprocessor register, transfer schedule, and provider-change control | Task | Shared | Legal | Critical | Backlog | TWN-1001 | Providers, locations, purposes, safeguards, notice process, and owner objections are current and reviewable |
| TWN-1013 | Complete and document DPO appointment assessment | Decision | Shared | Legal | High | Backlog | TWN-1001 | Decision cites actual monitoring and processing facts, reviewer, date, trigger for reassessment, and counsel question |
| TWN-1014 | Implement access, portability, and correction fulfilment | Task | Standard | Security | Critical | Backlog | TWN-1003, TWN-1004 | Verified requests return or correct scoped data across active systems with completion evidence |
| TWN-1015 | Implement verified deletion fulfilment | Task | Standard | Security | Critical | Backlog | TWN-1003, TWN-1005, TWN-1022 | Deletion propagates to active systems, indexes, queues, objects, and suppression-safe tombstones subject to legal holds |
| TWN-1016 | Implement paid value-added summary export as a separate service | Task | Custom B2B | Operations | Medium | Backlog | TWN-1004 | Pricing gates only newly commissioned analysis; existing records, memories, Tiers, scores, summaries, and other stored customer outputs remain available without purchase |
| TWN-1017 | Draft Store agreement and controller-processor DPA | Task | Shared | Legal | Critical | Backlog | TWN-1001 | Instructions, roles, security, subprocessors, assistance, deletion/return, audit, incident, and liability terms are reviewable |
| TWN-1018 | Draft approved retention and deletion schedule | Task | Shared | Legal | Critical | Backlog | TWN-1001 | Each data class records purpose, authority, minimum, maximum, trigger, hold handling, and deletion method |
| TWN-1019 | Draft incident and personal-data-breach procedure | Task | Shared | Legal | Critical | Backlog | TWN-1001 | Detection, containment, evidence, processor notice, 72-hour assessment support, communication, and ownership are defined |
| TWN-1020 | Complete direct-marketing lawful-basis and channel assessment | Decision | Shared | Legal | Critical | Backlog | TWN-1001 | LINE consent, objection, suppression, analytics use, Tier use, and Pro Campaign conditions have counsel questions and owners |
| TWN-1021 | Draft export, suspension, termination, and offboarding terms | Task | Shared | Legal | High | Backlog | TWN-1001 | Ordinary export, paid generated analysis, grace period, deletion, legal holds, and service termination are distinguished |
| TWN-1022 | Implement deletion propagation jobs and evidence | Task | Standard | Data | Critical | Backlog | TWN-1005 | Database, objects, indexes, caches, queues, and backup expiry produce verifiable completion or exception evidence |
| TWN-1023 | Implement restriction, consent withdrawal, and objection fulfilment | Task | Standard | Security | Critical | Backlog | TWN-1003, TWN-1005 | Processing and outbound contact stop at the correct scope while legally required records remain protected and auditable |

## 14. Post-Phase-1 Milestone 11 - Pro Campaigns And Intelligence

**Epic:** Add approved proactive sales and advanced BI only after the transition gate.

| ID | Task | Type | Plan | Area | Priority | Status | Depends On | Acceptance |
|---|---|---|---|---|---|---|---|---|
| TWN-1100 | Approve separate Pro Campaign and intelligence scope | Decision | Pro | Product | Critical | Backlog | TWN-1010, explicit product-owner approval | Scope, pricing boundary, legal conditions, success measures, and launch authorization are recorded before implementation |
| TWN-1101 | Implement Pro entitlement for Campaign and intelligence interfaces | Task | Pro | Platform | Critical | Backlog | TWN-1100 | Server-side gates prevent Standard drafting, scheduling, sending, personalization, and attribution |
| TWN-1102 | Implement Campaign consent, objection, suppression, quiet hours, caps, and cooldown | Task | Pro | Campaign | Critical | Backlog | TWN-1101, TWN-1002 | Store/purpose/Channel consent is enforced and STOP suppresses scheduled and active delivery immediately |
| TWN-1103 | Implement Campaign draft, commercial envelope, and owner approval | Task | Pro | Campaign | Critical | Backlog | TWN-1101, TWN-0504 | Tawan cannot change approved products, prices, dates, audience rules, budget, or limits |
| TWN-1104 | Implement eligible-audience selection and Campaign scheduler | Task | Pro | Campaign | Critical | Backlog | TWN-1102, TWN-1103 | Ineligible, suppressed, capped, out-of-window, and expired Customers are excluded before scheduling |
| TWN-1105 | Implement Campaign result tracking and inspectable attribution | Task | Pro | Analytics | High | Backlog | TWN-0802, TWN-1104 | Attribution window, reason, event path, and reconciliation are visible |
| TWN-1106 | Implement RFM and owner-defined Customer segmentation | Task | Pro | Analytics | High | Backlog | TWN-0806, TWN-1101 | Outputs record version, evidence window, explanation, store scope, and insufficient-data state |
| TWN-1107 | Implement product affinity and basket recommendations | Task | Pro | Analytics | High | Backlog | TWN-0806, TWN-1101 | Evidence is inspectable and recommendations never perform automatic price, stock, or Campaign actions |
| TWN-1108 | Implement anonymous benchmark export and re-identification safeguards | Task | Pro | Security | Critical | Backlog | TWN-1002, TWN-1101 | No Customer identifiers/free text leave stores; thresholds, suppression, outliers, and review are recorded |
| TWN-1109 | Test Pro Campaign safety, recipient consent, entitlement, and recommendation evidence | Review | Pro | Security | Critical | Backlog | TWN-1102 through TWN-1108, TWN-1111 through TWN-1118 | Standard denial, opt-out, caps, expiry, idempotency, sensitive-trait exclusion, and explanations pass |
| TWN-1110 | Run owner-approved synthetic Campaign and Pro intelligence acceptance | Review | Pro | Campaign | Critical | Backlog | TWN-1109 | Outcomes reconcile without violating contact policy and every commercial action remains human-approved |
| TWN-1111 | Implement bounded Campaign personalization and idempotent delivery | Task | Pro | Campaign | Critical | Backlog | TWN-1104 | Personalization stays inside the approved envelope; retries never duplicate delivery and every result is recorded |
| TWN-1112 | Implement Customer lifetime-value analysis | Task | Pro | Analytics | High | Backlog | TWN-1106 | Outputs record model version, value window, confidence, explanation, and insufficient-data state |
| TWN-1113 | Implement next-best-offer recommendations | Task | Pro | Analytics | High | Backlog | TWN-1106, TWN-1107 | Recommendations cite eligible products and evidence and cannot schedule or send a Campaign |
| TWN-1114 | Implement demand recommendations | Task | Pro | Analytics | High | Backlog | TWN-0806, TWN-1101 | Results record horizon, evidence, confidence, explanation, and owner action without changing stock or price |
| TWN-1115 | Implement promotion-leakage recommendations | Task | Pro | Analytics | High | Backlog | TWN-0806, TWN-1101 | Results distinguish approved discount effects and record evidence without automatic commercial changes |
| TWN-1116 | Implement operational anomaly recommendations | Task | Pro | Analytics | High | Backlog | TWN-0806, TWN-1101 | Store-local thresholds, evidence, confidence, explanation, and owner disposition are inspectable |
| TWN-1117 | Implement Customer cohort analysis | Task | Pro | Analytics | High | Backlog | TWN-1106 | Cohort definition, evidence window, store scope, comparison, and insufficient-data state are inspectable |
| TWN-1118 | Implement Customer churn-risk analysis | Task | Pro | Analytics | High | Backlog | TWN-1106 | Model version, prediction window, confidence, explanation, consent limits, and owner disposition are inspectable |

## 15. Current Execution Order

1. Complete `TWN-0005` after explicit GitHub push approval.
2. Complete `TWN-0006` and verify Markdown links with the friend/AI account.
3. Complete `TWN-0007` using the Notion API or a stable authenticated session; update existing tasks instead of creating duplicates.
4. Start `TWN-0101`; do not start production implementation before discovery.
5. Execute Milestones 2 through 10 in order, allowing only reviewed parallel work with disjoint ownership.
6. Start Milestone 11 only after `TWN-1010` and separate Pro product approval.

## Related Documents

- [Product specification](PRODUCT_SPEC.md)
- [Architecture](ARCHITECTURE.md)
- [Data model](DATA_MODEL.md)
- [Security](SECURITY.md)
- [Decision log](DECISIONS.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Notion import package](notion-import/README.md)
- [Thai PDPA research](../research/2026-08-17-thailand-pdpa-tawan-data.md)
