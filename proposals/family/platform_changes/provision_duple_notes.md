# `scripts/provision_duple.py` changes needed for the `family` archetype

Line references are against the current file **after** the 2026-07-28 upstream update
(commits `23376f1`/`29cbbe3`/`dc3dc81`/`3893ddb`/`e7b70d3`, "yaml-driven router + per-Duple
service wording" v0.3.0) — this notes file was rewritten once against that version, so it
should stay accurate unless the file moves again before this is reviewed. All of this is
platform-tier — only the Duply team can make and run these changes.

## 1. Archetype whitelist (line 187)

```python
if archetype not in ("finance", "lifestyle", "commerce"):
```
→
```python
if archetype not in ("finance", "lifestyle", "commerce", "family"):
```

Also update the error message on the same line and the comment in `register/_template.yaml` (`archetype: "" # finance | lifestyle | commerce` → add `| family`).

## 2. `_AGENTS` → needs a 6th, archetype-conditional agent (lines 39–45)

Today `_AGENTS` is a flat list applied to every archetype uniformly. The `family` archetype needs one more agent — `schedule.nudge` — for daily bedtime/routine/quest-due reminders (see `../duple/schedule/` in this proposal for the actual engine+cron code, and the plan file's §1 for why this isn't just a repurposed `reach.alert`).

Minimal-diff refactor:
```python
_AGENTS_BASE = [
    "chat.reply",
    "memory.dream",
    "memory.noter",
    "reach.alert",
    "knowledge.extract",
]

_ARCHETYPE_EXTRA_AGENTS: dict[str, list[str]] = {
    "family": ["schedule.nudge"],
}

def _agents_for(archetype: str) -> list[str]:
    return _AGENTS_BASE + _ARCHETYPE_EXTRA_AGENTS.get(archetype, [])
```

Then wherever `for agent_id in _AGENTS:` iterates during agent_profiles seeding, swap in `for agent_id in _agents_for(archetype):`. Zero effect on existing finance/lifestyle/commerce Duples — they get exactly the same 5 agents as before.

## 3. `_TOOLS` — add a `"family"` entry (alongside `finance`/`lifestyle`/`commerce`, lines 47–71)

```python
"family": {
    "chat.reply":        ["generic", "family.quest", "family.guild", "family.parent"],
    "schedule.nudge":     [],  # template-driven pushes, not tool-calling — see prompts/schedule_nudge_system_prompt.json
    "reach.alert":        [],  # unused — REACH.enabled=False in duple_settings.py for this archetype
    "memory.noter":       [],
    "memory.dream":       [],
    "knowledge.extract":  [],
},
```

## 4. `_DEFAULT_PROMPTS` — add `family`-flavored seeds, and note the noter/dream key change (lines 79–124)

**Important:** the `dc3dc81` "fix provision noter/dream seed" commit changed what `memory.noter`/`memory.dream` actually read. The old `{"note": "..."}` placeholder was silently ignored — the real (only) creator-configurable key is `focus_areas`:

```python
"memory.noter": {"focus_areas": ""},
"memory.dream": {"focus_areas": ""},
"knowledge.extract": {},
```

Real drafted content for these two lives in `../prompts/memory_noter_system_prompt.json` and `../prompts/memory_dream_system_prompt.json` — apply via `jsonb_set` after provisioning, same as `chat.reply`'s.

Add a `schedule.nudge` seed entry too:
```python
"schedule.nudge": {
    "coverage": "Send proactive reminders about routines and quests the user is tracking.",
    "stance": "Calm and steady, never guilt-tripping — a quiet nudge, not a lecture.",
    "goal": "Get the kid to act now, feeling reminded by someone they look up to, not nagged.",
    "philosophy": "One nudge per event, no repeats within the same window. Say it once, plainly, then let it go.",
    "examples": [],
},
```
(Placeholder only — the real draft is `../prompts/schedule_nudge_system_prompt.json`.)

## 5. `schema_template.sql` block-strip logic — needs to become multi-way

Currently (unchanged by the 2026-07-28 update):
```python
if archetype != "finance":
    # strip everything between "-- BEGIN FINANCE" / "-- END FINANCE"
```

Once `../schema/family_block.sql`'s `-- BEGIN FAMILY` / `-- END FAMILY` block is pasted into `schema_template.sql` (right after `-- END FINANCE`), both blocks coexist and the strip logic needs to skip whichever one doesn't match the current archetype:

```python
ARCHETYPE_BLOCKS = {"finance": "FINANCE", "family": "FAMILY"}

for block_archetype, marker in ARCHETYPE_BLOCKS.items():
    if archetype != block_archetype:
        lines, in_block = [], False
        for line in sql.splitlines():
            if f"-- BEGIN {marker}" in line:
                in_block = True
            elif f"-- END {marker}" in line:
                in_block = False
            elif not in_block:
                lines.append(line)
        sql = "\n".join(lines)
```

## 6. `_generate_scaffold()` now writes 15 files, not 10 — this proposal package matches the new shape

Since the 2026-07-28 update, a fresh Duple's scaffold includes (beyond the original `duple_settings.py`/`.env.example`/`chat/router/router_config.yaml`/`chat/reply/context_builder.py`/`chat/card/*`):
- `__init__.py` at the duple root — makes `duples/dom/` importable. Drafted: `../duple/__init__.py`.
- `memory/mem_config.py` + `memory/__init__.py` — new per-Duple memory schema (moved out of a flat file into a subfolder by `29cbbe3`). Drafted: `../duple/memory/mem_config.py`, customized with family-relevant `observable_fields` rather than left at the bare non-finance default (see that file's docstring). **Note:** `guide/03-domains.md` line 40 still documents the old flat path (`duples/{duple_id}/mem_config.py`) — that doc line is stale relative to the actual generated path; flag it to the team as a small doc fix while they're in this area.
- `chat/service/service_messages.py` — new SERVICE-lane wording file. Drafted: `../duple/chat/service/service_messages.py`, Dom-voiced, wired for the one `service_routes` entry this Duple uses (`LANG_UPDATE`).

`duple_settings.py`'s `CHAT` dict also gained a `"dump_prompt": False` field (`e7b70d3`) — included in `../duple/duple_settings.py`.

## 7. `router_config.yaml` is now archetype-conditional and data-driven (v0.3.0, `23376f1`)

Three new top-level keys creators can now set (previously hardcoded in platform Python): `ticker_regex` (optional — omit for this archetype, no tickers), `service_routes` (SERVICE-lane text-pattern routing), `postback_routes` (LINE postback/button-tap routing, currently only auto-generated for `archetype == "finance"`).

`../duple/chat/router/router_config.yaml` includes a `service_routes` entry for `LANG_UPDATE` (every Duple should keep this per PATCH-NOTES.md) but deliberately **omits `postback_routes`** — see the open question below.

### Open question: does `postback_routes` support a SERVICE-lane mutation, or only a card re-render?

The one real example of `postback_routes` (khun's `router_config.yaml`) only shows `card_type` dispatch — tapping a postback re-renders a card, it doesn't appear to trigger a DB write. The plan's proof-of-completion flow (plan §8) needs a parent to tap Approve/Reject on a pushed card and have that **write** to `quest_submissions`/`wallets` — a SERVICE-lane mutation, not a card render. It's not clear from this repo whether `postback_routes` can express that, or whether approve/reject needs a different mechanism entirely (e.g. staying as an LLM tool call via `family.parent.review_submission`, with the parent typing "อนุมัติ" instead of tapping a button — functional but worse UX). **This needs a direct answer from whoever owns router.py** before the card/postback design in this package can be considered final — flagged rather than guessed at.

## 8. `examples` in `chat.reply`'s `system_prompt` must be JSON strings, not plain text (`e7b70d3`)

New rule (`guide/04-prompts.md`): each example's reply value must be a JSON string matching the output schema — `{"messages": [...], "card_type": ..., "card_subject": ...}` (this Duple uses `card_subject` as its `subject_field_name`, not `card_ticker` — see `../duple/chat/card/card_config.py`). `../prompts/chat_reply_system_prompt.json` is already in this format.

## 9. New infra dependency not covered by any existing code path: object storage for proof photos

Nothing in this repo touches object storage today (schema_template.sql is Postgres-only, and the 2026-07-28 update didn't add any). The proof-of-completion flow (plan §8) needs: a storage bucket (e.g. Supabase Storage `family-proofs`), and a webhook-side handler that downloads a LINE image message via the Messaging API (`message/{id}/content`) and re-hosts it at `{guild_id}/{duply_id}/{quest_instance_id}.jpg`, writing that URL into `quest_submissions.photo_url`. This is still the single biggest net-new infra item in the whole proposal — worth scoping/estimating before committing to the rest.

## 10. Not a provision_duple.py change, but adjacent: `scripts/gen_tool_catalog.py`

`PACK_HEADERS`/`PACK_ORDER` hardcode known packs, but unknown packs still render via a fallback header — so merging `../tools/family_tool_catalog.yaml` into `data/tool_catalog.yaml` works without touching this script. Optional nice-to-have: add `family.quest`/`family.guild`/`family.parent` to `PACK_ORDER` for a cleaner generated doc section order.
