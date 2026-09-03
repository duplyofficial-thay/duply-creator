# Tawan Security And Privacy

**Status:** Required control baseline; not evidence of implementation

**Updated:** 2026-08-18

This document translates the approved product decisions and Thai PDPA research into engineering requirements. It is not a legal opinion. Thai counsel must approve the legal documents and processing positions before production use of real customer data.

## 1. Security Objectives

1. A Store Workspace cannot read, write, retrieve, cache, search, or infer another store's operational or customer data.
2. Tawan cannot authorize itself through model output or conversation text.
3. Price, stock, payment, policy, consent, and commercial state remain correct under retries, concurrency, and partial failure.
4. Customer data is processed only for documented purposes, retained only as justified, and available for applicable rights workflows.
5. Support and Platform Administrator access is exceptional, time-limited, reason-coded, and auditable.
6. Security incidents can be detected, contained, investigated, and escalated early enough for the controller to meet legal deadlines.

## 2. Responsibility Model

The expected starting position is:

- Store: controller for customer service, Store Knowledge, Customer Memory, Customer Tiers, Transactions, Tasks, Campaigns, and store analytics.
- Duply: processor when operating Tawan on documented store instructions.
- Duply: separate controller for narrow independently determined purposes such as account administration, billing, platform security, and any approved identifiable product telemetry.
- Duply and store roles may differ for a specific activity based on actual decisions, regardless of contract labels.

Required legal artifacts include a privacy notice, store agreement, data-processing agreement, retention schedule, subprocessor list, cross-border mechanism, rights procedure, incident procedure, and direct-marketing assessment.

See [Thai PDPA research](../research/2026-08-17-thailand-pdpa-tawan-data.md) for sources and counsel questions.

## 3. Threat Model

| Threat | Example | Required response |
|---|---|---|
| Cross-store data leak | Store A prompt or query retrieves Store B catalog or Customer Memory | Schema-scoped credentials, trusted Store Context, cache/vector isolation, adversarial isolation tests |
| Prompt-based privilege escalation | Customer says they are staff or asks the model to call an owner tool | Authorization in deterministic code using authenticated identity and capability |
| Hallucinated commercial fact | Model invents stock, price, discount, policy, or delivery time | Approved-source retrieval, validation, fail to Task, no model-direct write |
| Duplicate financial action | LINE or network retry creates two Orders or payment transitions | Unique idempotency key, atomic transition, replay returns prior result |
| Stock race | Two Customers reserve the last unit | Atomic reservation/availability procedure and non-negative invariant |
| Malicious upload | Document contains malware, prompt injection, secrets, or another store's data | File scanning, type/size limits, protected storage, content isolation, review before publish |
| Knowledge poisoning | Uploaded or inferred text silently changes a price or policy | Knowledge Candidate staging, provenance, conflict review, authorized publication |
| Payment evidence exposure | Slip image is public or retained indefinitely | Private object storage, short signed access, strict capability, retention and deletion |
| Marketing abuse | Campaign ignores opt-out or sends too frequently | Immediate suppression, consent ledger, quiet hours, cooldown, idempotent delivery |
| Support misuse | Platform Administrator browses store data without need | Just-in-time support session, reason, expiry, least privilege, audit and review |
| Re-identification | Hashed LINE IDs are used as anonymous benchmark keys | No linkable Customer keys, aggregation thresholds, suppression, risk testing |
| Model/subprocessor disclosure | Personal data is sent to an unapproved foreign provider | Data-flow inventory, minimization, DPA, transfer mechanism, configuration and logs |
| Secret exposure | Tokens or credentials enter Git, prompts, logs, or exports | Secret manager/env files, scanners, redaction, rotation, least privilege |

## 4. Isolation Controls

### Database

- Separate Postgres schema and native role per Store Workspace.
- Role has no access to other Store Workspace schemas.
- Runtime chooses from preconfigured credential references after Store Context resolution.
- No arbitrary schema name from a request, prompt, URL, or tool argument.
- Migrations include explicit privileges and automated negative-access tests.
- Shared platform tables expose only fields required for routing and administration.

### Cache, search, vectors, queues, and objects

- Keys and namespaces begin with an internal Store Workspace identifier.
- Retrieval queries require Store Context filters enforced inside the module.
- Vector indexes do not combine stores unless they provide native, tested isolation equivalent to separate indexes.
- Payment evidence and uploaded sources use private object paths and short-lived signed access.
- Queue messages carry an internal Store Workspace identifier signed or derived by trusted runtime code.

### Analytics

- Store Analytics remain inside the store boundary where practical.
- Shared export removes direct identifiers, free text, rare categories, and linkable Customer keys.
- Minimum cohort thresholds and small-cell suppression are mandatory.
- Re-identification tests and export-version records are required.
- Cross-store identifiable or pseudonymous model training is disabled by default.

## 5. Authentication And Authorization

- Dashboard authentication must use supported Duply identity; no anonymous owner routes.
- Multi-factor authentication is required for Platform Administrators and should be offered to Store Owners.
- Authorization checks Store Workspace membership plus Capability for every operation.
- Owner-only actions include staff capability grants, exceptional price authority, Campaign approval, permanent Store Knowledge publication, final Phase 1 payment decisions, retention changes, and sensitive exports.
- `knowledge_editor` and `payment_review` allow preparation, inspection, and recommendation; they do not confer owner-only final approval.
- Staff onboarding cannot rely on display-name matching alone. Ambiguous matches require a stronger identifier and explicit owner decision.
- Support access uses a separate just-in-time grant with target store, reason, duration, actor, ticket or incident reference, and audit log.
- Database and tool authorization remain effective even if the model is compromised.

## 6. AI Safety Controls

- The model has no direct database credentials.
- Tools expose narrow validated commands rather than generic SQL, URLs, or table mutation.
- Read and action tools are distinct.
- Action tools validate authorization, state transition, idempotency, price authority, and input bounds.
- Tool results use structured status codes internally. User-facing text is rendered separately.
- Prompt content, uploaded documents, Store Knowledge, and Customer messages are untrusted data, not executable instructions.
- Retrieval returns provenance and validity; stale or conflicting critical facts cannot be used as authoritative.
- Sensitive personal traits are blocked from segmentation and Campaign targeting.
- Model and rule versions are recorded for Customer Memory inferences, Knowledge Candidates, and BI recommendations.

## 7. Data Protection Controls

### Purpose and minimization

Maintain a processing inventory for:

- transaction and service delivery;
- Customer Memory and personalization;
- direct marketing;
- Store Analytics;
- Duply platform administration and security;
- Anonymous Benchmarks.

Each activity records purpose, lawful basis, data categories, recipients, retention, security, and controller/processor role. “Future analytics” is not a sufficient standalone purpose.

### Retention

Retention is policy-driven by data class and purpose:

- raw conversation content: short, store-configurable, justified period;
- unconfirmed inference: short expiry;
- approved Customer Memory: until stale, corrected, deleted, relationship end, or purpose end;
- Transaction and tax evidence: exact legally required period confirmed by counsel;
- consent, objection, security, and rights evidence: enough to demonstrate compliance and resolve claims;
- Anonymous Benchmarks: retained only after robust de-identification.

Platform policy sets counsel-approved minimums, maximums, and defaults. Store Owners choose only inside those bounds; they cannot shorten statutory minimums, extend raw-message storage beyond the platform maximum, or remove a valid legal hold.

Deletion reaches primary tables, replicas, caches, vectors, object storage, exports, logs, and backups through deletion or documented backup-expiry controls. Legal hold is explicit and scoped.

### Rights

Provide verified workflows for access, machine-readable portability where applicable, correction, objection, restriction, deletion or anonymization, and consent withdrawal. Direct-marketing objection suppresses immediately.

Ordinary store export includes existing store-controlled Customer, operational, memory, tier, Journey, Transaction, Task, consent, Campaign, Catalog, and approved knowledge records. Paid offerings may cover newly commissioned BI, migration, cleaning, consulting, and proprietary anonymous benchmarks, not the exercise of legal rights.

### Sensitive data

- Detect and classify accidental sensitive content.
- Do not infer health, disability, religion, political opinion, sexual behaviour, biometrics, criminal history, or proxies for Customer Tier or marketing.
- Redact or quarantine sensitive content before optional model or analytics use.
- Obtain counsel-approved explicit consent or exception for any necessary sensitive processing.
- Define special handling for minors before serving a business likely to involve them.

## 8. Direct Marketing

Outbound Campaign execution is enabled only for Pro Store Workspaces after the Phase 1 transition gate. Consent, objection, and immediate suppression controls remain shared foundations and must already be enforced for any permitted customer communication.

- Permission and objection are scoped by Store Workspace, Customer, purpose, and Channel.
- Transaction processing and marketing permission are separate.
- Record notice wording/version, source, actor, time, and evidence.
- `STOP` and Thai equivalents take effect immediately across scheduled and active deliveries.
- Enforce frequency caps, quiet hours, Campaign expiry, and cooldown.
- Store Owner approves commercial terms and audience rules.
- Tawan may personalize only within approved constraints.
- Customer-specific price does not become a general Campaign price.

## 9. Upload And Knowledge Security

- Permit only approved types and bounded sizes.
- Validate content type from bytes, not filename alone.
- Scan files before parsing.
- Store originals privately with checksum, uploader, source, and retention class.
- Fetch URLs only from approved domains using SSRF-safe networking and response limits.
- Treat document instructions as content; they cannot override system policy or authorize tools.
- Parse and extract in an isolated worker with no store credentials beyond the target Store Context.
- Publish only reviewed Knowledge Candidates.
- Never place credentials, private keys, tokens, or payment identifiers into Store Knowledge.

## 10. Payment And Transaction Integrity

- PromptPay identifier is secret configuration, never committed.
- Payment evidence uses protected storage, an exact hash, a normalized visual fingerprint, and bank-reference/time checks where available.
- Duplicate checks are Store Workspace-wide. An unresolved duplicate conflict blocks owner approval; a probable fingerprint false positive requires a separate owner-only, reason-coded resolution, and one confirmed bank transaction reference can never pay two Transactions or be overridden.
- Phase 1 AI extraction and staff review are advisory; the Store Owner makes the final paid decision.
- Payment amount, currency, Transaction, reference, and review state are validated in deterministic code.
- Allowed transitions are atomic and append to history.
- Repeated webhook, message, or tool execution with the same idempotency key returns the first result.
- Refund and dispute permissions are separate from payment-review permission.
- Logs redact bank data and evidence URLs.

## 11. Infrastructure And Secrets

- Secrets live in platform secret management or local ignored env files, never Git.
- Rotate LINE, database, model, storage, and tunnel credentials after suspected disclosure and on a documented schedule.
- Production, staging, and development credentials and data are separate.
- Demo environments use synthetic personal and payment data.
- Backups are encrypted, access-controlled, retention-bound, and restore-tested.
- Dependency and container scanning run before release.
- Paid API calls log cost immediately after success and before downstream parsing.

## 12. Logging And Audit

Audit events include:

- authentication and failed access;
- role and Capability changes;
- Platform Administrator support sessions;
- permanent Store Knowledge publication;
- price, discount, Campaign, payment, and staff approvals;
- Customer Memory correction and deletion;
- consent and objection;
- exports and rights requests;
- schema migration and retention jobs;
- incident actions.

Logs contain correlation identifiers and Store Workspace identifiers but minimize Customer content. Audit access is restricted and itself logged.

## 13. Incident Response

The controller may need to notify the PDPC without delay and, where feasible, within 72 hours after awareness of a qualifying breach. High-risk incidents may also require prompt notice to affected people. Duply's internal processor notification target must be materially shorter than 72 hours.

Required capability:

1. detection and alerting;
2. incident ownership and severity;
3. containment and credential rotation;
4. affected Store Workspace and data analysis;
5. risk assessment and evidence preservation;
6. rapid store/controller notification;
7. PDPC and Customer notification templates;
8. remediation and post-incident review;
9. incident register even when external notification is not required.

## 14. Verification

### Mandatory automated tests

- cross-store read/write attempts for every module interface;
- authorization matrix by role and Capability;
- arbitrary schema and identifier injection;
- prompt-based tool escalation;
- stock and capacity concurrency;
- idempotent Order, payment, Campaign, and notification replay;
- price precedence and expired Approval rejection;
- consent withdrawal and immediate Campaign suppression;
- retention and deletion propagation;
- Knowledge Candidate conflict and publication gating;
- protected media access;
- export scope and Customer-rights verification;
- anonymous benchmark small-cell suppression.

### Mandatory operational exercises

- backup restore;
- credential rotation;
- cross-store isolation probe against staging;
- failed Channel and database recovery;
- duplicate webhook replay;
- breach-response tabletop against the 72-hour deadline;
- store offboarding export and deletion rehearsal.

## 15. Production Blockers

- Thai counsel sign-off is absent.
- Private runtime interfaces and data flows are unverified.
- Cross-store isolation tests are incomplete.
- LINE media ingestion/delivery is unverified.
- Rights, retention, export, and deletion workflows are incomplete.
- Incident, backup, and restore exercises are incomplete.
- Paid API cost logging is absent.
- Any high-severity independent review finding remains unresolved.

## Related Documents

- [Product specification](PRODUCT_SPEC.md)
- [Architecture](ARCHITECTURE.md)
- [Data model](DATA_MODEL.md)
- [Thai PDPA research](../research/2026-08-17-thailand-pdpa-tawan-data.md)
