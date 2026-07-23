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
SELECT agent_id, jsonb_pretty(duple_prompt) FROM {schema}.agent_profiles;
```

One row per agent. The agents you'll edit most:

| `agent_id` | Purpose |
|---|---|
| `chat.reply` | Main chat persona — what users experience directly |
| `memory.noter` | What to extract and track from conversations |
| `memory.dream` | How to consolidate memories over time |
| `reach.alert` | How alerts are phrased |

---

## The `duple_prompt` Column

A JSONB object. The exact keys vary per agent — read what's already there before editing. General structure for `chat.reply`:

```json
{
  "persona": "You are Grace, a concise lifestyle assistant...",
  "instructions": "Keep replies short. Never use bullet points for simple answers...",
  "tools": "Use get_search for current events. Only call get_memories when [MEMORY TOPICS] appears in context...",
  "coverage": "Focus on scheduling, tasks, and day-to-day lifestyle..."
}
```

You can add, modify, or remove keys. The platform injects the entire `duple_prompt` object into the model's system message.

---

## How to Edit Safely

**Always use `jsonb_set()`** — not a plain `UPDATE ... SET duple_prompt = '{...}'`. A full-column overwrite silently wipes keys you didn't include.

Update a single key:
```sql
UPDATE {schema}.agent_profiles
SET duple_prompt = jsonb_set(duple_prompt, '{persona}', '"You are Grace, a concise lifestyle assistant who..."')
WHERE agent_id = 'chat.reply';
```

Add a new key:
```sql
UPDATE {schema}.agent_profiles
SET duple_prompt = jsonb_set(duple_prompt, '{coverage}', '"Focus on scheduling, tasks, and day-to-day planning."', true)
WHERE agent_id = 'chat.reply';
```

Remove a key:
```sql
UPDATE {schema}.agent_profiles
SET duple_prompt = duple_prompt - 'coverage'
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
