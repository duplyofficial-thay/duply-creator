-- migrate_reach_user_rules.sql
-- Renames reach_custom_rules → reach_user_rules with JSONB condition column.
-- Run ONCE in Supabase SQL editor for each schema (thay_ai, khun_ai).
--
-- reach_custom_rules columns:  id, duply_id, ticker, condition (TEXT), threshold, status, created_at, fired_at
-- reach_user_rules columns:    id, duply_id, trigger_type, condition (JSONB), status, fired_at, created_at
--
-- Run order: migration BEFORE deploying new code to Pi.
-- After running, scp reach_engine.py + hooks.py + reach_cron.py to Pi.
-- line-webhook-service (uses set_alert.py) also needs docker compose build.

-- ── thay_ai ──────────────────────────────────────────────────────────────────

CREATE TABLE thay_ai.reach_user_rules (
    id            SERIAL PRIMARY KEY,
    duply_id      TEXT NOT NULL,
    trigger_type  TEXT NOT NULL DEFAULT 'price_alert',
    condition     JSONB NOT NULL,
    status        TEXT NOT NULL DEFAULT 'active',
    fired_at      TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_thay_reach_user_rules_active
  ON thay_ai.reach_user_rules (status) WHERE status = 'active';
CREATE INDEX idx_thay_reach_user_rules_duply
  ON thay_ai.reach_user_rules (duply_id, status);

-- Migrate existing rows (one-shot rules keep their status: active → active, fired → fired)
INSERT INTO thay_ai.reach_user_rules
  (duply_id, trigger_type, condition, status, fired_at, created_at)
SELECT
  duply_id,
  'price_alert',
  jsonb_build_object('ticker', ticker, 'op', condition, 'value', threshold),
  status,
  fired_at,
  created_at
FROM thay_ai.reach_custom_rules;

DROP TABLE thay_ai.reach_custom_rules;

-- ── khun_ai ───────────────────────────────────────────────────────────────────

CREATE TABLE khun_ai.reach_user_rules (
    id            SERIAL PRIMARY KEY,
    duply_id      TEXT NOT NULL,
    trigger_type  TEXT NOT NULL DEFAULT 'price_alert',
    condition     JSONB NOT NULL,
    status        TEXT NOT NULL DEFAULT 'active',
    fired_at      TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_khun_reach_user_rules_active
  ON khun_ai.reach_user_rules (status) WHERE status = 'active';
CREATE INDEX idx_khun_reach_user_rules_duply
  ON khun_ai.reach_user_rules (duply_id, status);

-- Khun has no existing rules (stub hooks, reach.alert not yet enabled)
-- but migrate any rows that exist just in case:
INSERT INTO khun_ai.reach_user_rules
  (duply_id, trigger_type, condition, status, fired_at, created_at)
SELECT
  duply_id,
  'price_alert',
  jsonb_build_object('ticker', ticker, 'op', condition, 'value', threshold),
  status,
  fired_at,
  created_at
FROM khun_ai.reach_custom_rules;

DROP TABLE khun_ai.reach_custom_rules;

-- ── Verification ─────────────────────────────────────────────────────────────
-- Run these SELECTs to confirm migration succeeded:
--
-- SELECT COUNT(*) FROM thay_ai.reach_user_rules;
-- SELECT COUNT(*) FROM khun_ai.reach_user_rules;
-- SELECT * FROM thay_ai.reach_user_rules LIMIT 5;
