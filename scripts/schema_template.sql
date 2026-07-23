-- schema_template.sql
-- Placeholders: __SCHEMA__ → {duple_id}_ai, __DUPLE_ID__ → {duple_id}
-- Run by provision_duple.py — do not run manually.

CREATE TABLE __SCHEMA__.agent_profiles (
    agent_id        TEXT NOT NULL PRIMARY KEY,
    system_prompt   JSONB,
    is_active       BOOLEAN DEFAULT true,
    updated_at      TIMESTAMPTZ DEFAULT now(),
    version         TEXT DEFAULT '1.0.0',
    created_at      TIMESTAMPTZ DEFAULT now(),
    duple           TEXT,
    domain          TEXT,
    function        TEXT,
    status          TEXT NOT NULL DEFAULT 'active',
    edited_by       TEXT,
    edited_at       TIMESTAMPTZ,
    tools_enabled   JSONB,
    uses_tools      BOOLEAN DEFAULT false
);

CREATE TABLE __SCHEMA__.user_profiles (
    duply_id                    TEXT NOT NULL PRIMARY KEY,
    nickname                    TEXT,
    tier                        TEXT DEFAULT 'free',
    status                      TEXT DEFAULT 'active',
    system_lang                 TEXT DEFAULT 'TH',
    chat_lang                   TEXT DEFAULT 'TH',
    knowledge_level             TEXT DEFAULT 'unknown',
    closeness                   DOUBLE PRECISION DEFAULT 0,
    behavior                    JSONB DEFAULT '{}',
    preferences                 JSONB DEFAULT '{}',
    created_at                  TIMESTAMPTZ DEFAULT now(),
    updated_at                  TIMESTAMPTZ DEFAULT now(),
    interaction_count           INTEGER NOT NULL DEFAULT 0,
    ai_interact_count           INTEGER DEFAULT 0,
    card_interact_count         INTEGER DEFAULT 0,
    service_interact_count      INTEGER DEFAULT 0,
    rapport                     DOUBLE PRECISION DEFAULT 0.0,
    goal                        TEXT,
    terms_version               TEXT,
    privacy_policy_accepted_at  TIMESTAMPTZ,
    privacy_policy_version      TEXT,
    terms_accepted_at           TIMESTAMPTZ,
    disclaimer_accepted_at      TIMESTAMPTZ,
    disclaimer_version          TEXT,
    identity_summary            TEXT,
    last_dream_at               TIMESTAMPTZ,
    archetype_data              JSONB DEFAULT '{}',
    roles                       TEXT[] DEFAULT '{}'
);

CREATE TABLE __SCHEMA__.user_memories (
    id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    duply_id            TEXT NOT NULL,
    topic               TEXT NOT NULL,
    summary             TEXT NOT NULL,
    importance          INTEGER DEFAULT 5,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now(),
    last_referenced_at  TIMESTAMPTZ,
    status              TEXT NOT NULL DEFAULT 'pending',
    created_by          TEXT NOT NULL DEFAULT '__DUPLE_ID__',
    shared_with         TEXT[] DEFAULT '{}',
    last_dream_at       TIMESTAMPTZ,
    details             JSONB DEFAULT '{}'
);

CREATE TABLE __SCHEMA__.interact_log (
    id          BIGSERIAL PRIMARY KEY,
    duply_id    TEXT NOT NULL,
    role        TEXT NOT NULL,
    type        TEXT NOT NULL,
    content     TEXT,
    meta        JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    turn_id     UUID NOT NULL DEFAULT gen_random_uuid()
);

CREATE TABLE __SCHEMA__.agent_call_log (
    id                      SERIAL PRIMARY KEY,
    agent_id                TEXT NOT NULL,
    duply_id                TEXT,
    request_id              TEXT,
    timestamp               TIMESTAMPTZ DEFAULT now(),
    tokens_prompt_cached    INTEGER,
    tokens_prompt_uncached  INTEGER,
    tokens_completion       INTEGER,
    cache_hit_rate          DOUBLE PRECISION,
    cost_usd                DOUBLE PRECISION,
    model                   TEXT,
    latency_total_ms        DOUBLE PRECISION,
    ttft_ms                 DOUBLE PRECISION,
    error                   TEXT,
    fallback_used           BOOLEAN DEFAULT false,
    iterations              INTEGER,
    cost_bkk                DOUBLE PRECISION,
    tool_calls_detail       JSONB,
    response_text           TEXT
);

CREATE TABLE __SCHEMA__.dream_log (
    id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    duply_id            TEXT NOT NULL,
    duple_id            TEXT NOT NULL,
    run_date            DATE NOT NULL,
    turns_processed     INTEGER,
    memories_promoted   INTEGER DEFAULT 0,
    memories_archived   INTEGER DEFAULT 0,
    memories_merged     INTEGER DEFAULT 0,
    memories_reactivated INTEGER DEFAULT 0,
    profile_accepted    INTEGER DEFAULT 0,
    profile_rejected    INTEGER DEFAULT 0,
    error               TEXT,
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE __SCHEMA__.dream_observations (
    id               UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    duply_id         TEXT NOT NULL,
    duple_id         TEXT NOT NULL,
    dream_date       DATE NOT NULL,
    field            TEXT NOT NULL,
    signal           TEXT NOT NULL,
    current_value    TEXT,
    evidence         JSONB NOT NULL DEFAULT '[]',
    counter_evidence JSONB NOT NULL DEFAULT '[]',
    reasoning        TEXT NOT NULL,
    decision         TEXT NOT NULL DEFAULT 'pending',
    decision_reason  TEXT,
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE __SCHEMA__.knowledge_entries (
    id              UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    content         TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    published_date  DATE,
    expiry_date     DATE,
    source_id       TEXT,
    embedding       vector(1536) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE __SCHEMA__.reach_custom_rules (
    id          SERIAL PRIMARY KEY,
    duply_id    TEXT NOT NULL,
    ticker      TEXT NOT NULL,
    condition   TEXT NOT NULL,
    threshold   DOUBLE PRECISION NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ DEFAULT now(),
    fired_at    TIMESTAMPTZ
);

CREATE TABLE __SCHEMA__.reach_alert_log (
    id           SERIAL PRIMARY KEY,
    duply_id     TEXT NOT NULL,
    ticker       TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    detail       JSONB,
    message      TEXT,
    fired_at     TIMESTAMPTZ DEFAULT now(),
    delivered_at TIMESTAMPTZ,
    status       TEXT
);

CREATE TABLE __SCHEMA__.reach_broadcasts (
    id              SERIAL PRIMARY KEY,
    status          TEXT NOT NULL DEFAULT 'draft',
    messages        TEXT[] NOT NULL DEFAULT '{}',
    card            JSONB,
    target          JSONB NOT NULL DEFAULT '{}',
    sender          TEXT NOT NULL,
    total_count     INTEGER,
    delivered_count INTEGER DEFAULT 0,
    failed_count    INTEGER DEFAULT 0,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE __SCHEMA__.reach_broadcast_log (
    id           SERIAL PRIMARY KEY,
    broadcast_id INTEGER NOT NULL,
    duply_id     TEXT NOT NULL,
    status       TEXT NOT NULL,
    error_detail TEXT,
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- BEGIN FINANCE
CREATE TABLE __SCHEMA__.stock_universe (
    id              UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker          TEXT NOT NULL UNIQUE,
    classification  TEXT,
    themes          TEXT[],
    added_by        TEXT,
    price           NUMERIC,
    change_pct      NUMERIC,
    pt_tags         TEXT[],
    day_high        NUMERIC,
    day_low         NUMERIC,
    support_level   NUMERIC,
    support         NUMERIC,
    pivot           NUMERIC,
    resistance      NUMERIC,
    target_price    NUMERIC,
    ema50_dist      NUMERIC,
    rsi             NUMERIC,
    macd            NUMERIC,
    volume_label    TEXT,
    rr_ratio        NUMERIC,
    pt_ctx          TEXT,
    pt_updated_at   TIMESTAMPTZ,
    bf_tags         TEXT[],
    growth_score    NUMERIC,
    quality_score   NUMERIC,
    reality_score   NUMERIC,
    survival_score  NUMERIC,
    valuation_score  NUMERIC,
    valuation_status TEXT,
    fundamental_score NUMERIC,
    next_earning    DATE,
    fundamental_ctx TEXT,
    bf_updated_at   TIMESTAMPTZ,
    last_pt_tags    TEXT[],
    last_bf_tags    TEXT[],
    state_version   INTEGER,
    mkt_cap_size    TEXT,
    earnings_result TEXT,
    eps_surprise    NUMERIC,
    high_60d        NUMERIC,
    low_60d         NUMERIC,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
-- END FINANCE
