# Trello Import — Duply Board Export

**Exported:** 2026-09-04
**Source:** the Notion "Duply Agile Work Board" (now retired)
**Destination:** Trello — [Duple - Tawan](https://trello.com/b/HUbjHwDh/duple-tawan) and the Duply board

Notion is no longer used for tracking. This folder is the bridge: everything that lived on the Notion board, exported so nothing is stranded there.

## ✅ Migration status — complete (2026-09-04)

All 28 cards are on Trello, split across three boards by scope. There is one board per Duple plus a top-level board, per `CLAUDE.md`.

| Board | Cards | What lives here |
|---|---:|---|
| **[Duple - Thay](https://trello.com/b/0uIg9kTv/duple-thay)** | 17 | All Thay work: A/B model test, UX polish, the invest-domain agent, the shadow chain, the auto-post go/no-go, and the four marketing-plan cards |
| **[Duple - Tawan](https://trello.com/b/HUbjHwDh/duple-tawan)** | 8 | Platform gates Tawan is blocked on: credential rotation, RLS, TWN-0101 access, TWN-0104→0107 contracts, plus repo-visibility and the monthly retro |
| **[Duply Main](https://trello.com/b/oex0CmEZ/duply-main)** | 3 | Cross-Duple: the AI marketing playbook, and the Khun / Dom paused placeholders |

A **Backlog** list was added to each board — all three had only To Do / Doing / Done, and the not-yet-started cards would otherwise have piled into To Do. On the Tawan board, the two pre-existing cards whose descriptions already said `Status: BACKLOG` were moved into it so list and stated status agree.

Distribution — Thay: Backlog 12 · To Do 4 · Done 1. Tawan: Backlog 2 · Doing 4 · Done 2. Duply Main: Backlog 2 · To Do 1.

This folder is now a historical record of the migration, not a pending action.

## Files

| File | What it is |
|---|---|
| `duply-board-cards.csv` | All 28 cards, flat and importable. Quoted CSV, round-trip verified. Columns: `Name, Description, List, Labels, Due Date, Members, Type, Priority, Area, Story Points` |
| `duply-board-cards.md` | Same 28 cards, grouped by status, with full descriptions — the readable version, and the easier one to hand to an agent that will create the cards via API |

## Card counts by list

| List | Cards |
|---|---:|
| Blocked | 3 |
| In Review | 1 |
| To Do | 7 |
| Backlog | 14 |
| Done | 3 |

## Sprints (from the Notion Sprints database)

| Sprint | Dates | Goal |
|---|---|---|
| Sprint 1 — Gate & Polish | 4–13 Sep | Clear the A/B model gate, ship UX polish, design the invest-domain agent and build the PM half |
| Sprint 2 — Agent Build & Shadow Start | 14–20 Sep | Writer agent + persistence + cost logging. Shadow mode running by 16 Sep. Begin marketing channel research |
| Sprint 3 — Shadow Window & Marketing Draft | 21–27 Sep | Monitor shadow output against compliance guardrails; draft the marketing plan from real samples |
| Sprint 4 — Shadow Verdict & Go/No-Go | 28 Sep – 2 Oct | Evaluate two weeks of shadow output, make the auto-post go/no-go, finalise the marketing plan, retro |

Trello has no native sprint object — use a label, a checklist on a milestone card, or Trello's own board-per-sprint convention, whichever the team prefers.

## Suggested list mapping

The `List` column carries the Notion status verbatim. Map to Trello lists as suits the destination board:

| Notion status | Suggested Trello list |
|---|---|
| Blocked | Blocked (or Backlog with a `blocked` label) |
| In Review | ⏳ รอ Team / In Review |
| To Do | 📝 Creator — กำลังทำ / To Do |
| Backlog | Backlog |
| Done | ✅ Done |

If the destination board has fewer lists than these, keep the original status explicit in the card description rather than losing it — the convention recorded in `docs/tawan/DECISIONS.md` (2026-09-04).

## Caveats worth reading before importing

- **Descriptions are as authored on 3–4 Sep.** Card *properties* were re-read from Notion at export time, but if anyone edited a card *body* in Notion after 4 Sep, that edit is not captured here.
- **`TWN-*` ids are the join key — but the manifest they pointed at is gone.** `docs/tawan/TASK_BREAKDOWN.md` (149 cards) was deleted by the 4 Sep docs consolidation (`4dd9461`). `DECISIONS.md` still says the ids "remain the join key to the Git task manifest", which no longer resolves. Keep the ids in card titles regardless — they still link cards to code, commits and evidence — but see the note below about the missing manifest.
- **Don't import the Done cards into an active list.** Three are already complete and are here for history.
- **Two cards are security gates**, not ordinary work: credential rotation and RLS. Both are `Blocked` and both must close before customer data goes into `tawan_ai`.

## Related

- Plan and reasoning: [`../DUPLY_30_DAY_PLAN.md`](../DUPLY_30_DAY_PLAN.md)
- Tawan docs (consolidated 4 Sep to 4 files): [`../tawan/REQUIREMENTS.md`](../tawan/REQUIREMENTS.md) · [`../tawan/DESIGN.md`](../tawan/DESIGN.md) · [`../tawan/REFERENCE.md`](../tawan/REFERENCE.md) · [`../tawan/DECISIONS.md`](../tawan/DECISIONS.md)

## ⚠️ Open issue — the 149-card manifest has no live home

The 4 Sep consolidation (`4dd9461`) deleted `docs/tawan/TASK_BREAKDOWN.md` and `docs/tawan/CURRENT_TASK_STATUS.md`. Only **28 cards** were ever migrated to Trello — the 8 platform gates plus the 20 Duply-stream cards in this export. The Tawan milestone plan (Milestones 3–11, roughly 121 `TWN-*` cards with their dependency chains and acceptance criteria) is therefore in **neither** Trello nor the working tree; it exists only in git history at `9f8789a:docs/tawan/TASK_BREAKDOWN.md`.

That may be deliberate — the consolidated docs are cleaner, and much of that plan was blocked behind `TWN-0101` anyway. But `DECISIONS.md` still asserts the ids "remain the join key to the Git task manifest", so the decision record and the repo currently contradict each other. Worth resolving one way or the other:

- restore the manifest (or a trimmed version) so the dependency chains stay readable, **or**
- migrate the remaining `TWN-*` cards to Trello, **or**
- update `DECISIONS.md` to say the manifest was retired and git history is its archive.
- Legacy Notion CSVs: [`../tawan/notion-import/`](../tawan/notion-import/)
