# TWN-11 — Channels and Integrations

**Status:** Approved for documentation and implementation planning (2026-09-18)
**Phase:** 1 to 3; no non-LINE marketplace connector committed in Phase 1
**Depends on:** TWN-01 Product Direction, TWN-04 Workspace/Channel security

## Channel boundaries

The Duply website is the authenticated onboarding and management workspace.
Tawan Official is the management/sales-administration AI in Phase 1: it explains
available tasks, guides the Owner or staff, and sends alerts. A merchant's own
LINE OA is a separate customer-facing Channel. Any future connector customer-
selling behavior is a separately approved Channel capability and never changes
the management/customer boundary.
Customer LINE messages can never invoke management operations, and management
messages cannot access customer commerce data without an explicit workspace
Capability.

LINE OA is the only complete customer sales Channel in Phase 1. Tawan Official
remains the management Channel; Duply is the full evidence and settings surface.
Future connectors must preserve these Channel-type boundaries rather than merge
identities by similarity.

## Common Channel Adapter contract

Every adapter implements a versioned contract for:

- source identity, account/Channel binding, Store Workspace resolution, and
  idempotency/replay keys;
- inbound/outbound text, structured events, media metadata, delivery status,
  retries, rate limits, and provider error mapping;
- consent, suppression, audience, Capability, and customer-versus-management
  Channel rules;
- catalog/product/variant, stock, order, payment/status, and customer references
  only when the approved connector scope permits them;
- credential isolation, webhook signature/authentication, secret rotation,
  audit events, pause/resume, disconnect, and deletion propagation. No connector
  scope may mark payment paid, finalize a payment decision, execute or approve a
  refund, change a discount/price, change a subscription, or bypass Owner approval.

The adapter must derive Store Context server-side from an authenticated binding.
Client input, model output, source similarity, or an unlinked webhook cannot
choose a workspace. Each connector has separate credentials, permissions,
event mapping, rate limits, failure state, and audit history.

## Unified operational view without data mixing

Duply provides one combined operational view while retaining source-specific
records. For example, stock is shown as separate quantities for the merchant's
LINE/OA process, Shopee, Lazada, TikTok, Facebook, or Instagram, with source,
timestamp, reservation, and confidence. A roll-up can show total or available
stock only when the source rules and reconciliation state permit it; it never
overwrites the source record or hides a conflict.

Tawan answers with the relevant source and freshness. Conflicting stock, price,
order, or delivery facts create a reconciliation Task and pause affected
automation rather than guessing. Cross-source customer identity matching is
workspace-local, evidence-backed, and never assumed from a similar name alone.

## Phase 1 inputs

Phase 1 supports manual entry, guided templates, CSV, Google Sheets, and
Owner-approved Google Drive/API sources. The Owner explicitly selects files or
folders and approves the source before Tawan reads them. Folder approval is not
a silent blanket import: every newly added file enters quarantine, is scanned
and validated, and remains non-retrievable until the Owner approves that file or
an explicitly documented, narrowly scoped folder policy. Imports are quarantined
and checked for format, duplicate/outdated data, malware, prompt injection,
sensitive content, conflicts, and useful insights. Tawan reports findings and
proposed mappings to the Owner; the data becomes Store Brain, catalog, stock,
price, order, or customer-facing truth only after validation and required Owner
approval.

Google Drive access is least-privilege and source-specific. Revocation,
disconnect, deletion, and stale-source handling propagate to extracted facts,
vectors, caches, prompts, exports, and audit references under TWN-05/TWN-08.

## Connector activation and scope approval

During initial setup, the Owner approves each connector's requested scopes once:
for example, read catalog, read orders, receive events, send customer messages,
update stock, or create orders. Scope changes, reauthorization, changed
credentials, or a new data category require a fresh Owner approval. Approval is
not a blanket permission to perform commercial actions; TWN-07/TWN-09 payment,
refund, discount, deletion, and exception boundaries still apply.

Every connector must support pause, disconnect, reauthorize, and safe recovery.
If it fails, becomes unauthorized, exceeds rate limits, or returns conflicting
data, Tawan pauses affected automation, preserves reason-coded evidence, alerts
the Owner, and creates reconciliation work. It does not silently retry a
financial or customer-facing action.

## Phase 2 connector-selection scorecard

Score each candidate 0–5 with evidence for:

| Criterion | Required question |
| --- | --- |
| Merchant demand | Do pilot merchants repeatedly request it and can demand be measured? |
| API authorization | Are scopes, terms, webhooks, and commercial use legally/technically permitted? |
| Reliability | Are delivery, rate limits, retries, idempotency, and reconciliation workable? |
| Security/privacy | Can credentials, Store Context, consent, retention, and deletion be enforced? |
| Cost | What are provider fees, infrastructure cost, support cost, and expected unit economics? |
| Maintenance | Can Duply monitor version changes, failures, and support burden? |
| Measurable value | Does it improve time saved, order accuracy, stock accuracy, or revenue with evidence? |

Product and technical approval require a documented score, threat/risk review,
pilot evidence, rollback plan, owner-facing consent/scope copy, and a decision
record before implementation.

## Later candidates and Instagram

Later candidates are **Shopee, Facebook, TikTok, Instagram, and Lazada**. They
are possibilities only; no build order is promised. POS, Discord, and other
connectors remain future possibilities only if demand and approval justify them.

Tawan Official Instagram primarily markets Tawan/Duply. It may promote current
partners only with partner approval and a separate opt-in commercial agreement
covering content, identity, permissions, usage, and withdrawal. It is not a
silent customer-data or merchant-showcase channel.

## Acceptance gates

- Customer LINE OA and Tawan Official management Channel pass negative
  cross-channel authorization tests.
- Adapter tests cover Store Context, identity, idempotency, media, delivery,
  consent, errors, credentials, pause/disconnect, and deletion propagation.
- Unified views preserve per-source stock/order/price records and visibly flag
  conflicts and freshness.
- Google Drive/API imports require Owner-selected sources, validation, approval,
  and prompt-injection/malware/conflict checks.
- Connector scopes are Owner-approved and re-approved after scope or credential
  changes; no scope can finalize payment, approve refunds, alter discounts, or
  bypass Owner approval; failed/unauthorized/conflicting adapters pause safely.
- No non-LINE connector enters Phase 1 without product/technical approval.

## Out of scope

Implementing Shopee, Facebook, TikTok, Instagram, Lazada, POS, Discord, or any
other post-LINE connector in Phase 1; merging customer identities across stores;
or allowing a connector to bypass existing payment, privacy, or Owner-approval
boundaries.
