# Reach Domain — Design

Scope: `Thay.reach.alert` (custom + big-move price alerts — the only agent
this doc goes deep on). `Thay.reach.broadcast` (admin/manual push messaging)
also lives in this domain and shares its dispatch/gating machinery — see the
"Also in this domain" note at the bottom; it hasn't had its own design pass
yet.

For current file paths, DB schema, config values, and cron/gating status see
`reach-domain-reference.md`. For dated build history see `docs/progress/PROGRESS.md`
(search "reach"). This doc is for **why**, not **what** or **when**.

---

## Naming & domain boundary

Reach is a Core Domain, parallel to Chat/Meta — not a submodule of Chat.
Chat is reactive (user-initiated turn); Reach is proactive (system-initiated
push). This is why the agent is `Thay.reach.alert`, not `Thay.chat.reach`
(the earlier name, superseded). The boundary matters operationally too:
Reach's own `interact_log` writes use `lane='REACH'`, which noter's lane
guard excludes and dream's `type='chat'` filter naturally skips — Reach
never triggers memory extraction or counts as user engagement
(`interaction_count` not incremented), because no user turn happened.

## Mission (Phase 1 scope, still current)

Two trigger types, both scoped to the user's personal watchlist:

- **(a) Custom alert** — user-requested in chat ("แจ้งฉันตอน NVDA แตะ $200"),
  parsed via a tool call (`set_alert`) inside the existing
  `agent_loop.py` — no separate NLU pipeline. One-shot: fires once, then
  disables itself, matching how retail alert products behave (user
  re-creates if they want it again). `set_alert` is a generic-tier tool
  (not finance-specific) — trigger validation is duple-scoped via
  `duple_settings.REACH["enabled_triggers"]`.
- **(b) Big-move alert** — system-detected, recurring. Reach engine watches
  each user's watchlist tickers for a significant price move each cycle.
  Same ticker can fire again on a later move, so cooldown/dedup applies —
  unlike (a).

**Still explicitly out of scope:** `Thay.reach.digest` (daily/weekly
summary), campaign/marketing broadcasts framed as personalized content,
CORE-universe non-personalized alerts, and PT-tag-based alert classification
(breakout/breakdown/etc. — Phase 1 uses a plain % move threshold; tagging
needs its own pass over `pt-core/tagging.py`).

## Message generation reuses `agent_loop.py` — a deliberate Phase 1 trade-off

Fire-time copy goes through the same `agent_loop.py` used by
`Thay.chat.reply`, not a lightweight direct-completion call. Rationale: one
code path to maintain, consistent persona/voice with in-chat Thay, and
volume stays low because both trigger types are already gated (one-shot
disables itself; big-move has session dedup + a daily cap). The known
trade-off: `agent_loop.py`'s multi-turn tool-calling budget
(`MAX_TOOL_ITERATIONS`, `MAX_PARSE_RETRIES`) is more machinery than a
single-sentence generation task strictly needs. Revisit if
digest/campaign volume makes the overhead a real cost — not a blocker today.

## Scheduling: one dispatch table, not one cron per alert type

`reach_jobs (job_id, job_type, cadence, next_run_at, enabled, config)` — a
single cron (`reach_cron.py`) polls this table and dispatches by
`job_type`, so a new job type (`broadcast`, later `digest`) registers as a
new row instead of new cron infrastructure. **Validated**: `broadcast`
shipped 2026-07-16 as exactly this — a new `reach_jobs` row (`job_type
='broadcast'`), zero changes to `reach_cron.py`'s polling logic. No
priority queue or retry engine yet — deliberately deferred until a second
consumer beyond alert+broadcast makes the real requirements clear (avoids
guessing an abstraction from one data point).

## Detection: one batched price fetch per cycle, not per-user

The engine gathers the union of unique tickers across every active custom
rule and every user's watchlist, then calls the PT engine **once** per
cycle for that whole set. A ticker held by 50 users' watchlists is still
exactly one HTTP call, not 50 — this is the shape that keeps Reach's cost
flat as the user base grows, since the alternative (per-user fetch) scales
with users × watchlist size instead of unique-tickers-in-play.

## Dedup model: session-based, Supabase-only (superseded the original day-boundary plan)

The original Phase 1 draft proposed a 04:00-BKT calendar-day dedup
boundary. Live behavior (see reference doc) is **session-based** instead —
the dedup/limit window resets at each new market open, not at a fixed
clock time. Both dedup and the daily push limit are Supabase-only (no
Redis): `reach_alert_log` is the durable source of truth, so state survives
process restarts and needs no cache warm-up. `reach_state.py` (an earlier
Redis-based cooldown module) was removed once this landed.

**Quiet hours** were added after the original "no quiet hours for Phase 1"
call — see reference doc for the current window. Revisit properly (batched,
morning-delivered) once `Thay.reach.digest` exists; digest is the natural
home for that behavior, alert is not.

**LIVE-only firing** — the engine only evaluates during LIVE market state;
PRE/POST market cycles are a no-op. This avoids firing on stale
pre/post-market prices that don't reflect a real intraday move.

## Token handling: env now, per-Duple later (unchanged design)

`line_push.py` currently reads `LINE_CHANNEL_ACCESS_TOKEN` from env (dev
test OA — same token `line-webhook-service` uses for inbound). The
per-Duple path (`duply_duples.line_channel_access_token`) is the intended
Phase 2 design once production cutover happens — OA-pairing means a dev
token can only push to dev-paired `line_id`s, which is exactly why rollout
is allowlist-gated today rather than a code limitation.

## Also in this domain: `Thay.reach.broadcast`

Shipped 2026-07-16. Admin/manual push messaging — `reach_broadcast.py` CLI
writes a row to `reach_broadcasts` (`target: {"all": true} | {"duply_ids":
[...]}`), the same `reach_cron.py` dispatch picks it up via
`job_type='broadcast'`, delivery is logged per-recipient to
`reach_broadcast_log`.

**Gating** follows the same pattern as alert: reads `duple_settings.REACH["gate_roles"]`
via `gate_roles_from_str()` (unified 2026-07-23 — was using separate
`REACH_BROADCAST_DRY_RUN`/`REACH_BROADCAST_ALLOWLIST` env vars which are
now removed).

**Audience resolution** (`{"all": true}` target): queries
`public.duply_users` with no `Accept-Profile` header (public schema) and
filters `channels->line->>user_id` is not null. Two bugs fixed 2026-07-23:
wrong schema header sent (was `Accept-Profile: thay_ai`) and unencoded
PostgREST column path (`channels->>line->>user_id` invalid; correct:
`urllib.parse.quote("channels->line->>user_id", safe="")`).

As of 2026-07-23 the `broadcast` job row exists but `enabled=false` —
code is correct, deliberately held until the creator-role broadcast workflow
is agreed.

## Deferred

- `Thay.reach.digest`, `Thay.reach.campaign`
- CORE-universe broadcast alerts (non-personalized, all users)
- Tag-based alert classification (replacing the plain % threshold)
- Priority queue / retry engine inside `reach_jobs`
- Lighter direct-completion message path (if `agent_loop.py` overhead
  becomes a real cost once volume grows)
- A real design pass for `reach.broadcast` before it's enabled
