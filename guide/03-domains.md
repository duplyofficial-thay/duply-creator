# Domains — What Each Part Does

A Duple is composed of domains. Each domain is a distinct capability with its own agents, configuration, and gate.

---

## chat — Reactive Chat (always on)

**What it does:** Handles every incoming LINE message. Classifies intent, routes to AI lane (LLM reply), card lane (pre-built response), or service lane (data mutation like watchlist update). Writes to `interact_log` after every turn. Dispatches `memory.noter` in the background.

**What you configure:**
- `duple_prompt` in `agent_profiles` for `chat.reply` — your persona, instructions, tool guidance, coverage scope
- `router_config.yaml` — routing rules (which phrases trigger cards vs AI)
- `CHAT.gate_roles` in `duple_settings.py` — who can chat (default: `"all"`)

**Tools available to your Duple**

Tools are assigned per Duple in `{schema}.agent_profiles.tools_enabled`. Check yours:
```sql
SELECT agent_id, tools_enabled FROM {schema}.agent_profiles WHERE agent_id = 'chat.reply';
```

Tools are organised into packs. The packs your Duple has depend on your archetype and what the Duply team added after provisioning.

**Generic pack** — available to all archetypes:

| Tool | What it does |
|---|---|
| `get_search` | Search recent news by keyword |
| `get_memories` | Fetch user's long-term memory topics |
| `get_knowledge` | Search ingested documents (requires knowledge enabled) |
| `set_alert` | Set a price alert for a ticker (requires reach.alert enabled) |

**Finance generic pack** (`finance.generic`) — added to all finance Duples by default:

| Tool | What it does |
|---|---|
| `get_watchlist` | User's saved tickers with current price and tags |
| `get_earnings` | Upcoming earnings dates, EPS, beat/miss |
| `get_calendar` | This week's earnings + high-impact economic events |
| `get_sector` | Overview of all major market sectors |
| `get_macro` | Macro price data or macro news |
| `get_theme` | 21 market themes (tech, energy, defence, etc.) |

**Finance market packs** — one of these is added by the Duply team after provisioning, depending on your Duple's market focus:

| Pack | Tool | What it does |
|---|---|---|
| `finance.set` | `get_stock` | Full price + technical + fundamental + news analysis for SET-listed tickers |
| `finance.us` | `get_stock` | Same analysis for US-listed tickers |

If your finance Duple covers both markets, the team can add both packs.

---

## memory — Memory System

### memory.noter (per-turn extraction)

**What it does:** After every AI-lane reply, extracts facts, preferences, and context from the conversation and writes them to `{schema}.memory_topics`. Runs in a background thread — never delays the reply.

**What you configure:**
- `duple_prompt` in `agent_profiles` for `memory.noter` — extraction focus, what to track, what to ignore

### memory.dream (nightly consolidation)

**What it does:** Nightly job (04:00 BKT). Reads all `pending` memory rows accumulated that day, consolidates into long-term topics, updates/archives/creates entries. This is what makes the Duple feel like it "remembers" across sessions.

**What you configure:**
- `duple_prompt` in `agent_profiles` for `memory.dream` — consolidation style, topic taxonomy, retention rules

**Note:** dream runs automatically on all Duples each night. No gate needed.

---

## reach — Proactive Messaging

### reach.alert (event-triggered push)

**What it does:** Sends proactive LINE push messages when user-configured triggers fire — e.g. a price alert the user set via `set_alert`. Runs on a cron every 15 minutes on market days.

**What you configure:**
- `REACH.gate_roles` in `duple_settings.py` — who receives alerts (default: `"creator"` during testing)
- `REACH.enabled_triggers` — which trigger types your Duple supports (e.g. `["price_above", "price_below"]`)
- `duple_prompt` in `agent_profiles` for `reach.alert` — how alert messages are phrased

**Rollout pattern:** Start with `gate_roles: "creator"` (you only) → test with `gate_roles: "tester"` → open with `gate_roles: "all"`.  
Gate change requires editing `duple_settings.py` + a rebuild (contact Duply team).

### reach.broadcast (admin push)

**What it does:** Sends a push message to a defined audience on demand. Useful for announcements, content drops, market summaries.

**Status:** Built, disabled by default. Contact the Duply team to enable and define your broadcast workflow.

---

## knowledge — Document Retrieval (RAG)

**What it does:** Ingests documents you provide → stores as vector embeddings in `{schema}.knowledge_chunks` → the `get_knowledge` tool retrieves relevant chunks when the LLM needs them.

**What you configure:**
- Content: send documents to the Duply team, who run `knowledge/ingest.py`
- `KNOWLEDGE.gate_roles` in `duple_settings.py`

**Status:** Pipeline is live. Ingestion is manual (CLI). No self-serve upload UI yet.

---

## What's Not Yet Configurable

| Feature | Status |
|---|---|
| Custom card types | Currently Thay-specific. Contact Duply team if your Duple needs stock cards or custom card layouts |
| `memory.invest` (portfolio manager) | Not built |
| `meta` agent (self-improving) | Not built |
| Social publishing (Facebook, Instagram) | Not built |
