# Tawan Current Task Status

**Updated:** 2026-09-03

**Source:** [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md), current local Git commits,
and verified local test output.

## Overall Status

There are 149 tracked Tawan cards in the local canonical manifest:

| Status | Count | Meaning |
|---|---:|---|
| Done | 5 | Committed and verified complete |
| Review | 15 | Local implementation or evidence exists; final integration/acceptance remains |
| Ready | 1 | Can start as soon as the required human access is granted |
| Blocked | 8 | External dependency prevents responsible execution |
| Backlog | 120 | Planned work waiting for earlier cards or a later phase |

## Done

- `TWN-0002`: canonical product and technical documents.
- `TWN-0003`: Thai PDPA research and counsel questions.
- `TWN-0004`: portable Tawan handoff skill.
- `TWN-0005`: approved Tawan foundation merged to canonical `main` in PR #4.
- `TWN-0006`: commit-pinned Markdown handoff links added to the Notion hub.

## Review: Local Evidence Exists

- `TWN-0001`: historical Notion reconciliation.
- `TWN-0201`, `0202`, `0204`, `0205`: local test, migration, fixture, registration, and replay foundation.
- `TWN-0406`: memory source/confidence validation.
- `TWN-0503`, `0505`, `0507`, `0508`: task idempotency, unsafe discount protection, lifecycle authority, and explainable customer tiers.
- `TWN-0602`, `0603`, `0604`, `0606`: price precedence, order authority, stock reservation, and payment evidence collision rules.
- `TWN-0615`: reply-time capture command validation.

These cards are not falsely marked Done because runtime persistence, database
transactions, or owner acceptance still needs to be connected where noted in
the manifest.

## Ready

- `TWN-0101`: obtain read-only access to the Duply runtime, data/Supabase,
  dashboard, and deployment repositories.

## Review: External Board Reconciliation Still Needed

- `TWN-0001`: historical Notion reconciliation remains a review item.
- `TWN-0007`: existing Notion Board records still require an owner-approved dry run before any bulk update.

## Explicitly Blocked

| Cards | Blocker | Help needed |
|---|---|---|
| `TWN-0007` | Existing Notion record reconciliation | Owner approval of the dry-run mapping before updating or archiving human-maintained records |
| `TWN-0102` | LINE destination and Store Context | Duply webhook path, mapping input, and failure behavior |
| `TWN-0103` | Runtime dispatch and tools | Read-only runtime access and agent/tool registry contract |
| `TWN-0104` | Knowledge/vector/memory/raw-message contract | Authoritative tables, retrieval filters, retention, deletion, and owner |
| `TWN-0105` | Shared write infrastructure | Authorization, idempotency, queue, cache, storage, audit, and retry contracts |
| `TWN-0106` | LINE media and delivery | Staging OA/simulator, media limits, Flex/retry/delivery contracts |
| `TWN-0107` | Migration and recovery infrastructure | Staging database, runner, rollback, backup/restore, and cost ledger |
| `TWN-0108` | Discovery synthesis | Completion of `TWN-0102` through `0107` |

## Backlog By Milestone

| Milestone | Cards | Count | Main outcome |
|---|---|---:|---|
| 0 | `TWN-0001` to `0007` | 7 | Source of truth, Git, Notion, and handoff |
| 1 | `TWN-0101` to `0108` | 8 | Verified Duply runtime/data/LINE discovery |
| 2 | `TWN-0201` to `0207` | 7 | Test harness, migration replay, fixtures, and isolation |
| 3 | `TWN-0301` to `0314` | 14 | Store Workspace, roles, MFA, audit, limits, and secrets |
| 4 | `TWN-0401` to `0412` | 12 | Knowledge ingestion, customer memory, retention, and review |
| 5 | `TWN-0501` to `0512` | 12 | Journeys, tasks, approvals, tiers, and notifications |
| 6 | `TWN-0601` to `0617` | 17 | Catalog, order, payment, fulfilment, shipping, and LINE journey |
| 7 | `TWN-0701` to `0713` | 13 | Owner/staff dashboard |
| 8 | `TWN-0801` to `0812` | 12 | Standard operational analytics |
| 9 | `TWN-0901` to `0905` | 5 | Restaurant, beauty, wholesale, and construction validation |
| 10 | `TWN-1001` to `1023` | 23 | Legal, rights, recovery, incident, and pilot readiness |
| 11 | `TWN-1100` to `1118` | 19 | Pro Campaigns and intelligence |

## Current Next Order

1. Friend provides read-only access for Duply runtime, Supabase/data,
   dashboard, and deployment.
2. Confirm a disposable Supabase/Postgres environment and apply migrations
   `0010`, `0020`, and `0030`.
3. Connect local policies to database transactions and the LINE adapter.
4. Run two-store isolation and the complete fashion journey.
5. Begin dashboard and Standard analytics after the operational API boundary is
   known.
6. Begin Pro Campaign work only after Phase 1 acceptance and separate Pro
   approval.

## Git Handoff Note

The reviewed Tawan foundation is merged to `origin/main` via PR #4 at
`095eb84045bdd4cbb2a349cff04d42a5cf816acf`. The Notion hub now links to the
canonical Markdown files at that immutable commit. The local checkout still
has unrelated uncommitted user files; they were not included in the merge.

Current verification: 21 unit tests pass and Python compilation passes. The
SQL migrations have been statically planned and rendered, but not applied to a
live Supabase project.
