"""
DRAFT — duples/{duple_id}/chat/card/card_renderer.py for the family archetype.

Pure formatting: takes the shapes data_fetcher.py returns and produces LINE
flex message "bubble" dicts. No DB/platform dependency, so this half can be
finished and unit-tested independent of how data_fetcher gets wired to the
real schema. Kid-friendly styling: bigger, colorful, playful — deliberately
not modeled on thay/khun's finance-card look.

Each render_* function returns the `contents` bubble only (not the full
{"type": "flex", "altText": ..., "contents": ...} envelope — pipeline.py
adds altText per the existing thay pattern).
"""

_COLOR_XP = "#6C5CE7"
_COLOR_COIN = "#F5A623"
_COLOR_BG = "#FFFFFF"
_COLOR_HEADER = "#2ECC71"


def _bubble(header_text: str, header_color: str, body_contents: list[dict], footer_contents: list[dict] | None = None) -> dict:
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": header_color,
            "paddingAll": "16px",
            "contents": [
                {"type": "text", "text": header_text, "color": "#FFFFFF", "weight": "bold", "size": "lg"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": _COLOR_BG,
            "spacing": "md",
            "contents": body_contents,
        },
    }
    if footer_contents:
        bubble["footer"] = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": footer_contents}
    return bubble


def render_quest_list_card(quests: list[dict], lang: str = "TH") -> dict:
    if not quests:
        empty = "วันนี้ไม่มีเควสจ้า พักผ่อนได้เลย!" if lang == "TH" else "No quests today — enjoy the break!"
        return _bubble("เควสวันนี้" if lang == "TH" else "Today's Quests", _COLOR_HEADER,
                       [{"type": "text", "text": empty, "wrap": True}])

    status_emoji = {"assigned": "⬜", "submitted": "⏳", "approved": "✅", "rejected": "❌", "expired": "⌛"}
    rows = []
    for q in quests:
        emoji = status_emoji.get(q["status"], "⬜")
        rows.append({
            "type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": f"{emoji} {q['title']}", "wrap": True, "flex": 4, "size": "sm"},
                {"type": "text", "text": f"+{q['xp_reward']}xp/{q['coin_reward']}🪙", "flex": 3, "size": "xs", "color": "#888888", "align": "end"},
            ],
        })
    return _bubble("เควสวันนี้" if lang == "TH" else "Today's Quests", _COLOR_HEADER, rows)


def render_wallet_card(wallet: dict, lang: str = "TH") -> dict:
    body = [
        {"type": "box", "layout": "horizontal", "contents": [
            {"type": "text", "text": "🪙 เหรียญ" if lang == "TH" else "🪙 Coins", "size": "md"},
            {"type": "text", "text": str(wallet["coin_balance"]), "size": "md", "weight": "bold", "align": "end"},
        ]},
        {"type": "box", "layout": "horizontal", "contents": [
            {"type": "text", "text": "✨ XP", "size": "md"},
            {"type": "text", "text": str(wallet["total_xp"]), "size": "md", "weight": "bold", "align": "end"},
        ]},
        {"type": "box", "layout": "horizontal", "contents": [
            {"type": "text", "text": "🏅 Level", "size": "md"},
            {"type": "text", "text": str(wallet["level"]), "size": "md", "weight": "bold", "align": "end"},
        ]},
    ]
    return _bubble("กระเป๋าเงินของฉัน" if lang == "TH" else "My Wallet", _COLOR_COIN, body)


def render_leaderboard_card(rows: list[dict], scope: str, lang: str = "TH") -> dict:
    title = ("แร้งกิ้งครอบครัว" if scope == "family" else "แร้งกิ้งทั่วโลก") if lang == "TH" else \
             ("Family Leaderboard" if scope == "family" else "Global Leaderboard")
    if not rows:
        return _bubble(title, _COLOR_XP, [{"type": "text", "text": "ยังไม่มีข้อมูลจ้า" if lang == "TH" else "No data yet", "wrap": True}])

    medals = ["🥇", "🥈", "🥉"]
    body = []
    for i, r in enumerate(rows[:20]):
        rank_label = medals[i] if i < 3 else f"{i + 1}."
        name = r.get("nickname") or r["duply_id"]
        body.append({
            "type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": f"{rank_label} {name}", "flex": 4, "size": "sm", "wrap": True},
                {"type": "text", "text": f"{r['total_xp']} xp", "flex": 3, "size": "xs", "color": "#888888", "align": "end"},
            ],
        })
    return _bubble(title, _COLOR_XP, body)


def render_family_dashboard_card(data: dict, lang: str = "TH") -> dict:
    header = data.get("guild_name") or ("ห้องครอบครัว" if lang == "TH" else "Family Room")
    members = data.get("members", [])
    if not members:
        return _bubble(header, _COLOR_HEADER, [{"type": "text", "text": "ยังไม่มีสมาชิกจ้า" if lang == "TH" else "No members yet", "wrap": True}])

    role_emoji = {"parent": "👑", "child": "🧒"}
    body = []
    for m in members:
        emoji = role_emoji.get(m.get("role"), "🧒")
        name = m.get("nickname") or m["duply_id"]
        done = m.get("done_today", 0)
        body.append({
            "type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": f"{emoji} {name}", "flex": 4, "size": "sm", "wrap": True},
                {"type": "text", "text": f"✅ {done} today", "flex": 3, "size": "xs", "color": "#888888", "align": "end"},
            ],
        })
    return _bubble(header, _COLOR_HEADER, body)


def render_reward_shop_card(rewards: list[dict], lang: str = "TH") -> dict:
    title = "ร้านรางวัล" if lang == "TH" else "Reward Shop"
    if not rewards:
        return _bubble(title, _COLOR_COIN, [{"type": "text", "text": "ยังไม่มีรางวัลตอนนี้จ้า" if lang == "TH" else "No rewards set up yet", "wrap": True}])

    body = []
    for r in rewards:
        body.append({
            "type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": r["title"], "flex": 4, "size": "sm", "wrap": True},
                {"type": "text", "text": f"{r['cost_coins']}🪙", "flex": 2, "size": "xs", "color": "#888888", "align": "end"},
            ],
        })
    return _bubble(title, _COLOR_COIN, body)
