# Editing Prompts and Persona

Your Duple's behavior is driven by **two separate tables**:

| Table | Column | What it holds | Scope |
|---|---|---|---|
| `public.duply_duples` | `persona` | Who your Duple is — character, tone, background | Shared across ALL agents |
| `{schema}.agent_profiles` | `system_prompt` | Per-agent operational config — tools, format rules, coverage | One row per agent |

Edit both. The platform injects `persona` first, then each agent's `system_prompt` on top.

---

## Connecting to Your Schema

Use the credentials the Duply team gave you (role name + password) to connect to the shared Supabase Postgres instance. Any Postgres client works: psql, DBeaver, TablePlus, DataGrip, or just ask Claude Code to run the queries for you.

Connection details:
- **Host:** provided by Duply team
- **Database:** `postgres`
- **Schema:** `{your_duple_id}_ai`
- **Role:** `{your_duple_id}_role` (or as provided)

---

## 1. Editing Persona (`public.duply_duples`)

This is the **shared character block** — who your Duple is at a human level. It's the same string injected into every agent (chat, reach, dream, noter). Write it like a brief character brief, not a system instruction.

Thay's real persona as a reference:
```
Thay: a Thai male US-stock companion, late 30s, ex-fund manager turned friend.
Direct, dry humor, no fluff, calm and warm, never dramatic.
Finance = expertise, outside finance = engage naturally.
Chat like a person, not a report.
```

Update yours:
```sql
UPDATE public.duply_duples
SET persona = 'Grace: ...'
WHERE duple_id = '{your_duple_id}';
```

Changes are live after Redis cache expiry (~24h) or a manual flush by the Duply team.

---

## 2. Editing Per-Agent Config (`{schema}.agent_profiles`)

Each agent has its own row with a `system_prompt` JSONB column. This is where operational behavior lives — tools routing, formatting rules, coverage scope, response examples.

Read what's there first:
```sql
SELECT agent_id, jsonb_pretty(system_prompt) FROM {schema}.agent_profiles;
```

The agents you'll edit most:

| `agent_id` | Purpose |
|---|---|
| `chat.reply` | Main chat behavior — tool priorities, format rules, coverage scope |
| `memory.noter` | What to extract and remember from conversations |
| `memory.dream` | How to consolidate memories into long-term topics |
| `reach.alert` | How alert messages are written |

Thay's `chat.reply` keys as a reference:
```json
{
  "philosophy": "GARP + early-stage growth with catalysts. Small/mid caps fair game...",
  "platform":   "LINE chat. Lead with the point. 1-2 sentences per bubble, max 3 bubbles...",
  "tools":      "Priority: get_stock_us → get_macro_us. get_search only if asked...",
  "coverage":   "US-listed stocks and ETFs only.",
  "bond":       "0-1: new, guide gently. 3-6: direct. 6+: casual, roast ok...",
  "examples":   [{"user": "ASTS น่าซื้อมั้ย", "thay": "RSI 51 เพิ่งเด้งจาก EMA50..."}]
}
```

Keys are flexible — add, remove, or rename to fit your Duple.

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
SET system_prompt = jsonb_set(system_prompt, '{coverage}', '"Your coverage scope here."', true)
WHERE agent_id = 'chat.reply';
```

Remove a key:
```sql
UPDATE {schema}.agent_profiles
SET system_prompt = system_prompt - 'bond'
WHERE agent_id = 'chat.reply';
```

---

## When Changes Take Effect

- **`public.duply_duples.persona`** — live after Redis cache expiry (~24h) or manual flush
- **`{schema}.agent_profiles.system_prompt`** — same cache TTL, same flush path

Ask the Duply team to flush `{duple_id}:agent:{agent_id}:prompt` from Redis for an immediate update.

---

## Tips

- **`persona` = character, `system_prompt` = behavior.** Don't mix them — keep persona human-readable, keep system_prompt operational.
- **Test after every meaningful change** via LINE. Check `{schema}.agent_call_log` if something looks off.
- **noter and dream prompts matter as much as chat.reply.** They shape what the Duple remembers and how it builds user understanding over time.
