# Duply — 30-Day Working Plan (3 Sep – 2 Oct 2026)

**Living plan.** No hard deadline. Updated whenever priorities shift.
**Capacity:** ~4 hrs/day per person, Mon–Fri, in 2-hour sessions. Weekends deliberately light.
**Moved out of Notion 2026-09-04** — tracking is now Trello + GitHub.

- **Person 1 — Wasu ("Heng"):** Duply platform + Thay
- **Person 2 — Touchap ("First"):** Tawan + backend

The two lanes are independent — nothing below needs both people at once except the Friday sync and the monthly retro.

---

## 1. Bottlenecks — scheduled earliest

| Task | Owner | Why it blocks |
|---|---|---|
| Rotate leaked Supabase credentials | P2 | Still open. The project now holds the real commerce schema. |
| Add RLS to new `tawan_ai` tables | P2 | 12 new tables created with **no Row Level Security**. With a public `service_role_key`, highest exposure on the board. |
| `TWN-0101` — grant read-only repo access | P2 | The real trigger: 8 cards sit Blocked behind it. |
| A/B test: Gemini 3.1 Flash Lite vs GPT-5.4-mini | P1 | Gate — no prompt polish proceeds until a model is chosen. ✅ **Done early** |
| Invest-domain agent running by ~16 Sep | P1 | Shadow mode is **2 weeks of elapsed time**. Miss it and shadow + marketing plan slip past month end. |

## 2. Person 1 — Thay backlog, in dependency order

| # | Task | Size | Depends on |
|---|---|---|---|
| 2 | **A/B test** — Gemini 3.1 Flash Lite vs GPT-5.4-mini, on Thai naturalness + proactive weaving | Small | Nothing — gates the rest |
| 1 | **UX polish** — LINE Rich Menu (Watchlist / Theme / Macro+Sector) + onboarding first-command examples | Small | Rich Menu: nothing. Copy/prompt half: the A/B gate |
| 3 | **Invest domain** — paper portfolio agent (PM Opus → Writer Sonnet) → 2-week shadow → auto-post X + FB | Large | A/B for prompt tuning. Content source for #4 |
| 4 | **Marketing plan** — channel mix (X/FB/LINE OA), timeline, messaging | Medium | #3 — needs real shadow output to be written honestly |

## 3. Daily schedule

### Week 1 — 3–6 Sep

| Date | Day | P1 — Duply/Thay | P2 — Tawan/backend | Hrs |
|---|---|---|---|---|
| 3 Sep | Thu | Planning · set up A/B harness + eval criteria | **Rotate Supabase credentials** | 2 |
| 4 Sep | Fri | Run A/B — Thai naturalness · proactive weaving | `TWN-0101` grant repo access · begin `TWN-0104` | 4 |
| 5–6 Sep | Sat–Sun | Light — read back A/B samples | Light | ≤1 |

### Week 2 — 7–13 Sep

| Date | Day | P1 — Duply/Thay | P2 — Tawan/backend | Hrs |
|---|---|---|---|---|
| 7 Sep | Mon | **A/B decision** — pick model, write up evidence | `TWN-0104` · `TWN-0105` contracts | 4 |
| 8 Sep | Tue | UX polish — LINE Rich Menu, 3 buttons | `TWN-0106` · `TWN-0107` contracts | 4 |
| 9 Sep | Wed | UX polish — onboarding first-commands + prompt copy | **RLS policies on new `tawan_ai` tables** | 4 |
| 10 Sep | Thu | **Invest domain — design** PM(Opus)→Writer(Sonnet) | `TWN-0108` repo map + contradiction report | 4 |
| 11 Sep | Fri | Build PM agent (selection + reasoning capture) | `TWN-0203` disposable Postgres replay · **Fri sync** | 4 |
| 12–13 Sep | Sat–Sun | Light | Light | ≤1 |

### Week 3 — 14–20 Sep

| Date | Day | P1 — Duply/Thay | P2 — Tawan/backend | Hrs |
|---|---|---|---|---|
| 14 Sep | Mon | Build Writer agent (PM calls → post drafts) | `TWN-0301` registration + shared archetype config | 4 |
| 15 Sep | Tue | Persistence + **cost-ledger logging** | `TWN-0302` Store Resolver + Store Context | 4 |
| 16 Sep | Wed | 🚩 **Shadow mode starts** — drafts only, nothing posted | `TWN-0303` per-store least-privilege schema roles | 4 |
| 17 Sep | Thu | Marketing plan — channel mix research | `TWN-0304` canonical roles + capability grants | 4 |
| 18 Sep | Fri | Shadow review #1 · weekly review | `TWN-0308` append-only audit events · **Fri sync** | 4 |
| 19–20 Sep | Sat–Sun | Light | Light | ≤1 |

### Week 4 — 21–27 Sep

| Date | Day | P1 — Duply/Thay | P2 — Tawan/backend | Hrs |
|---|---|---|---|---|
| 21 Sep | Mon | Marketing plan — messaging + positioning | `TWN-0309` MFA · `TWN-0310` rate limits | 4 |
| 22 Sep | Tue | Shadow monitoring + leftover UX polish | `TWN-0311` security monitoring + alerts | 4 |
| 23 Sep | Wed | Marketing plan — timeline + per-channel cadence | `TWN-0314` secret + key lifecycle management | 4 |
| 24 Sep | Thu | Shadow review #2 — compliance guardrails | `TWN-0312` access review · `TWN-0305` support sessions | 4 |
| 25 Sep | Fri | Weekly review · buffer | `TWN-0313` security exit review · **Fri sync** | 4 |
| 26–27 Sep | Sat–Sun | Light | Light | ≤1 |

### Week 5 — 28 Sep – 2 Oct

| Date | Day | P1 — Duply/Thay | P2 — Tawan/backend | Hrs |
|---|---|---|---|---|
| 28 Sep | Mon | Shadow evaluation — is auto-post safe? | `TWN-0307` cross-store adversarial tests | 4 |
| 29 Sep | Tue | Marketing plan — finalise | `TWN-0401` protected source upload + registry | 4 |
| 30 Sep | Wed | 🚩 **GO/NO-GO on auto-post to X + FB** | `TWN-0406` structured Customer Memory | 4 |
| 1 Oct | Thu | Go → wire auto-post w/ disclosure. No-go → human-in-loop | `TWN-0408` raw-message expiry + Interaction Events | 4 |
| 2 Oct | Fri | **Monthly retro + re-plan (both)** · buffer | **Monthly retro** · buffer | 4 |

## 4. Verification baseline — what is actually proven

Run and confirmed 2026-09-04, not assumed:

```bash
python3 -m unittest discover -s tests -p "test_*.py"   #  Ran 21 tests, OK
PYTHONPYCACHEPREFIX=/tmp/duply-creator-pycache python3 -m compileall scripts duples   # clean
```

21 tests across `test_migration_runner.py` (7), `test_provision_duple.py` (5), `test_tawan_policies.py` (9). Migrations `0010`/`0020`/`0030` applied to Supabase `fpjevusrpausqunjhubk` / `tawan_ai`: 59 tables, 96 indexes, no existing platform tables changed.

**What this does not prove:** no Supabase, LINE, runtime, backup, queue or object-storage integration is tested; tests run with no network and no real credentials; schema *creation* is verified but the authoritative runner, rollback and recovery environment are not. This is why 15 cards sit in **Review** rather than **Done** — the manifest is deliberately strict, and that strictness is worth keeping.

## 5. Risks and open items

1. **RLS is missing on the new tables.** Per `tawan/CURRENT_TASK_STATUS.md`: *"Supabase warned that the new tables were created without Row Level Security… RLS policies and runtime authorization must be completed before storing customer data or exposing these tables through client keys."* With an unrotated, publicly-leaked `service_role_key`, this is the highest-exposure item. **Hard gate: no customer data in these tables until both are closed.**
2. **Credential rotation is still open** and now riskier — the migrations landed on that same project.
3. **Codex is building ahead of the project's own gates.** Milestone 4–6 features are implemented while Milestone 1 discovery is Blocked and Milestone 3 security is Backlog. To the team's credit these are *not* marked Done — they sit in **Review**, which is the honest call. Still needs an explicit decision: is the gating obsolete, or does this code need rework once `TWN-0104`–`0107` land?
4. **"Auto-post X + FB" contradicts a documented rule.** The marketing team design says *"Draft only, always. Nothing this team produces gets posted, sent, or published automatically"* — written for Thay's financial-compliance exposure. The 30 Sep go/no-go must explicitly amend the rule or keep a human in the loop. See `marketing/briefs/2026-08-06-thay-content-roadmap.md`.
5. **Paid-call cost tracking.** The A/B test and the recurring PM-Opus → Writer-Sonnet agent are real money. Ledger each call at success time, before parsing the response.
6. **Invest-domain build estimate is the weakest number here.** Four sessions to design and build a two-agent system with persistence is tight. If it slips, cut scope — protect the 16 Sep shadow start rather than the feature set.
7. **Two agents on one worktree is causing real collisions.** On 4 Sep, Codex committed while a Claude session had changes staged and swept them into its own commit (`afce807`). Nothing was lost that time. `CLAUDE.md`'s one-agent-per-repo rule exists for this reason.
8. **Weekends are intentionally empty.** If work keeps spilling into them, cut the weekday load rather than absorbing it.

---

**Related:** [`trello-import/`](trello-import/) (card export) · [`tawan/README.md`](tawan/README.md) (Tawan docs index) · [`tawan/CURRENT_TASK_STATUS.md`](tawan/CURRENT_TASK_STATUS.md) (live status)
