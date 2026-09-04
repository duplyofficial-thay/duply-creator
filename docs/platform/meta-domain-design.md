# Duply Platform + Meta-Agent — Top-Level Spec (draft)

Status: top-level / directional. Not an implementation plan. Written after
today's session that (a) generalized reply-service to a multi-model backend,
(b) built context_builder.py, (c) fixed the card_type schema mismatch, and
(d) surfaced the need for a platform-level hierarchy before building
thay.meta. This doc captures the hierarchy and agent architecture agreed on;
open questions are marked explicitly rather than guessed at.

---

## 1. Hierarchy

```
Duply (platform)
  └── tenant (e.g. "thay")          ← product level. One tenant = one product/brand.
        ├── goal / milestone / core persona   ← tenant-level, set at onboarding
        ├── domain: chat                       ← a domain groups related agents
        │     ├── agent: reply                 ← today's chat.reply
        │     ├── agent: noter                  ← memory extraction
        │     └── agent: dream                  ← daily profile refresh
        ├── domain: reach (social media)        ← not built yet
        ├── domain: research                    ← not built yet
        └── meta (tenant-level, sibling to all domains)
              ├── frontier  (planner/CEO)
              ├── worker    (secretary — writes config, not code)
              └── po-chat   (conversational interface for the product owner)
```

Every schema created from this point forward carries `tenant_id` as the
first-class root key, `domain` and `agent_id` as the next two. Today's
`agent_profiles` table (keyed loosely on a dot-string like `chat.reply`)
should be understood as `(tenant='thay', domain='chat', agent='reply')` —
migrate the key shape to three real columns rather than a compound string,
so cross-domain / cross-agent queries (which meta needs) are possible
without string parsing.

**Persona inheritance follows the same three levels**: tenant core persona →
optional domain-level adjustment → agent-level adjustment. An agent's final
system prompt is the tenant persona with layered, additive adjustments — not
an independently-authored persona per agent. This is what keeps a user's
experience of "Thay" consistent whether they're talking to chat.reply or
(later) a reach/social agent.

**Open question**: does domain-level persona override need to exist as a
real field from day one, or can it stay empty/unused until a second domain
(reach/research) actually needs it? Leaning toward: create the column now
(near-zero cost), leave it unused until needed — same reasoning applied
throughout today's session (cheap to add now, expensive to retrofit later).

---

## 2. Onboarding flow (how a new tenant is created)

This is the flow "Thay" itself should be understood as having gone through
implicitly — internal product now, but should be buildable as a real UI flow
later without redesigning the data model.

1. Create product (name, branding)
2. Set long-term goal + milestones — becomes the North Star metric(s) that
   Frontier plans against
3. Set core persona (tenant-level)
4. Choose which domains/services to enable, from default templates
5. Choose which tools to connect per agent, from a platform tool catalog
   (free vs paid, usage limits)
6. Choose tier (free/paid) — governs usage limits enforced before every
   agent_loop.run()

After step 6, the tenant can either keep managing everything through the UI,
or hand ongoing operation to their own meta (frontier/worker/po-chat) —
tenant's choice, not forced.

**Open question**: exact free/paid tool and usage-limit boundaries — not
needed for the top-level spec, defer to a pricing/limits doc once there's a
second tenant actually asking.

---

## 3. Meta agent architecture (per tenant)

### 3.1 Frontier (planner / "CEO")
- Runs on a cron (daily, TBD frequency), plus can schedule its own future
  wake-ups by writing to a task/inbox table (self-continuation without
  needing a long-lived session — this is how it stays cheap and avoids
  context-window/token exhaustion over long timeframes).
- Reads: usage/performance/cost metrics (see §5), the PO-chat inbox (what
  the product owner asked recently), current state of all agent prompts
  under the tenant.
- Writes: nothing directly. Proposes changes and dispatches them through
  Worker, the same as PO-chat does for safe actions.
- Model: Claude Opus (highest capability, infrequent calls — cost is
  amortized over a whole day/tenant, not per-conversation).
- Reasons in `observation → hypothesis → proposed action → expected impact`
  form, not just metric dumps — every recommendation should be framed as
  a testable change against the tenant's stated goal.

### 3.2 Worker ("secretary")
- The only agent with write access, and only to the config/content layer —
  never core code (agent_loop.py, context_builder.py, backend
  infrastructure). What it *can* write:
  - agent prompt fields (persona, tone, examples, output schema — all
    within a given agent's `agent_profiles` row)
  - which tools are enabled for a given agent
  - content pieces (draft articles, social posts) for domains that produce
    content
  - operational actions from a fixed catalog (restart a service, clear a
    specific cache key) — catalog is closed, extended only by a human/dev
    session (e.g. Claude Code), never invented by Worker or Frontier at
    runtime
- Writes ideally go through the same API layer the future admin UI will use
  (see §6) rather than touching Supabase directly — so validation,
  versioning, and audit logging live in one place regardless of whether a
  human clicked a button or an agent called a tool.
- Every write is logged via the existing tool-call logging pattern
  (`agent_call_log`-style) — no separate audit mechanism needed.
- Model: DeepSeek (cheap, high call volume expected).

### 3.3 PO-chat (product-owner-facing conversational agent)
- What the product owner (assumed no dev knowledge) actually talks to —
  via Telegram or similar, in natural product-owner language, not
  technical status reports. Should role-play as "Thay, thinking about his
  own product," not as a technical assistant.
- Read access is unrestricted (querying state/metrics never needs
  gatekeeping).
- Write access is always mediated through Worker, never direct — PO-chat
  has no write-tool of its own, only a "dispatch to Worker" tool. This is
  a deliberate security boundary: even a successfully-manipulated PO-chat
  (e.g. via a crafted message) can at most create a task, not execute one.
- Decision rule per incoming write request:
  - **Safe, matches an established pattern** → dispatch to Worker
    synchronously, respond "done" once Worker confirms.
  - **Novel / ambiguous / crosses into brand-risk territory** (e.g.
    anything domain=reach/social, since that's externally visible) →
    respond "let me think about this" and place it in Frontier's inbox for
    the next planning cycle (or an explicit advisor call — see below).
- Advisor escalation (PO-chat calling Frontier synchronously mid-conversation)
  is allowed but rate-limited and gated by explicit conditions (novel case +
  explicit urgency from PO) — not triggered just because PO-chat is
  "unsure," to avoid runaway cost from routing too much through the
  expensive model.
- Model: DeepSeek.
- UX for slow actions: no Telegram-native "typing" primitive assumed —
  acknowledge immediately in text ("on it"), then follow up in the same
  chat once Worker's action completes. This is prompted behavior (the
  model writes the acknowledgment itself, in the same turn it decides to
  call the dispatch tool) — no separate infra needed for that first
  message. It is not the same as a multi-step progress stream; anything
  beyond one immediate ack is out of scope for now.

---

## 4. Zero-coupling principle

No domain agent (chat.reply, future reach/research agents) has any
awareness that meta exists. They read their config (prompt, enabled tools)
from the same store they already read from today — meta changes *what's in
the store*, never the agent's code. This means:
- Meta can be added to an existing tenant without touching any agent's code.
- Rollback of a meta-driven change is just reading a previous version of
  the config, same mechanism as rolling back a human-made UI change.
- Frontier has no direct feedback channel from an agent when a prompt
  change goes wrong — it only sees the effect through metrics (§5), which
  implies a lag between "change deployed" and "Frontier knows if it
  worked." No canary/A-B mechanism exists yet to shorten this — flagged as
  a real gap, not solved here.

---

## 5. What Frontier tracks (metrics surface)

Three categories, all tenant-scoped:

- **User/growth**: DAU/WAU/MAU, retention, bond-score distribution and
  progression, drop-off points in conversations.
- **Product performance**: the 5-axis harness categories built today
  (format/error/retry, latency, cost, tone, answer quality) — should run
  periodically against live production data, not just ad-hoc benchmark
  sessions like today's.
- **Cost/business**: cost per user, per conversation, trend over time,
  broken out by backend — especially important while there's no revenue
  model yet ("free during beta"), since every user is currently a pure
  cost center.

**Open question**: the concrete North Star metric(s) — must be set per
tenant at onboarding (§2 step 2), not decided by the platform. Nothing to
resolve here; flagging so it isn't silently skipped when the onboarding UI
is actually built.

---

## 6. Config write path (UI / API layer)

The product owner (and, later, other tenants' owners) is not expected to
ever edit Supabase directly — that's reserved for debugging/emergency use
only. The real write path is a UI, backed by an API/function layer (e.g.
`update_agent_prompt(tenant, domain, agent, field, value)`), which:
- performs validation and versioning in one place
- is the same path Worker calls as a tool — Worker is not "writing to
  Supabase," it's calling the same functions a human clicking Save would
  trigger
- means schema-safety issues like today's card_type mismatch become
  structurally harder to reintroduce, since there's one point of truth for
  what a valid write looks like, not N independent write-sites

**Open question, not resolved**: does this API layer get built before or
after the first version of meta ships? Building it first avoids a later
migration (Worker currently writing straight to Supabase, then having to
switch to calling an API); building meta first gets a working system
sooner but means a migration later. Recommendation if forced to choose now:
build a minimal version of the API layer first — even without a real UI on
top of it — since Worker needs *something* other than raw Supabase writes
to satisfy the "debug-only" boundary this section describes, and retrofitting
Worker's write-tool later is exactly the kind of rework this session's
bugs (hardcoded agent_id, key mismatches) kept coming from.

---

## 7. Explicitly out of scope for this draft

- Multi-tenant UI implementation itself — no second tenant exists yet;
  what's required now is only that every new schema carries `tenant_id`
  from day one, not that a tenant-switcher UI gets built.
- Tool marketplace / pricing mechanics — matters once there's a second
  tenant with a different vertical; not before.
- Circuit-breaker design for a misbehaving Frontier (e.g. proposing the
  same rejected action repeatedly) — flagged as needed, not designed here.
- Who exactly counts as "human sign-off" for high-risk actions, and whether
  that's the same Telegram channel as PO-chat or a separate one — flagged,
  not resolved.
- A/B or canary mechanism for prompt changes, to shorten Frontier's
  feedback lag (§4) — flagged as a real gap, not designed here.

---

## 8. What's settled vs. what's still open (summary)

**Settled** — safe to build against:
- 4-level hierarchy (Duply → tenant → domain → agent) and 3-level persona
  inheritance
- 3-agent meta architecture and each agent's model/role/read-write
  boundaries
- Zero-coupling (domain agents unaware of meta)
- Safe-action vs. needs-judgment as the only real risk gate (not identity
  of who's asking)
- Worker never writes core code — config/content layer only, from a fixed
  action catalog
- Logging via existing tool-call pattern, no new audit mechanism
- chat.reply's Loading Animation (not push-quota) for in-conversation
  "still working" UX

**Open** — needs a decision before the relevant part gets built:
- North Star metric definition (per-tenant, set at onboarding — not a
  platform-wide default)
- API/UI layer vs. meta build order (§6)
- Exact worker action catalog beyond the two examples used today
  (restart, clear-cache)
- Circuit breaker for runaway/repetitive Frontier proposals
- Canary/A-B mechanism to shorten Frontier's feedback lag
- Who human-sign-off actually is, and which channel
