# Starter reward examples — DRAFT, inspiration for parents, not seeded centrally

Unlike quests, rewards are **not** seeded as global templates — `reward_catalog` is
guild-scoped by design (each family's rewards reflect what that family can actually
give: screen time rules differ, allowance differs, what a kid wants differs). These
are examples a parent can copy via the `create_reward` tool when setting up their
family, not rows in a seed script. Pricing follows `xp_coin_level_design.md`'s tiers.

## Small (50-100 coins) — same-day payoff

- ขนมพิเศษ 1 ชิ้น — 50
- เวลาเล่นจอเพิ่ม 30 นาที — 80
- เลือกเมนูของหวานหลังมื้อเย็น — 60

## Medium (200-400 coins) — end-of-week payoff

- เลือกหนังดูกับครอบครัวคืนนี้ — 250
- ของเล่นชิ้นเล็ก/สติกเกอร์ที่อยากได้ — 300
- ไปกินร้านโปรดวันเสาร์ — 350

## Big (800-1500 coins) — multi-week saving goal

- ของเล่นชิ้นใหญ่ที่อยากได้มานาน — 1000
- ไปเที่ยวสวนสนุก/สถานที่โปรดวันหยุด — 1200
- เลือกกิจกรรมครอบครัวทั้งวันในวันหยุด — 1500

## Tips for parents setting these up

- Keep at least one small reward always available — same-day payoff matters, not
  just a distant big prize.
- Price against what your kid actually earns per day (~50-70 coins is the design
  assumption here) — adjust up/down once you see real numbers from `get_wallet`.
- It's fine to retire or reprice a reward later (`reward_catalog.is_active`) if it
  turns out mispriced — nothing about a past redemption changes retroactively.
