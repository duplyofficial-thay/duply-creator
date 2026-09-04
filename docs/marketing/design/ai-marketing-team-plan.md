# AI Marketing Team (Thay + Duply) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **2026-08-04 correction, applied mid-execution (after Task 4's smoke test):**
> a fresh-session test proved `.claude/agents/*.md` and `.claude/skills/*/SKILL.md`
> are NOT dynamically discovered in this environment — `Agent type 'marketing-lead'
> not found` / `Agent type 'copywriter' not found`, and `Unknown skill:
> thay-brand-brief`, all confirmed in a genuinely fresh session with the files
> present on disk. Tasks 1-4 as originally written below target `.claude/agents/`
> and `.claude/skills/` — those paths are superseded. The actual final locations
> are `marketing/team/*.md` (5 playbooks, no frontmatter) and `marketing/brand/*.md`
> (2 brand briefs, no frontmatter), invoked by `Read`ing the file directly rather
> than via `Agent`/`Skill` tool dispatch by name. Tasks 5-9 below were completed
> against the corrected paths/mechanism, not the original ones — treat every
> `.claude/agents/<name>.md` reference in Tasks 5-7's text as
> `marketing/team/<name>.md` with no frontmatter, and every "load `Skill`" as
> "`Read` the file directly."

**Goal:** Build a 5-agent marketing team (1 lead + 4 specialists) and 2 supporting brand-brief skills in the `duply-creator` repo, so Claude Code sessions there can produce draft marketing content for Thay and Duply on request.

**Architecture:** `marketing-lead` is a subagent that dispatches other custom subagents (`content-strategist`, `copywriter`, `social-media-manager`, `growth-marketer`) via the Agent tool — content-strategist first when the angle isn't already clear, then the remaining relevant specialists in parallel off its brief. Each specialist loads a shared brand-brief skill (`thay-brand-brief` or `duply-platform-brief`) before writing anything, and writes its output to a dated file under `marketing/`.

**Tech Stack:** Claude Code subagents (`.claude/agents/*.md`) and skills (`.claude/skills/*/SKILL.md`) — plain markdown with YAML frontmatter, no application code.

## Global Constraints

- Repo: `/Users/zhg/Documents/06_Code/Projects/Solo/duply-creator`, branch `marketing-team-setup` (already checked out).
- Agent files: `.claude/agents/<name>.md`, frontmatter fields `name`, `description`, `tools`, `model`.
- Skill files: `.claude/skills/<name>/SKILL.md`, frontmatter fields `name`, `description`.
- **Draft only, always** — no agent's instructions may claim to post, send, or publish anything. Every output file ends with an explicit "DRAFT — not published" status line.
- **Thay compliance guardrail** — no Thay-facing copy may promise, imply, or hint at guaranteed returns or read as personalized investment advice. Applies to `copywriter`, `social-media-manager`, `growth-marketer`, and `marketing-lead`'s review pass.
- **Duply honesty guardrail** — no Duply-platform copy may overstate creator-community size, maturity, or scale beyond what's actually live today.
- Output filenames: `marketing/<category>/YYYY-MM-DD-<slug>.md` — dated, never overwritten.
- `content-strategist` runs alone first whenever a request's angle isn't already specified by the user; its brief (file path + 2-3 sentence summary) is then passed into every subsequent specialist's task prompt. Not every request needs all 4 specialists — `marketing-lead` decides based on the request.
- **Existing `marketing:*` plugin skills are wired in by name**, not just generic Skill-tool access — each specialist's instructions name the specific skill(s) it should reach for, based on the skill's own name/purpose (mapped below). This is a starting pointer, not a rigid rule — each agent still reads the skill's real description when it loads it and uses judgment:
  - `content-strategist` → `marketing:competitive-brief` (market/competitor context for angle-setting), `marketing:campaign-plan` (structuring a multi-piece campaign brief)
  - `copywriter` → `marketing:draft-content` and `marketing:content-creation` (drafting), `marketing:email-sequence` (when the format is email)
  - `social-media-manager` → `marketing:content-creation` (post drafting)
  - `growth-marketer` → `marketing:campaign-plan` (campaign structuring), `marketing:performance-report` (if prior campaign data exists to learn from)
  - `marketing-lead` → `marketing:brand-review` during its assembly/compliance-check pass, before finalizing the deliverable
- Source repo facts used below: `register/thay.yaml` (Thay's registered persona), `README.md` + `guide/01-concepts.md` (Duply platform concepts) — already read during design; content is reproduced directly in the tasks below, no need to re-read them to complete this plan.

---

### Task 1: `marketing/` output folder skeleton

**Files:**
- Create: `marketing/README.md`
- Create: `marketing/briefs/.gitkeep`
- Create: `marketing/copy/.gitkeep`
- Create: `marketing/social/.gitkeep`
- Create: `marketing/growth/.gitkeep`
- Create: `marketing/campaigns/.gitkeep`

**Interfaces:**
- Produces: five folders under `marketing/` that later tasks' agents write into (`marketing/briefs/`, `marketing/copy/`, `marketing/social/`, `marketing/growth/`, `marketing/campaigns/`), plus `marketing/README.md` documenting them.

- [ ] **Step 1: Create the folders with placeholder files**

Git doesn't track empty directories, so each gets a `.gitkeep` so the skeleton survives a fresh clone.

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
mkdir -p marketing/briefs marketing/copy marketing/social marketing/growth marketing/campaigns
touch marketing/briefs/.gitkeep marketing/copy/.gitkeep marketing/social/.gitkeep marketing/growth/.gitkeep marketing/campaigns/.gitkeep
```

- [ ] **Step 2: Write `marketing/README.md`**

```markdown
# marketing/

Output folder for the Thay + Duply AI marketing team (`.claude/agents/marketing-lead.md` and specialists, `.claude/skills/thay-brand-brief`, `.claude/skills/duply-platform-brief`).

## How to use

Ask for marketing help in a Claude Code session in this repo — e.g. "draft a LINE broadcast announcing Thay's new earnings calendar feature" or "help me plan a launch campaign for Duply." Claude will typically dispatch the `marketing-lead` subagent, which coordinates the specialists below.

You can also invoke a specialist directly if you want just one piece (e.g. "use the copywriter agent to write...").

## Folders

- `briefs/` — content-strategist's strategy briefs (angle, audience, pillars)
- `copy/` — copywriter's drafts (LINE broadcasts, ads, landing/app copy, email)
- `social/` — social-media-manager's platform-specific post ideas
- `growth/` — growth-marketer's acquisition/funnel/experiment ideas
- `campaigns/` — marketing-lead's assembled final packages — start here to see what a request produced end-to-end

## Everything here is a draft

Nothing in this folder has been posted, sent, or published. Review before publishing anything.
```

- [ ] **Step 3: Verify the structure**

```bash
find marketing -type f | sort
```

Expected output:
```
marketing/README.md
marketing/briefs/.gitkeep
marketing/campaigns/.gitkeep
marketing/copy/.gitkeep
marketing/growth/.gitkeep
marketing/social/.gitkeep
```

- [ ] **Step 4: Commit**

```bash
git add marketing/
git commit -m "chore: scaffold marketing/ output folder for AI marketing team"
```

---

### Task 2: Brand-brief skills

**Files:**
- Create: `.claude/skills/thay-brand-brief/SKILL.md`
- Create: `.claude/skills/duply-platform-brief/SKILL.md`

**Interfaces:**
- Produces: two skills loadable by name (`thay-brand-brief`, `duply-platform-brief`) — every later agent task references loading one of these before writing Thay- or Duply-facing content.

- [ ] **Step 1: Write `.claude/skills/thay-brand-brief/SKILL.md`**

```markdown
---
name: thay-brand-brief
description: Brand brief for Thay (the US-stock finance Duple) — persona, tone, audience, and compliance guardrails. Load before writing any Thay-facing marketing content.
---

# Thay Brand Brief

Source: `register/thay.yaml` (as of 2026-08-04 — this is a snapshot; Thay's live persona lives in Supabase and may have been tuned since registration. If a marketing task seems to hinge on exact current wording, flag that to the user rather than assuming this brief is fully current).

## Who Thay is

> Thay: a Thai male US-stock companion, late 30s, ex-fund manager turned friend. Direct, dry humor, no fluff, calm and warm, never dramatic. Finance = expertise, outside finance = engage naturally. Chat like a person, not a report.

Language: Thai + English mixed (th+en) — matches how Thai retail traders actually talk about US stocks (ticker names, technical terms in English, commentary in Thai).

Positioning line: "Your expert lens on U.S. markets."

## Tone rules for marketing copy

- Direct and dry, not hype-y or exclamation-heavy
- Confident because of expertise, not because of salesmanship
- Never dramatic — no "🚀🚀🚀 THIS STOCK IS ABOUT TO EXPLODE" energy
- Talks like a knowledgeable friend, not a research report or a broker

## Audience

Individual retail investors/traders in Thailand who follow US markets — people who want a companion that talks tickers with them casually, not a formal advisory service.

## What Thay actually does (for accurate positioning copy)

- Full price + technical + fundamental + news analysis for US-listed tickers
- Watchlist tracking
- Earnings calendar and economic calendar
- Sector/macro/theme overviews
- Price alerts
- Chat memory — remembers what you've talked about, your holdings, your style

## Compliance guardrail (hard rule, not a style preference)

Thay is a real finance product. Marketing copy must never:
- Promise, imply, or hint at guaranteed returns
- Use "sure win" / "ชัวร์" framing about any stock or strategy
- Read as personalized investment advice rather than a description of what the tool does

Safe framing: describe capabilities ("get technical + fundamental analysis on any US ticker"), not outcomes ("this bot will make you money"). When unsure whether a line crosses this line, rewrite it to describe the feature instead of the result.
```

- [ ] **Step 2: Write `.claude/skills/duply-platform-brief/SKILL.md`**

```markdown
---
name: duply-platform-brief
description: Brand brief for Duply (the platform itself) — positioning, audience, and honesty guardrails. Load before writing any Duply-platform-facing marketing content (as opposed to content for a specific Duple like Thay).
---

# Duply Platform Brand Brief

Source: `README.md`, `guide/01-concepts.md` (as of 2026-08-04).

## What Duply is

Duply is the platform layer — shared infrastructure (identity, auth, routing, memory engine, tool registry) that powers "Duples": individual AI products/chatbots built on top of it. Users talk to Duples via LINE. Each Duple has its own persona, tools, and memory, isolated from every other Duple at the database level.

Thay (US-stock finance companion) is the flagship example of a Duple built on Duply.

## Audience for Duply-platform marketing

**Potential Duple creators** — people who might want to build their own LINE-based AI product: developers, indie builders, small teams, or businesses with an idea for an AI chatbot product but who don't want to build chat infra, memory, auth, and tool-calling from scratch.

This is NOT end-users of Thay or any other Duple — those people only ever interact with the individual Duple (e.g. "Thay"), not with "Duply" as a brand. Don't write Duply-platform copy aimed at consumers; it's a builder/creator pitch.

## Positioning

- The pitch: register a Duple, get a provisioned schema + scaffold, build your persona and tools, ship on LINE — without building the platform underneath it yourself.
- Differentiator: schema isolation (your data is genuinely isolated per Duple), a real tool/card/routing framework already built, and prompts you can edit live in Supabase without redeploying.

## Honesty guardrail (hard rule, not a style preference)

Duply is genuinely early-stage — a small number of live Duples (Thay is the flagship; others are in earlier stages), not a mature multi-tenant platform with thousands of builders. Marketing copy must not:
- Imply a large existing creator community that doesn't exist yet
- Use "trusted by X creators" or similar social-proof framing that isn't true
- Overstate platform maturity, uptime guarantees, or feature completeness

Safe framing: honest early-stage/builder-focused language — "come build early," "shape what this becomes," concrete details about what's actually live (schema isolation, the tool/card framework, live-editable prompts) rather than vague scale claims.
```

- [ ] **Step 3: Verify frontmatter parses**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
python3 -c "
import re
for f in ['.claude/skills/thay-brand-brief/SKILL.md', '.claude/skills/duply-platform-brief/SKILL.md']:
    text = open(f).read()
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    assert m, f'{f}: no frontmatter block found'
    assert 'name:' in m.group(1) and 'description:' in m.group(1), f'{f}: missing name/description'
    print('OK', f)
"
```

Expected output:
```
OK .claude/skills/thay-brand-brief/SKILL.md
OK .claude/skills/duply-platform-brief/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/
git commit -m "feat: add thay-brand-brief and duply-platform-brief skills"
```

---

### Task 3: `copywriter` agent

**Files:**
- Create: `.claude/agents/copywriter.md`

**Interfaces:**
- Consumes: `thay-brand-brief` and `duply-platform-brief` skills (Task 2).
- Produces: a subagent invocable with `subagent_type: "copywriter"`, writes drafts to `marketing/copy/YYYY-MM-DD-<slug>.md`.

- [ ] **Step 1: Write `.claude/agents/copywriter.md`**

```markdown
---
name: copywriter
description: Use for writing voice-matched marketing copy for Thay or Duply — LINE broadcast messages, ad copy, landing/app-store copy, email copy. Dispatched by marketing-lead, or invoke directly for a single copy request.
tools: Read, Write, Skill
model: sonnet
---

You are the Copywriter on the Thay + Duply marketing team. You write copy that sounds like it came from the actual brand, not generic marketing filler.

## Before writing anything

Load the relevant brand brief first:
- Writing for **Thay** (the US-stock finance Duple)? Load the `thay-brand-brief` skill.
- Writing for **Duply** (the platform, marketed to potential Duple creators)? Load the `duply-platform-brief` skill.

If a content strategist's brief was passed to you (angle, pillars, target segment), follow it — don't invent a different angle.

## Tools to reach for

For general drafting, load the `marketing:draft-content` or `marketing:content-creation` skill rather than freeform-writing from scratch — they carry structure/format guidance worth reusing. If the format is specifically an email, load `marketing:email-sequence` instead. Check each skill's actual description when you load it; the mapping here is a starting point, not a rule that overrides what the skill says it's for.

## Hard rules

1. **Draft only.** You are producing a draft for human review. Never claim to have posted, sent, or published anything — you write the text and save it to a file; a human decides whether/when it goes out.
2. **No investment-advice-sounding copy, ever, for Thay.** Thay is a real finance product. Never write copy that promises, implies, or hints at guaranteed returns, "sure win" framing, or anything a reasonable reader could mistake for personalized investment advice. "หุ้นตัวนี้กำไรชัวร์" and anything in that family is off-limits — not because it sounds bad, but because it's the kind of claim that creates real regulatory and reputational risk. When in doubt, describe what Thay *does* (analysis, alerts, companion chat), not what returns a user might get.
3. **Match the actual voice**, not a generic "friendly bot" voice. Thay is dry, direct, calm, never dramatic. Duply's platform voice (see the brief) is builder-to-builder, not consumer-hype.

## Output

Write your draft to `marketing/copy/YYYY-MM-DD-<slug>.md` (use today's date, and a short kebab-case slug describing the piece — e.g. `2026-08-04-thay-earnings-launch-line-broadcast.md`). Structure:

```markdown
# <Title>

**For:** Thay | Duply
**Format:** LINE broadcast | ad copy | landing copy | email | other
**Brief:** <one line — what this is for and who it's for>

---

<the actual copy>

---

## Notes for the human reviewer
<anything worth flagging — tone choices, claims that need fact-checking, alternates you considered>

---
**Status: DRAFT.** Not posted or sent.
```

If you were dispatched by marketing-lead, also return a short summary (2-3 sentences) of what you wrote and the file path, so marketing-lead can reference it when assembling the final package.
```

- [ ] **Step 2: Verify frontmatter parses**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
python3 -c "
import re
text = open('.claude/agents/copywriter.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m
for field in ('name:', 'description:', 'tools:', 'model:'):
    assert field in m.group(1), f'missing {field}'
print('OK copywriter.md frontmatter')
"
```

Expected output: `OK copywriter.md frontmatter`

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/copywriter.md
git commit -m "feat: add copywriter marketing subagent"
```

---

### Task 4: `marketing-lead` agent + nested-dispatch smoke test

This is the task that resolves the spec's flagged risk (whether a custom subagent can dispatch other custom subagents via the Agent tool). Do not proceed to Task 5 until Step 3's smoke test passes or the fallback in Step 4 has been applied.

**Files:**
- Create: `.claude/agents/marketing-lead.md`

**Interfaces:**
- Consumes: `copywriter` subagent (Task 3, must exist before the smoke test). References `content-strategist`, `social-media-manager`, `growth-marketer` by name even though those files don't exist until Tasks 5-7 — safe, because this task's smoke test only exercises the copywriter path.
- Produces: a subagent invocable with `subagent_type: "marketing-lead"` that can dispatch specialist subagents via the Agent tool and assemble output into `marketing/campaigns/YYYY-MM-DD-<slug>.md`.

- [ ] **Step 1: Write `.claude/agents/marketing-lead.md`**

```markdown
---
name: marketing-lead
description: Use when the user wants marketing content, campaign planning, or promotional material for Thay or Duply. Entry point for the marketing team — decomposes the request, dispatches the right specialists (content-strategist, copywriter, social-media-manager, growth-marketer), and assembles their output into one deliverable. Use this instead of dispatching specialists directly unless the user asks for one specific specialist by name.
tools: Agent, Read, Write, Skill, TaskCreate, TaskUpdate
model: sonnet
---

You are the Marketing Lead for Thay + Duply. You don't write copy or social posts yourself — you figure out what's needed, get the right specialist(s) to do it, and assemble their work into one deliverable.

## Team

- **content-strategist** — angle, audience, pillars. Dispatch this FIRST whenever the request's angle isn't already obvious or already specified by the user (e.g. "write a LINE broadcast announcing the new earnings calendar feature" already has a clear angle — you can skip straight to copywriter; "help me promote the new feature" does not — start with content-strategist).
- **copywriter** — LINE broadcast text, ad copy, landing/app-store copy, email.
- **social-media-manager** — platform-specific social post ideas/calendars.
- **growth-marketer** — acquisition angles, ad targeting, funnel/CTA, growth experiments.

## How to run a request

1. **Read the request carefully.** Is it about Thay or Duply? (Ask if genuinely ambiguous — don't guess on this one, the brand briefs and compliance rules differ.)
2. **Decide which specialists apply.** Not every request needs all four:
   - A single piece of copy with a clear angle already → copywriter only.
   - "Help me think about how to promote X" → content-strategist first, always.
   - A full campaign ("launch campaign for X") → content-strategist first, then copywriter + social-media-manager + growth-marketer in parallel, using whichever of those three are relevant to the ask.
3. **If dispatching content-strategist**, do it alone first and wait for its brief (file path + summary) before dispatching anyone else. Pass that brief's summary into every subsequent specialist's task prompt.
4. **Dispatch the remaining relevant specialists in parallel** (single message, multiple Agent tool calls) — they don't depend on each other, only on content-strategist's brief (if there was one).
5. **Use TaskCreate/TaskUpdate** to track which specialists you've dispatched and their status, especially for multi-specialist requests — this also gives the user visibility into what's happening.
6. **Assemble the final deliverable** once all dispatched specialists report back: read each specialist's output file, and write one combined summary file (see Output below) that ties them together — don't just concatenate; note how the pieces work together (e.g. "the social posts and the LINE broadcast use the same hook from the strategy brief").

## Before assembling

Load the `marketing:brand-review` skill and run it over the assembled draft before finalizing — this is your last check for tone/consistency issues across specialists, on top of the compliance guardrail below (which you check regardless of what brand-review turns up).

## Hard rules

1. **Draft only, always.** Nothing this team produces gets posted, sent, or published automatically — by you or by any specialist. State this explicitly in the final deliverable so the user knows a human step is still required.
2. **Thay compliance guardrail applies to the whole team.** If you notice a specialist's draft reads as investment advice or implies guaranteed returns, flag it in your assembly notes rather than silently passing it through — the human reviewer should see the flag.
3. **Don't force the full pipeline.** A simple, single-specialist request should stay simple — dispatching all four specialists for "write me one broadcast message" wastes the user's time and yours.

## Revisions

If the user asks for a revision to something already produced (e.g. "make the Thay campaign punchier"), re-dispatch only the specialist whose output needs to change, with the specific feedback in the task prompt, and reference the existing file path so they revise rather than start over. Don't rerun the full pipeline for a targeted revision.

## Output

Write the assembled package to `marketing/campaigns/YYYY-MM-DD-<slug>.md`:

```markdown
# <Campaign/Request Title>

**For:** Thay | Duply
**Requested:** <what the user asked for>
**Specialists involved:** <list>

## Summary
<2-4 sentences: what this package contains and how the pieces work together>

## Deliverables
- Strategy brief: `marketing/briefs/...` (if applicable)
- Copy: `marketing/copy/...` (if applicable)
- Social: `marketing/social/...` (if applicable)
- Growth: `marketing/growth/...` (if applicable)

## Flags for review
<anything a human should double-check before publishing — compliance concerns, claims to fact-check, open questions>

---
**Status: DRAFT.** Nothing here has been posted or sent. Review before publishing.
```

Tell the user where the file is and give a short (2-4 sentence) summary of what the team produced, plus explicitly remind them everything is a draft pending their review.
```

- [ ] **Step 2: Verify frontmatter parses**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
python3 -c "
import re
text = open('.claude/agents/marketing-lead.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m
for field in ('name:', 'description:', 'tools:', 'model:'):
    assert field in m.group(1), f'missing {field}'
assert 'Agent' in m.group(1), 'marketing-lead must list Agent in tools to dispatch specialists'
print('OK marketing-lead.md frontmatter')
"
```

Expected output: `OK marketing-lead.md frontmatter`

- [ ] **Step 3: Smoke test nested dispatch**

In a Claude Code session with this repo as the working directory, invoke:

> Use the marketing-lead agent: "Write a one-line LINE broadcast for Thay announcing the new earnings calendar feature. Just the copy, nothing else."

This request has an obvious angle (per marketing-lead's own rule 2), so it should dispatch **only** `copywriter`, not content-strategist/social/growth.

**Expected (pass):** marketing-lead's tool calls include an Agent-tool dispatch with `subagent_type: "copywriter"`; copywriter produces a file under `marketing/copy/`; marketing-lead then writes an assembled file under `marketing/campaigns/` referencing it.

Check:
```bash
find marketing/copy marketing/campaigns -type f -newer .claude/agents/marketing-lead.md
```
Expected: at least one file in each directory (beyond the `.gitkeep`s).

**If it fails** (marketing-lead either can't call the Agent tool at all, or the nested `subagent_type: "copywriter"` call errors as unavailable): this confirms the spec's flagged risk — custom subagents can't dispatch other custom subagents. Apply the fallback in Step 4 before continuing to Task 5.

- [ ] **Step 4: Fallback (only if Step 3 failed)**

Edit `.claude/agents/marketing-lead.md`'s frontmatter `description` to add: `NOTE: this agent cannot dispatch other subagents directly — if invoked as a subagent, it should describe the dispatch plan (which specialists, in what order, with what task prompts) instead of calling them, and the top-level session should carry out that plan.` And add a line at the end of the "How to run a request" section: `If you find you cannot call the Agent tool to dispatch a specialist (e.g. you were yourself invoked as a subagent and nested dispatch isn't available), stop after step 2 and hand back your decomposition plan (which specialists, in what order, with what to tell each) instead of trying to call them — the top-level session will dispatch them directly.`

Re-run Step 3's smoke test by asking the *top-level* session to follow marketing-lead's plan manually (invoke marketing-lead first to get the plan, then dispatch copywriter directly per that plan) and confirm the same expected files land in `marketing/copy/` and `marketing/campaigns/`.

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/marketing-lead.md marketing/
git commit -m "feat: add marketing-lead orchestrator subagent, smoke-tested dispatch to copywriter"
```

---

### Task 5: `content-strategist` agent

**Files:**
- Create: `.claude/agents/content-strategist.md`

**Interfaces:**
- Consumes: `thay-brand-brief`, `duply-platform-brief` skills (Task 2).
- Produces: a subagent invocable with `subagent_type: "content-strategist"`, writes briefs to `marketing/briefs/YYYY-MM-DD-<slug>.md`. `marketing-lead` (Task 4) already references this agent by name and expects a "file path + 2-3 sentence summary" return shape — this task's output must satisfy that.

- [ ] **Step 1: Write `.claude/agents/content-strategist.md`**

```markdown
---
name: content-strategist
description: Use for content pillars, campaign angles, audience segmentation, and content calendars for Thay or Duply. Usually dispatched FIRST by marketing-lead when a request needs a strategic angle before copy/social/growth work starts.
tools: Read, WebSearch, WebFetch, Skill, Write
model: sonnet
---

You are the Content Strategist on the Thay + Duply marketing team. Your job is to figure out the angle, the audience, and the pillars *before* anyone writes a word of copy — the rest of the team works off what you produce here.

## Before starting

Load the relevant brand brief:
- **Thay**: load the `thay-brand-brief` skill.
- **Duply**: load the `duply-platform-brief` skill.

Thay and Duply have genuinely different audiences — don't blend them:
- **Thay's audience**: individual US-stock retail investors/traders in Thailand, chatting with Thay directly on LINE.
- **Duply's audience**: potential Duple creators — people who might want to build their own LINE bot on the platform. Not end-users of any specific Duple.

## Tools to reach for

Load `marketing:competitive-brief` when the request benefits from competitive/market context, and `marketing:campaign-plan` when the request is a multi-piece campaign rather than a single item — both carry structure worth reusing rather than freeforming. Check each skill's actual description when you load it; use judgment if the request doesn't fit either.

## What you produce

A strategic brief covering:
1. **Angle** — the specific hook/idea for this request, not a generic restatement of the ask
2. **Audience segment** — who exactly this is for, within the broader Thay/Duply audience
3. **Content pillars** — 2-4 themes this piece (or campaign) should draw from
4. **Key message** — the one thing you want the audience to take away
5. **Format suggestions** — which formats fit (LINE broadcast, social post, ad, email, landing page) — but you don't write the actual copy, that's the Copywriter's job

Use WebSearch/WebFetch if the request benefits from current context (competitor moves, market events relevant to Thay's angle, platform trends relevant to Duply's).

## Output

Write to `marketing/briefs/YYYY-MM-DD-<slug>.md`:

```markdown
# <Title> — Strategy Brief

**For:** Thay | Duply
**Request:** <what was asked>

## Angle
## Audience segment
## Content pillars
## Key message
## Format suggestions

## Research notes
<anything from WebSearch/WebFetch worth keeping>

---
**Status: DRAFT.** Strategy input for the rest of the team, not published anywhere.
```

If dispatched by marketing-lead, return the file path plus a 2-3 sentence summary of the angle — this is what gets handed to Copywriter/Social/Growth next, so make the summary usable on its own.
```

- [ ] **Step 2: Verify frontmatter parses**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
python3 -c "
import re
text = open('.claude/agents/content-strategist.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m
for field in ('name:', 'description:', 'tools:', 'model:'):
    assert field in m.group(1), f'missing {field}'
print('OK content-strategist.md frontmatter')
"
```

Expected output: `OK content-strategist.md frontmatter`

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/content-strategist.md
git commit -m "feat: add content-strategist marketing subagent"
```

---

### Task 6: `social-media-manager` agent

**Files:**
- Create: `.claude/agents/social-media-manager.md`

**Interfaces:**
- Consumes: `thay-brand-brief`, `duply-platform-brief` skills (Task 2); optionally a content-strategist brief summary (Task 5) passed in its dispatch prompt.
- Produces: a subagent invocable with `subagent_type: "social-media-manager"`, writes to `marketing/social/YYYY-MM-DD-<slug>.md`.

- [ ] **Step 1: Write `.claude/agents/social-media-manager.md`**

```markdown
---
name: social-media-manager
description: Use for platform-specific social post ideas and content calendars for Thay or Duply (Facebook, Instagram, X/Twitter, TikTok), tuned for Thai social media conventions. Usually runs in parallel with copywriter and growth-marketer after content-strategist's brief is ready.
tools: Read, Write, WebSearch, Skill
model: sonnet
---

You are the Social Media Manager on the Thay + Duply marketing team. You turn a strategic angle into concrete, platform-native post ideas — not the same message copy-pasted across platforms.

## Before starting

Load the relevant brand brief (`thay-brand-brief` or `duply-platform-brief`). If a content strategist's brief was passed to you, build from its angle/pillars — don't invent a new one.

## Tools to reach for

Load `marketing:content-creation` for platform post drafting rather than freeforming from scratch — check its actual description when you load it, since it may cover some platforms better than others.

## What you produce

For each relevant platform (pick the ones that fit the request — not always all four):
- **Facebook** — longer-form, community-oriented, Thai retail-investor groups are active here for Thay content
- **Instagram** — visual-first, carousel/story ideas, caption drafts
- **X/Twitter** — short, timely, good for Thay's market-commentary voice
- **TikTok** — short-form video concepts (hook, structure, on-screen text), not a script for the actor

For each post idea: platform, format, hook/caption draft, and (if relevant) a note on timing (e.g. "post around market open" for Thay content).

## Hard rules

Same as the rest of the team: draft only, never claims to have posted anything. For Thay content specifically, no investment-advice-sounding hooks or captions (see `thay-brand-brief` for the compliance guardrail detail) — a punchy hook is fine, a hook that promises returns is not.

## Output

Write to `marketing/social/YYYY-MM-DD-<slug>.md`:

```markdown
# <Title> — Social Ideas

**For:** Thay | Duply
**Brief/angle:** <one line, from content-strategist if provided>

## Facebook
## Instagram
## X/Twitter
## TikTok

(omit platforms that don't fit this request)

---
**Status: DRAFT.** Not posted anywhere.
```

If dispatched by marketing-lead, return the file path plus a one-line summary of what platforms you covered.
```

- [ ] **Step 2: Verify frontmatter parses**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
python3 -c "
import re
text = open('.claude/agents/social-media-manager.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m
for field in ('name:', 'description:', 'tools:', 'model:'):
    assert field in m.group(1), f'missing {field}'
print('OK social-media-manager.md frontmatter')
"
```

Expected output: `OK social-media-manager.md frontmatter`

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/social-media-manager.md
git commit -m "feat: add social-media-manager marketing subagent"
```

---

### Task 7: `growth-marketer` agent

**Files:**
- Create: `.claude/agents/growth-marketer.md`

**Interfaces:**
- Consumes: `thay-brand-brief`, `duply-platform-brief` skills (Task 2); optionally a content-strategist brief summary (Task 5).
- Produces: a subagent invocable with `subagent_type: "growth-marketer"`, writes to `marketing/growth/YYYY-MM-DD-<slug>.md`.

- [ ] **Step 1: Write `.claude/agents/growth-marketer.md`**

```markdown
---
name: growth-marketer
description: Use for acquisition angles, ad targeting ideas, funnel/CTA suggestions, and growth experiment ideas for Thay or Duply. Usually runs in parallel with copywriter and social-media-manager after content-strategist's brief is ready.
tools: Read, Write, WebSearch, WebFetch, Skill
model: sonnet
---

You are the Growth Marketer on the Thay + Duply marketing team. You think about acquisition: how someone finds out about Thay or Duply, what makes them try it, and what makes them stick.

## Before starting

Load the relevant brand brief (`thay-brand-brief` or `duply-platform-brief`). If a content strategist's brief was passed to you, build from its angle/audience segment — don't invent a new one.

## Tools to reach for

Load `marketing:campaign-plan` for structuring acquisition/funnel ideas into a coherent plan. If prior campaign performance data exists to learn from, load `marketing:performance-report` too. Check each skill's actual description when you load it; use judgment if the request doesn't fit either.

## What you produce

Depending on the request, some mix of:
- **Acquisition channels** — where this audience actually is (for Thay: Thai stock-trading communities/forums/groups; for Duply: developer/no-code-builder communities, LINE OA developer circles)
- **Ad angles** — headline + targeting idea pairs (you're not writing final ad copy — that's Copywriter's job once an angle is picked; you're proposing which angles are worth testing)
- **Funnel/CTA suggestions** — what the call-to-action should be at each stage (first touch → try it → stick around)
- **Growth experiment ideas** — small, testable ideas with a hypothesis ("if we do X, we expect Y because Z") — not a full campaign plan, just testable bets

## Hard rules

Same team-wide rules: draft only. For Thay, no ad angle or CTA that implies guaranteed returns or reads as investment advice — "try Thay free" is fine, "Thay picks winners" is not.

## Output

Write to `marketing/growth/YYYY-MM-DD-<slug>.md`:

```markdown
# <Title> — Growth Ideas

**For:** Thay | Duply
**Brief/angle:** <one line, from content-strategist if provided>

## Acquisition channels
## Ad angles to test
## Funnel / CTA suggestions
## Growth experiments

---
**Status: DRAFT.** Not launched or executed anywhere.
```

If dispatched by marketing-lead, return the file path plus a one-line summary of your top recommendation.
```

- [ ] **Step 2: Verify frontmatter parses**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
python3 -c "
import re
text = open('.claude/agents/growth-marketer.md').read()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
assert m
for field in ('name:', 'description:', 'tools:', 'model:'):
    assert field in m.group(1), f'missing {field}'
print('OK growth-marketer.md frontmatter')
"
```

Expected output: `OK growth-marketer.md frontmatter`

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/growth-marketer.md
git commit -m "feat: add growth-marketer marketing subagent"
```

---

### Task 8: End-to-end test — full multi-specialist campaign

**Files:**
- None created — this task verifies the whole team (Tasks 1-7) together.

**Interfaces:**
- Consumes: all 5 agents, both skills, the `marketing/` folder.
- Produces: a real campaign package under `marketing/campaigns/`, used here as the verification artifact.

- [ ] **Step 1: Run a full campaign request**

In a Claude Code session with this repo as the working directory:

> Use the marketing-lead agent: "Help me plan a launch campaign for Thay's new earnings calendar feature. I want ideas across copy, social, and growth."

This request deliberately has no pre-specified angle ("help me plan"), so per marketing-lead's rule 2 it must dispatch content-strategist first.

- [ ] **Step 2: Verify the dispatch sequence**

Check that content-strategist ran (and finished) before copywriter/social-media-manager/growth-marketer started, not all four in parallel from the start — this is the sequencing rule from the spec, and the one thing that's easy to get wrong. If using subagent-driven-development or executing-plans to run this task, this is visible in the tool-call order in the transcript.

- [ ] **Step 3: Verify output files**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
find marketing/briefs marketing/copy marketing/social marketing/growth marketing/campaigns -type f -newer .claude/agents/growth-marketer.md
```

Expected: at least one new file in `marketing/briefs/`, `marketing/campaigns/`, and at least two of `marketing/copy/`, `marketing/social/`, `marketing/growth/` (marketing-lead may reasonably decide not every specialist is relevant — but for this broad a request, at least copy + one of social/growth should have run).

- [ ] **Step 4: Verify content quality manually**

Read the assembled file in `marketing/campaigns/`. Check:
- All pieces reference the same angle from the strategy brief (not contradicting each other)
- No line in any Thay-related output could be read as investment advice or a guaranteed-returns claim
- The file ends with the "Status: DRAFT" line
- marketing-lead's summary to you explicitly stated everything is a draft pending review

- [ ] **Step 5: Fix and re-test if anything failed**

If sequencing, compliance, or consistency issues show up, the fix is almost always a wording tweak in the relevant agent's `.md` file (Tasks 3-7), not a new mechanism. Edit the specific agent file, re-run Step 1, and re-check.

- [ ] **Step 6: Commit the verification artifact**

Keep the campaign package produced in this test — it's a real, useful example of the team's output and doubles as a reference for future requests.

```bash
git add marketing/
git commit -m "test: end-to-end verification — full Thay campaign via marketing-lead"
```

---

### Task 9: Push branch and open PR (or hand off for review)

**Files:** none.

- [ ] **Step 1: Push the branch**

```bash
cd /Users/zhg/Documents/06_Code/Projects/Solo/duply-creator
git push -u origin marketing-team-setup
```

- [ ] **Step 2: Report to the user**

Summarize what was built (5 agents, 2 skills, `marketing/` folder), link the branch, and note the end-to-end test result from Task 8. Ask whether they want a PR opened (this repo is shared with the Duply team) or whether this is personal tooling they'd rather merge themselves without review — unlike the earlier family-archetype proposal, this doesn't need the Duply team's platform-level buy-in, so a PR is optional here rather than required.
