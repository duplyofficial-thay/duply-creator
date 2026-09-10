# XP / coin / level design — DRAFT, first-pass numbers for testing

These are starting numbers, not fixed rules — easy to retune once real usage shows
whether kids are leveling up too fast/slow or rewards feel too cheap/expensive.
Nothing here needs a schema change to adjust (`xp_reward`/`coin_reward` are per-row
in `quest_templates`, `level` is computed in Python, not enforced by the DB).

## Difficulty → reward (used by `content/starter_quests_seed.sql` and by parents
authoring their own quests via `create_quest`)

| Difficulty | XP | Coins | Feel |
|---|---|---|---|
| easy | 10 | 10 | daily habit-sized (brush teeth, tidy toys) |
| medium | 25 | 25 | needs some effort (homework, 15 min exercise) |
| hard | 50 | 50 | a real push (deep-clean the room, exam review) |

1 coin = 1 XP by design — keeps the mental math simple for a kid ("10 coin quest = 10
XP quest"). They're still separate columns/ledger entries so this ratio can be broken
later (e.g. a "bonus XP, no coins" quest type) without a schema change.

## Expected income (assumption, to sanity-check reward pricing against)

Assuming a kid completes ~3-5 quests/day, mostly easy/medium with an occasional hard
one: roughly **50-70 coins/day**, **350-490 coins/week**. Reward pricing below is
calibrated against this — recalibrate once real data replaces the assumption.

## Level thresholds (cumulative total_xp required)

| Level | Cumulative XP needed |
|---|---|
| 1 | 0 |
| 2 | 50 |
| 3 | 120 |
| 4 | 220 |
| 5 | 350 |
| 6 | 520 |
| 7 | 730 |
| 8 | 1000 |
| 9 | 1320 |
| 10 | 1700 |
| 11 | 2150 |
| 12 | 2670 |

Gaps grow (50 → 70 → 100 → 130 → ...) so leveling feels quick at first (levels 1-3
in the first week or two at ~50-70 xp/day) and gradually slows — deliberate, so early
engagement is rewarded but level doesn't become meaningless by month two.

Reference implementation (wherever `wallets.level` gets recomputed after a
`currency_ledger` insert — this is Python logic, not a DB constraint):

```python
LEVEL_THRESHOLDS = [0, 50, 120, 220, 350, 520, 730, 1000, 1320, 1700, 2150, 2670]

def level_for_xp(total_xp: int) -> int:
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if total_xp >= threshold:
            level = i + 1
    # Beyond the table: extend the same growing-gap pattern rather than hard-stop.
    if total_xp > LEVEL_THRESHOLDS[-1]:
        last_gap = LEVEL_THRESHOLDS[-1] - LEVEL_THRESHOLDS[-2]
        extra = total_xp - LEVEL_THRESHOLDS[-1]
        gap = last_gap + 70
        while extra >= gap:
            extra -= gap
            level += 1
            gap += 70
    return level
```

## Reward pricing guidance (for `content/starter_reward_examples.md` and parents
authoring their own via `create_reward`)

Calibrated against ~50-70 coins/day:

| Tier | Coin cost | Feel |
|---|---|---|
| Small | 50-100 | same-day payoff (a snack, 30 min extra screen time) |
| Medium | 200-400 | end-of-week payoff (pick the movie, a small toy) |
| Big | 800-1500 | multi-week saving goal (a bigger toy, a weekend outing) |

Keep at least one "small" reward always available — same-day payoff matters a lot
for younger kids and for the ADHD-support angle from the original brief (immediate,
visible reward for effort, not just a distant big prize).
