# Tawan Supabase schema requirements

**Document ID:** TAWAN-DATA-001  
**Version:** 1.0 planning baseline  
**Date:** 2026-09-18  
**Status:** Design review required; do not apply to production

## 1. Purpose

This document reconciles the existing Tawan SQL drafts with the TWN-01–TWN-12
implementation contract. It is the data-model companion to
`TAWAN_IMPLEMENTATION_SPEC_REQUIREMENTS.md` and
`IMPLEMENTATION_HANDOFF_TWN01_TWN12.md`.

The current SQL in `scripts/migrations/0020_tawan_commerce_data_layers.sql`
and `0030_tawan_operational_safety.sql` is a useful workflow draft. It is not
yet an approved production migration.

## 2. Important architecture decision before coding

The current draft provisions tables inside a separate `__SCHEMA__` per Duple.
The approved requirements also require every merchant-owned record to carry an
immutable `store_workspace_id`, with server-derived Store Context and RLS.
These are two different tenancy models.

### Recommended model

Use one canonical shared Supabase schema for Tawan operational data, with:

- `store_workspace_id NOT NULL` on every merchant-owned table;
- foreign keys to `store_workspaces(id)`;
- RLS on every exposed table;
- server-side Store Context resolution from authenticated membership/Channel;
- composite unique keys and indexes beginning with `store_workspace_id`;
- no client-provided workspace selector trusted for authorization.

The existing per-Duple schema may remain as a legacy compatibility boundary
until Duply confirms a migration plan. Do not mix the two models in the same
runtime path. The TWN-04 architecture/security gate must approve the final
choice and attach cross-workspace negative tests.

## 3. Common columns

Every shared operational table should use the following where applicable:

| Column | Type | Requirement |
| --- | --- | --- |
| `id` | `uuid` | `gen_random_uuid()` primary key |
| `store_workspace_id` | `uuid` | Required tenant boundary and FK; never client-authoritative |
| `created_at` | `timestamptz` | Server default `now()` |
| `updated_at` | `timestamptz` | Server-maintained on mutable records |
| `created_by` | `uuid/text` | Auth/member/provider actor reference where relevant |
| `updated_by` | `uuid/text` | Auth/member/provider actor reference where relevant |
| `correlation_id` | `text` | Trace across webhook, task, payment, and audit work |
| `idempotency_key` | `text` | Required for external/replayed events; unique in the correct scope |
| `retention_class` | `text` | Required for data with different deletion/retention rules |
| `deleted_at` | `timestamptz` | Soft deletion only where rights/legal hold require it |

Do not store API keys, payment credentials, raw card data, or durable raw chat
transcripts in ordinary tables. Store only a secret-manager reference, an
object reference, or a minimised/redacted hash as appropriate.

## 4. Canonical table groups

### A. Workspace, identity, access, and entitlement

| Table | Required columns |
| --- | --- |
| `store_workspaces` | `id`, `workspace_key`, `display_name`, `business_type`, `timezone`, `locale`, `currency`, `status` (`onboarding/active/payment_due/past_due/grace_period/suspended/closed`), `paid_through`, `created_at`, `updated_at`, `closed_at` |
| `workspace_memberships` | `id`, `store_workspace_id`, `user_id`, `role` (`store_owner/workspace_admin/store_staff`), `primary_owner`, `status`, `joined_at`, `removed_at`, `invited_by`, `last_verified_at` |
| `workspace_capabilities` | `id`, `store_workspace_id`, `membership_id`, `capability`, `allowed`, `effective_at`, `expires_at`, `granted_by`, `reason` |
| `channels` | `id`, `store_workspace_id`, `channel_type` (`tawan_official/merchant_line_oa/management_line`), `provider`, `external_channel_id`, `credential_ref`, `environment` (`sandbox`/`production`), `adapter_version`, `scopes`, `status`, `verified_at`, `disconnected_at`, `capabilities`, `created_at` |
| `channel_bindings` | `id`, `store_workspace_id`, `channel_id`, `membership_id`, `bound_by`, `binding_method`, `status`, `binding_version`, `verified_at`, `revoked_at`, `correlation_id` |
| `store_entitlements` | `id`, `store_workspace_id`, `plan`, `status`, `provider`, `provider_subscription_ref`, `effective_at`, `paid_through`, `grace_until`, `cancelled_at`, `feature_limits`, `source_event_id`, `created_at` |
| `subscription_events` | `id`, `store_workspace_id`, `provider`, `provider_event_id`, `event_type`, `payload_redacted`, `occurred_at`, `processed_at`, `processing_state`, `idempotency_key` |

`store_entitlements.status` must use the approved state machine. The current
draft values (`trial`, `active`, `paused`, `expired`, `cancelled`) are not
sufficient for `payment_due`, `past_due`, `grace_period`, `suspended`, and
`closed` handling.

Add a partial unique constraint so each workspace has at most one active
`primary_owner`, and a deferred/transactional constraint or trigger requiring
exactly one `primary_owner` with role `store_owner` whenever a workspace is
active or entitled. Owner transfer, demotion, and membership deletion must be
one audited transaction that cannot leave an active workspace without an owner.
The membership is the canonical owner record; do not duplicate `owner_user_id`
in `store_workspaces`. A management Channel binding must reference an active
membership, and active bindings must be unique per channel.

### A1. Onboarding, connectors, and support access

| Table | Required columns |
| --- | --- |
| `onboarding_workspaces` | `id`, `store_workspace_id`, `state` (`draft/review/needs_owner_decision/test_ready/live_ready/blocked`), `checklist_version`, `owner_approval_ref`, `started_at`, `completed_at`, `blocked_reason` |
| `onboarding_checklist_items` | `id`, `store_workspace_id`, `onboarding_id`, `item_key`, `status`, `evidence_ref`, `reviewed_by`, `reviewed_at`, `owner_decision_ref` |
| `connector_accounts` | `id`, `store_workspace_id`, `provider`, `adapter_version`, `environment`, `external_account_ref`, `credential_ref`, `status`, `connected_at`, `disconnected_at`, `reauthorize_at` |
| `connector_scopes` | `id`, `store_workspace_id`, `connector_account_id`, `scope`, `allowed`, `approved_by`, `approved_at`, `expires_at`, `revoked_at` |
| `support_access_grants` | `id`, `store_workspace_id`, `support_actor_ref`, `incident_ref`, `reason`, `capabilities`, `starts_at`, `expires_at`, `revoked_at`, `approved_by`, `correlation_id` |

Support access is time-limited, reason-coded, least-privilege, and audited. A
connector cannot use a broad account record as permission to finalize payment,
approve refunds, change pricing, or change subscription.

### B. Customers, Channels, conversations, and consent

| Table | Required columns |
| --- | --- |
| `customers` | `id`, `store_workspace_id`, `external_ref`, `display_name`, `phone_redacted`, `email_redacted`, `status`, `first_seen_at`, `last_seen_at`, `deleted_at` |
| `channel_identities` | `id`, `store_workspace_id`, `customer_id`, `channel_id`, `external_user_id`, `conversation_ref`, `verification_status`, `first_seen_at`, `last_seen_at` |
| `conversations` | `id`, `store_workspace_id`, `customer_id`, `channel_id`, `conversation_ref`, `state`, `bot_state`, `paused_until`, `started_at`, `last_event_at`, `closed_at` |
| `interaction_events` | `id`, `store_workspace_id`, `customer_id`, `channel_id`, `conversation_id`, `event_type`, `payload_minimised`, `source_interaction_ref`, `actor_ref`, `correlation_id`, `idempotency_key`, `occurred_at`, `retention_class` |
| `outbound_messages` | `id`, `store_workspace_id`, `conversation_id`, `channel_id`, `message_type`, `body_snapshot`, `structured_payload`, `provenance`, `status`, `provider_message_ref`, `idempotency_key`, `sent_at` |
| `consent_records` | `id`, `store_workspace_id`, `customer_id`, `purpose`, `channel_id`, `status`, `notice_version`, `wording_version`, `source`, `actor_ref`, `recorded_at`, `withdrawn_at`, `suppression_result` |
| `customer_contact_controls` | `id`, `store_workspace_id`, `customer_id`, `channel_id`, `state`, `blocked_until`, `max_inbound_per_hour`, `max_outbound_per_week`, `reason`, `changed_by` |
| `data_subject_requests` | `id`, `store_workspace_id`, `customer_id`, `request_type`, `status`, `identity_check_ref`, `scope`, `received_at`, `due_at`, `legal_hold`, `approver_ref`, `completion_ref`, `completed_at` |

Raw chat, if temporarily needed, belongs in a separately protected retention
store. It must have an expiry and must not silently become durable memory or
training data.

### C. Store Brain, sources, and memory

| Table | Required columns |
| --- | --- |
| `knowledge_sources` | `id`, `store_workspace_id`, `source_type`, `object_ref`, `source_url`, `approved_domain`, `checksum`, `content_type`, `sensitivity`, `status`, `uploaded_by`, `retention_class`, `created_at` |
| `knowledge_source_versions` | `id`, `store_workspace_id`, `source_id`, `version`, `checksum`, `effective_at`, `expires_at`, `supersedes_id`, `scan_state`, `prompt_injection_scan_state`, `created_at` |
| `knowledge_candidates` | `id`, `store_workspace_id`, `source_id`, `source_version_id`, `candidate_type`, `content_redacted`, `structured_value`, `provenance`, `confidence`, `status`, `requested_by`, `approved_by`, `approval_id`, `decided_at` |
| `published_store_knowledge` | `id`, `store_workspace_id`, `candidate_id`, `content`, `structured_value`, `effective_at`, `expires_at`, `version`, `published_by`, `status` |
| `customer_memories` | `id`, `store_workspace_id`, `customer_id`, `category`, `normalized_value`, `source_interaction_id`, `source_type`, `confidence`, `confirmed_at`, `effective_at`, `expires_at`, `sensitivity`, `status`, `supersedes_id`, `deleted_at` |
| `customer_tiers` | `id`, `store_workspace_id`, `customer_id`, `tier`, `source_type`, `evidence`, `confidence`, `approved_by`, `override_reason`, `effective_at`, `expires_at` |

Embeddings/vectors must include workspace and source-version metadata and must
be filtered by Store Context before retrieval. Never rely on vector similarity
alone for tenancy.

### D. Catalog, inventory, and demand

| Table | Required columns |
| --- | --- |
| `catalog_items` | `id`, `store_workspace_id`, `kind`, `sku`, `name`, `description`, `category`, `images`, `active`, `effective_at`, `updated_at` |
| `catalog_variants` | `id`, `store_workspace_id`, `catalog_item_id`, `variant_code`, `attributes`, `active` |
| `inventory_locations` | `id`, `store_workspace_id`, `name`, `location_type`, `timezone`, `active` |
| `inventory_balances` | `id`, `store_workspace_id`, `variant_id`, `location_id`, `on_hand`, `reserved`, `low_stock_threshold`, `overnight_sell_limit`, `version`, `updated_at` |
| `inventory_events` | `id`, `store_workspace_id`, `variant_id`, `location_id`, `event_type`, `quantity_delta`, `source_ref`, `occurred_at`, `idempotency_key` |
| `price_rules` | `id`, `store_workspace_id`, `catalog_item_id`, `variant_id`, `price_kind`, `amount`, `currency`, `conditions`, `effective_at`, `expires_at`, `approval_id` |
| `wishlist_requests` | `id`, `store_workspace_id`, `customer_id`, `variant_id`, `requested_quantity`, `request_type`, `status`, `restock_target_at`, `notified_at`, `created_at` |
| `store_availability_profiles` | `id`, `store_workspace_id`, `timezone`, `closing_time`, `reservation_minutes`, `overnight_enabled`, `overnight_sell_limit_policy`, `effective_at`, `approved_by` |
| `store_availability_periods` | `id`, `store_workspace_id`, `location_id`, `weekday`, `opens_at`, `closes_at`, `closed`, `effective_from`, `effective_until` |
| `store_holidays` | `id`, `store_workspace_id`, `location_id`, `holiday_date`, `reason`, `overnight_override`, `approved_by` |

### E. Sales, payment, fulfilment, and refunds

| Table | Required columns |
| --- | --- |
| `sales_journeys` | `id`, `store_workspace_id`, `customer_id`, `business_module`, `state`, `summary`, `expressed_need`, `estimated_value`, `assigned_staff_ref`, `next_action_at`, `last_activity_at`, `version` |
| `transactions` | `id`, `store_workspace_id`, `transaction_ref`, `environment` (`sandbox`/`production`), `customer_id`, `journey_id`, `transaction_type`, `state`, `currency`, `subtotal`, `discount_total`, `grand_total`, `price_context`, `address_snapshot`, `idempotency_key`, `expires_at` |
| `transaction_lines` | `id`, `store_workspace_id`, `transaction_id`, `catalog_item_id`, `variant_id`, `item_name_snapshot`, `variant_snapshot`, `quantity`, `unit_price`, `line_total` |
| `stock_reservations` | `id`, `store_workspace_id`, `transaction_id`, `variant_id`, `location_id`, `quantity`, `state`, `expires_at`, `released_at` |
| `payments` | `id`, `store_workspace_id`, `transaction_id`, `environment` (`sandbox`/`production`), `method`, `state`, `expected_amount`, `received_amount`, `currency`, `bank_reference_redacted`, `owner_decision_ref`, `provider_event_namespace`, `created_at`, `updated_at` |
| `payment_evidence` | `id`, `store_workspace_id`, `payment_id`, `environment`, `object_ref`, `content_hash`, `normalized_fingerprint`, `extracted_fields_redacted`, `validation_state`, `duplicate_reason`, `created_at` |
| `transaction_amendments` | `id`, `store_workspace_id`, `transaction_id`, `requested_by`, `requested_changes`, `current_snapshot`, `status`, `approval_id`, `reason`, `applied_at` |
| `shipments` | `id`, `store_workspace_id`, `transaction_id`, `carrier`, `tracking_number`, `fulfilment_state`, `address_snapshot`, `dispatched_at`, `delivered_at` |
| `returns` | `id`, `store_workspace_id`, `transaction_id`, `shipment_id`, `return_type`, `state`, `reason`, `resolution`, `requested_by`, `approved_by`, `completed_at` |
| `refund_requests` | `id`, `store_workspace_id`, `transaction_id`, `environment`, `requested_by`, `amount`, `currency`, `reason`, `status`, `approval_id`, `provider_ref`, `idempotency_key`, `completed_at` |

Merchant subscription billing must use separate tables (`subscription_events`
and provider billing records), never the customer Order `payments` table.

### F. Work queues, dashboard, audit, and operations

| Table | Required columns |
| --- | --- |
| `tasks` | `id`, `store_workspace_id`, `task_type`, `status`, `priority`, `customer_id`, `journey_id`, `transaction_id`, `assignee_ref`, `required_capability`, `title`, `detail`, `due_at`, `escalation_at`, `deduplication_key`, `resolution_code`, `resolved_at` |
| `approvals` | `id`, `store_workspace_id`, `approval_type`, `proposed_action`, `scope`, `requester_ref`, `approver_ref`, `status`, `reason`, `requested_at`, `decided_at`, `expires_at`, `audit_correlation` |
| `recommendations` | `id`, `store_workspace_id`, `recommendation_type`, `evidence_refs`, `confidence`, `explanation`, `model_version`, `rule_version`, `audience_capability_snapshot`, `assignee_ref`, `status`, `expires_at`, `decision_ref` |
| `daily_store_metrics` | `store_workspace_id`, `metric_date`, `business_timezone`, counts/totals, `computed_at`, `source_watermark` |
| `daily_digests` | `id`, `store_workspace_id`, `business_date`, `channel_id`, `recipient_membership_snapshot`, `content_redacted`, `recommendation_ids`, `status`, `sent_at`, `idempotency_key` |
| `audit_events` | `id`, `store_workspace_id`, `event_type`, `actor_ref`, `role`, `capability`, `target_type`, `target_ref`, `action`, `prior_state`, `new_state`, `result`, `reason`, `evidence_ref`, `correlation_id`, `occurred_at` |
| `usage_ledger` | `id`, `store_workspace_id`, `provider`, `model`, `event_type`, token counts, `cost_amount`, `currency`, `request_ref`, `idempotency_key`, `succeeded_at` |
| `job_runs` | `id`, `store_workspace_id`, `job_type`, `scheduled_for`, `started_at`, `finished_at`, `state`, rows/evidence, `idempotency_key` |
| `incident_records` | `id`, `store_workspace_id`, `severity`, `incident_commander_ref`, `containment_owner_ref`, `detected_at`, `contained_at`, `owner_notified_at`, `status`, `evidence_refs`, `reactivation_approval_ref`, `closed_at` |
| `retention_jobs` | `id`, `store_workspace_id`, `data_class`, `scope`, `scheduled_for`, `started_at`, `finished_at`, `state`, `rows_affected`, `deletion_evidence_ref`, `legal_hold_ref`, `idempotency_key` |

For `daily_store_metrics`, the primary key must be `(store_workspace_id,
metric_date)`, not only `metric_date`.

## 5. Required keys, constraints, and indexes

- Prefix tenant indexes with `store_workspace_id`.
- Replace single-tenant unique keys with scoped keys, for example:
  `UNIQUE (store_workspace_id, external_ref)`,
  `UNIQUE (store_workspace_id, channel_id, external_user_id)`, and
  `UNIQUE (store_workspace_id, metric_date)`.
- Child foreign keys should include the tenant where possible, so a child from
  Workspace A cannot reference a parent from Workspace B.
- Use `CHECK` constraints for states, non-negative money/quantity, valid
  time windows, and `reserved <= on_hand`.
- Use append-only history tables for state transitions and audit records.
- Use partial indexes for work queues (`status` not terminal) and expiring
  facts (`expires_at`).
- Use `security_invoker` for exposed views, or keep views in a non-exposed
  schema and explicitly deny public access.

## 6. RLS requirements

RLS must be enabled on every exposed table. Policies must resolve membership
from server-side auth context, not `user_metadata`, a request body, a model
output, or a user-supplied `store_workspace_id`.

Every write policy must include both `USING` and `WITH CHECK`; every update
must first be selectable under the same workspace policy. Exposed views must
use `security_invoker = true` (or be kept in a non-exposed schema), and Data
API grants must be explicit rather than blanket grants. Request paths must not
use the Supabase `service_role` key as a substitute for user authorization;
privileged background jobs need a separately reviewed boundary and audit trail.

Sandbox/production isolation must be enforced at the database boundary:
`transactions`, `payments`, `payment_evidence`, `refund_requests`, `channels`,
and provider-event namespaces carry the same constrained environment, and
composite foreign keys or trigger checks reject a sandbox record or callback
from attaching to or changing production state.

Minimum negative tests:

1. Customer from Workspace A cannot read or write Workspace B data.
2. Staff cannot perform Owner-only payment, refund, subscription, export,
   deletion, pricing, or Channel-binding actions.
3. Customer LINE OA cannot invoke management operations.
4. A revoked/expired entitlement cannot create new service work after
   `paid_through`, but rights/read-only support remain policy-governed.
5. Vector, cache, analytics, dashboard, Storage, export, and support paths
   cannot bypass the workspace policy.

## 7. Gaps in the current SQL draft

Before implementation, reconcile these items:

1. Add the canonical workspace/membership/channel tables or document the
   verified equivalent in the Duply platform.
2. Add `store_workspace_id` and scoped keys if using a shared schema; otherwise
   obtain written TWN-04 approval for the per-Duple schema model and prove RLS
   and cross-schema isolation.
3. Replace the incomplete entitlement states and add `paid_through` and
   provider event idempotency.
4. Add onboarding records, source versions/quarantine, conversations, raw-chat
   retention controls, wishlist/restock requests, recommendations/digests,
   refund requests, and incident evidence.
5. Add subscription billing records separate from customer Order payments.
6. Add tenant scope to `daily_store_metrics`; review all global unique keys and
   indexes.
7. Add RLS policies, grants, Storage policies, vector filters, and negative
   tests before any table is exposed through the Data API.
8. Confirm the authoritative Supabase project, migration owner, backup/restore
   procedure, and whether these drafts are local-only or already deployed.
9. Review `scripts/provision_duple.py`: it currently grants `SELECT` on all
   provisioned tables to `anon` and `authenticated`. That is incompatible with
   customer-data activation unless each table has verified RLS policies and the
   grants are deliberately limited to the required API surface. Do not treat a
   schema name or a UI restriction as a substitute for RLS.
10. Add exactly-one-owner enforcement, membership-linked Channel binding,
    environment-consistent transaction/payment/refund records,
    onboarding/connector/support tables, availability profiles, and
    retention/incident evidence before implementation.

## 8. Implementation gate

This document is a design contract, not permission to apply migrations. The
next implementation card should be: **“TWN data-model decision — approve
shared-schema + `store_workspace_id` or approved per-Duple isolation model.”**

The migration owner must attach schema diff, RLS policies, advisor output,
negative isolation test output, and rollback/restore evidence before marking it
Done.
