# Patch Notes

Changes to the Duply platform that affect Duple creators.

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
- `agent_profiles.duple_prompt` — creator-editable prompt layer, no redeploy needed
- `agent_call_log` — LLM call log per schema (cost, latency, cache hit rate)
- Telegram alerting for platform errors (Duply team only)
