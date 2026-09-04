# Tawan Documentation Index

**Updated:** 2026-09-04

Every Tawan document, categorised. Statuses below are quoted from each document's own header — they are not a second opinion, so if a document's header changes, update this row too.

Work tracking lives in **Trello** — [Duple - Tawan](https://trello.com/b/HUbjHwDh/duple-tawan) — and **GitHub**. Notion is retained as historical reference only and is not updated as a parallel board. Stable `TWN-*` ids are the join key between the Git manifest, Trello cards, code, and evidence.

---

## Start here

Reading in this order gets a new person or agent oriented without chat history.

| # | Document | Why this order |
|---|---|---|
| 1 | [`../../CLAUDE.md`](../../CLAUDE.md) | Repo entry point: session workflow, Trello boards, canonical terminology |
| 2 | [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md) | What Tawan is meant to do before how it is built |
| 3 | [`COMMERCE_DESIGN.md`](COMMERCE_DESIGN.md) | The current Phase 1 design |
| 4 | [`CURRENT_TASK_STATUS.md`](CURRENT_TASK_STATUS.md) | What is actually done vs claimed |
| 5 | [`PHASE_1_ROADBLOCKS.md`](PHASE_1_ROADBLOCKS.md) | What is blocked and who must clear it |

---

## Product and scope

| Document | What it is | Status (per its own header) |
|---|---|---|
| [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md) | Product behaviour, tiers, and acceptance criteria | Approved product baseline (2026-08-18) |
| [`COMMERCE_DESIGN.md`](COMMERCE_DESIGN.md) | Phase 1 design: catalog + dual-role sales chat (เซลส์/เลขา) + PromptPay checkout | Draft v3 (2026-08-27) — multi-tenant single-schema, replaces the per-store-Duple assumption in v2 |

> `COMMERCE_DESIGN.md` was previously filed under `docs/superpowers/specs/` and described elsewhere as a "superseded historical draft." That description was wrong — v3 is current and describes the live multi-tenant model. Moved here 2026-09-04.

---

## Architecture and data

| Document | What it is | Status (per its own header) |
|---|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Boundaries, isolation, flows, dependencies | Approved target architecture; **implementation has not started** |
| [`DATA_MODEL.md`](DATA_MODEL.md) | Entities, lifecycle, invariants | Logical model approved; additive store-scoped migration applied and live-verified |
| [`DATA_FLOW.md`](DATA_FLOW.md) | How data moves through the live schema | Live schema: Supabase `fpjevusrpausqunjhubk`, schema `tawan_ai` |
| [`OWNED_DATA_IMPLEMENTATION_PLAN.md`](OWNED_DATA_IMPLEMENTATION_PLAN.md) | Plan for the store-owned data implementation | Proposed for local Supabase implementation |

---

## Security

| Document | What it is | Status (per its own header) |
|---|---|---|
| [`SECURITY.md`](SECURITY.md) | Threats, privacy, marketing, retention, launch blockers | Required control baseline; **not evidence of implementation** |
| [`../research/2026-08-17-thailand-pdpa-tawan-data.md`](../research/2026-08-17-thailand-pdpa-tawan-data.md) | Thai PDPA research and counsel questions | Research starting point — explicitly **not legal advice** |

⚠️ Two open security items are not yet closed and are tracked on the board, not here: the leaked Supabase credentials still require rotation, and the new `tawan_ai` tables were created **without Row Level Security**. No customer data belongs in those tables until both are resolved.

---

## Planning and delivery

| Document | What it is | Status (per its own header) |
|---|---|---|
| [`TASK_BREAKDOWN.md`](TASK_BREAKDOWN.md) | Canonical `TWN-*` task manifest — 149 cards across 12 milestones | Canonical task manifest for Git and tracker synchronisation |
| [`CURRENT_TASK_STATUS.md`](CURRENT_TASK_STATUS.md) | Live status by state: Done / Review / Ready / Blocked / Backlog | Updated 2026-09-03 |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | Ordered milestones and verification steps | Approved planning baseline; implementation not started |
| [`PHASE_1_ROADBLOCKS.md`](PHASE_1_ROADBLOCKS.md) | Blocked cards + the exact checklist Duply platform must answer | Working handoff for Duply platform coordination |

**How these relate:** `TASK_BREAKDOWN.md` defines the cards and never changes their IDs. `CURRENT_TASK_STATUS.md` says where each one stands right now. `PHASE_1_ROADBLOCKS.md` explains why the blocked ones are blocked. Trust `CURRENT_TASK_STATUS.md` over any status written inside a plan document.

---

## Decisions and review

| Document | What it is |
|---|---|
| [`DECISIONS.md`](DECISIONS.md) | Approved decision history, dated. Append here when something is decided — do not leave a decision only in chat |
| [`TEAM_DATA_MODEL_GAP_REVIEW.md`](TEAM_DATA_MODEL_GAP_REVIEW.md) | Team review that found the original model strong on privacy/authority/auditability but incomplete for daily Thai retail operation |

---

## Testing and evidence

| Document | What it is | Status |
|---|---|---|
| [`TESTING.md`](TESTING.md) | Supported local commands, scope, and what the tests do **not** prove | Resolved locally for `TWN-0201`; database and integration evidence remain environment-dependent |

Verified 2026-09-04:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
PYTHONPYCACHEPREFIX=/tmp/duply-creator-pycache python3 -m compileall scripts duples
```

21 tests pass, compilation clean. This proves creator-kit logic only — no Supabase, LINE, runtime, queue or storage integration is covered, and tests run with no network and no real credentials.

---

## Artifacts and legacy

| Path | What it is | Keep? |
|---|---|---|
| [`tawan-delivery-dashboard.html`](tawan-delivery-dashboard.html) | Standalone Tawan Delivery Dashboard (single-file HTML) | Active |
| [`notion-import/`](notion-import/) | CSVs built to import the `TWN-*` manifest into Notion (`tawan-tasks.csv`, `tawan-sprints.csv`, `tawan-existing-sprints.csv`) | **Legacy** — tracking moved to Trello + GitHub. Kept for history; do not treat as a live sync target |

---

## Conventions

- Filenames in this folder are `UPPER_SNAKE_CASE.md`. Dated filenames belong in `docs/research/`, not here.
- A document's own header carries its status; this index mirrors it rather than inventing one.
- `Done` requires a committed change plus verification evidence. A checkbox in a tracker is not evidence.
- Status claims go stale. Check `git log --oneline -15` and `CURRENT_TASK_STATUS.md` before trusting any of them.
