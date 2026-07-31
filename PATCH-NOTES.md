# Patch Notes

Changes to the Duply platform that affect Duple creators.

---

## v0.4.0 — Dom provisioned + creator schema autonomy (2026-07-31)

### Dom (`dom_ai`) provisioned

Dom is live in Supabase. Schema, role, base tables, and 5 agent_profiles are ready.
Credentials sent separately — connect via psql or TablePlus with the `dom_role` connection string.

### Creators can now manage their own schema

`dom_role` (and all future Duple roles) now has `CREATE` privilege on its own schema.
You can `CREATE TABLE`, `DROP TABLE`, `ALTER TABLE` in `dom_ai` directly — no need to
wait for the Duply team to run migrations for you.

An event trigger (`auto_grant_on_create`) is installed automatically: any table you
create is immediately accessible to the platform (`service_role`, `anon`, `authenticated`)
without any extra `GRANT` step on your end.

This means you can iterate on your schema freely via psql or any Postgres client.

### reach.schedule — coming to platform (not yet shipped)

Dom's `schedule/` domain (bedtime reminders, quest-due nudges) will be absorbed into
the platform as `reach_schedule_engine` — a third handler in `reach_cron` alongside
`alert` and `broadcast`. This covers the "time-based recurring push" pattern generically,
so Dom and any future Duple can use it without building their own cron infrastructure.

A new `reach_schedules` table will be added to `schema_template.sql` when this ships.
**Dom: hold off on building `duple/schedule/` for now** — use `reach_schedules` instead
once it's available. We'll update here when it's ready.

### provision_duple.py bug fix

`pgrst.db_schemas` update step now uses `quote_literal()` instead of `format()/%L`
(the Supabase API was rejecting `%` in SQL strings). No impact on existing Duples.

---

## v0.3.0 — yaml-driven router + per-Duple service wording (2026-07-28)

### `router_config.yaml` — new sections

The router now reads two additional sections from your Duple's
`router_config.yaml`. Previously SERVICE and postback patterns were hardcoded
in platform code; they are now fully creator-configurable.

**`service_routes`** — text patterns that route to the SERVICE lane:
```yaml
service_routes:
  # Always include LANG_UPDATE so users can switch TH/EN
  - patterns: ["TH", "EN", "TH LANG", "EN LANG"]
    match: exact
    type: LANG_UPDATE
    payload: self

  # Uncomment to enable watchlist add/remove:
  # - patterns: ["ADD "]
  #   match: prefix
  #   type: PROFILE_UPDATE
  #   op: add
  #   field: watchlist
  #   max: 5
  #   payload: rest_words
```

**`postback_routes`** — LINE card button callbacks (finance Duples only):
```yaml
postback_routes:
  - patterns: ["TAG|"]
    match: prefix
    card_type: tag_info
    payload: rest
```

**`ticker_regex`** — now optional. Omit it (or set it to nothing) for
non-finance Duples and the router will never try to match tickers:
```yaml
ticker_regex: "^[A-Z][A-Z0-9.]{0,9}$"   # SET market (DR tickers up to 10 chars)
# ticker_regex: "^[A-Z][A-Z0-9.]{0,5}$"  # US market (max 6 chars)
# omit entirely → no ticker routing
```

`provision_duple.py` scaffolds `service_routes` with LANG_UPDATE pre-wired
and PROFILE_UPDATE commented as an example.

### New file: `chat/service/service_messages.py`

SERVICE lane reply wording is now per-Duple. A new file
`duples/<id>/chat/service/service_messages.py` provides
`render_service_messages(result)` — the function that turns a `run_service()`
result dict into user-facing LINE message strings.

`provision_duple.py` generates this file automatically (Thai wording default).
Edit it to customize confirmation messages for your Duple's language and persona.

```python
# Example: change the add-to-watchlist confirmation text
if op == "add":
    if added:
        lines.append(f"เพิ่ม {', '.join(added)} เรียบร้อยครับ ({n}/{mx})")
```

### PROFILE_UPDATE action (replaces WATCHLIST_ADD / WATCHLIST_DEL)

The SERVICE lane action types `WATCHLIST_ADD` and `WATCHLIST_DEL` have been
renamed to `PROFILE_UPDATE`. If you have any custom code that pattern-matches
on `result["action"]`, update those checks:

```python
# Before
if result["action"] == "WATCHLIST_ADD": ...

# After
if result["action"] == "PROFILE_UPDATE" and result["op"] == "add": ...
```

The result shape also changed:

| Field | Before | After |
|-------|--------|-------|
| action | `"WATCHLIST_ADD"` / `"WATCHLIST_DEL"` | `"PROFILE_UPDATE"` |
| list key | `"watchlist"` | `"list"` (generic) |
| count key | `"watchlist_count"` | `"count"` |
| `op` | — | `"add"` / `"remove"` |
| `field` | — | `"watchlist"` (or any archetype_data field) |

---

## v0.2.0 — Domain Gate System (2026-07-23)

### Domain gates are now fully enforced

All four domains now have live `enabled` + `gate_roles` flags in `duple_settings.py` that the platform actually reads:

| Domain | `enabled` | `gate_roles` |
|--------|-----------|--------------|
| `CHAT` | — (always on) | ✅ gatekeeper — controls who can message |
| `REACH` | ✅ reach_cron exits early if False | ✅ controls who receives alerts |
| `MEMORY` | ✅ dream skips this Duple if False | ✅ noter skips users who don't qualify |
| `KNOWLEDGE` | ✅ ingest.py refuses to run if False | ✅ controls who can query |

Previously `MEMORY.enabled` and `KNOWLEDGE.enabled` were declared in `duple_settings.py` but not enforced. Now they are.

### Other changes

- `duple_settings.py` — `enabled` field added to `REACH`, `MEMORY`, `KNOWLEDGE` blocks in the generated scaffold
- Editing files in `duples/` now only requires a **container restart**, not a rebuild (bind mount added to all webhook services)
- `system_prompt` — corrected terminology in guide (was incorrectly called `duple_prompt` in some docs)
- Guide: team post-provisioning checklist added to `guide/03-domains.md` (docker-compose entry, cron, Cloudflare, LINE Console steps)

---

## v0.1.0 — Platform Launch (2026-07-23)

Initial release. The following is available for new Duples from day one.

### Chat

- LINE webhook handler with signature verification
- Three response lanes: AI (LLM), Card (pre-built response), Service (data mutation)
- Intent router via `router_config.yaml` — creator-configurable
- Full conversation history injected as real `user`/`assistant` messages (not a flattened string)
- `interact_log` written after every turn

### Memory

- **memory.noter** — per-turn extraction, runs after every AI-lane reply (background thread, no latency impact)
- **memory.dream** — nightly consolidation at 04:00 BKT, creates/updates/archives long-term memory topics

### Reach

- **reach.alert** — proactive price alerts via LINE push, cron every 15 minutes on market days
- **reach.broadcast** — admin-initiated push messaging (built, disabled by default — contact Duply team to enable)
- Role-based rollout gate (`creator` → `tester` → `all`) for each domain independently

### Tools (archetype = finance)

- `get_stock` — PT + BF + NS analysis, multi-ticker support
- `get_watchlist` — user's saved tickers with price and analysis tags
- `get_earnings` — earnings dates, EPS, beat/miss history
- `get_calendar` — this week's earnings + high-impact economic events
- `get_sector` — major sector overview
- `get_macro` — macro price data or macro news
- `get_theme` — 21 market themes
- `set_alert` — set price alerts (above/below) for any ticker
- `get_search` — news search by keyword or topic
- `get_memories` — retrieve user's long-term memory topics
- `get_knowledge` — RAG search over ingested documents

### Infrastructure

- Native Postgres role isolation per Duple schema — role cannot access other Duples' data
- Per-Duple `duple_settings.py` for domain gates and enabled triggers
- `agent_profiles.system_prompt` — creator-editable prompt layer, no redeploy needed
- `agent_call_log` — LLM call log per schema (cost, latency, cache hit rate)
- Telegram alerting for platform errors (Duply team only)
