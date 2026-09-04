# Chat Domain — Design

Scope: how the reactive turn (router → lane → render → send) is wired for
`Thay.chat.reply`. Companion docs: `chat-domain-reference.md` (current file
locations, wiring status, signatures) and `docs/progress/PROGRESS.md`
(dated build history, cutover decisions). This doc is for **why**, not
**what's currently wired** — several of the target-state ideas below are
still not built; the reference doc says which.

---

## Mental model: run-LLM vs skip-LLM, not "3 lanes"

```
router.classify(text)
  ├─ resolvable deterministically → SKIP LLM
  │    ├─ CARD    → card.render_card()      (ticker / keyword / TAG|)
  │    └─ SERVICE → service module          (ADD/DEL / TH-EN)
  └─ not resolvable → RUN LLM
       └─ reply (LLM) → emits card intent → card.render_card()
```
The AI path's LLM output loops back through the **same** `render_card()` as
the CARD fast path. CARD/SERVICE are shortcuts the router is confident
enough to take without an LLM — renderer is a shared concern of both paths,
not owned by any single lane.

## Control plane vs data plane

```
Control plane (in-process) — per-turn business workflow
  reply_flow → context → router → reply/card → render → send
                                       │
                                       │ HTTP (data fetch only)
                                       ▼
Data plane (HTTP microservices) — shared, platform-scoped engines
  pt-us:8002   ns:8007   bf:8010   settrade:8000   calendar:8003
```
Decision rule for "module vs separate process": a component becomes an HTTP
microservice only when it has a real reason — **different scale, different
deploy cadence, or different owner**. reply/card/router/render are one
business workflow ("handle a turn") — same scale, same deploy, same owner,
so they stay in-process modules. pt/ns/bf are data sources any Duple can
call (Platform-scoped per `CLAUDE.md`), with genuinely different
scale/deploy/ownership — HTTP is what keeps them reusable across Duples.

Engine HTTP clients are the shared data-access layer; individual tools must
not hand-roll raw HTTP to engines.

## Modular monolith, not microservices — the process decision

The old `reply-service`/`service-service`/`noter-service` split into
separate HTTP processes because they were being carved out of n8n **one at a
time** during a parallel-run migration — a migration artifact, not the
target architecture. Once migration lands, in-process modules split by
**business feature** (`reply/ card/ noter/`), never by technical layer
(`services/ utils/`). This reasoning held: `reply-service` (the standalone
HTTP wrapper) was deleted 2026-07-16 once `line_webhook_service.py` started
calling the turn handler directly in-process — see reference doc.

**When to extract a microservice later:** if reply becomes CPU-bound and
needs independent scaling, or a module gets a genuinely separate
owner/deploy cadence. Drawing module boundaries on feature lines from day
one keeps that extraction cheap later — cheaper than paying distributed-
system tax (network hops, service discovery, tracing) before it's needed.

## One card-intent contract, no adapter layer (2026-07-13, still the model)

**Problem found:** reply emitted `mc`/`st`/`mc_ns` while router and the
renderer spoke `macro`/`sector`/`macro_ns`. Feeding reply output straight
into `render_card()` fell through every branch → `None` → no card. A
permanent translation shim would have been a code smell.

**Decision:** unify on **one canonical card-intent vocabulary** — the short
codes reply already emits. Rationale: the LLM is the hardest producer to
control, so the deterministic side speaks the LLM's already-validated
vocabulary rather than translating at a boundary. Churn lands on the
deterministic side (router config + card), which is easy to test.
`render_card()` accepts a router-produced route or a reply-produced object
interchangeably — both carry the same `card_type`/`card_ticker` fields,
duck-typed, no adapter.

This vocabulary now lives in `CardConfig.valid_card_types` (per-Duple,
`duples/thay/chat/card/card_config.py`), not a hardcoded constant in
`agent_loop.py` — a later, separate refactor (the archetype/multi-tenant
work) made the *vocabulary itself* Duple-owned data rather than shared
platform code, without touching this section's actual rationale: still one
canonical set, still no adapter layer, still LLM-drives-the-vocabulary.

## Context belongs to the request, not to reply

`context_builder.py` is a request-scoped concern (it assembles everything a
turn needs: profile, history, market ctx, memory topics, agent prompt) —
conceptually it should live in a shared `context/` module, not inside
`reply/`, and should support **lazy/partial loading** rather than one
`load_everything()`: the fast path (CARD/SERVICE) only needs `watchlist` +
`chat_lang` from the profile, and forcing it through the full 5-item load
would make the deterministic path as heavy as the LLM path for no reason.

**Why partial matters concretely:** `resolve_target()` (CARD lane) needs
only `{watchlist, system_lang}` — one Redis key, already warm. Running the
full context load just to render a card would be pure waste on the
highest-frequency path.

This target design is only **partially realized** — see reference doc for
what actually exists today (`context/user_profile.py`'s fast-path fetch vs.
`context_builder.py` still unmoved). Not a regression, just an unfinished
step in the migration staging (see Build Order below).

## Card dedup — ported from n8n, a genuine missing-feature fix

n8n Subflow D's `AI_Output` node deduped an AI-lane card against the last 6
messages of the current session (reset at the last `[resumed after Xh]`
marker) before rendering — this was missing entirely from an earlier draft
of the Python port. `card/dedup.py`'s `suppress_if_recently_shown()` fixes
that gap and is wired into the live turn handler. The **`isMix` case**
(an AI-lane turn that emits both text and a surviving card) writes **3**
interact_log rows, not 2 — missing this would mean dedup could never see a
previously-shown AI-lane card, silently defeating the whole feature.

## Terminology cleanup: `ai_id` → `duple_id` (2026-07-14)

`ai_id` was legacy naming inconsistent with `duply_duples.duple_id`, the
real Supabase column. Renamed across the Python chat/dream layer, Redis key
formats, and — since this was still closed beta with no external consumers
— the live Supabase columns themselves. n8n's own Gatekeeper/Subflow-C code
still uses `ai_id`/hardcoded schema inconsistently, deliberately **not**
replicated in the Python side; n8n is being migrated away from, not
extended. The Python `gatekeeper.py` rewrite went further than a rename: it
removed the `destination → tenant` DB lookup entirely (n8n queried a
nonexistent `duply_duples.ai_id` column, silently dropping traffic for any
tenant not already warm in an untimed cache) — the Python service is
deployed **per-Duple**, so `DUPLE_ID` comes from env, not a runtime lookup.
This is a stronger fix than patching the column name would have been: it
deletes the whole class of "new tenant silently drops traffic" bug, not
just today's instance of it.

## Cutover strategy (revised 2026-07-14 — still the live plan)

Originally planned as shadow-write + diff against n8n before cutover.
Superseded: Python's tool set diverged from n8n's frozen Subflow D (more
tools added since), so a mechanical diff against n8n output would disagree
even when Python is *correct* — it validates the wrong thing. Revised plan:
build an HTTP wrapper around the turn handler, rewire n8n to call it
**non-destructively** (leave the old nodes in place, just re-point the
connection, so rollback is re-activating the previous `versionId` per
`CLAUDE.md`'s REST-API-PATCH pattern, not a rebuild). Validate via real
output to real users/testers using the monitoring already built
(`request_logger.py`'s `/health`, `error_rate_5min`, rolling window,
`agent_call_log`) instead of a new shadow-diff table. `end_of_turn`/
interact_log cutover is a deliberately separate, later, atomic switch
coordinated with retiring n8n's own `Interact_log` node — wiring both
would double-log. As of 2026-07-17 this plan is **superseded again** in
practice: `line_webhook_service.py` now calls the turn handler fully
in-process (no HTTP wrapper needed, since webhook and turn-handling live in
the same process) — see reference doc for exactly what's live vs.
dev-only.

## Known gaps — status as of 2026-07-17

- ~~No LINE webhook signature verification~~ — **fixed.** `gatekeeper.py`
  now does HMAC-SHA256 verification against `X-Line-Signature`, wired into
  the live request path. This was flagged as a real gap on 2026-07-14; it
  no longer is.
- **interact_log/end_of_turn wiring exists but is off by default.** Built
  and callable, gated behind an env flag that isn't set on the deployed Pi
  service — meaning turns handled by `line-webhook-service` today don't
  write `interact_log` or trigger noter. This wasn't explicit in the
  original migration-boundary framing (which described it as "ported, not
  wired" — it's now wired, just disabled). See reference doc.
- **Allowlist-of-testers vs. all-current-traffic for eventual cutover** —
  still not decided.
- **Renderer/sender split** — still not done; rendering and sending remain
  inside `card/pipeline.py` and `line_webhook_service.py` respectively, not
  extracted into their own modules. Not urgent — no second consumer of
  render/send exists yet to justify the extraction.

## Build order — current staging (see reference doc for exact file locations)

1. ✅ Unify card contract — done 2026-07-13, since relocated to `CardConfig` (still the same vocabulary/no-adapter decision).
2. 🟡 Context loading — partial: fast-path (`context/user_profile.py`) exists; full-path `context_builder.py` not moved out of `duples/thay/chat/reply/`.
3. ⏳ Renderer/sender extraction — not started.
4. ✅ Turn handler in-process — `reply_flow.py` (renamed from `orchestrator.py` 2026-07-16) is live-tested end-to-end, called directly by `line_webhook_service.py`. The standalone HTTP wrapper this step originally called for is no longer needed — webhook and turn-handling collapsed into one process instead.
5. ⏳ Production cutover (real user traffic off n8n) — not done. `line-webhook-service`'s own systemd unit self-describes as dev/test OA, not production; n8n's stack (including its Cloudflare tunnel) is still running alongside it.

## Open questions

- Does n8n Gatekeeper already forward the full `user_info` (watchlist +
  language) in a way Python could reuse for a cheap cutover path? Not
  investigated — moot if cutover goes through the webhook-swap plan above
  instead.
- Allowlist-of-testers vs. all-current-traffic for the eventual cutover —
  not decided.
