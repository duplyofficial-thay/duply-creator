# Concepts — How Duply Works

## Vocabulary

| Term | Meaning |
|---|---|
| **Duply** | The platform layer — shared infra (auth, routing, identity, Redis, DB) |
| **Duple** | One AI product built on Duply. Has its own persona, tools, schema, LINE OA |
| **Agent** | A named component inside a Duple. Named `{duple}.{domain}.{function}`, e.g. `Thay.chat.reply` |
| **agent_id** | The schema-relative ID used in DB. No Duple prefix: `chat.reply`, `memory.dream`. Schema provides the context |
| **duply_id** | User ID — text format like `A0002`. Not a UUID |
| **duple_id** | Which Duple a user is talking to — e.g. `thay`, `grace` |
| **archetype** | Category of Duple: `finance`, `lifestyle`, `commerce`. Controls which tool packs are available |
| **schema_name** | Each Duple gets its own Postgres schema: `{duple_id}_ai` |

---

## The Three-Tier Model

```
platform/      ← shared code: chat shell, tool registry, memory engine, reach engine
archetype/     ← shared tool packs per category (finance tools, lifestyle tools)
duple/         ← your code: persona, router config, card config, duple_settings.py
```

Your work as a creator lives entirely in the **duple tier** — the `duples/<duple_id>/` folder and your schema in Supabase. You never touch platform or archetype code.

---

## The Core Rule

**LLM proposes → Python decides → DB writes**

The model never writes to the database directly. Every write goes through Python validation rules. This means:
- Your persona and instructions live in `agent_profiles` (Supabase table)
- The platform reads them at runtime and injects them into the model's context
- You edit prompts in the DB — no code deploy needed for prompt changes

---

## Schema Isolation

Your Duple gets its own Postgres schema (`{duple_id}_ai`) and a dedicated native Postgres role scoped to that schema only. That role cannot read or write any other Duple's data. The Duply team verifies this isolation before handing you the credentials.

---

## Agents in a Duple

Every Duple runs the same set of agents (configured differently per Duple):

| Agent | What it does |
|---|---|
| `chat.reply` | Handles each LINE message — routes to AI, card, or service response |
| `memory.noter` | Extracts memories from each AI-lane turn (runs after reply is sent) |
| `memory.dream` | Nightly consolidation of memories into long-term topics (04:00 BKT) |
| `reach.alert` | Proactive push messages triggered by market events or user-set alerts |
| `reach.broadcast` | Admin-initiated push to all users (disabled by default) |
| `knowledge.extract` | Ingests documents for RAG retrieval via `get_knowledge` tool |

Each agent has its own prompt block in `{schema}.agent_profiles`. You configure persona and behavior there.
