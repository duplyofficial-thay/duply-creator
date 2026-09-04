---
name: tawan-project-handoff
description: Restore and transfer the verified Tawan commerce-project context from its canonical Git repository. Use when Codex, Claude, another account, or a new teammate needs to resume Tawan planning or implementation; prepare or receive a handoff; answer what has been approved, changed, blocked, or should happen next; or work on Tawan product, architecture, data, security, dashboard, LINE, analytics, Campaign, subscription-tier, or Notion project records.
---

# Tawan Project Handoff

Rebuild the project state from Git and the approved Tawan documents before reasoning about new work. Treat this skill as a navigation and continuity procedure, not as a replacement source of truth.

## Resume Workflow

1. Locate the checkout whose `origin` is `duplyofficial-thay/duply-creator`. Prefer the repository containing this skill. Do not edit a duplicate checkout.
2. Read the repository `AGENTS.md` when present, then follow its required entry-document order. If it is absent, continue from the tracked records below and report the missing project instructions.
3. Run `git status --short --branch`, `git remote -v`, `git branch -vv`, and `git log -15 --oneline --decorate`. Preserve unrelated and uncommitted work.
4. Read [references/HANDOFF.md](references/HANDOFF.md) for the project map and known state.
5. Read the canonical product records in this order:
   - `CLAUDE.md`
   - `docs/tawan/README.md`
   - `docs/tawan/CURRENT_TASK_STATUS.md`
   - `docs/tawan/DECISIONS.md`
   - `docs/tawan/PRODUCT_SPEC.md`
   - `docs/tawan/ARCHITECTURE.md`
   - `docs/tawan/DATA_MODEL.md`
   - `docs/tawan/SECURITY.md`
   - `docs/tawan/IMPLEMENTATION_PLAN.md`
6. For privacy, retention, marketing, export, or Thai-law work, also read `docs/research/2026-08-17-thailand-pdpa-tawan-data.md` and verify current law with primary Thai authorities before advising or shipping.
7. Report the verified branch, working-tree state, latest relevant decision, present milestone, blockers, and proposed next action before editing.

## Source Priority

For approved business intent, resolve conflicts in this order:

1. `docs/tawan/DECISIONS.md`
2. `docs/tawan/PRODUCT_SPEC.md`
3. Architecture, data, and security documents
4. `docs/tawan/IMPLEMENTATION_PLAN.md`
5. The bundled handoff snapshot
6. Notion mirrors, chat transcripts, and older specifications

For implementation status, inspect current tracked code, tests, configuration, and Git history. Implementation proves what exists; it does not override a newer approved product decision. Treat uncommitted files as work in progress and identify their owner before relying on them.

Do not silently reconcile conflicting requirements. Name the conflict and ask the product owner when the canonical records do not resolve business intent.

## Non-Negotiable Invariants

- Use one shared Tawan implementation with a separately provisioned Tawan Instance, `duple_id`, schema, role, Channel identity, Store Knowledge, and Customer data for each store.
- Never share or infer a universal Customer profile across stores.
- Never invent price, stock, discount, delivery, payment, policy, or other store facts.
- Let the model propose; require deterministic authorization and database writes.
- Require Store Owner approval for permanent knowledge, exceptional commercial terms, and final Phase 1 payment decisions.
- Keep outbound Campaign drafting, scheduling, delivery, personalization, attribution, and Campaign intelligence in the Pro tier after the Phase 1 transition gate. Standard retains operational analytics and consent/objection foundations.
- Keep Campaign consent store-specific, purpose-specific, and Channel-specific, with immediate opt-out suppression.
- Treat predictions as recommendations with evidence, confidence, and an insufficient-data state.
- Do not claim production readiness while private Duply runtime, Supabase, dashboard, LINE, legal, or deployment dependencies remain unverified.

## Work And Handoff Discipline

- Explain planned edits and impacted files in plain language before changing code or approved baselines.
- Obtain product-owner approval before nontrivial implementation or any change to business rules.
- Use Git as the handoff medium. Commit a working milestone before another agent uses the same checkout.
- Append shipped decisions to `docs/tawan/DECISIONS.md`; update affected product and technical documents in the same milestone.
- Run available lint, unit, integration, link, secret, and real staging checks. Never hide failures or represent mocked evidence as a real integration run.
- Run an independent review for correctness, security, cross-store leakage, tier-boundary errors, and specification drift.
- Show `git status` before committing. Never push, rewrite history, or touch production without explicit authority.
- Record every successful paid API call in the project's cost ledger before parsing its response.

## Work Tracking — Trello

**As of 2026-09-04, tracking is GitHub + Trello only. Notion is retired** and must not be created, updated, or treated as a source of state. [references/NOTION_STRUCTURE.md](references/NOTION_STRUCTURE.md) is kept for historical context only.

Git remains the technical authority; Trello tracks work in flight. Boards (see `CLAUDE.md`): **Duply** for platform-level work, **Thay** and **Tawan** per Duple. The Tawan board is the creator ↔ team handoff layer:

```
📝 Creator — กำลังทำ  →  ⏳ รอ Team  →  🔧 Team กำลัง deploy  →  ✅ Done
```

When updating a card:

1. Read the canonical Git documents first and record the full 40-character commit SHA. Verify it is reachable from the canonical remote's default branch — never present a local-only or temporary-branch commit as pushed state.
2. Move the card to the next list and comment what was done and what happens next. A move without a comment loses the reason.
3. Leave unavailable owner, status, or estimate metadata blank or marked `Unspecified`; never infer it.
4. Move approved decisions into Git first, push with authorization, then update the card from that remote state.
5. A card is only `Done` when a committed change and verification evidence exist. A checkbox is not evidence.

## Continuation Brief

Before implementation, produce a short brief containing:

- **Verified state:** repository, branch, latest relevant commit, and working-tree changes.
- **Approved scope:** only the decisions relevant to the requested work.
- **Current boundary:** what is implemented, documented, blocked, or post-Phase-1.
- **Risks:** privacy, cross-store isolation, commercial authority, tier access, cost, and dependency concerns.
- **Next action:** smallest safe milestone, impacted files/repositories, checks, and any owner decision required.

When handing work to another account or tool, update the repository documents, commit, and push to the canonical default or permanent protected branch with authorization. Verify the receiving person and intended AI integration can open the pinned sources before declaring the handoff ready. The receiving agent must repeat this workflow instead of trusting a prose summary alone.
