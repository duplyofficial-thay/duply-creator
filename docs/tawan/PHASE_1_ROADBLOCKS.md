# Tawan Phase 1 Roadblocks And Feature Plan

**Status:** Working handoff for Duply platform coordination

**Updated:** 2026-08-20

## Purpose

This document summarizes what must be prepared by the Duply platform team so Phase 1 Tawan work does not stay blocked. It also groups the full plan into phases and feature areas so a teammate can coordinate roadblocks without reading the full chat history.

## Current Engineering Status

`TWN-0201` has started the local test foundation in the creator-kit repository.

This is an intentional unblocking exception while `TWN-0108` remains blocked. It is limited to local, no-network, no-secret creator-kit tests and does not authorize runtime, database, LINE, or paid-service implementation before `TWN-0104` through `TWN-0107` are answered by Duply platform.

Supported local commands:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
PYTHONPYCACHEPREFIX=/tmp/duply-creator-pycache python3 -m compileall scripts duples
```

Current evidence:

- Unit tests run locally without network or real credentials.
- Script and Duple Python files compile with bytecode cache redirected to `/tmp`.
- Real provisioning still requires `PyYAML`.
- Supabase, LINE, private runtime, backup, queue, and object-storage tests remain blocked until Duply confirms the real interfaces.

## Immediate Blocked Cards

### TWN-0104 - Knowledge, Vector, Memory, And Raw-Message Contracts

**Blocked because:** the creator kit shows logical tables, but the real runtime knowledge and memory retrieval contracts live outside this repository.

Duply platform must provide:

- current knowledge tables and whether `knowledge_entries`, `knowledge_chunks`, or another table is authoritative;
- vector extension and embedding dimensions actually used in production;
- retrieval filters required for store isolation;
- raw message storage location, encryption, retention, expiry, and deletion behavior;
- memory promotion/dream flow and which fields Tawan may read or update;
- existing cross-Duple memory boundaries and any shared tables;
- owner/staff review path for publishing permanent knowledge.

Required output before unblocking:

- table/interface map;
- retention and deletion rules;
- store-boundary proof or known gap;
- owner for each unresolved data contract.

### TWN-0105 - Command Authorization, Idempotency, Cache, Queue, And Object Storage

**Blocked because:** Tawan writes will touch shared subsystems that are not defined in the creator kit.

Duply platform must provide:

- command execution interface and authorization source;
- role/capability model used by runtime tools;
- idempotency key format and replay behavior for writes;
- cache key convention and store isolation policy;
- queue topic/job naming and retry/dead-letter behavior;
- object storage buckets, path conventions, signed URL rules, and retention classes;
- audit log event format for writes, denials, retries, support access, and sensitive actions.

Required output before unblocking:

- one write-contract document;
- tenancy controls for cache, queue, and object storage;
- failure and retry rules;
- test scenarios for duplicate write, revoked access, and cross-store denial.

### TWN-0106 - LINE Media, Flex Message, Image Validation, And Delivery Contracts

**Blocked because:** Phase 1 depends on real LINE OA media and delivery behavior, but those adapters are not in this repo.

Duply platform must provide:

- webhook signature verification and normalized inbound event format;
- LINE destination-to-store mapping inputs;
- text, image, and file size/type limits;
- media download, validation, quarantine, and protected storage flow;
- PromptPay slip handling constraints;
- Flex message template boundaries;
- delivery result, retry, and failure callback behavior;
- staging LINE OA account or agreed simulator for end-to-end testing.

Required output before unblocking:

- inbound and outbound Channel interface;
- media limits and storage policy;
- retry/idempotency rules;
- staging test credentials handled outside Git.

### TWN-0107 - Migration, Rollback, Backup, Restore, And Cost-Ledger Interfaces

**Blocked because:** creator-kit currently has SQL templates/scripts, but not the real migration, backup, restore, or paid-call ledger path.

Duply platform must provide:

- authoritative migration repository and runner;
- migration naming, manifest, apply, rollback, replay, and ordering policy;
- disposable database or local Supabase/Postgres verification path;
- backup and restore owner, command, frequency, recovery objective, and evidence format;
- credential rotation procedure;
- paid API cost-ledger interface and required fields;
- rule that paid calls are ledgered immediately after success and before response parsing.

Required output before unblocking:

- migration/rollback runbook;
- backup/restore runbook;
- cost-ledger contract;
- non-production environment where migration tests may run.

## Roadblocks For Friend To Clear With Duply

1. Confirm all private repositories needed for Phase 1: runtime, data/Supabase migrations, dashboard, deployment, and infrastructure.
2. Give read-only access first; do not provide production secrets in chat or Git.
3. Identify one Duply technical owner for each system: runtime, data, LINE, dashboard, legal/security, operations.
4. Confirm the local verification environment: Python version, test command, local Postgres/Supabase approach, and whether Docker is allowed.
5. Confirm the Tawan Store Workspace isolation pattern: schema-per-store, role-per-store, trusted Store Resolver, and support-session audit.
6. Confirm LINE staging account and whether media/Flex/payment-slip flows can be tested without real customers.
7. Confirm backup, restore, rollback, and credential-rotation commands before database work begins.
8. Confirm cost-ledger API/table and required fields before any paid model/OCR/media analysis call is added.
9. Confirm dashboard repository ownership before dashboard cards begin.
10. Confirm Thai legal owner/counsel review path before customer data, retention, export, marketing, and payment evidence are tested with real data.

## Phase And Feature Summary

### Phase 0 - Source Of Truth And Handoff

Features:

- canonical product, architecture, data, security, decision, and task docs;
- portable handoff skill for Claude/Codex;
- Notion board and Git source alignment;
- stable `TWN-*` task IDs.

Goal:

- no teammate should need chat history to continue the project.

### Phase 1A - Runtime And Data Discovery

Features:

- LINE destination and Store Context verification;
- archetype loading and agent dispatch verification;
- knowledge/vector/memory/raw-message contract verification;
- authorization, idempotency, cache, queue, storage contract verification;
- LINE media/Flex delivery contract verification;
- migration, rollback, backup, restore, and cost-ledger verification;
- repository map and revised file-level plan.

Goal:

- replace assumptions with verified Duply interfaces before production code.

### Phase 1B - Test Harness And Migration Foundation

Features:

- local unit-test command;
- syntax/compile check;
- rollback-capable migration manifest;
- disposable Postgres/Supabase verification;
- two-store synthetic fixtures;
- five-demo-business fixtures;
- registration, archetype, migration replay, and isolation tests.

Goal:

- prove changes locally before touching live Duply runtime.

### Phase 1C - Store Workspace And Access Foundation

Features:

- Tawan registration path;
- shared commerce archetype configuration;
- trusted Store Resolver;
- schema/role isolation per Store Workspace;
- canonical roles: `platform_admin`, `store_owner`, `store_staff`, `customer`;
- staff capabilities;
- audited platform-admin support sessions;
- store settings, subscription boundaries, MFA, rate limits, security monitoring, and secret lifecycle.

Goal:

- make cross-store leakage structurally difficult, not merely prompt-dependent.

### Phase 1D - Knowledge And Customer Memory

Features:

- protected source upload;
- approved URL import with SSRF protection;
- document parsing and Knowledge Candidate extraction;
- owner review, approval, publication, expiry, and supersession;
- daily digest and configurable weekly/monthly review;
- structured Customer Memory with source, confidence, first_seen, last_seen, confirmed_at;
- memory correction, deletion, retention;
- raw-message expiry and structured Interaction Events;
- prompt-injection, knowledge-poisoning, stale-fact, and cross-store retrieval tests;
- onboarding templates and OCR adapter.

Goal:

- Tawan can learn useful store/customer facts without teaching itself unsafe or unapproved claims.

### Phase 1E - Sales Journey, Tasks, Approvals, Tiers, And Notifications

Features:

- store-specific Customer identity;
- Sales Journey lifecycle;
- Task lifecycle, assignment, due time, escalation, and history;
- initial task types and deterministic deduplication;
- owner-only Approval records;
- unauthorized-discount escalation without promise;
- Interaction Event and Task/Approval analytics events;
- Customer Tier rules, recommendation review, and manual override;
- staff/owner notification policy, delivery result, retry, and deduplication.

Goal:

- turn conversations into accountable work and controlled human approvals.

### Phase 1F - Retail Commerce, LINE, And Manual Payment

Features:

- catalog items, variants, stock locations, and availability;
- deterministic price precedence;
- order lifecycle and immutable confirmed line snapshots;
- stock reservation, configurable expiry, and release;
- PromptPay QR generation;
- protected payment evidence storage;
- payment extraction and duplicate evidence blocking;
- manual payment-review task and owner decision;
- fulfilment, completion, refund, dispute, and failure handling;
- LINE webhook verification, inbound media handling, Flex replies, retries, and fail-to-human orchestration.

Goal:

- complete the first fashion/accessories journey: question, product answer, order, QR, slip, owner review, fulfilment, and completed order.

### Phase 1G - Core Dashboard

Features:

- dashboard repository, deployment, and authentication verification;
- subscription-aware navigation and authorization;
- overview and urgent-work queue;
- customer list/profile/journey/history;
- transactions and payment-review views;
- catalog/service management;
- settings and staff access;
- approval and sales-opportunity queues;
- customer memory, tier, and consent controls;
- task, assignment, escalation, and approval-history views;
- Tawan Brain candidate and digest review views;
- responsive, empty, error, retry, and unauthorized states.

Goal:

- give store owners and staff an action-first workspace, especially on mobile.

### Phase 1H - Standard Analytics

Features:

- versioned commerce/service event taxonomy;
- store-scoped event ingestion and idempotency;
- hourly projections and store-local daily close;
- revenue, units, average value, funnel, repeat purchase, refund/cancellation, stock movement, response time, escalation, unresolved journey, and staff workload measures;
- Standard operational analytics dashboard.

Goal:

- provide trusted operational reporting without Pro campaign execution.

### Phase 1I - Multi-Business Validation

Features:

- restaurant modifiers, preparation slots, substitutions;
- beauty services, resources, booking, no-show;
- wholesale quotation, quantity pricing, validity, order conversion;
- construction leads, quotation, project, milestones, change orders, progress payments;
- common-model pressure review.

Goal:

- prove the shared commerce model can expand beyond fashion without pretending every vertical is production-complete.

### Phase 1J - Compliance, Recovery, And Pilot Readiness

Features:

- processing inventory and controller/processor role matrix;
- Thai counsel approval;
- rights request intake and routing;
- ordinary store-data export and offboarding grace period;
- retention schedules and legal holds;
- backup restore, migration rollback, credential rotation rehearsal;
- duplicate webhook, partial failure, incident, and breach timing tests;
- dependency, secret, performance, and plan-cost reviews;
- independent architecture/security/spec review;
- pilot acceptance and sign-off;
- privacy notices, subprocessors, DPO assessment, DPA, retention/deletion, incident procedure, direct-marketing assessment, export/offboarding terms, deletion propagation, consent withdrawal, and objection fulfilment.

Goal:

- become ready for a real pilot without hiding legal, data, security, or recovery risk.

### Phase 2 - Pro Campaigns And Intelligence

Features:

- separate Pro Campaign and intelligence scope;
- Pro entitlement gates;
- campaign consent, objection, suppression, quiet hours, caps, cooldown;
- campaign draft, commercial envelope, owner approval;
- eligible audience selection and scheduler;
- campaign result tracking and attribution;
- RFM and owner-defined segmentation;
- product affinity and basket recommendations;
- anonymous benchmark export and re-identification safeguards;
- bounded personalization and idempotent delivery;
- CLV, next-best offer, demand, promotion leakage, operational anomaly, cohort, and churn-risk analysis.

Goal:

- add proactive sales and business intelligence only after Phase 1 proves safety, consent, and store isolation.

## Recommended Next Work Order

1. Finish and commit `TWN-0201`.
2. Ask Duply platform to answer `TWN-0104` through `TWN-0107` using the checklists above.
3. Start `TWN-0202` migration manifest only after `TWN-0201` is accepted.
4. Start `TWN-0203` only after Duply confirms the disposable database path.
5. Start `TWN-0204` fixtures after the migration structure exists.
6. Start `TWN-0205` after registration fixtures and migration replay are testable.
