# Invest Domain — Design

Scope: `Thay.invest.pm` (autonomous paper portfolio manager) and
`Thay.invest.writer` (social content from pm decisions). Both agents are
tightly coupled — pm produces structured decisions, writer consumes them —
and are documented together here.

For current file paths, schema, config values, and cron status see
`invest-domain-reference.md` (to be created). For dated build history see
`docs/progress/PROGRESS.md`. This doc is for **why**, not **what** or **when**.

---

## Why invest is a separate domain from chat

Chat is reactive: one user's question, one turn, texting tone.
Invest is autonomous: no user trigger, scheduled, investment-memo tone, public audience.
The two have incompatible constraints in every dimension — trigger, audience, voice, and output format. Folding invest into chat would mean sharing a codebase optimised for low latency / conversational tone with a process that needs deliberate multi-step reasoning across an entire portfolio. They stay separate.

The relationship is one-directional: invest reads the same PT/BF/NS data layer
chat reads (Redis ctx strings, same TTLs), but chat never reads invest's
decisions. Meta (not yet built) is the coordinator if cross-domain awareness
is ever needed.

---

## Flow

```
Screener (rule-based, no LLM)
  → 5–10 candidates from stock_universe
PM Agent (Claude Opus)
  → reads ctx strings + port_positions + port_snapshots
  → emits structured decision: action / ticker / sizing / thesis
Writer Agent (Claude Sonnet)
  → one post per significant decision
  → platform-specific format (X = 280 chars punchy; FB = reasoning paragraph)
Publish
  → shadow mode during first ~2 weeks (log only, no real post)
  → auto-publish after shadow period validation
```

---

## Screener — rule-based gate before LLM

The screener's job is to cut `stock_universe` (all tickers with fresh data)
down to a short candidate list so the PM Agent reasons over signal, not noise.
No LLM in this step — a rule engine is cheaper, faster, and reproducible.

**Why rule-based:** The screener doesn't need judgment — it needs a consistent
filter so PM Agent sees the same quality of input every run. LLM-based
pre-filtering would add latency, cost, and non-determinism to a gate that is
purely mechanical.

**Input:** `stock_universe` rows with fresh `pt_data` and `bf_data` jsonb
(rows with stale or null data are excluded — same staleness logic PT/BF engines
already emit via their `status` field).

**Filter logic (candidates must pass all three):**

| Layer | Rule | Rationale |
|---|---|---|
| PT | at least one bullish momentum or breakout tag present | surface stocks showing real price action, not just any stock |
| PT | no conflicting bearish override tag blocking the bullish one | tag conflict governance already handled in `tagging.py` — trust it |
| BF | `quality_score` above a minimum threshold (calibrate during shadow period) | avoid chasing momentum in fundamentally weak names |
| NS | no extreme negative sentiment article in last 24h | skip stocks mid-crisis where any buy thesis is noise |

**CORE + EXTENDED** tickers are eligible; TEMPORARY and BENCHMARK are excluded
(BENCHMARK = SPX/NDX used for comparison only; TEMPORARY = one-off coverage
with no BF depth).

Existing positions in `port_positions` are always passed to PM Agent even if
they don't pass the screener — PM Agent must see its own book to manage it.

---

## PM Agent — Claude Opus

### Why Claude Opus (not GPT-5.4-mini or Gemini)

Chat's `gpt-5.4-mini` is optimised for low latency and cost at high turn
volume. PM runs twice a day against a fixed candidate list — latency and
per-call cost matter far less. The task is portfolio reasoning: reading
multiple ctx strings, comparing against thesis history, sizing a position,
and writing a thesis that holds up over days. This is the task Opus was
built for. Using the same model as chat would also muddle the model
selection rationale — invest is the natural home for the heavier model.

### Decision space

PM Agent may only emit one of these actions per ticker per run:

| Action | Meaning |
|---|---|
| `BUY` | Open new position |
| `ADD` | Increase existing position (requires existing `port_positions` row) |
| `TRIM` | Reduce position — must state how much and why |
| `SELL` | Full exit — must state exit thesis |
| `HOLD` | Explicit hold with updated thesis note (not silence — silence = no row written) |
| `WATCH` | Candidate noted but no position taken — tracked as thesis draft |

**LLM proposes → Python decides** applies here too: PM Agent outputs a JSON
decision; a rules layer validates action legality (e.g. ADD on a ticker with
no open position is rejected, SELL on a ticker not in portfolio is rejected)
before any write.

### Position sizing

- Starting paper capital: defined in config (e.g. $100k notional — chosen to make % moves feel real and post-worthy, not arbitrary)
- Max positions: 10
- Max allocation per position: 20%
- Default sizing: conviction-proportional within the 20% cap; PM Agent states target weight in its decision
- Cash reserve: minimum 10% always

These are deliberate constraints, not PM Agent discretion. The rules layer
enforces them — PM Agent can propose 30% weight on a conviction trade; Python
clips to 20%.

### Context passed to PM Agent each run

1. Current `port_positions` (all active + WATCH rows)
2. Latest `port_snapshots` row (previous portfolio state — basis for before/after framing)
3. Screener output: ctx strings (pt/bf/ns) for each candidate
4. Current market state (`market:ctx` from Redis) — PRE/LIVE/POST/CLOSED
5. Today's economic events from `macro:ctx:event`

The prompt is Supabase-backed (`agent_profiles`, `invest.pm` row) following
the platform standard. The `philosophy` and `coverage` blocks are
code-owned (locked); `business` block is Supabase-editable (portfolio rules
that may change).

---

## Writer Agent — Claude Sonnet

### Why Sonnet (not Gemini)

Original design noted Gemini for the writer. Gemini 2.5 Flash is retiring
Oct 16 2026; the natural replacement (Gemini 3.1 Flash Lite) is untested in
this stack. Sonnet is already wired in `backends.py` and produces good
creative Thai text. Single-model simplicity (Claude for both PM + Writer)
also means one API key, one usage dashboard, and no model-mismatch debugging.

### Output contract

Writer receives PM Agent's structured decision (ticker, action, thesis, sizing)
and produces platform-specific posts:

**X (Twitter):** ≤280 chars. No thread for now — single punchy post.
Format: position action + ticker + one-sentence why + current entry/exit price.
No em-dash, no parentheses, no hashtag spam. Reads like a trader's note, not a press release.

**Facebook:** 2–4 sentences. More reasoning, same direct tone.
Adds: what the position size is (% of portfolio), what would change the thesis.
No LinkedIn-style "I'm excited to share" opener.

**Content types** (drive format + which platforms):

| Type | Trigger | Platforms |
|---|---|---|
| `trade_entry` | BUY or ADD action | X + FB |
| `trade_exit` | SELL action | X + FB |
| `thesis_update` | HOLD with material thesis change | FB only |
| `portfolio_update` | Weekly Sunday snapshot | X + FB |
| `watch_note` | WATCH action (no position) | X only — shorter |

`TRIM` generates a `thesis_update` not a `trade_exit` — partial size reduction
is portfolio management, not a story in itself.

---

## Shadow mode — why it comes before auto-publish

Auto-publishing to a public persona with no review is a brand risk if the
PM Agent makes a bad call or the Writer produces off-tone content. But a
permanent approval gate defeats the autonomous content angle entirely.

**Shadow mode** is a bounded review window, not a permanent gate:
- All runs execute the full pipeline (screener → PM → writer)
- Posts are written to `port_posts` with `status='shadow'` instead of publishing
- Owner reviews shadow posts via Telegram daily digest or direct DB query
- After ~2 weeks of shadow runs look correct, flip `INVEST_SHADOW_MODE=false` and rebuild
- No code change needed after that — shadow mode is a single env var

This validates two things the design can't verify analytically: that PM Agent's
decision cadence is reasonable (not over-trading, not ignoring clear signals)
and that Writer's tone is consistently on-brand before real followers see it.

---

## Publish timing — decision time ≠ post time

PM runs at US market boundaries (pre-market 08:00 ET, post-market 17:00 ET).
Those map to 19:00 BKK and 04:00 BKK respectively.

**Pre-market run (19:00 BKK):** post immediately — Thai investors are awake,
market context is fresh ("markets open in 30 min, here's what I'm watching").

**Post-market run (04:00 BKK):** queue for 07:30 BKK publish — Thai audience
wakes up to Thay's post-market recap before their own day starts.
Content is dated to the previous trading day, which is accurate.

The `port_posts` table carries `scheduled_at` (when to publish) separate from
`created_at` (when generated) and `published_at` (when actually sent).
A lightweight publish cron checks `status='queued' AND scheduled_at <= now()`
every 5 minutes — same pattern as `reach_cron.py`.

---

## Schema decisions

### `port_positions`

```sql
port_positions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker           TEXT NOT NULL,
    shares           NUMERIC NOT NULL,          -- paper share count
    allocation_pct   NUMERIC NOT NULL,          -- % of portfolio at entry
    entry_price      NUMERIC NOT NULL,
    entry_date       DATE NOT NULL,
    current_price    NUMERIC,                   -- updated each run
    unrealized_pnl   NUMERIC,                   -- current_price vs entry
    realized_pnl     NUMERIC DEFAULT 0,         -- populated on SELL/TRIM
    thesis           TEXT NOT NULL,
    thesis_log       JSONB DEFAULT '[]',         -- array of {date, thesis, action}
    exit_triggers    JSONB DEFAULT '{}',         -- {target_price, stop_loss, thesis_break}
    status           TEXT NOT NULL DEFAULT 'active',  -- active / closed / watch
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
)
```

`unrealized_pnl` is computed and written by each PM run, not derived at query
time — PM Agent needs the number in its context and computing it in SQL on
every read adds no value here.

### `port_snapshots`

```sql
port_snapshots (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date             DATE NOT NULL UNIQUE,
    snapshot         JSONB NOT NULL,            -- full positions array at this moment
    total_value      NUMERIC NOT NULL,
    cash_remaining   NUMERIC NOT NULL,
    ytd_pnl          NUMERIC,
    created_at       TIMESTAMPTZ DEFAULT now()
)
```

One row per trading day. PM Agent reads the previous snapshot as its
before-state. `snapshot` jsonb is the positions array verbatim — not a
diff — so historical state is always self-contained without joining.

### `port_posts`

```sql
port_posts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform         TEXT NOT NULL,             -- x / fb
    content          TEXT NOT NULL,
    content_type     TEXT NOT NULL,             -- trade_entry / trade_exit / thesis_update / portfolio_update / watch_note
    ticker           TEXT,                      -- null for portfolio-wide posts
    position_id      UUID REFERENCES thay_ai.port_positions(id),
    status           TEXT NOT NULL DEFAULT 'shadow',  -- shadow / queued / published / failed
    scheduled_at     TIMESTAMPTZ,
    published_at     TIMESTAMPTZ,
    price_at_publish NUMERIC,
    price_7d         NUMERIC,                   -- filled in later by publish cron
    price_30d        NUMERIC,
    created_at       TIMESTAMPTZ DEFAULT now()
)
```

`price_7d` / `price_30d` are null at publish time and backfilled by a simple
cron (or the next PM run) — they're for post-performance tracking, not needed
at publish.

---

## What this design does not cover

- **Real money** — paper only. No brokerage API, no real execution, ever.
- **Sentiment score as a hard filter** — NS sentiment is not a numeric score yet (see thay.md NS Card Status). Until it is, the screener uses NS as a negative signal only (crisis exclusion), not a positive one.
- **IG (Instagram)** — IG Business API requires an image and more OAuth surface than X + FB. Phase 2 if X + FB content proves engaging.
- **Follower / engagement feedback loop** — port_posts tracks `price_7d/30d` (stock performance) not post engagement. Engagement metrics (likes, shares) are not modelled — the goal is content quality first, not algorithmic optimisation.
- **Thay.meta coordination** — Meta is not built. When it is, it will read `port_posts` and `port_positions` to report on invest domain health, but that is Meta's problem, not invest's.
