-- family_block.sql — DRAFT proposal, not wired into scripts/schema_template.sql yet.
--
-- To adopt: paste this whole block into scripts/schema_template.sql, immediately
-- after the existing "-- END FINANCE" line, as its own "-- BEGIN FAMILY" / "-- END FAMILY"
-- marker block (mirroring the FINANCE block already there). Same placeholders apply:
-- __SCHEMA__ → {duple_id}_ai, __DUPLE_ID__ → {duple_id}.
--
-- provision_duple.py's block-stripping logic is currently a binary
-- `if archetype != "finance": strip FINANCE block`. It needs to become multi-way so a
-- FINANCE-archetype Duple gets FINANCE stripped-out-if-not-finance, and a FAMILY-archetype
-- Duple gets FAMILY stripped-out-if-not-family, with both blocks able to coexist in the
-- same template file. See ../platform_changes/provision_duple_notes.md.
--
-- Unlike the rest of this template (no FKs, no indexes anywhere), these new tables
-- deliberately add both — flagged to the Duply team as an intentional improvement,
-- not an inconsistency to "fix" elsewhere.

-- BEGIN FAMILY

CREATE TABLE __SCHEMA__.family_guilds (
    id           UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    name         TEXT NOT NULL,
    invite_code  TEXT NOT NULL UNIQUE,
    created_by   TEXT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE __SCHEMA__.family_members (
    id         UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    guild_id   UUID NOT NULL REFERENCES __SCHEMA__.family_guilds(id) ON DELETE CASCADE,
    duply_id   TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    role       TEXT NOT NULL DEFAULT 'child' CHECK (role IN ('parent', 'child')),
    joined_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE (guild_id, duply_id)
);
CREATE INDEX idx_family_members_duply_id ON __SCHEMA__.family_members(duply_id);
CREATE INDEX idx_family_members_guild_id ON __SCHEMA__.family_members(guild_id);

CREATE TABLE __SCHEMA__.quest_templates (
    id             UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    guild_id       UUID REFERENCES __SCHEMA__.family_guilds(id) ON DELETE CASCADE,
    title          TEXT NOT NULL,
    description    TEXT,
    category       TEXT NOT NULL DEFAULT 'custom' CHECK (category IN ('homework', 'chore', 'habit', 'custom')),
    difficulty     TEXT NOT NULL DEFAULT 'easy' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    xp_reward      INTEGER NOT NULL DEFAULT 10,
    coin_reward    INTEGER NOT NULL DEFAULT 10,
    recurrence     TEXT NOT NULL DEFAULT 'daily' CHECK (recurrence IN ('once', 'daily', 'weekly', 'custom')),
    requires_proof BOOLEAN NOT NULL DEFAULT false,
    is_active      BOOLEAN NOT NULL DEFAULT true,
    created_by     TEXT NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT now(),
    updated_at     TIMESTAMPTZ DEFAULT now()
);
-- guild_id IS NULL == a global starter-pack template seeded centrally (not family-authored).
CREATE INDEX idx_quest_templates_guild_id ON __SCHEMA__.quest_templates(guild_id);

CREATE TABLE __SCHEMA__.quest_instances (
    id             UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id    UUID REFERENCES __SCHEMA__.quest_templates(id) ON DELETE SET NULL,
    duply_id       TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    guild_id       UUID NOT NULL REFERENCES __SCHEMA__.family_guilds(id) ON DELETE CASCADE,
    title          TEXT NOT NULL,
    xp_reward      INTEGER NOT NULL,
    coin_reward    INTEGER NOT NULL,
    requires_proof BOOLEAN NOT NULL,
    due_date       DATE NOT NULL,
    status         TEXT NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned', 'submitted', 'approved', 'rejected', 'expired')),
    created_at     TIMESTAMPTZ DEFAULT now(),
    updated_at     TIMESTAMPTZ DEFAULT now()
);
-- title/xp_reward/coin_reward/requires_proof are denormalized copies taken at assignment
-- time so later edits to quest_templates don't rewrite already-assigned history.
CREATE INDEX idx_quest_instances_duply_due ON __SCHEMA__.quest_instances(duply_id, due_date);
CREATE INDEX idx_quest_instances_guild_due ON __SCHEMA__.quest_instances(guild_id, due_date);
CREATE INDEX idx_quest_instances_status ON __SCHEMA__.quest_instances(status);

CREATE TABLE __SCHEMA__.quest_submissions (
    id                UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    quest_instance_id UUID NOT NULL REFERENCES __SCHEMA__.quest_instances(id) ON DELETE CASCADE,
    duply_id          TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    proof_type        TEXT NOT NULL CHECK (proof_type IN ('photo', 'self_report')),
    photo_url         TEXT,
    note              TEXT,
    submitted_at      TIMESTAMPTZ DEFAULT now(),
    reviewed_by       TEXT,
    reviewed_at       TIMESTAMPTZ,
    review_status     TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'approved', 'rejected')),
    review_note       TEXT
);
-- photo_url points at object storage (e.g. a Supabase Storage bucket) — the platform's
-- webhook handler downloads the LINE image and re-hosts it there; this column is never
-- a raw LINE message/content URL (those aren't durable). See platform_changes/ notes.
CREATE INDEX idx_quest_submissions_instance ON __SCHEMA__.quest_submissions(quest_instance_id);
CREATE INDEX idx_quest_submissions_duply_status ON __SCHEMA__.quest_submissions(duply_id, review_status);

CREATE TABLE __SCHEMA__.wallets (
    duply_id     TEXT NOT NULL PRIMARY KEY REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    coin_balance INTEGER NOT NULL DEFAULT 0,
    total_xp     INTEGER NOT NULL DEFAULT 0,
    level        INTEGER NOT NULL DEFAULT 1,
    updated_at   TIMESTAMPTZ DEFAULT now()
);
-- Denormalized fast-read balance — leaderboard queries hit this table directly, not a
-- live SUM() over currency_ledger. currency_ledger below is the append-only source of
-- truth; every wallet mutation writes one ledger row AND updates this row in the same
-- Python transaction (never write either table directly from the LLM).
CREATE INDEX idx_wallets_total_xp ON __SCHEMA__.wallets(total_xp DESC);

CREATE TABLE __SCHEMA__.currency_ledger (
    id          BIGSERIAL PRIMARY KEY,
    duply_id    TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    delta_coins INTEGER NOT NULL,
    delta_xp    INTEGER NOT NULL DEFAULT 0,
    reason      TEXT NOT NULL,
    ref_id      UUID,
    created_at  TIMESTAMPTZ DEFAULT now()
);
-- reason examples: 'quest_approved:{quest_instance_id}', 'redeemed:{redemption_id}',
-- 'redeemed_refund:{redemption_id}', 'manual_adjust'.
CREATE INDEX idx_currency_ledger_duply_id ON __SCHEMA__.currency_ledger(duply_id);

CREATE TABLE __SCHEMA__.reward_catalog (
    id          UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    guild_id    UUID NOT NULL REFERENCES __SCHEMA__.family_guilds(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT,
    cost_coins  INTEGER NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_by  TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_reward_catalog_guild_id ON __SCHEMA__.reward_catalog(guild_id);

CREATE TABLE __SCHEMA__.reward_redemptions (
    id            UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    reward_id     UUID NOT NULL REFERENCES __SCHEMA__.reward_catalog(id) ON DELETE CASCADE,
    duply_id      TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    guild_id      UUID NOT NULL REFERENCES __SCHEMA__.family_guilds(id) ON DELETE CASCADE,
    cost_coins    INTEGER NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'fulfilled', 'rejected')),
    requested_at  TIMESTAMPTZ DEFAULT now(),
    reviewed_by   TEXT,
    reviewed_at   TIMESTAMPTZ,
    fulfilled_at  TIMESTAMPTZ
);
-- cost_coins is a snapshot at redemption time (reward_catalog.cost_coins may change later).
-- Coins are deducted immediately on redemption request (currency_ledger 'redeemed:{id}')
-- and refunded (currency_ledger 'redeemed_refund:{id}') if a parent rejects it.
CREATE INDEX idx_reward_redemptions_duply_status ON __SCHEMA__.reward_redemptions(duply_id, status);

CREATE TABLE __SCHEMA__.schedules (
    id               UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    duply_id         TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    label            TEXT NOT NULL,
    time_of_day      TIME NOT NULL,
    days_of_week     INTEGER[] NOT NULL DEFAULT '{0,1,2,3,4,5,6}',
    message_override TEXT,
    is_active        BOOLEAN NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);
-- days_of_week: 0=Sun..6=Sat. label examples: 'bedtime', 'homework_start', 'wake_up'.
-- message_override NULL == persona-driven default nudge text, not a fixed string.
CREATE INDEX idx_schedules_duply_active ON __SCHEMA__.schedules(duply_id, is_active);

CREATE TABLE __SCHEMA__.schedule_nudge_log (
    id          BIGSERIAL PRIMARY KEY,
    schedule_id UUID NOT NULL REFERENCES __SCHEMA__.schedules(id) ON DELETE CASCADE,
    duply_id    TEXT NOT NULL REFERENCES __SCHEMA__.user_profiles(duply_id) ON DELETE CASCADE,
    fired_at    TIMESTAMPTZ DEFAULT now(),
    message     TEXT,
    status      TEXT NOT NULL DEFAULT 'sent'
);
-- Mirrors reach_alert_log's shape. schedule_cron.py checks this before firing to avoid
-- double-sending the same schedule entry within one day.

-- END FAMILY
