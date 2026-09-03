# Team Data Model Gap Review

**Updated:** 2026-09-03

The team review found that the original model was strong on privacy,
authority, and auditability but incomplete for the daily operation of a Thai
LINE shop. The responses below are the implementation comments to keep beside
the model.

## Pilot-Critical Gaps

### 1. Human takeover

**Comment:** `sales_journeys.assigned_staff_ref` does not pause the bot. The
new `conversation_controls` record is the source of truth for one channel
conversation. Staff can set `paused_by_staff` or `paused_until`, and the reply
flow must check it before generating a response. Every change records actor,
reason, version, and time. This prevents simultaneous owner and bot replies.

### 2. Outbound message and reply provenance

**Comment:** `outbound_messages` records ordinary replies, order messages,
payment reminders, task alerts, and future Campaign messages. It stores a
delivery idempotency key, retry state, body snapshot where policy permits,
structured payload, correlation ID, and provenance. Provenance must identify
the approved knowledge IDs, operational records, price snapshot, and human
approval used to form the reply. Raw body retention follows the approved
policy; the delivery fact and provenance remain structured evidence.

### 3. Usage, cost, and customer limits

**Comment:** `usage_ledger` records every successful paid model/OCR/embedding
call immediately after the provider success and before response parsing. The
store can measure cost per customer, conversation, and period. Tawan must
enforce `customer_contact_controls` and store-level limits before expensive
calls. Standard and Pro pricing must be based on observed usage, not guesses.

## Operational Gaps

### 4. Order amendments

**Comment:** Confirmed transaction lines remain immutable. `transaction_amendments`
preserves the requested change, original snapshot, approval, and resulting
version. Approved amendments create a new revision and revalidate price,
stock, payment, and customer confirmation; they do not overwrite history.

### 5. Shipping, COD, returns, and exchanges

**Comment:** `shipments` covers carrier, tracking, delivery state, address
snapshot, and COD amount. `returns` and `return_lines` cover refund/exchange
approval, received condition, and restocking. Fashion Phase 1 must test return
and exchange paths before claiming the vertical is complete.

### 6. Migration drift

**Comment:** `schema_migration_history` records version, checksum, executor,
and execution reference per Store Workspace. `store_settings.config_version`
is configuration state, not migration state.

### 7. Thai documents and tax

**Comment:** `tax_configs` and `tax_documents` provide the data foundation for
tax snapshots and per-store/per-year document numbering. The exact numbering,
VAT, receipt, and tax-invoice rules require Thai accounting/legal confirmation
before production use.

### 8. Opening hours, resources, and branches

**Comment:** `store_branches`, `branch_hours`, and `branch_holidays` replace a
single closing-time assumption. Branch-aware catalog, staff, pricing, booking,
and fulfilment routing remains a follow-up implementation. Until that work is
complete, the pilot should explicitly run as single-location.

### 9. Scheduled job evidence

**Comment:** `job_runs` records reservation expiry, retention deletion, hourly
aggregates, daily close, ingestion, and export jobs. A scheduled job is not
complete merely because it ran; it must record state, rows, errors, and
evidence, including partial failure.

## Explicit Product and Legal Decisions

### 10. Cross-border AI processing

**Comment:** `processing_activities` records purpose, data categories,
recipients, regions, legal-basis reference, retention, and subprocessors per
store. Thai counsel must confirm notice, consent/lawful basis, contract,
subprocessor, and cross-border transfer requirements before real customer
messages are sent to an external model.

### 11. Cross-store payment-slip fingerprints

**Comment:** Store-scoped duplicate detection remains the privacy-preserving
default. A platform-wide salted hash/fingerprint service could detect reuse
without exposing customer identity, but it would be cross-store processing and
must be separately approved, documented, access-controlled, and audited. It is
not silently added to a store schema.

### 12. Entitlement and downgrade behaviour

**Comment:** `store_entitlements` records plan, status, effective/expiry dates,
and limits. Downgrade stops new Pro Campaign actions but does not erase
historical Campaign or analytics records. Export and retention follow the
approved contract and legal policy.

### 13. Pilot scope decision

**Comment:** Phase 1 fashion is single-location unless the pilot store needs
branches. The schema can represent branches now, but branch-aware routing is
not claimed complete. Returns, exchanges, shipping, COD, staff takeover,
outbound provenance, and usage controls are now part of the fashion pilot
acceptance checklist.

## New Migration

The physical additions are in
`scripts/migrations/0030_tawan_operational_safety.sql`. It is reversible and
must be applied after `0010` and `0020`. It has not been applied to a live
Supabase project.
