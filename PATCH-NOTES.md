# Patch Notes

Changes to the Duply platform that affect Duple creators.

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
