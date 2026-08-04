# AI Marketing Team for Thay + Duply

## Context

The user wants a small team of Claude Code subagents and skills — modeled as
marketing "positions" — to help brainstorm content and promote two things:
**Thay** (the live US-stock finance Duple) and **Duply** (the platform
itself, marketed to people who might want to build their own Duple —
same audience as Dom's search for early users). This lives in the shared
`duply-creator` repo so it's available to anyone using Claude Code there,
not just the user's personal machine.

The team should feel like an actual team, not a single prompt wearing
different hats: a `marketing-lead` agent takes a request, decomposes it,
dispatches focused specialist subagents, and assembles their output into
one deliverable. Specialists lean on the `marketing:*` plugin skills
already available in this environment (content-creation, campaign-plan,
seo-audit, etc.) rather than reimplementing that logic — this design only
adds the two things that don't already exist: Thay/Duply-specific brand
knowledge, and the team structure itself.

## Architecture

```
User request
     │
     ▼
marketing-lead (agent)
     │  1. reads thay-brand-brief / duply-platform-brief skills
     │  2. decides which specialists actually apply (not always all 4)
     │  3. dispatches content-strategist FIRST if strategy/angle is in question
     │  4. passes strategist's brief to the remaining relevant specialists
     │     IN PARALLEL (copywriter / social-media-manager / growth-marketer)
     │  5. assembles results into one deliverable, saves to marketing/
     ▼
marketing/campaigns/YYYY-MM-DD-<slug>.md  (+ specialist working files)
```

For small requests ("write me one LINE broadcast message"), the Lead skips
straight to the one relevant specialist — no forced full pipeline.

**Hard rule, stated explicitly in `marketing-lead`'s instructions:** every
agent produces drafts only. Nothing is auto-posted to social, auto-sent as
a LINE broadcast, or otherwise published. Publishing is a separate,
explicit action the user takes afterward.

## Agents (`duply-creator/.claude/agents/`)

| Agent | Responsibility | Tools |
|---|---|---|
| `marketing-lead` | Intake request, decompose, dispatch specialists (sequenced per above), assemble final deliverable, enforce draft-only rule | Agent, Read, Write, Skill, TaskCreate, TaskUpdate |
| `content-strategist` | Content pillars, campaign angles, audience segmentation — Thay's audience (US-stock retail traders in Thailand) is distinct from Duply's (potential creators) | Read, WebSearch, WebFetch, Skill |
| `copywriter` | Voice-matched copy: LINE broadcast text, ad copy, landing/app-store copy, email. **Never writes anything that reads as investment advice or implies guaranteed returns** (Thay is a finance product — real compliance/reputational risk) | Read, Write, Skill |
| `social-media-manager` | Platform-specific post ideas/calendars for Thai social conventions (Facebook, IG, X, TikTok) | Read, Write, WebSearch, Skill |
| `growth-marketer` | Acquisition angles, ad targeting ideas, funnel/CTA suggestions, growth experiments. Same compliance guardrail as copywriter for anything touching Thay | Read, Write, WebSearch, WebFetch, Skill |

**Revision path:** a follow-up request like "revise the Thay campaign, make
it punchier" re-dispatches only the relevant specialist with the feedback
attached — not a full pipeline rerun.

## Skills (`duply-creator/.claude/skills/`)

- **`thay-brand-brief`** — persona, tone, audience, do/don't, sourced from
  `register/thay.yaml`. Documented caveat: this is a snapshot, not a live
  read of Supabase's `agent_profiles`/`duply_duples.persona` — if Thay's
  live persona has been tuned since registration, this brief may lag.
  Worth a periodic manual refresh, not an automated one (out of scope here).
- **`duply-platform-brief`** — Duply-as-platform positioning: what it is,
  who it's for (potential Duple creators), what's genuinely live today
  (2-3 Duples, early-stage) so copy doesn't overclaim maturity or scale.

No third "workflow" skill — the Lead's own dispatch logic lives in its
agent instructions; a separate skill would just duplicate that.

## Output structure

```
marketing/
  README.md              — how to invoke the team, folder guide
  briefs/                 content-strategist outputs
  copy/                   copywriter outputs
  social/                 social-media-manager outputs
  growth/                 growth-marketer outputs
  campaigns/              marketing-lead's assembled final packages
```

Filenames are dated and slugged: `marketing/campaigns/2026-08-04-thay-earnings-feature-launch.md` — never overwritten, always a new dated file per request.

## Risks / open items

- **Nested subagent dispatch is unverified.** `marketing-lead` is designed
  to dispatch the other 4 custom subagents via the Agent tool. Whether a
  custom project-level subagent can itself call the Agent tool to dispatch
  further custom subagents (vs. that capability being reserved for the
  top-level session) is not confirmed — this needs an early smoke test
  during implementation. Fallback if unsupported: `marketing-lead`'s
  instructions describe the dispatch plan, and the *user's own top-level
  Claude Code session* does the actual dispatching by following them —
  same division of labor, just one level shallower.

## Testing / verification

These are prompt/config files, not application code — verification means
actually invoking `marketing-lead` with a real sample request (e.g. "draft
a launch announcement for Thay's new earnings-calendar feature") once
built, and checking: the right specialists got dispatched, their outputs
share one consistent angle (not contradicting each other), the compliance
guardrail held (no investment-advice-sounding copy), and the assembled
file landed in the right place under `marketing/`.
