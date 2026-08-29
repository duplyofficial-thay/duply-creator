"""
DRAFT — duples/{duple_id}/chat/card/card_config.py for the family archetype.

Follows thay's CARD_CONFIG pattern (shared by chat.reply AND reach.alert/
schedule.nudge, one object, to avoid the two-places-to-keep-in-sync problem
thay's own card_config.py documents) rather than khun's all-stub pattern —
cards are the primary UX for a kids' product (quest list / wallet /
leaderboard need to look good, not read like a finance ticker row), so this
archetype should not ship stub-only on day one.

subject_field_name is "card_subject" (not "card_ticker" — nothing here is a
ticker). Its meaning is card_type-dependent: quest_list/wallet/schedule
ignore it (subject is always "the current user", already known from
duply_id); leaderboard uses it for scope ("global" or "family");
family_dashboard/reward_shop ignore it (always the caller's own guild).
"""

from agent_loop import CardConfig, build_json_shape_hint

CARD_CONFIG = CardConfig(
    valid_card_types=frozenset({None, "quest_list", "wallet", "leaderboard", "family_dashboard", "reward_shop"}),
    ticker_required_card_types=frozenset(),
    subject_field_name="card_subject",
    fallback_message="ขออภัยจ้า ระบบขัดข้องนิดหน่อย ลองใหม่อีกทีนะ",
)

REPLY_OUTPUT_PROMPT = (
    f"JSON only, no markdown fence: {build_json_shape_hint(CARD_CONFIG)}\n"
    "card types: quest_list=today's quests, wallet=coin/XP/level balance, "
    'leaderboard=ranking (card_subject must be "global" or "family"), '
    "family_dashboard=guild member overview, reward_shop=redeemable rewards. "
    "Only attach a card when the user is explicitly asking to see one of "
    "these (or a router keyword already routed here) — everyday coaching "
    "conversation ('what should I do now', 'why sleep early') stays "
    "card_type=null, plain text. card_type: null by default."
)

SCHEDULE_NUDGE_OUTPUT_PROMPT = (
    f"Return a JSON object exactly: {build_json_shape_hint(CARD_CONFIG)}\n"
    "No markdown fence. Nudges are plain text pushes — do not attach a card "
    "(card_type=null, card_subject=null) unless explicitly told otherwise later."
)
