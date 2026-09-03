# Tawan Notion Import Package

**Prepared:** 2026-08-18

**Source commit:** `c0c1a22cd7af01af0362305ca823f1c0721ed387`

This package mirrors the canonical Tawan task manifest into import-ready CSV files.

## Files

- [Task cards](tawan-tasks.csv): 149 rows covering `TWN-0001` through `TWN-1118`.
- [Existing Sprint updates](tawan-existing-sprints.csv): Sprint 1 through Sprint 3. Match these records by exact Sprint title and update them in place.
- [New Sprint records](tawan-sprints.csv): Sprint 4 through Sprint 27. Create these only after confirming no exact-title record already exists.

## Safe Import Rules

1. Use the existing Tawan Board and Sprints databases under `Retr > Duply Project`.
2. Match task records by exact `Task ID`; never use a fuzzy title match automatically.
3. Match Sprint records by exact `Sprint` title. Update Sprint 1 through Sprint 3 in place and never import a duplicate Sprint 3.
4. Show a dry-run mapping before modifying an existing record.
5. Do not merge, archive, replace, or delete a human-maintained record without explicit owner approval.
6. Preserve comments, history, relations, and human-authored fields.
7. Leave `Assignee` and `Story Points` empty until the team estimates and accepts the work.
8. Map `Sprint Plan` to the existing `Sprint` relation when the connector supports relation lookup.
9. Keep Sprint 23 as the separate Pro approval gate. Do not start Sprint 24 through Sprint 27 until `TWN-1100` is approved.
10. Verify 149 unique Task IDs and 27 total Sprint records after import.
11. Link each imported record back to the canonical GitHub Markdown after the source commit is pushed to a permanent branch.

## Intended Sprint Boundary

- Sprint 1 through Sprint 22: documentation, discovery, Standard Phase 1, compliance, and pilot acceptance.
- Sprint 23: optional Custom B2B export implementation and separate Pro scope approval.
- Sprint 24 through Sprint 27: Pro Campaigns and intelligence, gated by Sprint 23 approval.

The CSV `Source` field currently points to the repository homepage because the source commit is local-only. Replace it with a full commit-pinned Markdown URL after explicit GitHub push approval.
