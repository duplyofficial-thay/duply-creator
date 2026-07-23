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

**`chat.reply` key reference:**

| Key | Required | What it controls |
|---|---|---|
| `philosophy` | ✅ | Investment/domain philosophy, decision-making stance, personality under pressure |
| `platform` | ✅ | LINE-specific formatting rules — bubble length, line breaks, emoji use |
| `tools` | ✅ | When and how to call each tool. List your tools by priority order |
| `coverage` | ✅ | What topics this Duple covers and what falls outside its scope |
| `bond` | ✅ | How tone shifts with closeness score (0–10 scale in `user_profiles`) |
| `business` | optional | Business model, subscription info, paid features — leave empty if not relevant |
| `examples` | optional | List of `{user, <name>}` example Q&A pairs in your Duple's language/style |

Every key is injected into the prompt as `[KEY]\nvalue`. You can add custom keys — they'll appear in the same format. The one key you must never add here: **`output`** — that's a hardcoded code constant, not read from DB.

**Finance Duple (Thay) example:**
```json
{
  "philosophy": "GARP + early-stage growth with catalysts. Small/mid caps fair game...",
  "platform":   "LINE chat. Lead with the point. 1-2 sentences per bubble, max 3 bubbles...",
  "tools":      "Priority: get_stock → get_macro. Use get_watchlist when user asks 'what should I watch'. get_search only if they ask for news.",
  "coverage":   "US-listed stocks and ETFs only. Crypto only on direct ask.",
  "bond":       "0-1: new, guide gently. 3-6: direct. 6+: casual, roast ok.",
  "examples":   [{"user": "ASTS น่าซื้อมั้ย", "thay": "RSI 51 เพิ่งเด้งจาก EMA50..."}]
}
```

**Non-finance Duple (lifestyle/commerce) — same keys, different values:**
```json
{
  "philosophy": "Practical and warm. Help users find what suits them, not what's trending. No pressure.",
  "platform":   "LINE chat. Short and conversational. 1-2 sentences per bubble.",
  "tools":      "Use get_search when user asks about something specific or recent. Use get_memories before recommending — check what they've liked before.",
  "coverage":   "Fashion, wellness, food in Thailand. Finance and medical advice: acknowledge and redirect.",
  "bond":       "0-2: helpful stranger. 3-6: friend who knows your taste. 7+: casual, personal, know their style.",
  "examples":   []
}
```

The `tools` block is the most important difference across archetypes — describe exactly the tools your Duple actually has (check `tools_enabled` in Supabase).

---

**`reach.alert` key reference:**

Unlike `chat.reply`, the reach agent reads only these specific keys. Extra keys are ignored.

| Key | What it controls |
|---|---|
| `coverage` | What this Duple sends alerts about — which assets, which event types |
| `stance` | Tone: factual, cautious, energetic, etc. |
| `goal` | What a good alert achieves for the user |
| `philosophy` | High-level approach — what's worth interrupting the user for |
| `examples` | List of example alert messages (optional but useful for style consistency) |

**`output`** is code-locked — never set it here.

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
