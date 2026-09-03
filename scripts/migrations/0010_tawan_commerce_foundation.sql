-- Tawan commerce foundation migration.
-- Duply must reconcile this with the authoritative Supabase migration repository
-- before applying it outside local verification.

CREATE TABLE __SCHEMA__.tawan_migration_probe (
    id          BIGSERIAL PRIMARY KEY,
    duple_id    TEXT NOT NULL DEFAULT '__DUPLE_ID__',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- DOWN

DROP TABLE __SCHEMA__.tawan_migration_probe;
