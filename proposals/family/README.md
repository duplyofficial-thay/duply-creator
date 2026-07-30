# Proposal: `family` archetype — "Dom", a gamified daily-life secretary for kids

Draft handoff package for a new Duply archetype: **Dom** — a steady, quietly
charismatic big-brother/leader figure kids look up to — a LINE bot parents give to
their kids that assigns quests (homework, chores, habits), tracks proof-of-completion
(parent approves), awards XP/levels and virtual coins, supports redeeming coins for
parent-fulfilled rewards, and groups families into a "guild" with both family-internal
and global leaderboards, plus daily bedtime/routine reminders. Full design reasoning,
confirmed product decisions, and risk notes live in the plan file this package was
generated from: `~/.claude/plans/system-analyst-and-playful-pudding.md`.

**Nothing here has been pushed or executed.** This is a draft to review with the Duply
team before anything touches the real repo/database. Re-synced 2026-07-29 against the
platform's "yaml-driven router + per-Duple service wording" update (v0.3.0) that landed
upstream while this was being drafted — see `platform_changes/provision_duple_notes.md`
for exactly what changed and how this package was adjusted.

## What's in this folder

| Path | What it is | Status |
|---|---|---|
| `register/dom.yaml` | Registration file draft | Named — review `owner:` field, then move to `register/` and push |
| `schema/family_block.sql` | New Postgres tables (11 tables, FKs+indexes) | Ready to paste into `scripts/schema_template.sql` |
| `tools/family_tool_catalog.yaml` | 15 new custom tools across 3 packs | Ready to merge into `data/tool_catalog.yaml` |
| `duple/__init__.py`, `duple/memory/__init__.py` | Package markers (matches current scaffold shape) | Ready |
| `duple/duple_settings.py` | Domain gates for this archetype | Preview of what provisioning should scaffold |
| `duple/memory/mem_config.py` | Per-Duple memory schema (new platform concept, 2026-07-28) | Customized `observable_fields` for family use, not left at bare default |
| `duple/chat/router/router_config.yaml` | Keyword→card routing + new `service_routes` | `postback_routes` deliberately omitted — open question, see notes file §7 |
| `duple/chat/service/service_messages.py` | SERVICE-lane wording (new platform concept, 2026-07-28) | Wired for `LANG_UPDATE` only |
| `duple/chat/card/*.py` | Full card subsystem (config/pipeline/renderer/dedup/data_fetcher) | Renderer logic is real; data_fetcher has TODO markers where real DB queries plug in |
| `duple/schedule/*.py` | New custom domain: daily bedtime/routine/quest-due nudges | Engine logic + cron entry point drafted; DB/LINE-push calls marked TODO |
| `prompts/*` | Persona + `chat.reply` + `schedule.nudge` + `memory.noter`/`memory.dream` system_prompt drafts | Ready to seed after provisioning; `examples` already in the required JSON-string format |
| `platform_changes/provision_duple_notes.md` | Exact line-level diffs needed in `scripts/provision_duple.py`, plus one open design question | For the Duply team to review/implement/answer |
| `platform_changes/message_to_team.md` | Draft message summarizing the PR + the open question | Copy/paste to whoever owns the platform code |
| `content/starter_quests_seed.sql` | 15 global starter quest_templates (guild_id NULL) across homework/chore/habit | Run once against `dom_ai` after provisioning |
| `content/xp_coin_level_design.md` | Difficulty→XP/coin tiers, level threshold table, reward-pricing guidance | First-pass numbers, easy to retune post-launch |
| `content/starter_reward_examples.md` | Example reward-catalog entries for parents (not seeded centrally — guild-scoped by design) | Inspiration to hand to test families |

## What's still needed before this can move

1. **One open design question** (`platform_changes/provision_duple_notes.md` §7): can
   `postback_routes` trigger a SERVICE-lane DB write (needed for the parent's
   Approve/Reject tap on a proof submission), or only re-render a card? This affects
   whether the proof-review flow works as designed.
2. **Duply team review** — this introduces a brand-new archetype, 6 new agent-pack
   entries, 11 new tables, 15 new custom tools, and one genuinely new piece of infra
   (object storage for proof photos — flagged in `platform_changes/provision_duple_notes.md`
   §9, the single biggest unknown to scope early).
3. Once the team is on board: they edit `provision_duple.py` per the notes file, paste
   the SQL block, run provisioning — same flow as `guide/02-onboarding.md`, just with a
   new archetype option.

## Build order (single release — nothing here is gated behind a later "phase")

1. Register + SQL schema → team provisions
2. Tool packs wired by team → creator builds against them
3. Persona/prompts seeded, conversational loop working
4. Card subsystem + router keywords
5. Proof/approval flow end-to-end (photo storage is the long-pole item — surface early)
6. Leaderboards (global + family)
7. `schedule.nudge` cron for bedtime/routine reminders (last — most infra-dependent)

## Confirmed product decisions (asked directly, not assumed)

- **Proof review:** parent manually approves via LINE (photo + Approve/Reject). Quests
  marked `requires_proof=false` auto-approve on submit.
- **Currency:** 100% virtual coins/XP, never real money, never moved through the bot.
- **Rollout:** build the full feature set together, not a staged MVP.
