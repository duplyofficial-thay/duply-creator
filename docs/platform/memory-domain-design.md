# Memory Domain — Design

Scope: `Thay.memory.dream` (nightly consolidation agent). `Thay.memory.noter`
(per-turn extraction, the other agent in this domain) has its own operational
detail in `CLAUDE.md`/`CLAUDE-TOOLS.md` — not duplicated here; this doc only
covers dream's decisions.

For current file paths, schema, config values, and the agent's turn-by-turn
flow, see `memory-domain-reference.md`. For dated history (incidents, build
sessions, migrations applied), see `docs/progress/DREAM-PROGRESS.md`. This
doc is for **why**, not **what** or **when**.

---

## Why dream exists

Reactive chat (`chat.reply`) responds turn-by-turn and can't see the shape of
a user's behavior across many conversations. Dream runs nightly, reads the
accumulated log since the user's last run, and proposes two kinds of
structured state: durable **memories** (topic + summary, e.g. a holding
thesis) and **profile observations** (a field/value change with evidence).
Neither is written directly — `rules.py` is the sole gate, per the platform
principle "LLM proposes → Python decides" (`CLAUDE.md`).

## Per-Duple MemConfig (2026-07-24, replaces ArchetypeConfig registry)

Phase 3 (2026-07-16) moved finance's topics/fields into `archetypes.py`'s
`ArchetypeConfig` registry keyed by archetype string (`"finance"`,
`"lifestyle"`). That worked for two Duples with identical config but broke
immediately: Khun shared Thay's finance config because both are finance —
so adding a Duple with different finance config was impossible without adding
a new archetype string, which adds a new registry entry the platform team
controls instead of the Duple owner.

**2026-07-24 refactor:** `ArchetypeConfig` registry replaced by per-Duple
`mem_config.py` files (`duples/{id}/mem_config.py`), mirroring the
`card_config.py` pattern used for chat. `archetypes.py` defines the
`MemConfig` dataclass and a `load_mem_config(duple_id)` importlib loader;
platform code is archetype-agnostic. Each Duple owns its config directly
instead of sharing it through an archetype string.

```python
# duples/thay/mem_config.py
MEM_CONFIG = MemConfig(
    default_topics=["personal_facts", "investment_pattern", "holding_thesis"],
    observable_fields=frozenset({"risk_appetite", "trading_style", ...}),
    holdings_topic="holding_thesis",  # finance only
)
```

Two field categories, intentionally separated:

- **`FLAT_PROFILE_FIELDS`** (platform-fixed, same for every Duple) — flat
  schema columns in `user_profiles`: `knowledge_level`, `goal`,
  `behavior.tags`, `preferences.response_length`, `preferences.tone`. Not
  configurable. Dream/noter may always observe these.
- **`observable_fields`** (per-Duple, in `MemConfig`) — archetype-specific
  JSONB fields stored in `user_profiles.archetype_data`. Finance Duples list
  `risk_appetite`, `trading_style`, `time_horizon`, `investment_style`.
  A lifestyle Duple lists whatever fields its schema actually has. The allowed
  set for rules.py is `FLAT_PROFILE_FIELDS | mem_config.observable_fields`.

Three decisions still worth keeping:

- **Plain Python file, not DB-driven.** `rules.py` is the correctness gate
  behind "LLM never writes to DB directly." A DB-editable allowlist would let
  a bad edit silently defeat that gate — a different, worse risk class than
  `agent_profiles.tools_enabled` (which only degrades LLM *capability*, never
  data correctness). Keep this in code, reviewed like any other change.
- **Explicit parameter, never a module-level global.** `dream.py`'s `main()`
  loops every active Duple in one process — a global would leak one Duple's
  config into another's request mid-loop.
- **Unknown/missing mem_config degrades to DEFAULT_MEM_CONFIG, never
  silently inherits finance's write behavior.** `load_mem_config()` falls
  back to `DEFAULT_MEM_CONFIG` (personal_facts only, no holdings sync) on
  any import error. A missing file reduces capability, never grants a Duple
  finance's ticker-writing/holdings-sync logic it never asked for.

## Prompt: Supabase blocks, not disk files (2026-07-16)

Replaced `prompts/core/dream.txt` + `prompts/{archetype}/dream.txt` assembly
with the same two-part pattern `chat.noter` uses: locked platform blocks in
`public.agent_profiles.system_prompt`, Duple-owned overrides in
`{schema}.agent_profiles.duple_prompt`. `[[ALLOWED_FIELDS]]`/`[[DEFAULT_TOPICS]]` sentinels in the template fill
from the same `MemConfig` that `rules.py` enforces against — one source of
truth for what the prompt *tells* the LLM and what `rules.py` *allows* it
to do. `get_agent_prompt()` returns `{}` when a Duple has no DB row rather
than raising — the platform template in `public.agent_profiles` is
self-sufficient. Only `instructions` and `output_format` are required
blocks; `focus_areas` is optional (Duple-specific guidance, can be empty).

## Memory status machine — why `archived` is single-purpose

`archived` is reserved exclusively for `archive_pending_by_ids()`'s
consumed-pending sweep (pending → archived after dream reads it). No other
code path may ever write it. This is a hard-won constraint: an earlier
version let the `deactivate` *action* write `status: "archived"` too,
matched only by `(duply_id, topic)`. Since `fetch_context()` never reads
`archived` rows, an archived default topic became invisible to dream — a
later run then recreated it from scratch, silently losing everything the old
row held. Full incident writeup: `docs/progress/DREAM-PROGRESS.md`
(2026-07-06). The fix (`deactivate` → `inactive`, not `archived`) is why
`inactive` supports reactivation (`priority: active` on an `inactive` row
flips it back in the same write) and why default topics are locked out of
`deactivate`/`create(priority=inactive)` entirely — see reference doc for
the current rule text.

`archive_pending_by_ids(ids)` archives only the IDs captured in
`fetch_context` before the LLM call — not all pending rows at that moment.
This prevents a race condition where noter writes that arrive during the
dream run get silently consumed (old `archive_all_pending()` archived
everything regardless of when it was written).

## Redis: DEL + SET, never TTL

`_refresh_redis()` always deletes then sets, never sets with an expiry. A
TTL'd key can be served stale between expiry and the next dream run; DEL+SET
guarantees a key is either fresh or absent — callers must already handle
"key missing" (Supabase fallback), so a fresh miss is a safe failure mode
where a stale hit would not be.

## Deferred / open

- **Noter fragmentation (still open).** `memory.noter`'s upsert only checks
  for an existing `pending` row before merge-vs-insert — never `active`/
  `inactive`. Since `archive_pending_by_ids()` clears the pending pool every
  cycle, noter's next observation on an already-consolidated topic inserts a
  new orphaned row instead of merging into the canonical one (confirmed
  live: rows accumulated under one topic for a single user). Scoped, not
  implemented — see `docs/progress/DREAM-PROGRESS.md`.
- **`prompts/*.txt` cleanup debt.** The disk-based prompt files are dead
  code since the Supabase-blocks migration above but haven't been deleted
  yet — still present on both Mac and Pi as of 2026-07-17. Low risk (nothing
  imports them) but worth removing once someone's touching this directory
  again, to stop them reading as live.
