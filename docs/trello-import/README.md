# Trello Import — Duply Board Export

**Exported:** 2026-09-04
**Source:** the Notion "Duply Agile Work Board" (now retired)
**Destination:** Trello — [Duple - Tawan](https://trello.com/b/HUbjHwDh/duple-tawan) and the Duply board

Notion is no longer used for tracking. This folder is the bridge: everything that lived on the Notion board, exported so nothing is stranded there.

## ✅ Migration status — complete (2026-09-04)

All 28 cards are now on the **[Duple - Tawan](https://trello.com/b/HUbjHwDh/duple-tawan)** board. 8 had been migrated earlier; the remaining 20 were created on 4 Sep with full descriptions.

A **Backlog** list was added to the board (it previously had only To Do / Doing / Done), because 19 not-yet-started cards would otherwise have piled into To Do. The two pre-existing cards whose descriptions already said `Status: BACKLOG` were moved into it so list and stated status agree.

Final distribution: **Backlog 16 · To Do 5 · Doing 4 · Done 3.**

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
- **`TWN-*` ids are the join key.** Where a card corresponds to a manifest card, keep the id in the title so Trello, `docs/tawan/TASK_BREAKDOWN.md`, code and evidence stay linkable. Cards here that are not `TWN-*` are Duply-stream work with no manifest entry.
- **Don't import the Done cards into an active list.** Three are already complete and are here for history.
- **Two cards are security gates**, not ordinary work: credential rotation and RLS. Both are `Blocked` and both must close before customer data goes into `tawan_ai`.

## Related

- Plan and reasoning: [`../DUPLY_30_DAY_PLAN.md`](../DUPLY_30_DAY_PLAN.md)
- Tawan manifest: [`../tawan/TASK_BREAKDOWN.md`](../tawan/TASK_BREAKDOWN.md) — 149 `TWN-*` cards, of which only the first eight Duply Platform cards had reached Trello as of 4 Sep
- Live status: [`../tawan/CURRENT_TASK_STATUS.md`](../tawan/CURRENT_TASK_STATUS.md)
- Legacy Notion CSVs: [`../tawan/notion-import/`](../tawan/notion-import/)
