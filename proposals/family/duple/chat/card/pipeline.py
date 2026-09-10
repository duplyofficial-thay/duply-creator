"""
DRAFT — duples/{duple_id}/chat/card/pipeline.py for the family archetype.

Wires data_fetcher -> card_renderer, mirroring thay's pipeline.py shape:
render_card_with_status() duck-types `route` (reads .card_type/.card_subject)
rather than importing router's RouteDecision class, so card/ stays free of
any import-time dependency on router/ — same reasoning thay's file documents.
"""

from card_renderer import (
    render_quest_list_card,
    render_wallet_card,
    render_leaderboard_card,
    render_family_dashboard_card,
    render_reward_shop_card,
)
from data_fetcher import (
    fetch_quests,
    fetch_wallet,
    fetch_leaderboard,
    fetch_family_members,
    fetch_rewards,
)

_ALT_TEXT = {
    "quest_list": {"TH": "เควสวันนี้", "EN": "Today's Quests"},
    "wallet": {"TH": "กระเป๋าเงิน", "EN": "My Wallet"},
    "leaderboard": {"TH": "แร้งกิ้ง", "EN": "Leaderboard"},
    "family_dashboard": {"TH": "ห้องครอบครัว", "EN": "Family Room"},
    "reward_shop": {"TH": "ร้านรางวัล", "EN": "Reward Shop"},
}


def _card_alt_text(card_type: str, lang: str) -> str:
    return _ALT_TEXT.get(card_type, {}).get(lang, "การ์ด")


def render_card(route, user_ctx: dict) -> dict | None:
    """route: router.RouteDecision (lane must be CARD). user_ctx must include
    duply_id; system_lang optional (default TH). Returns
    {"contents": flex_json, "altText": ...} or None — callers must handle
    None explicitly."""
    return render_card_with_status(route, user_ctx)[0]


def render_card_with_status(route, user_ctx: dict) -> tuple[dict | None, str | None]:
    """(card, fail_status). fail_status is None for "nothing to show yet"
    (e.g. no quests today) since that's a valid empty-state card, not a
    failure — card_renderer already handles empty lists gracefully. Reserved
    for genuine fetch errors once data_fetcher is wired to the real DB."""
    lang = (user_ctx.get("system_lang") or "TH").upper()
    duply_id = user_ctx.get("duply_id")
    card_type = route.card_type

    if card_type == "quest_list":
        quests = fetch_quests(duply_id)
        card = render_quest_list_card(quests, lang=lang)
        return {"contents": card, "altText": _card_alt_text(card_type, lang)}, None

    if card_type == "wallet":
        wallet = fetch_wallet(duply_id)
        card = render_wallet_card(wallet, lang=lang)
        return {"contents": card, "altText": _card_alt_text(card_type, lang)}, None

    if card_type == "leaderboard":
        scope = (getattr(route, "card_subject", None) or "family").lower()
        if scope not in ("global", "family"):
            scope = "family"
        rows = fetch_leaderboard(duply_id, scope)
        card = render_leaderboard_card(rows, scope, lang=lang)
        return {"contents": card, "altText": _card_alt_text(card_type, lang)}, None

    if card_type == "family_dashboard":
        data = fetch_family_members(duply_id)
        card = render_family_dashboard_card(data, lang=lang)
        return {"contents": card, "altText": _card_alt_text(card_type, lang)}, None

    if card_type == "reward_shop":
        # guild_id resolution happens inside fetch_family_members/fetch_rewards
        # in the real implementation (via family_members) — user_ctx carries
        # only duply_id here, matching every other card type in this file.
        guild_data = fetch_family_members(duply_id)
        rewards = fetch_rewards(guild_data.get("guild_id", ""))
        card = render_reward_shop_card(rewards, lang=lang)
        return {"contents": card, "altText": _card_alt_text(card_type, lang)}, None

    return None, None
