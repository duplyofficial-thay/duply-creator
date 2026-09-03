-- Tawan operational safety and real-shop workflows.
-- Review with Duply and Thai counsel before production application.

CREATE TABLE __SCHEMA__.conversation_controls (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel             TEXT NOT NULL,
    conversation_ref    TEXT NOT NULL,
    state               TEXT NOT NULL DEFAULT 'bot_active' CHECK (state IN ('bot_active', 'paused_by_staff', 'paused_until', 'closed')),
    paused_until        TIMESTAMPTZ,
    changed_by          TEXT NOT NULL,
    reason              TEXT,
    version             INTEGER NOT NULL DEFAULT 1,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (channel, conversation_ref)
);

CREATE TABLE __SCHEMA__.outbound_messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID REFERENCES __SCHEMA__.customers(id),
    channel             TEXT NOT NULL,
    conversation_ref    TEXT,
    message_type        TEXT NOT NULL CHECK (message_type IN ('reply', 'order_confirmation', 'payment_reminder', 'task_notification', 'owner_alert', 'campaign')),
    body_snapshot       TEXT,
    structured_payload  JSONB NOT NULL DEFAULT '{}',
    provenance           JSONB NOT NULL DEFAULT '{}',
    correlation_id      TEXT NOT NULL,
    idempotency_key     TEXT NOT NULL UNIQUE,
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'suppressed', 'cancelled')),
    provider_message_ref TEXT,
    attempt_count       INTEGER NOT NULL DEFAULT 0,
    last_error          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at             TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.usage_ledger (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID REFERENCES __SCHEMA__.customers(id),
    event_type          TEXT NOT NULL,
    provider             TEXT,
    model               TEXT,
    prompt_tokens       INTEGER,
    completion_tokens   INTEGER,
    cost_amount         NUMERIC(14, 6),
    currency            TEXT NOT NULL DEFAULT 'USD',
    request_ref         TEXT,
    idempotency_key     TEXT NOT NULL UNIQUE,
    succeeded_at        TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.customer_contact_controls (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES __SCHEMA__.customers(id),
    channel             TEXT NOT NULL,
    state               TEXT NOT NULL DEFAULT 'allowed' CHECK (state IN ('allowed', 'blocked', 'quiet', 'rate_limited')),
    blocked_until       TIMESTAMPTZ,
    max_inbound_per_hour INTEGER,
    max_outbound_per_week INTEGER,
    reason              TEXT,
    changed_by          TEXT NOT NULL,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (customer_id, channel)
);

CREATE TABLE __SCHEMA__.transaction_amendments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    requested_by        TEXT NOT NULL,
    requested_changes   JSONB NOT NULL,
    current_snapshot    JSONB NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'applied', 'expired')),
    approval_id         UUID REFERENCES __SCHEMA__.approvals(id),
    resulting_version   INTEGER,
    reason              TEXT,
    requested_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at          TIMESTAMPTZ,
    applied_at          TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.shipments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    carrier             TEXT,
    service_level       TEXT,
    tracking_number     TEXT,
    fulfilment_state    TEXT NOT NULL DEFAULT 'pending' CHECK (fulfilment_state IN ('pending', 'packed', 'shipped', 'delivered', 'failed', 'returned')),
    address_snapshot    JSONB NOT NULL,
    cod_amount          NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (cod_amount >= 0),
    dispatched_at       TIMESTAMPTZ,
    delivered_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.returns (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID NOT NULL REFERENCES __SCHEMA__.transactions(id),
    shipment_id         UUID REFERENCES __SCHEMA__.shipments(id),
    return_type         TEXT NOT NULL CHECK (return_type IN ('return', 'exchange')),
    state               TEXT NOT NULL DEFAULT 'requested' CHECK (state IN ('requested', 'approved', 'in_transit', 'received', 'rejected', 'completed')),
    reason              TEXT NOT NULL,
    resolution          TEXT,
    restock_state       TEXT NOT NULL DEFAULT 'pending' CHECK (restock_state IN ('not_applicable', 'pending', 'restocked', 'not_restocked')),
    requested_by        TEXT NOT NULL,
    approved_by         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.return_lines (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id           UUID NOT NULL REFERENCES __SCHEMA__.returns(id),
    transaction_line_id UUID NOT NULL REFERENCES __SCHEMA__.transaction_lines(id),
    quantity            NUMERIC(12, 3) NOT NULL CHECK (quantity > 0),
    condition           TEXT,
    restocked_quantity  NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (restocked_quantity >= 0),
    UNIQUE (return_id, transaction_line_id)
);

ALTER TABLE __SCHEMA__.payments
    DROP CONSTRAINT payments_method_check;
ALTER TABLE __SCHEMA__.payments
    ADD CONSTRAINT payments_method_check CHECK (method IN ('promptpay', 'bank_transfer', 'cash', 'cod', 'other'));

CREATE TABLE __SCHEMA__.schema_migration_history (
    version             INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    checksum            TEXT NOT NULL,
    applied_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    applied_by          TEXT NOT NULL,
    execution_ref       TEXT
);

CREATE TABLE __SCHEMA__.store_branches (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_code         TEXT NOT NULL UNIQUE,
    name                TEXT NOT NULL,
    address             JSONB,
    timezone            TEXT NOT NULL DEFAULT 'Asia/Bangkok',
    active              BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.branch_hours (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id           UUID NOT NULL REFERENCES __SCHEMA__.store_branches(id),
    weekday             INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    opens_at            TIME,
    closes_at           TIME,
    closed              BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (branch_id, weekday)
);

CREATE TABLE __SCHEMA__.branch_holidays (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id           UUID NOT NULL REFERENCES __SCHEMA__.store_branches(id),
    holiday_date        DATE NOT NULL,
    reason              TEXT,
    UNIQUE (branch_id, holiday_date)
);

CREATE TABLE __SCHEMA__.job_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type            TEXT NOT NULL,
    scheduled_for       TIMESTAMPTZ,
    started_at          TIMESTAMPTZ,
    finished_at         TIMESTAMPTZ,
    state               TEXT NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'succeeded', 'failed', 'partial', 'cancelled')),
    rows_read           INTEGER NOT NULL DEFAULT 0,
    rows_written        INTEGER NOT NULL DEFAULT 0,
    error_detail        TEXT,
    evidence             JSONB NOT NULL DEFAULT '{}',
    idempotency_key     TEXT NOT NULL UNIQUE
);

CREATE TABLE __SCHEMA__.store_entitlements (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan                TEXT NOT NULL CHECK (plan IN ('standard', 'pro', 'custom')),
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('trial', 'active', 'paused', 'expired', 'cancelled')),
    effective_at        TIMESTAMPTZ NOT NULL,
    expires_at          TIMESTAMPTZ,
    feature_limits      JSONB NOT NULL DEFAULT '{}',
    source_ref          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.tax_configs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tax_id              TEXT,
    tax_name            TEXT NOT NULL,
    rate                NUMERIC(7, 4) NOT NULL CHECK (rate >= 0),
    inclusive           BOOLEAN NOT NULL DEFAULT false,
    effective_at        TIMESTAMPTZ NOT NULL,
    expires_at          TIMESTAMPTZ,
    approved_by         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.tax_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      UUID REFERENCES __SCHEMA__.transactions(id),
    document_type       TEXT NOT NULL CHECK (document_type IN ('quotation', 'order', 'receipt', 'tax_invoice')),
    document_year       INTEGER NOT NULL,
    document_number     TEXT NOT NULL,
    customer_snapshot   JSONB NOT NULL DEFAULT '{}',
    tax_snapshot        JSONB NOT NULL DEFAULT '{}',
    issued_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_type, document_year, document_number)
);

CREATE TABLE __SCHEMA__.processing_activities (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purpose             TEXT NOT NULL,
    data_categories     JSONB NOT NULL,
    recipients          JSONB NOT NULL DEFAULT '[]',
    transfer_region     TEXT,
    legal_basis_ref     TEXT,
    retention_policy_ref TEXT,
    subprocessors       JSONB NOT NULL DEFAULT '[]',
    approved_at         TIMESTAMPTZ,
    approved_by         TEXT,
    version             TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_outbound_messages_delivery ON __SCHEMA__.outbound_messages(status, created_at);
CREATE INDEX idx_usage_ledger_customer_time ON __SCHEMA__.usage_ledger(customer_id, succeeded_at);
CREATE INDEX idx_shipments_transaction ON __SCHEMA__.shipments(transaction_id, fulfilment_state);
CREATE INDEX idx_returns_transaction ON __SCHEMA__.returns(transaction_id, state);
CREATE INDEX idx_job_runs_type_state ON __SCHEMA__.job_runs(job_type, state, scheduled_for);

-- DOWN

DROP TABLE __SCHEMA__.processing_activities;
DROP TABLE __SCHEMA__.tax_documents;
DROP TABLE __SCHEMA__.tax_configs;
DROP TABLE __SCHEMA__.store_entitlements;
DROP TABLE __SCHEMA__.job_runs;
DROP TABLE __SCHEMA__.branch_holidays;
DROP TABLE __SCHEMA__.branch_hours;
DROP TABLE __SCHEMA__.store_branches;
DROP TABLE __SCHEMA__.schema_migration_history;
ALTER TABLE __SCHEMA__.payments DROP CONSTRAINT payments_method_check;
ALTER TABLE __SCHEMA__.payments ADD CONSTRAINT payments_method_check CHECK (method IN ('promptpay', 'bank_transfer', 'cash', 'other'));
DROP TABLE __SCHEMA__.return_lines;
DROP TABLE __SCHEMA__.returns;
DROP TABLE __SCHEMA__.shipments;
DROP TABLE __SCHEMA__.transaction_amendments;
DROP TABLE __SCHEMA__.customer_contact_controls;
DROP TABLE __SCHEMA__.usage_ledger;
DROP TABLE __SCHEMA__.outbound_messages;
DROP TABLE __SCHEMA__.conversation_controls;
