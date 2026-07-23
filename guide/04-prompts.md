# Editing Prompts and Persona

Your Duple's behavior is driven by the `agent_profiles` table in your schema. You own the `duple_prompt` column — the platform owns `system_prompt`. You never touch `system_prompt`.

---

## Connecting to Your Schema

Use the credentials the Duply team gave you (role name + password) to connect to the shared Supabase Postgres instance. Any Postgres client works: psql, DBeaver, TablePlus, DataGrip, or just ask Claude Code to run the queries for you.

Connection details:
- **Host:** provided by Duply team
- **Database:** `postgres`
- **Schema:** `{your_duple_id}_ai`
- **Role:** `{your_duple_id}_role` (or as provided)

---

## The `agent_profiles` Table

```sql
SELECT agent_id, jsonb_pretty(system_prompt) FROM {schema}.agent_profiles;
```

One row per agent. The agents you'll edit most:

| `agent_id` | Purpose |
|---|---|
| `chat.reply` | Main chat persona — what users experience directly |
| `memory.noter` | What to extract and track from conversations |
| `memory.dream` | How to consolidate memories over time |
| `reach.alert` | How alerts are phrased |

---

## The `system_prompt` Column

A JSONB object — **this is the column you own and edit**. The exact keys vary per agent. Read what's already there before editing. For `chat.reply`, Thay's live keys as a reference:

```json
{
  "philosophy": "GARP + early-stage growth with catalysts. Small/mid caps fair game...",
  "platform":   "LINE chat. Lead with the point. 1-2 sentences per bubble, max 3 bubbles...",
  "tools":      "Priority: get_stock_us → get_macro_us. get_search only if asked...",
  "coverage":   "US-listed stocks and ETFs only. Other assets via proxy ETF.",
  "bond":       "0-1: new, guide gently. 3-6: direct, challenge. 6+: casual, roast ok...",
  "examples":   [{"user": "...", "thay": "..."}]
}
```

Keys are flexible — add, remove, or rename to fit your Duple's needs. The platform injects the entire `system_prompt` object into the model's context.

---

## How to Edit Safely

**Always use `jsonb_set()`** — not a plain `UPDATE ... SET system_prompt = '{...}'`. A full-column overwrite silently wipes every key you didn't include.

Update a single key:
```sql
UPDATE {schema}.agent_profiles
SET system_prompt = jsonb_set(system_prompt, '{philosophy}', '"Your philosophy here..."')
WHERE agent_id = 'chat.reply';
```

Add a new key:
```sql
UPDATE {schema}.agent_profiles
SET system_prompt = jsonb_set(system_prompt, '{coverage}', '"Focus on scheduling, tasks, and day-to-day planning."', true)
WHERE agent_id = 'chat.reply';
```

Remove a key:
```sql
UPDATE {schema}.agent_profiles
SET system_prompt = system_prompt - 'coverage'
WHERE agent_id = 'chat.reply';
```

---

## When Changes Take Effect

Prompt changes are **live immediately** — no redeploy needed. The platform caches prompts in Redis (24h TTL). To force an immediate refresh, ask the Duply team to flush `{duple_id}:agent:{agent_id}:prompt` from Redis, or just wait for the cache to expire.

---

## Tips

- **Test after every meaningful change.** Send a LINE message to your Duple and check the response. The platform logs every LLM call to `{schema}.agent_call_log` — useful for debugging.
- **Keep persona in `persona`, behavior rules in `instructions`.** Don't mix them into one long block — easier to edit individual aspects later.
- **noter and dream prompts matter.** If `chat.reply` is what users see, noter/dream are what make the Duple feel like it "gets" the user over time. Spend time on their extraction and consolidation rules.
