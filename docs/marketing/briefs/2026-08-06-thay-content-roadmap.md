# Thay — Long-Term Content Roadmap (main arc + daily spin-off engine)

**For:** Thay
**Requested:** A long-term content plan — where to start, how it progresses, a main story arc, plus a daily-news-reactive spin-off layer, with an automated pipeline.
**Builds on:** [2026-08-06-thay-viral-content-format-research.md](2026-08-06-thay-viral-content-format-research.md) (format research + trust levers) and the founder-intro discussion from this thread.

> **Revised 2026-09-03 to match the approved Sep–Oct plan.** The original version of this doc opened with a founder-led video as Phase 0 and treated it as the mandatory starting point. That is no longer the plan. The content engine is now the **paper portfolio agent** (see "The content engine" below), and the founder-intro piece is deferred rather than blocking. The trust-sequencing logic in the arc table still holds and is kept; only the starting point and the automation shape changed. The full month-by-month schedule lives in the Notion **Duply — 30-Day Working Plan**; this doc holds the content reasoning behind it.

## How to read this

Two layers running at the same time, not two separate plans:
- **The main arc** — a slow-building sequence of trust, from "nobody knows Thay" to "Thay has a public track record people check." This determines *what kind* of content is credible to post at any given point.
- **The spin-off engine** — a fast, daily-cadence layer that reacts to real market events, always using whatever format the current arc phase has unlocked. It never runs ahead of the arc.

## The content engine — paper portfolio agent

This is the source of essentially all Thay marketing content, and it replaces the founder-first bootstrap as the starting point.

**Shape:** a **PM agent (Claude Opus)** makes paper-portfolio calls with its reasoning captured → a **Writer agent (Claude Sonnet)** turns those calls into post drafts → **2 weeks of shadow mode** (runs daily, drafts only, nothing published) → a go/no-go decision on posting to X + FB.

Why this replaces the founder-video start: the original argument was that Thay has no track record on day one, so the founder is the only credible trust source available. A real paper portfolio with visible reasoning and honest scoring *is* a track record, and it starts compounding from the day it begins running rather than waiting on production of a video. It also generates content continuously instead of one-off.

**Two scheduling facts that matter:**
- The 2-week shadow window is **elapsed time, not effort**. The agent must be built and running by ~16 Sep for shadow to close by ~30 Sep.
- Every PM (Opus) and Writer (Sonnet) call is real recurring spend. Ledger each call at success time, before parsing the response.

## Main story arc

The sequencing logic below is unchanged and still governs what is *credible* to post at each stage. What changed is that the paper portfolio agent now produces the material for Phases 2 and 3 directly, rather than these being hand-made in order.

| Phase | When | What ships | Why this order | Format(s) used |
|---|---|---|---|---|
| **0 — Foundation** | **Deferred** | 1–2 founder-led videos: origin story, why a "no-hype" AI, explicit "this is AI, here's the philosophy, no guaranteed returns" framing | Was the trust bootstrap when Thay had no track record. The paper portfolio now provides that instead. Still worth making later as a channel-anchor piece — it is no longer a blocker. | Founder-fronted |
| **1 — Meet Thay** | Alongside the agent build | Real chat screenshots — especially the "first-time investor's nervous question" format — so the audience meets the character through action, not description | People trust what they see Thay actually do more than what a founder says Thay will do | First-Time Investor's Real Question |
| **2 — Show the reasoning** | From shadow-mode start, then ongoing forever | Real calls, reasoning visible — now produced by the PM→Writer agent rather than hand-recorded | The trust-building backbone, and the phase that banks the raw material Phase 3 needs | Reasoning-first posts (agent-generated) |
| **3 — Public track record** | Once the portfolio has enough history | Recurring "scorecard" — right calls *and* wrong calls, honestly, on a regular cadence | Almost nobody in the finfluencer space will publish their misses. It's the hardest thing for a competitor to fake, and it compounds — every week it exists it gets more credible. The paper portfolio makes this automatic rather than a manual discipline. | "Thay's Scorecard" |
| **4 — Bond & personality** | Once there's a real user base | Bond-tier demo content (new user vs. long-time user), light dry-roast reactions, low frequency | Personality without trust reads as gimmick; personality after trust reads as charm | Bond-Tier Demo + calibrated Dry-Roast |

## The spin-off engine (daily news layer)

Runs continuously alongside the arc, once the reasoning-first format is live.

**What triggers a spin-off:**
1. A stock in Thay's actual coverage moves significantly
2. A macro data release Thay's own tools already track (`get_stock` → `get_macro`, per the existing `chat.reply` config)
3. A trending finance topic where Thay's actual reasoning adds something real

**What a spin-off is NOT:** commentary on random pop-culture trends unrelated to finance. Spin-offs stay inside Thay's real lane — the engine trades *frequency* for *speed*, not scope for volume.

## Publishing automation — the open decision

This is the one point where the current plan and this repo's existing rules disagree, and it is deliberately left open rather than quietly resolved.

**The existing rule**, from the marketing team design: **"Draft only, always. Nothing this team produces gets posted, sent, or published automatically"** — written specifically because Thay carries real compliance exposure (the same reason the finfluencer-disclosure research mattered). The original argument for it: a market-crash day is exactly when an unreviewed auto-post does real damage, and exactly the day an event-triggered engine is most likely to fire.

**The current plan** proposes auto-posting agent output to X + FB after the shadow period.

**How this gets resolved:** the 2-week shadow window exists precisely to produce the evidence for this decision. At the shadow 2-week mark (~30 Sep) there is an explicit **go/no-go**:

- **Go** — auto-post is permitted, and this rule is formally amended, with disclosure and guardrail checks wired into the publishing path (AI disclosure, no guaranteed-return language, no hype).
- **No-go** — the pipeline keeps a human checkpoint: auto-detect → auto-draft → **human review + post**. Automatic up to the checkpoint, never automatic publishing.

Whichever way it lands, it should be recorded as a decision with its reasoning — not left as drift between two documents that contradict each other.

## Immediate next step

The A/B test (Gemini 3.1 Flash Lite vs GPT-5.4-mini, on Thai naturalness and proactive weaving) gates all prompt work, including the Writer agent's voice tuning. That runs first, then the agent build, targeting shadow-mode start on 16 Sep.

---
**Status: Roadmap/planning.** Superseded sections marked inline above. Schedule and task tracking live in Notion (Duply Agile Work Board + 30-Day Working Plan).
