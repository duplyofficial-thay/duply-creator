<!-- markdownlint-configure-file {"MD024": {"siblings_only": true}} -->

# Tawan Implementation Plan

**Status:** Approved planning baseline; implementation not started

**Updated:** 2026-08-18

**Rule:** No live or paid action is authorized by this plan. Each milestone requires its own reviewed change and verification.

## 1. Objective

Deliver a production-ready Phase 1 Tawan foundation that supports many isolated Store Workspaces, completes one fashion retail journey through LINE, demonstrates the dashboard and analytics, and validates the common model against restaurant, salon, wholesale, and construction scenarios.

## 2. Delivery Principles

- Work in the canonical checkout: `/Users/zhg/Documents/06_Code/Projects/Duply/duply-creator`.
- One agent edits a working tree at a time; branches or worktrees are required for parallel work.
- Read the actual private runtime before assigning files or changing interfaces there.
- Use migrations with rollback; do not treat `schema_template.sql` as sufficient lifecycle management.
- Build deterministic domain logic before wiring an LLM.
- Add the failing test before each risky business rule where practical.
- Use synthetic data until legal and security launch gates pass.
- Log every paid API charge immediately after success and before response parsing.
- Commit each working milestone with its verification evidence.
- Run an independent standards, security, and specification review before completion.

## 3. Workstreams

### Creator kit

Owns registration, creator-facing configuration, commerce schema/migrations, Tawan-owned tools, prompts, documentation, local test fixtures, and provisioning changes.

### Duply runtime

Owns trusted Store Context resolution, role-aware agent dispatch, tool registry, command execution, LINE webhook/media handling, Channel interface, memory/knowledge runtime, reach delivery, idempotency, and shared observability.

### Data platform

Owns Supabase projects, schema roles, migrations, protected objects, backups, retention jobs, shared anonymous aggregates, and restore procedures.

### Dashboard

Owns Store Owner/Staff authentication, operational pages, approvals, configuration, analytics, and rights/export workflows. Its repository and deployment target must be verified before implementation.

### Legal and operations

Owns Thai counsel review, contracts, privacy notices, marketing basis, retention approval, subprocessors, incident procedure, support process, pricing, and customer onboarding.

## 4. Milestone 0 - Documentation Baseline

### Deliverables

- Canonical glossary and Tawan documentation.
- Older 2026-08-05 draft marked superseded.
- Thai PDPA research retained with authoritative citations.
- Known private-platform assumptions called out explicitly.

### Exit criteria

- Internal links pass.
- No contradictory Phase 1, tenancy, payment, marketing, or export claims remain in active Tawan docs.
- Independent documentation review completed.
- Documentation-only commit created without unrelated files.

## 5. Milestone 1 - Runtime And Data Discovery

This milestone is read-only until a proposed integration change is approved.

### Required access

- `duply-agents` runtime repository;
- `duply-astro` or actual Supabase migration repository;
- non-production Supabase project and schema conventions;
- current LINE webhook and media contracts;
- dashboard repository or decision to create one;
- cost-ledger interface;
- deployment and backup procedures.

### Audit questions

1. How does the webhook map LINE destination to Duple and schema today?
2. How should each separately provisioned Tawan Instance/Duple load the shared Tawan archetype implementation and per-store configuration without copying code?
3. What is the real agent-dispatch interface and role source?
4. What are the real knowledge table, vector, ingestion, and retrieval contracts?
5. Where are raw messages stored and how are they expired?
6. How are tool writes authorized and made idempotent?
7. How are inbound images validated and passed to models or tools?
8. How are outbound images and Flex messages delivered?
9. What migration runner and rollback process are available?
10. What are the cache, queue, object-storage, logging, and backup tenancy controls?
11. Which paid APIs are called and how does the cost ledger record them?
12. Which repository should own the dashboard and anonymous analytics pipeline?

### Deliverables

- Verified context map of repositories and runtime ownership.
- Verified one-to-one provisioning contract from Tawan Instance/Duple to Store Workspace, schema, role, and Channel identity.
- Interface notes for Store Resolver, Channel, commands, tools, knowledge, memory, and notifications.
- Gap report against [ARCHITECTURE.md](ARCHITECTURE.md).
- Revised file-level plan with no guessed private paths.
- Threat-model review with the Duply technical owner.

### Exit criteria

- Every private-platform dependency has an owner and verified interface.
- Dashboard ownership is known.
- No unresolved architectural blocker is hidden inside creator-kit work.
- Product owner approves any proposed platform-level change before editing begins.

## 6. Milestone 2 - Test Harness And Migration Foundation

### Creator-kit changes

- Add a documented Python test command using the repository's agreed toolchain.
- Add isolated unit tests for provisioning and schema selection.
- Add a migration directory and migration manifest for commerce changes.
- Add a disposable Postgres verification path.
- Add synthetic fixtures for two Store Workspaces and all five demo businesses.
- Add documentation and checks for secrets and environment variables.

### Initial tests

- schema block selection for finance, lifestyle, and commerce;
- migration apply and rollback on disposable Postgres;
- schema-role negative access between two stores;
- duplicate migration execution;
- invalid registration and configuration;
- no real credentials or personal data in fixtures.

### Exit criteria

- Fresh database can be created, migrated, rolled back, and recreated locally.
- Existing finance/lifestyle provisioning tests remain green.
- Two synthetic stores cannot access one another.

## 7. Milestone 3 - Store Workspace And Access Foundation

### Deliverables

- Tawan product registration and Store Workspace provisioning model.
- Shared Tawan implementation/configuration mechanism without per-store code forks.
- Trusted Store Resolver in the runtime.
- Store Context propagation through chat, tools, knowledge, memory, cache, queue, and logging.
- Store Owner, Store Staff, Customer, and Platform Administrator access model.
- Staff Capability grants and audited support sessions.
- Store settings for timezone, currency, closing time, reservation expiry, notifications, and review cadence.

### Verification

- Cross-store read/write/cache/vector/object attempts fail.
- Customer conversation cannot claim an owner or staff Capability.
- Revoked staff access stops immediately.
- Support session expires and records actor, reason, target, and actions.
- Existing Thay, Khun, and Dom routing remains unchanged.

### Exit criteria

- Isolation tests pass through every implemented interface.
- Independent security review has no high-severity open finding.

## 8. Milestone 4 - Knowledge Ingestion And Customer Memory

### Ingestion

- Protected source upload and approved-URL import.
- File validation, malware scanning, OCR/parser adapters, checksum, and source record.
- Knowledge Candidate extraction with provenance, confidence, scope, effective/expiry dates, and conflict detection.
- Review, reject, approve, publish, supersede, and expire workflows.
- Knowledge editors can prepare and recommend; only the Store Owner can publish permanent Store Knowledge.
- Daily digest and configurable weekly/monthly review.
- Templates for stores without source data.

### Customer Memory

- Explicit versus inferred memory with source, confidence, dates, confirmation, model/rule version, and expiry.
- Customer correction and deletion.
- Customer Tier rules, Tawan recommendation, and Store Owner override.
- Purpose-specific raw message expiry.
- Sensitive-data classification and exclusion from scoring/marketing.

### Verification

- Prompt-injection content cannot publish or call a tool.
- Conflicting price or policy creates review work.
- Expired temporary fact is not retrieved.
- Unconfirmed inference expires.
- Customer correction supersedes prior value and changes downstream context.
- Store A source, vectors, or memories never appear in Store B.

### Exit criteria

- Published knowledge always has source and Approval.
- Rights and retention tests pass for implemented data classes.

## 9. Milestone 5 - Sales Journey, Tasking, And Approvals

### Deliverables

- Sales Journey and Interaction Event model.
- Task types and common state machine.
- Assignment, due time, priority, deduplication, escalation, and history.
- Approval model for knowledge, price, Campaign, payment, staff, and sensitive exports.
- Dashboard notification plus LINE owner/staff notification adapter.

### Verification

- Repeated uncertainty creates one actionable Task, not duplicates.
- Invalid status transitions fail without partial update.
- Capability controls assignment and resolution.
- Quiet hours delay non-critical LINE alerts.
- Critical high-value or payment Tasks escalate according to store settings.

### Exit criteria

- A Customer inquiry can create, assign, resolve, and audit a human follow-up without an Order.

## 10. Milestone 6 - Retail Commerce And Manual Payment

### Deliverables

- Catalog Items, relational variants, inventory balances, price rules, and reservations.
- Deterministic price precedence with calculation snapshot.
- Order and line-item snapshots.
- Atomic stock/capacity reservation and configured expiry.
- PromptPay QR adapter.
- LINE inbound payment-media path.
- Protected evidence storage, exact hash, normalized fingerprint, bank-reference checks, extracted candidate fields, and manual payment-review Task.
- Fulfilment and completion states.

### Verification

- customer-specific, Campaign, Tier, wholesale, and standard price precedence;
- expired or revoked special price rejected;
- last-unit concurrency permits only one reservation;
- repeated create command returns the same Order;
- reservation expiry releases stock exactly once;
- duplicate evidence blocks owner approval until a separately audited owner-only false-positive resolution, and one confirmed bank reference cannot pay two Transactions or be overridden;
- customer cannot mark payment paid;
- staff without `payment_review` cannot inspect or recommend;
- staff with `payment_review` still cannot make the final paid decision;
- only the Store Owner can approve or reject the final Phase 1 payment decision;
- no public slip URL or sensitive log output;
- refund/dispute states remain distinct.

### Exit criteria

- Fashion demo completes accurate question, product selection, variant, Order, QR, slip, payment-review Task, fulfilment, and completion through staging LINE.
- Paid API calls, if any, are recorded in the cost ledger at success time.

## 11. Milestone 7 - Core Dashboard

### Deliverables

- Overview action queue and operational measures.
- Customers, Sales Journeys, Transactions, Tasks, Catalog/Services, Tawan Brain, Analytics, and Settings areas.
- A subscription-aware navigation boundary that does not expose Campaign execution to Standard stores.
- Customer Memory correction, Customer Tier override, consent, special price, and audit views.
- Knowledge Candidate review and conflict comparison.
- Responsive phone and desktop layouts.
- Accessible loading, empty, error, expired-session, unauthorized, and retry states.

### Verification

- Role/Capability page and action matrix.
- Store switch and direct URL isolation.
- No private evidence URL in browser history or client logs.
- Mobile screenshots for owner approval workflows.
- Real staging data demonstration, using synthetic identities.
- Browser automation for the most important owner and staff journeys.

### Exit criteria

- A non-technical Store Owner can operate the full fashion demo from a phone without database access.

## 12. Milestone 8 - Standard Analytics

### Deliverables

- normalized view, interest, checkout, purchase, refund, and promotion events;
- hourly operational aggregates;
- store-local daily close;
- revenue, Transaction count, units, average value, refunds, cancellations, funnel, repeat rate, unresolved Journeys, response/escalation, top items, stock movement, and staff workload.

### Verification

- revenue reconciles to completed/refunded Transactions;
- hourly projection and daily close are distinguishable;
- Standard Store Workspaces cannot access Campaign drafting, scheduling, delivery, or attribution interfaces.

### Exit criteria

- Standard operational measures are store-isolated, reproducible, and reconcilable without Campaign processing.

## 13. Milestone 9 - Multi-Business Validation

Use synthetic scenarios, not production claims.

### Restaurant or bakery

- modifiers;
- preparation time;
- pickup/delivery slot;
- sold-out item and substitution.

### Beauty salon

- service duration;
- staff/resource availability;
- booking, reschedule, cancellation, and no-show.

### Wholesale

- versioned Quotation;
- quantity pricing;
- approval and validity;
- accepted quote conversion to Order.

### Construction

- lead and site visit;
- quotation and bill of quantities;
- accepted Project;
- milestones, change orders, material variance, deposit, progress payment, and overdue receivable.

### Exit criteria

- Shared Customer, Journey, Task, Approval, Transaction, payment, and analytics models represent all scenarios without unrelated nullable fields or bypassing invariants.
- Required module extensions are documented before implementation.

## 14. Milestone 10 - Compliance, Recovery, And Pilot Readiness

### Legal and privacy

- Thai counsel approves required documents and bases.
- Processing inventory and subprocessor list complete.
- Foreign AI/cloud transfer mechanism approved.
- Rights request, ordinary export, paid value-added export, offboarding, and deletion tested.

### Reliability and security

- backup restore rehearsal;
- migration rollback rehearsal;
- credential rotation exercise;
- duplicate webhook and partial-failure tests;
- breach-response tabletop with internal processor deadline and 72-hour controller deadline;
- independent code, architecture, security, and specification review;
- dependency and secret scans;
- performance and cost test at proposed plan limits.

### Pilot exit criteria

- All Phase 1 acceptance tests pass.
- No unresolved critical/high security finding.
- No unowned operational alert or manual step.
- Cost per store and per conversation is measured.
- Product owner and Duply technical owner approve the pilot release.

## 15. Post-Phase-1 Milestone 11 - Pro Campaigns And Intelligence

This Pro-only milestone is not a Phase 1 pilot dependency. It starts only after the Phase 1 transition gate is met and receives separate product approval.

### Deliverables

- Campaign draft, review, Approval, schedule, send, complete, and analysis workflow;
- permission by Store Workspace, Customer, purpose, and Channel;
- immediate opt-out suppression, quiet hours, caps, cooldowns, expiry, and idempotent delivery;
- owner-fixed commercial envelope with Tawan audience selection and personalization;
- inspectable Campaign attribution;
- RFM and configurable segmentation;
- lifetime value and cohort retention;
- churn and next-best-offer recommendations;
- affinity and basket analysis;
- demand forecasting;
- promotion effectiveness and discount leakage;
- anomaly alerts;
- approved Anonymous Benchmarks.

### Safety requirements

- minimum evidence threshold and insufficient-data state;
- model/rule version, evidence window, confidence, and explanation;
- no sensitive traits or prohibited proxies;
- no automatic price, stock, or Campaign action;
- Customer-level data remains store-local;
- anonymous export passes suppression and re-identification checks.

### Exit criteria

- An Owner-approved synthetic Campaign produces measurable, reconcilable outcomes without violating contact policy.
- Recommendations can be traced to store-local evidence and require human action.
- Shared benchmark dataset contains no linkable Customer or store-confidential small cells.

## 16. Documentation Deliverables During Implementation

- Update [DECISIONS.md](DECISIONS.md) whenever a shipped decision changes the baseline.
- Keep [DATA_MODEL.md](DATA_MODEL.md) aligned with migrations.
- Keep [ARCHITECTURE.md](ARCHITECTURE.md) aligned with verified repository ownership and interfaces.
- Record creator-facing platform changes in `PATCH-NOTES.md` and relevant guides.
- Update `CHECKLIST.md` for Tawan provisioning and operations.
- Maintain API/tool documentation from the authoritative registry.
- Generate release notes only for real shipped milestones.

## 17. Immediate Next Step After This Documentation Milestone

Request read-only access to the private Duply runtime/data repositories and schedule a short technical review with the Duply owner. Perform Milestone 1 discovery before writing production code. The first proposed code change should then be a test-harness and migration-foundation milestone, not the full commerce feature in one branch.

## Related Documents

- [Product specification](PRODUCT_SPEC.md)
- [Architecture](ARCHITECTURE.md)
- [Data model](DATA_MODEL.md)
- [Security](SECURITY.md)
- [Decision log](DECISIONS.md)
- [Task breakdown](TASK_BREAKDOWN.md)
