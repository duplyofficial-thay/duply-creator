# Domains — What Each Part Does

A Duple is composed of domains. Each domain is a distinct capability with its own agents, configuration, and gate.

---

## chat — Reactive Chat (always on)

**What it does:** Handles every incoming LINE message. Classifies intent, routes to AI lane (LLM reply), card lane (pre-built response), or service lane (data mutation like watchlist update). Writes to `interact_log` after every turn. Dispatches `memory.noter` in the background.

**What you configure:**
- `system_prompt` in `{schema}.agent_profiles` for `chat.reply` — persona, instructions, tool guidance, coverage scope. Add any blocks you want; all keys are included in the prompt automatically.
- `chat/reply/context_builder.py` — how your Duple assembles per-turn context (user profile, memory, history, real-time data). Unique to `chat` because each turn needs live context; reach/memory agents don't.
- `chat/router/router_config.yaml` — routing rules (which phrases trigger cards vs AI)
- `CHAT.gate_roles` in `duple_settings.py` — who can chat (default: `"creator"` — change to `"all"` to open)

**Tools available to your Duple**

Tools are assigned per Duple in `{schema}.agent_profiles.tools_enabled`. Check yours:
```sql
SELECT agent_id, tools_enabled FROM {schema}.agent_profiles WHERE agent_id = 'chat.reply';
```

Tools are organised into packs. The packs your Duple has depend on your archetype and what the Duply team added after provisioning. See **[guide/tool-catalog.md](tool-catalog.md)** for the full up-to-date list with all args.

The packs:
- **`generic`** — all archetypes (`get_search`, `get_memories`, `get_knowledge`, `set_alert`)
- **`finance.generic`** — all finance Duples (`get_watchlist`, `update_watchlist`)
- **`finance.set`** — SET-market Duples (`get_stock_set`, plus shared sector/macro/screener tools)
- **`finance.us`** — US-market Duples (`get_stock_us`, plus shared sector/macro/screener tools)

If your finance Duple covers both markets, the team can add both packs.

---

## memory — Memory System

### mem_config.py — per-Duple memory schema

`duples/{duple_id}/mem_config.py` tells the memory agents what your Duple's memory schema looks like. It is generated automatically by `provision_duple.py` — you normally don't need to touch it unless you're adding custom profile fields.

```python
MEM_CONFIG = MemConfig(
    default_topics=["personal_facts", "investment_pattern", "holding_thesis"],
    observable_fields=frozenset({
        "risk_appetite", "trading_style", "time_horizon", "investment_style",
    }),
    holdings_topic="holding_thesis",  # finance only — set to None if not applicable
)
```

| Field | What it controls |
|---|---|
| `default_topics` | Topics dream/noter will always maintain. Protected — can't be deactivated by the LLM. |
| `observable_fields` | Archetype-specific JSONB fields in `user_profiles.archetype_data` that dream/noter are allowed to observe and update. |
| `holdings_topic` | If set, create/update actions on this topic may include a `tickers: [...]` list that syncs to `archetype_data.holdings`. Finance-only. |

Platform-level fields (`knowledge_level`, `goal`, `behavior.tags`, `preferences.response_length`, `preferences.tone`) are always observable for every Duple — they don't need to be listed in `observable_fields`.

A change to `mem_config.py` requires a Docker rebuild (`docker compose build dream-agent`).

### memory.noter (per-turn extraction)

**What it does:** After every AI-lane reply, extracts facts, preferences, and context from the conversation and writes them to `{schema}.user_memories` as `pending` rows. Runs in a background thread — never delays the reply. Only fires for users who pass `MEMORY.gate_roles`.

**What you configure:**
- `MEMORY.gate_roles` in `duple_settings.py` — which users get memory extracted (default: `"creator"`)
- `focus_areas` block in `{schema}.agent_profiles.system_prompt` for `memory.noter` — Duple-specific extraction guidance: what topics to prioritize, what to ignore, personas-specific signals. Leave empty to use the platform default.

**Blocks noter reads from `system_prompt`** (platform template provides all required ones — you only need `focus_areas`):

| Block | Required | What it does |
|---|---|---|
| `output_format` | ✅ platform | JSON schema for the LLM's output |
| `instructions` | ✅ platform | Core extraction rules |
| `importance_guide` | ✅ platform | How to score importance 1–10 |
| `bond_rules` | ✅ platform | Closeness/rapport delta rules |
| `focus_areas` | optional | Your Duple's specific extraction focus |

All required blocks come from the locked platform template in `public.agent_profiles`. You only add `focus_areas` in your schema's `agent_profiles` row if you want custom guidance.

### memory.dream (nightly consolidation)

**What it does:** Nightly job (04:00 BKT). Reads all `pending` rows accumulated since the last run, consolidates into long-term memories (create/update/deactivate actions), updates user profile observations. This is what makes the Duple feel like it "remembers" across sessions.

**What you configure:**
- `MEMORY.enabled` in `duple_settings.py` — set to `False` to skip dream entirely for this Duple (default: `True`)
- `focus_areas` block in `{schema}.agent_profiles.system_prompt` for `memory.dream` — Duple-specific consolidation guidance: which topics matter most, how to handle conflicting signals. Optional — platform template is self-sufficient.

**Blocks dream reads from `system_prompt`** (same pattern as noter):

| Block | Required | What it does |
|---|---|---|
| `instructions` | ✅ platform | Core consolidation logic |
| `output_format` | ✅ platform | JSON schema for memory actions + observations |
| `focus_areas` | optional | Your Duple's custom topic priorities |

Dream works even if your Duple has no `agent_profiles` row — the platform template alone is enough to run.

---

## reach — Proactive Messaging

### reach.alert (event-triggered push)

**What it does:** Sends proactive LINE push messages when configured triggers fire. Runs on a cron every 15 minutes. Event triggers (e.g. price alerts) handle their own market-state checks internally; schedule triggers fire based on time, any day.

**What you configure:**
- `REACH.enabled` in `duple_settings.py` — set to `False` to stop the cron from running at all (default: `True`)
- `REACH.gate_roles` in `duple_settings.py` — who receives alerts (default: `"creator"` during testing)
- `REACH.enabled_triggers` in `duple_settings.py` — which trigger types your Duple checks. Leave `[]` to disable all triggers. Fill in only the types your Duple monitors:
  ```python
  "enabled_triggers": ["price_above", "price_below"]   # price alerts (finance)
  ```
  Available trigger types depend on your archetype — ask the Duply team what's registered for yours.
- `system_prompt` in `{schema}.agent_profiles` for `reach.alert` — how alert messages are phrased. Only these keys are read: `coverage`, `stance`, `goal`, `philosophy`, `examples`. Other keys are ignored.

**Rollout pattern:** Start with `gate_roles: "creator"` (you only) → test with `gate_roles: "tester"` → open with `gate_roles: "all"`.  
Gate change requires editing `duple_settings.py` + a container restart (contact Duply team).

### reach.broadcast (admin push)

**What it does:** Sends a push message to a defined audience on demand. Useful for announcements, content drops, market summaries.

**Status:** Built, disabled by default. Contact the Duply team to enable and define your broadcast workflow.

---

## knowledge — Document Retrieval (RAG)

**What it does:** Ingests documents you provide → stores as vector embeddings in `{schema}.knowledge_chunks` → the `get_knowledge` tool retrieves relevant chunks when the LLM needs them.

**What you configure:**
- `KNOWLEDGE.enabled` in `duple_settings.py` — must be `True` before sending docs to ingest (default: `False`)
- `KNOWLEDGE.gate_roles` in `duple_settings.py` — who can query knowledge (default: `"creator"`)
- Content: send documents to the Duply team, who run `knowledge/ingest.py` on your behalf

**Status:** Pipeline is live. Ingestion is currently team-run (CLI). No self-serve upload UI yet.

**To activate knowledge for your Duple:**
1. Set `KNOWLEDGE.enabled = True` in `duple_settings.py`
2. Send your documents (text files) + source URLs to the Duply team
3. Make sure `get_knowledge` is in `tools_enabled` for `chat.reply` (team adds during provisioning if finance pack)
4. Update your `tools` block in `system_prompt` to tell the LLM when to call it

---

## Team post-provisioning steps

After the Duply team provisions a new Duple, they also need to:

1. **Add the webhook service to `infra/platform/docker-compose.yml`** on Pi:
   ```yaml
   {duple_id}-line-webhook-service:
     image: duply-platform:latest
     container_name: {duple_id}-line-webhook-service
     restart: always
     network_mode: host
     working_dir: /app/platform/chat
     command: ["python3", "line_webhook_service.py"]
     env_file:
       - ../../.env.platform
       # add ../../.env.archetype.finance if this is a finance Duple
       - ../../duples/{duple_id}/.env
     volumes:
       - ../../duples:/app/duples:ro
   ```
   Then: `docker compose -f infra/platform/docker-compose.yml up -d {duple_id}-line-webhook-service`

2. **Add a reach cron entry** (if REACH.enabled=True):
   ```
   2,17,32,47 * * * *  set -a; . /home/duply/duply-agents/.env; . /home/duply/duply-agents/duples/{duple_id}/.env; set +a; /usr/bin/python3 /home/duply/duply-agents/platform/reach/reach_cron.py >> /home/duply/duply-agents/platform/reach/reach_{duple_id}.log 2>&1
   ```

3. **Cloudflare Zero Trust** → Tunnels → Edit → Public Hostnames → Add:
   `webhook-{duple_id}.duply.org` → `http://localhost:{PORT}`

4. **LINE Console** → Messaging API → Webhook URL:
   `https://webhook-{duple_id}.duply.org/webhook` (enable + verify)

---

## What's Not Yet Configurable

| Feature | Status |
|---|---|
| `memory.invest` (portfolio manager) | Not built |
| `meta` agent (self-improving) | Not built |
| Social publishing (Facebook, Instagram) | Not built |
