-- Tawan commerce data layers.
-- Every table is created inside one provisioned Store Workspace schema.
-- Duply must review this migration against the target Supabase project before
-- applying it outside local verification.

CREATE TABLE __SCHEMA__.store_settings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name        TEXT NOT NULL,
    business_type       TEXT NOT NULL,
    timezone            TEXT NOT NULL DEFAULT 'Asia/Bangkok',
    currency            TEXT NOT NULL DEFAULT 'THB',
    locale              TEXT NOT NULL DEFAULT 'th-TH',
    closing_time        TIME,
    reservation_minutes INTEGER NOT NULL DEFAULT 45 CHECK (reservation_minutes BETWEEN 1 AND 1440),
    review_cadence      TEXT NOT NULL DEFAULT 'weekly' CHECK (review_cadence IN ('daily', 'weekly', 'monthly')),
    subscription_plan   TEXT NOT NULL DEFAULT 'standard' CHECK (subscription_plan IN ('standard', 'pro', 'custom')),
    config_version      INTEGER NOT NULL DEFAULT 1,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.customers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_ref        TEXT NOT NULL UNIQUE,
    display_name        TEXT,
    phone               TEXT,
    email               TEXT,
    tier                TEXT NOT NULL DEFAULT 'standard',
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'restricted', 'deleted')),
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.channel_identities (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    channel             TEXT NOT NULL,
    external_user_id    TEXT NOT NULL,
    conversation_ref    TEXT,
    verification_status TEXT NOT NULL DEFAULT 'unverified',
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (channel, external_user_id)
);

CREATE TABLE __SCHEMA__.customer_memories (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    category            TEXT NOT NULL,
    normalized_value    JSONB NOT NULL,
    source_type         TEXT NOT NULL CHECK (source_type IN ('customer_stated', 'staff_confirmed', 'inferred', 'imported')),
    source_ref          TEXT,
    confidence          NUMERIC(5, 4) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    confirmed_at        TIMESTAMPTZ,
    effective_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at          TIMESTAMPTZ,
    model_version       TEXT,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'corrected', 'disputed', 'expired', 'deleted')),
    sensitivity         TEXT NOT NULL DEFAULT 'ordinary' CHECK (sensitivity IN ('ordinary', 'sensitive', 'restricted')),
    supersedes_id       UUID REFERENCES __SCHEMA__.customer_memories(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.customer_tiers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    tier                TEXT NOT NULL,
    source_type         TEXT NOT NULL CHECK (source_type IN ('rule', 'tawan_recommendation', 'owner_override')),
    evidence            JSONB NOT NULL DEFAULT '{}',
    confidence          NUMERIC(5, 4),
    suggested_at        TIMESTAMPTZ,
    approved_at         TIMESTAMPTZ,
    effective_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at          TIMESTAMPTZ,
    approver_ref        TEXT,
    override_reason     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.consent_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    purpose             TEXT NOT NULL,
    channel             TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN ('granted', 'withdrawn', 'objected', 'restricted')),
    notice_version      TEXT NOT NULL,
    wording_version     TEXT,
    source              TEXT NOT NULL,
    actor_ref           TEXT,
    evidence_ref        TEXT,
    reason              TEXT,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.data_subject_requests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID REFERENCES __SCHEMA__.customers(id),
    request_type        TEXT NOT NULL CHECK (request_type IN ('access', 'portability', 'correction', 'objection', 'restriction', 'deletion')),
    status              TEXT NOT NULL DEFAULT 'received' CHECK (status IN ('received', 'verifying', 'in_progress', 'completed', 'rejected', 'on_hold')),
    scope               JSONB NOT NULL DEFAULT '{}',
    received_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    due_at              TIMESTAMPTZ,
    decision            TEXT,
    legal_exception     TEXT,
    approver_ref        TEXT,
    completion_ref      TEXT,
    completed_at        TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.interaction_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID REFERENCES __SCHEMA__.customers(id),
    channel             TEXT NOT NULL,
    conversation_ref    TEXT,
    event_type          TEXT NOT NULL,
    payload             JSONB NOT NULL DEFAULT '{}',
    source              TEXT NOT NULL DEFAULT 'reply_flow',
    actor_ref           TEXT,
    correlation_id      TEXT NOT NULL,
    idempotency_key     TEXT NOT NULL UNIQUE,
    occurred_at         TIMESTAMPTZ NOT NULL,
    retention_class     TEXT NOT NULL DEFAULT 'structured',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.sales_journeys (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    business_module     TEXT NOT NULL,
    state               TEXT NOT NULL DEFAULT 'new' CHECK (state IN ('new', 'qualified', 'considering', 'checkout', 'won', 'lost', 'paused')),
    module_state        TEXT,
    summary             TEXT,
    expressed_need      TEXT,
    estimated_value     NUMERIC(14, 2),
    currency            TEXT NOT NULL DEFAULT 'THB',
    assigned_staff_ref  TEXT,
    source_channel      TEXT,
    outcome             TEXT,
    outcome_reason      TEXT,
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_activity_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    next_action_at      TIMESTAMPTZ,
    version             INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE __SCHEMA__.journey_interests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id          UUID NOT NULL REFERENCES __SCHEMA__.sales_journeys(id),
    catalog_item_id     UUID,
    variant_ref         TEXT,
    quantity            NUMERIC(12, 3),
    preference          JSONB NOT NULL DEFAULT '{}',
    interest_strength   TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.tasks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type           TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'assigned', 'in_progress', 'waiting_customer', 'waiting_owner', 'completed', 'cancelled', 'expired')),
    priority            TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    customer_id         UUID REFERENCES __SCHEMA__.customers(id),
    journey_id          UUID REFERENCES __SCHEMA__.sales_journeys(id),
    transaction_id      UUID,
    assignee_ref        TEXT,
    required_capability TEXT,
    title               TEXT NOT NULL,
    detail              JSONB NOT NULL DEFAULT '{}',
    due_at              TIMESTAMPTZ,
    escalation_at       TIMESTAMPTZ,
    deduplication_key   TEXT NOT NULL UNIQUE,
    resolution_code     TEXT,
    resolution_summary  TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at         TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.task_status_history (
    id                  BIGSERIAL PRIMARY KEY,
    task_id             UUID NOT NULL REFERENCES __SCHEMA__.tasks(id),
    prior_status        TEXT,
    new_status          TEXT NOT NULL,
    actor_ref           TEXT NOT NULL,
    reason              TEXT,
    correlation_id      TEXT NOT NULL,
    changed_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.approvals (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_type       TEXT NOT NULL,
    proposed_action     JSONB NOT NULL,
    scope               JSONB NOT NULL DEFAULT '{}',
    requester_ref       TEXT NOT NULL,
    approver_ref        TEXT,
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'revoked')),
    reason              TEXT,
    requested_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at          TIMESTAMPTZ,
    effective_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    audit_correlation   TEXT NOT NULL
);

CREATE TABLE __SCHEMA__.catalog_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kind                TEXT NOT NULL CHECK (kind IN ('product', 'menu_item', 'service', 'material', 'rental_item')),
    sku                 TEXT,
    name                TEXT NOT NULL,
    description         TEXT,
    category            TEXT,
    images              JSONB NOT NULL DEFAULT '[]',
    active              BOOLEAN NOT NULL DEFAULT true,
    tax_metadata        JSONB NOT NULL DEFAULT '{}',
    fulfilment_metadata JSONB NOT NULL DEFAULT '{}',
    effective_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (kind, sku)
);

CREATE TABLE __SCHEMA__.catalog_variants (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_item_id     UUID NOT NULL REFERENCES __SCHEMA__.catalog_items(id),
    variant_code        TEXT NOT NULL,
    attributes          JSONB NOT NULL DEFAULT '{}',
    active              BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (catalog_item_id, variant_code)
);

CREATE TABLE __SCHEMA__.inventory_locations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    location_type       TEXT NOT NULL DEFAULT 'store',
    active              BOOLEAN NOT NULL DEFAULT true,
    UNIQUE (name)
);

CREATE TABLE __SCHEMA__.inventory_balances (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id          UUID NOT NULL REFERENCES __SCHEMA__.catalog_variants(id),
    location_id         UUID NOT NULL REFERENCES __SCHEMA__.inventory_locations(id),
    on_hand             NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (on_hand >= 0),
    reserved            NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (reserved >= 0),
    low_stock_threshold NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (low_stock_threshold >= 0),
    version             INTEGER NOT NULL DEFAULT 1,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (variant_id, location_id),
    CHECK (reserved <= on_hand)
);

CREATE TABLE __SCHEMA__.price_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_item_id     UUID NOT NULL REFERENCES __SCHEMA__.catalog_items(id),
    variant_id          UUID REFERENCES __SCHEMA__.catalog_variants(id),
    price_kind          TEXT NOT NULL CHECK (price_kind IN ('standard', 'quantity', 'wholesale', 'tier', 'customer', 'campaign')),
    amount              NUMERIC(14, 2) NOT NULL CHECK (amount >= 0),
    currency            TEXT NOT NULL DEFAULT 'THB',
    conditions          JSONB NOT NULL DEFAULT '{}',
    priority            INTEGER NOT NULL DEFAULT 0,
    authorized_by      TEXT,
    effective_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at          TIMESTAMPTZ,
    approval_id         UUID REFERENCES __SCHEMA__.approvals(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_ref     TEXT NOT NULL UNIQUE,
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    journey_id          UUID REFERENCES __SCHEMA__.sales_journeys(id),
    transaction_type    TEXT NOT NULL DEFAULT 'order' CHECK (transaction_type IN ('order', 'booking', 'quotation', 'project', 'reservation', 'rental')),
    state               TEXT NOT NULL DEFAULT 'draft' CHECK (state IN ('draft', 'pending_confirmation', 'confirmed', 'awaiting_payment', 'paid', 'in_progress', 'completed', 'cancelled', 'expired', 'refunded', 'disputed')),
    currency            TEXT NOT NULL DEFAULT 'THB',
    subtotal            NUMERIC(14, 2) NOT NULL DEFAULT 0,
    discount_total      NUMERIC(14, 2) NOT NULL DEFAULT 0,
    grand_total         NUMERIC(14, 2) NOT NULL DEFAULT 0,
    price_context       JSONB NOT NULL DEFAULT '{}',
    fulfilment_mode     TEXT,
    address_snapshot    JSONB,
    idempotency_key     TEXT NOT NULL UNIQUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at          TIMESTAMPTZ
);

ALTER TABLE __SCHEMA__.tasks
    ADD CONSTRAINT tasks_transaction_fk FOREIGN KEY (transaction_id) REFERENCES __SCHEMA__.transactions(id);

CREATE TABLE __SCHEMA__.transaction_lines (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    catalog_item_id     UUID REFERENCES __SCHEMA__.catalog_items(id),
    variant_id          UUID REFERENCES __SCHEMA__.catalog_variants(id),
    item_name_snapshot  TEXT NOT NULL,
    variant_snapshot    JSONB NOT NULL DEFAULT '{}',
    quantity            NUMERIC(12, 3) NOT NULL CHECK (quantity > 0),
    unit_price          NUMERIC(14, 2) NOT NULL CHECK (unit_price >= 0),
    line_total          NUMERIC(14, 2) NOT NULL CHECK (line_total >= 0),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.transaction_status_history (
    id                  BIGSERIAL PRIMARY KEY,
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    prior_state         TEXT,
    new_state           TEXT NOT NULL,
    actor_ref           TEXT NOT NULL,
    reason              TEXT,
    correlation_id      TEXT NOT NULL,
    changed_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.stock_reservations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    variant_id          UUID NOT NULL REFERENCES __SCHEMA__.catalog_variants(id),
    location_id         UUID NOT NULL REFERENCES __SCHEMA__.inventory_locations(id),
    quantity            NUMERIC(12, 3) NOT NULL CHECK (quantity > 0),
    state               TEXT NOT NULL DEFAULT 'active' CHECK (state IN ('active', 'released', 'consumed', 'expired')),
    expires_at          TIMESTAMPTZ NOT NULL,
    released_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.payments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    method              TEXT NOT NULL CHECK (method IN ('promptpay', 'bank_transfer', 'cash', 'other')),
    state               TEXT NOT NULL DEFAULT 'pending' CHECK (state IN ('pending', 'under_review', 'paid', 'rejected', 'refunded', 'disputed')),
    expected_amount     NUMERIC(14, 2) NOT NULL CHECK (expected_amount >= 0),
    received_amount     NUMERIC(14, 2),
    currency            TEXT NOT NULL DEFAULT 'THB',
    bank_reference      TEXT,
    owner_decision_ref  TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.payment_evidence (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id          UUID NOT NULL REFERENCES __SCHEMA__.payments(id),
    object_ref          TEXT NOT NULL,
    content_hash        TEXT NOT NULL,
    normalized_fingerprint TEXT,
    extracted_fields    JSONB NOT NULL DEFAULT '{}',
    validation_state    TEXT NOT NULL DEFAULT 'pending' CHECK (validation_state IN ('pending', 'candidate', 'conflict', 'accepted', 'rejected')),
    duplicate_reason    TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (content_hash)
);

CREATE TABLE __SCHEMA__.knowledge_sources (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type         TEXT NOT NULL CHECK (source_type IN ('upload', 'url', 'template', 'api', 'pos')),
    object_ref          TEXT,
    source_url          TEXT,
    checksum            TEXT,
    content_type        TEXT,
    status              TEXT NOT NULL DEFAULT 'received',
    retention_class     TEXT NOT NULL DEFAULT 'source',
    created_by          TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.knowledge_candidates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           UUID NOT NULL REFERENCES __SCHEMA__.knowledge_sources(id),
    candidate_type      TEXT NOT NULL,
    content             TEXT NOT NULL,
    structured_value     JSONB NOT NULL DEFAULT '{}',
    provenance           JSONB NOT NULL DEFAULT '{}',
    confidence           NUMERIC(5, 4) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    scope               TEXT NOT NULL DEFAULT 'store',
    effective_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'published', 'superseded', 'expired')),
    requested_by        TEXT NOT NULL,
    approved_by         TEXT,
    approval_id         UUID REFERENCES __SCHEMA__.approvals(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at          TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.analytics_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID REFERENCES __SCHEMA__.customers(id),
    event_type          TEXT NOT NULL,
    event_version       TEXT NOT NULL DEFAULT '1.0',
    payload             JSONB NOT NULL DEFAULT '{}',
    occurred_at         TIMESTAMPTZ NOT NULL,
    idempotency_key     TEXT NOT NULL UNIQUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.daily_store_metrics (
    metric_date         DATE PRIMARY KEY,
    order_count         INTEGER NOT NULL DEFAULT 0,
    completed_order_count INTEGER NOT NULL DEFAULT 0,
    revenue_total       NUMERIC(14, 2) NOT NULL DEFAULT 0,
    customer_count      INTEGER NOT NULL DEFAULT 0,
    repeat_customer_count INTEGER NOT NULL DEFAULT 0,
    task_created_count  INTEGER NOT NULL DEFAULT 0,
    task_completed_count INTEGER NOT NULL DEFAULT 0,
    payment_review_count INTEGER NOT NULL DEFAULT 0,
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.audit_events (
    id                  BIGSERIAL PRIMARY KEY,
    event_type          TEXT NOT NULL,
    actor_ref           TEXT NOT NULL,
    target_ref          TEXT,
    action              TEXT NOT NULL,
    result              TEXT NOT NULL,
    reason              TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    correlation_id      TEXT NOT NULL,
    occurred_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_channel_identities_customer ON __SCHEMA__.channel_identities(customer_id);
CREATE INDEX idx_customer_memories_active ON __SCHEMA__.customer_memories(customer_id, status, expires_at);
CREATE INDEX idx_interaction_events_customer ON __SCHEMA__.interaction_events(customer_id, occurred_at);
CREATE INDEX idx_sales_journeys_customer ON __SCHEMA__.sales_journeys(customer_id, state);
CREATE INDEX idx_tasks_work_queue ON __SCHEMA__.tasks(status, priority, due_at);
CREATE INDEX idx_transaction_lines_transaction ON __SCHEMA__.transaction_lines(transaction_id);
CREATE INDEX idx_payments_review ON __SCHEMA__.payments(state, updated_at);
CREATE INDEX idx_analytics_events_type_date ON __SCHEMA__.analytics_events(event_type, occurred_at);

-- DOWN

DROP TABLE __SCHEMA__.audit_events;
DROP TABLE __SCHEMA__.daily_store_metrics;
DROP TABLE __SCHEMA__.analytics_events;
DROP TABLE __SCHEMA__.knowledge_candidates;
DROP TABLE __SCHEMA__.knowledge_sources;
DROP TABLE __SCHEMA__.payment_evidence;
DROP TABLE __SCHEMA__.payments;
DROP TABLE __SCHEMA__.stock_reservations;
DROP TABLE __SCHEMA__.transaction_status_history;
DROP TABLE __SCHEMA__.transaction_lines;
DROP TABLE __SCHEMA__.transactions;
DROP TABLE __SCHEMA__.price_rules;
DROP TABLE __SCHEMA__.inventory_balances;
DROP TABLE __SCHEMA__.inventory_locations;
DROP TABLE __SCHEMA__.catalog_variants;
DROP TABLE __SCHEMA__.catalog_items;
DROP TABLE __SCHEMA__.approvals;
DROP TABLE __SCHEMA__.task_status_history;
DROP TABLE __SCHEMA__.tasks;
DROP TABLE __SCHEMA__.journey_interests;
DROP TABLE __SCHEMA__.sales_journeys;
DROP TABLE __SCHEMA__.interaction_events;
DROP TABLE __SCHEMA__.data_subject_requests;
DROP TABLE __SCHEMA__.consent_records;
DROP TABLE __SCHEMA__.customer_tiers;
DROP TABLE __SCHEMA__.customer_memories;
DROP TABLE __SCHEMA__.channel_identities;
DROP TABLE __SCHEMA__.customers;
DROP TABLE __SCHEMA__.store_settings;
