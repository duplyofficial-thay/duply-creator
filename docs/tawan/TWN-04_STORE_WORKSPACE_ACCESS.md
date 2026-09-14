# TWN-04 — Store Workspace and Access

**Status:** Approved planning specification; TWN-04-T09 remains pending architecture/security approval and verified isolation tests (2026-09-14)

**Decision owner:** Store Owner/product owner (Arriyathanasak, `arriyathanasak@gmail.com`).

**Purpose:** Define the canonical Store Workspace tenancy, Store Context resolution, roles, capabilities, Channel binding, support access, subscription suspension, and cross-store isolation rules for Tawan. This is a design/security handoff; it does not authorize production data, live Channel activation, or schema changes.

## 1. Canonical tenancy model

Tawan uses one shared `tawan_ai` PostgreSQL schema with many Store Workspaces. Every store-owned row has a mandatory, immutable `store_workspace_id`. Shared tables are indexed and later partitionable by workspace and time; no table or schema is created per customer.

This model is acceptable only with database-enforced row-level security (RLS), server-derived Store Context, workspace-scoped foreign keys/indexes/caches, and negative cross-workspace tests. Application filtering alone is not a security boundary.

Customer operational data is stored in workspace-scoped relational tables. Documents, images, payment slips, and other binary files are stored in private object storage; the database stores only protected metadata and object references. A starting Store Knowledge quota is 1 GB per workspace, with atomic accounting and configurable warning thresholds at 70%, 85%, and 100%.

## 2. Store Workspace and identity tables

The canonical logical relationships are:

- `store_workspaces`: immutable workspace identity, status, timezone, quota, entitlement reference, and configuration version;
- `workspace_memberships`: Duply user, workspace, membership status, primary-owner flag, grantor, timestamps;
- `staff_capabilities`: membership, capability, grantor, effective/revoked timestamps, reason;
- `channel_identities`: Channel type, external identity, workspace binding, verification state, and revocation;
- `knowledge_sources` / `stored_documents`: protected source metadata and object references;
- `audit_events`: append-only security and business evidence.

Every child table carries workspace scope. Composite foreign keys or equivalent database checks prevent a child in Workspace A from referencing a parent in Workspace B. Unique constraints, search/vector indexes, analytics aggregates, cache keys, exports, background jobs, and queue items include workspace scope.

The same Duply user may manage multiple workspaces only through separate explicit memberships. A LINE user may also be bound to more than one workspace only through separate owner-approved memberships. Ambiguous messages are denied; a plain LINE message cannot choose the workspace. Resolution requires a signed deep link to an authenticated Duply/Tawan UI or a support-assisted linking flow.

## 3. Store Context resolution contract

Store Context is resolved before any data access, model prompt construction, tool call, file access, or outbound message. The trusted resolver accepts only server-observed identity and Channel evidence:

1. Authenticate the Duply user/session or verify the signed LINE webhook event.
2. Resolve the Channel identity and its verified workspace binding.
3. Resolve the active workspace membership and capability for the requested operation.
4. Check subscription entitlement and workspace status.
5. Set the workspace context transaction-locally for the request/job and make it immutable for the remainder of that operation.
6. Apply RLS and capability checks before reading or mutating data.

The resolver rejects any client-, model-, tool-, hidden-field-, URL-, or message-supplied `store_workspace_id`. It fails closed when context is absent, malformed, expired, or changed after being set. It also rejects mismatched IDs, stale sessions, revoked memberships, unverified Channel bindings, replayed webhooks, ambiguous workspace resolution, and context changes mid-request. Background jobs, retries, webhooks, cache lookups, and exports repeat the same context checks; they do not inherit an unverified context from a prior request.

## 4. RLS and isolation requirements

Before real customer data, every workspace-scoped table must have `NOT NULL store_workspace_id`, RLS enabled, and policies that derive scope from authenticated membership or a backend-controlled transaction context. RLS denies when context is absent, malformed, or changed. Normal requests use a separate non-bypass database role; the Supabase/service role is reserved for tightly controlled backend migrations or recovery and is never exposed to a browser, LINE client, model, staff member, or untrusted request.

The isolation contract applies to:

- database reads, writes, joins, and foreign-key checks;
- Store Knowledge, Customer Memory, Orders, payments, Tasks, consent, and audit records;
- document uploads, replacements, downloads, signed URLs, and deletion;
- retrieval, vectors, embeddings, prompt context, model caches, tools, logs, telemetry, queues, and exports;
- management LINE and merchant customer LINE routing;
- analytics and anonymous aggregates.

Every denied cross-workspace attempt creates a security audit event without copying secrets or raw sensitive documents. Negative tests must prove Store A cannot read, mutate, search, infer, export, or send data from Store B.

## 5. Roles and capabilities

Canonical roles are `platform_admin`, `store_owner`, `workspace_admin`, `store_staff`, and `customer`. `platform_admin` is a platform role and is not ordinary workspace membership. `workspace_admin` is an explicit workspace membership, not a replacement for the primary owner.

### Store Owner

There is exactly one primary owner. Enforce this with a partial unique database constraint on `(store_workspace_id)` where `primary_owner = true`, plus a transaction that atomically assigns the new owner, revokes the old owner flag, checks membership, and records both old and new owners. Owner deletion/demotion is rejected if it would leave zero owners; recovery is an audited Duply support workflow. Owner-only actions are appointing/removing administrators, granting/revoking sensitive capabilities, binding/revoking management Channels, publishing permanent Store Knowledge, approving final Phase 1 payment decisions, approving exports/deletion exceptions/legal settings, transferring ownership, closing/reactivating the workspace, and changing high-risk commercial settings.

### Workspace Admin

May manage routine workspace operations and assigned staff work within granted capabilities. An admin cannot self-grant owner/admin access, transfer ownership, publish permanent Store Knowledge unless explicitly granted the separate owner-only capability, approve final Phase 1 payment, approve legal/retention changes, or bypass entitlement/RLS.

### Store Staff

Staff receive individual capabilities rather than universal access:

- `manager` — operational coordination and permitted settings;
- `sales` — customer sales preparation and follow-up;
- `fulfilment` — fulfilment and delivery Tasks;
- `marketing` — approved operational messaging work; Pro campaign execution remains separately gated;
- `knowledge_editor` — prepare/review Knowledge Candidates, never publish permanent knowledge by default;
- `payment_review` — inspect evidence and recommend a decision, never make the final Phase 1 paid decision.

All capabilities are deny-by-default, workspace-scoped, server-checked on every request, and independently auditable. A role or capability never crosses Store Workspaces.

### Customer

Receives service only through the merchant's customer-facing Channel within one workspace. A customer identity is never linked across workspaces by name, phone, LINE similarity, embeddings, or model inference.

## 6. Legacy-role migration

Existing labels are mapped explicitly through a migration with `pending`, `mapped`, `needs_review`, `retired`, and `rolled_back` states:

- legacy `owner` → `store_owner`;
- legacy `employee` → `store_staff`;
- unknown, conflicting, or over-broad labels → `needs_review` with no elevated access.

No legacy label silently receives `workspace_admin`, owner-only capabilities, or cross-workspace access. Migration records source label, mapped role, reviewer/automation version, timestamp, and reason. Unknown/conflicting records remain denied until remediated. After the migration cutover date, legacy labels are rejected on write and cannot be reintroduced; rollback restores the previous mapping without elevating access. Existing memberships are rechecked when a Channel is linked or a sensitive action is attempted.

## 7. Channel separation and management identities

Tawan Official management LINE and the merchant customer-facing LINE OA are separate security domains with distinct Channel types, credentials, webhooks, routing, capabilities, and audit events.

Each management LINE ID must be verified from a signed LINE webhook event and linked through an already-authenticated owner action in Duply/Tawan UI or an equivalent trusted linking flow. An unlinked LINE chat cannot approve its own binding. The ID is then explicitly approved by the Store Owner, bound to the intended Duply membership and workspace, replay/idempotency checked, and immediately revocable with cache invalidation. Outbound messages verify the recipient binding before sending. Group IDs, duplicate bindings, revoked-user caches, and ambiguous memberships are denied or escalated.

Customer-channel messages cannot invoke staff-management operations. Management messages cannot access customer commerce data unless an explicit workspace-scoped capability authorizes that operation. The same LINE person appearing in both contexts is still resolved by Channel type and workspace binding, never by identity similarity alone.

## 8. Documents, object storage, and quotas

Files use private object storage with workspace-bound metadata and a path such as `private/{store_workspace_id}/{source_id}/{file_version}`. The backend performs quarantine, malware scanning, type/size checks, and prompt-injection/data-exfiltration checks before ingestion. There are no public paths; signed URLs are short-lived, operation-specific, and issued only after authorization.

The 1 GB **Store Knowledge** quota includes retained knowledge-source originals, versions, derived extraction files, quarantine items, and retry/orphan objects that remain retained under policy. Payment slips, raw chat, exports, backups, and temporary processing data use separate protected counters and retention policies; they cannot bypass the total storage safety budget or silently consume the knowledge quota. Bytes are reserved atomically before upload, released on failure/expiry, and counted consistently across file upload, CSV, Google Sheets, and website-import paths. At 70%, 85%, and 100%, idempotent notifications go to the Store Owner and Duply support. Repeated notices use hysteresis so a merchant is not spammed; usage is recalculated after deletion, expiry, failed upload, and concurrent reservation settlement. At 100%, new retained data is rejected while authorized cleanup remains available. Any quota override is time-limited, owner/platform-authorized, and audited.

Object reads, downloads, replacements, moves, deletions, retention expiry, quota decisions, and signed-URL issuance create audit events. Models never receive unrestricted storage access.

## 9. Subscription and membership lifecycle

Membership and subscription are separate concepts. A user may remain a recorded workspace member while entitlement is suspended. The canonical entitlement states are `active`, `payment_due`, `past_due`, `grace_period`, `suspended`, and `closed`.

After the paid-through day, the workspace becomes `suspended` and stops new customer-facing LINE replies, new API/tool actions, onboarding changes, Store Knowledge changes, queued outbound sends, new Orders, and payment operations. Existing Orders, Tasks, audit evidence, legally retained documents, membership records, and subscription history remain under their own retention schedules. No bulk deletion occurs at suspension.

Expired owners/admins receive only a restricted read-only view showing status, paid-through date, retention information, support route, and reactivation action. New data changes, exports, staff/capability changes, and operational work require reactivation or a documented support exception.

Reactivation restores the existing workspace and memberships after Duply confirms the new subscription and reruns entitlement, Channel, RLS, and safety checks. It does not create a duplicate workspace or bypass revoked memberships.

## 10. Platform Administrator support access

Platform Administrator access is break-glass only: time-limited, least-privilege, reason-coded, owner-notified where safe, and append-only audited. It does not become Store Owner access. Support access cannot silently change ownership, grant capabilities, bypass RLS, access another workspace, or export raw customer data. Security incidents may use an emergency path, but the reason, scope, actor, timestamps, and review outcome remain mandatory.

## 11. Audit and verification requirements

Audit events record actor, effective role/capability, workspace, action, object reference, result, timestamp, request/event ID, source Channel, reason code, and automation/reviewer version where applicable. Secrets, credentials, and raw sensitive documents are excluded from audit payloads.

TWN-04 is not implementation-ready until the architecture/security owner approves the model and tests cover:

1. RLS reads/writes/joins and cross-workspace foreign-key attempts.
2. Forged or mismatched workspace IDs, hidden fields, stale sessions, retries, background jobs, and webhooks.
3. Retrieval/vector/prompt/cache/tool/log/queue/export isolation.
4. Private object-storage paths, signed URLs, path traversal, copy/move, deletion, quarantine, and quota races.
5. Owner/admin/staff capability escalation and legacy-role migration.
6. Duplicate/revoked/ambiguous management LINE IDs and management/customer Channel separation.
7. Suspension, restricted read-only access, reactivation, and retention behaviour.
8. Break-glass support access and audit completeness.

## 12. Acceptance and out of scope

TWN-04-T01 through TWN-04-T08 are design-complete when this document evidences the chosen tenancy model, Store Context contract, roles/capabilities, legacy mapping, support access, and Channel authorization. TWN-04-T09 remains pending until the architecture/security owner approves the boundary and the negative isolation tests pass. Completion does not authorize production schema changes or real customer-data activation.

Out of scope: per-customer database schemas, public object storage, client-selected workspace context, cross-store identifiable matching, autonomous privilege escalation, silent platform-admin access, automatic owner transfer, and production migration before RLS/context verification.

## Approval evidence

- Product owner approved the TWN-04 decision rounds, including shared workspace-scoped tables, RLS/member-based access, private object storage, capability roles, separate management/customer Channels, security tests, and suspension/reactivation rules, on 2026-09-14.
- Architecture/security owner approval and verified negative isolation tests remain required before coding or real-data activation.
