"""
tests/test_card_renderer.py — rewritten 2026-07-13 against the real n8n
node code (RENDER_PT/RENDER_NS/RENDER_WL/RENDER_ST/RENDER_MC/RENDER_THEME).
Covers the invariants that were previously wrong or unverified: no stray
bubble-level "footer"/"hero" on single-ticker cards, tag caps (2 for the
single-ticker card, 1 for any list row), MC's has_tag:false never flips
the percent sign, penny-mode theme swap, NS renders every news item (no
cap at 3).
"""

import os
import sys

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from card_renderer import (  # noqa: E402
    render_pt_card, render_ns_card, build_pt_single_card, build_meta_row,
    fmt_pct, SECTOR_META, MACRO_META,
    render_bf_card, _bf_score_label, _bf_score_color, _bf_earning_suffix,
)

PT_ITEM_AAPL = {
    "ticker": "AAPL", "status": "SUCCESS",
    "display": {
        "marketState": "REGULAR", "updateTime": "13/07/2026 18:53",
        "regular": {"price": 213.5, "percent": 1.23},
        "extended": None,
        "analysis": {
            "tags": ["STAR-STACKED", "PRICING-POWER"],
            "EMA50": {"distPct": 5.0, "structure": "Above", "Trend": "Bullish"},
            "rsi": {"value": 55.0, "zone": "Neutral", "trend": "Rising"},
            "macd": {"value": 1.234, "trend": "Bullish", "histTrend": "Expanding"},
            "volume": {"pace": 1.5, "label": "Active", "current": 1000},
            "rr": {"ratio": 2.0, "status": "Lower Risk"},
        },
        "visualData": {"prices": {"sl": 190, "sup": 200, "p": 210, "res": 220, "tp": 230},
                        "positions": {"cur": 60, "prev": 55}},
    },
    "technicalRaw": {"currentPrice": 213.5, "ema50": 205.0, "macd": 1.234, "vol_pace": 1.5},
}

PT_ITEM_TLT = {
    "ticker": "TLT", "status": "SUCCESS",
    "display": {
        "marketState": "CLOSED",
        "regular": {"price": 91.2, "percent": -0.4},
        "extended": {"price": 91.3, "percent": 0.1},
        "analysis": {"tags": ["STAR-STACKED"]},
    },
}

TAG_DATA = {
    "STAR-STACKED": {"th": "ดาวเรียงตัว", "c1": "#134e4a", "c2": "#7c3aed", "tx": "#ffffff"},
    "PRICING-POWER": {"th": "กุมอำนาจราคา", "c1": "#7209B7", "c2": "#F72585", "tx": "#ffffff"},
}


def test_pt_single_card_no_bubble_level_footer_or_hero():
    """Real RENDER_PT has no bubble.hero and no bubble.footer — the
    ticker logo is an inline 18px box, and the footer row is the last
    item of body.contents."""
    card = build_pt_single_card("AAPL", PT_ITEM_AAPL, TAG_DATA, in_watchlist=False, lang="EN")
    assert card["type"] == "bubble"
    assert "hero" not in card
    assert "footer" not in card


def test_pt_single_card_caps_tags_at_two():
    card = build_pt_single_card("AAPL", PT_ITEM_AAPL, TAG_DATA, in_watchlist=False, lang="EN")
    tag_row = card["body"]["contents"][0]
    assert len(tag_row["contents"]) == 2


def test_pt_single_card_penny_mode_theme_swap():
    penny_item = dict(PT_ITEM_AAPL)
    penny_item["display"] = {**PT_ITEM_AAPL["display"], "regular": {"price": 12.0, "percent": 1.0}}
    card = build_pt_single_card("PENY", penny_item, TAG_DATA, in_watchlist=False)
    assert card["body"]["backgroundColor"] == "#0F172A"  # penny (<$50) dark theme
    normal = build_pt_single_card("AAPL", PT_ITEM_AAPL, TAG_DATA, in_watchlist=False)
    assert normal["body"]["backgroundColor"] == "#FFFFFF"


def test_pt_single_card_ema_color_from_raw_price_not_structure_text():
    """EMA50's color is `technicalRaw.currentPrice > technicalRaw.ema50`,
    NOT derived from the translated structure text — a real bug in an
    earlier draft of this file conflated the two."""
    item = dict(PT_ITEM_AAPL)
    item["technicalRaw"] = {"currentPrice": 100.0, "ema50": 205.0, "macd": 1.0, "vol_pace": 1.0}
    card = build_pt_single_card("AAPL", item, TAG_DATA, in_watchlist=False)
    indicator_block = card["body"]["contents"][4]
    ema_row = indicator_block["contents"][0]
    ema_color = ema_row["contents"][4]["color"]
    assert ema_color == "#E63946", "currentPrice(100) < ema50(205) -> down color, regardless of structure='Above'"


def test_pt_single_card_ipo_limited_skips_bar_and_indicators():
    item = dict(PT_ITEM_AAPL)
    item["status"] = "IPO_LIMITED"
    card = build_pt_single_card("NEWIPO", item, TAG_DATA, in_watchlist=False)
    assert len(card["body"]["contents"]) == 3  # tags, header block, footer only


def test_build_meta_row_invert_flips_regular_but_not_extended():
    """Confirmed against Directory_MC (runs before RENDER_MC): TLT/LQD's
    REGULAR percent is multiplied by -1 upstream; extended (after-hours)
    percent is left untouched. The row builder itself doesn't know
    "TLT"/"LQD" — the caller (_mc_card) decides via MC_INVERT."""
    row = build_meta_row("TLT", PT_ITEM_TLT, MACRO_META["TLT"], TAG_DATA, postback_data="TLT", invert=True)
    pct_text = row["contents"][2]["contents"][0]["text"]
    assert pct_text == "+0.40%", "raw -0.40% must flip to +0.40% when invert=True"
    ext_text = row["contents"][2]["contents"][1]["contents"][1]["text"]
    assert ext_text == "+0.10%", "extended percent (raw +0.1%) must NOT flip"


def test_build_meta_row_no_invert_leaves_sign_alone():
    row = build_meta_row("TLT", PT_ITEM_TLT, MACRO_META["TLT"], TAG_DATA, postback_data="TLT", invert=False)
    pct_text = row["contents"][2]["contents"][0]["text"]
    assert pct_text == "-0.40%"


def test_build_meta_row_caps_at_one_tag():
    item = dict(PT_ITEM_AAPL)
    row = build_meta_row("XLK", item, SECTOR_META["XLK"], TAG_DATA, postback_data="TECH")
    name_col = row["contents"][1]
    tag_slot = name_col["contents"][1]
    # with a tag: horizontal wrapper box holding exactly one chip (matches n8n
    # RENDER_MC/ST); without: the height-14px placeholder box
    if tag_slot.get("layout") == "horizontal":
        assert len(tag_slot["contents"]) == 1, "at most one tag chip in the wrapper"
        assert tag_slot["contents"][0].get("cornerRadius") == "100px"
    else:
        assert tag_slot.get("height") == "14px"


def test_fmt_pct():
    assert fmt_pct(1.5) == "+1.50%"
    assert fmt_pct(-0.4) == "-0.40%"
    assert fmt_pct(None) == "-"


def test_render_pt_card_single_dispatch():
    card = render_pt_card({"AAPL": PT_ITEM_AAPL}, mode="single", tag_data=TAG_DATA,
                           watchlist=["AAPL"], lang="EN")
    assert card["type"] == "bubble"
    assert "hero" not in card


def test_render_pt_card_single_no_data():
    card = render_pt_card({}, mode="single", tag_data=TAG_DATA, label="AAPL")
    assert "No data" in card["body"]["contents"][0]["text"]


def test_render_pt_card_wl_excludes_benchmarks_and_no_star():
    items = {"SPY": PT_ITEM_AAPL, "QQQ": PT_ITEM_AAPL, "NVDA": PT_ITEM_TLT}
    card = render_pt_card(items, mode="list", tag_data=TAG_DATA, card_type="wl")
    assert card["header"]["contents"][0]["text"] == "WATCHLIST"
    # exactly one row (NVDA) since SPY/QQQ are benchmarks excluded from rows
    row_wrappers = card["body"]["contents"]
    assert len(row_wrappers) == 1
    inner = row_wrappers[0]["contents"][0]
    assert inner["action"] == {"type": "postback", "data": "NVDA"}


def test_render_pt_card_st_sorts_desc_and_uses_header_footer():
    items = {
        "SPY": PT_ITEM_AAPL, "QQQ": PT_ITEM_AAPL,
        "XLK": {**PT_ITEM_AAPL, "display": {**PT_ITEM_AAPL["display"], "regular": {"price": 200, "percent": 0.5}}},
        "XLE": {**PT_ITEM_AAPL, "display": {**PT_ITEM_AAPL["display"], "regular": {"price": 90, "percent": 2.0}}},
    }
    card = render_pt_card(items, mode="list", tag_data=TAG_DATA, card_type="st", benchmarks=["SPY", "QQQ"])
    assert card["header"]["contents"][0]["text"] == "SECTORS"
    assert "footer" in card
    rows = [c for c in card["body"]["contents"] if c.get("type") == "box" and c.get("layout") == "horizontal"]
    names = [r["contents"][1]["contents"][0]["text"] for r in rows]
    assert names[0] == "Energy"  # XLE 2.0% > XLK 0.5%


def test_render_ns_card_renders_all_news_not_capped_at_three():
    ns_item = {
        "ticker": "AAPL", "companyName": "Apple Inc.",
        "news": [{"title": f"story {i}", "source": "Reuters", "date": "2026-07-10", "url": f"https://x/{i}"}
                 for i in range(5)],
    }
    card = render_ns_card({"AAPL": ns_item}, mode="single", watchlist=[])
    assert "hero" not in card and "footer" not in card
    body_texts = str(card["body"]["contents"])
    for i in range(5):
        assert f"story {i}" in body_texts


def test_render_ns_card_no_url_omits_action_key():
    ns_item = {"ticker": "AAPL", "news": [{"title": "x", "source": "R", "date": "d", "url": ""}]}
    card = render_ns_card({"AAPL": ns_item}, mode="single")
    news_row = card["body"]["contents"][3]
    assert "action" not in news_row


BF_ITEM_NVDA = {
    "ticker": "NVDA", "status": "SUCCESS", "updateTime": "13/07/2026 16:05",
    "ts": 1783933511704,
    "meta": {"modelType": "STANDARD", "dataAsOf": {"pendingPeriod": None, "isPostEarning": False}},
    "earningData": {"nextDate": "2099-08-26", "lastEps": {"date": "2026-05-20"}},
    "display": {
        "state": "STANDARD", "ticker": "NVDA", "companyName": "NVIDIA Corporation",
        "fiscalPeriod": "Q1/2027", "groupLabel": "Industry", "groupName": "Semiconductors",
        "mktCapVal": "5.1T", "mktCapSize": "LARGE", "betaVal": "2.2",
        "valuation": {"type": "P/E (TTM)", "score": 9.4, "value": "32.24x",
                      "industryAvg": "Ind. Avg: 57.82x", "forwardVal": "Fwd P/E: 23.50x", "status": "FAIR"},
        "pillars": [
            {"name": "GROWTH", "score": 10.0, "metric": "Rev Growth (YoY)", "value": "85.2%"},
            {"name": "QUALITY", "score": 10.0, "metric": "ROIC", "value": "63.0%"},
            {"name": "REALITY", "score": 10.0, "metric": "FCF Margin", "value": "47.0%"},
            {"name": "SURVIVAL", "score": 10.0, "metric": "Net Debt/EBITDA", "value": "-0.4x"},
        ],
        "tags": ["STAR-STACKED", "PRICING-POWER"],
    },
}


def test_bf_score_label_standard_vs_early():
    assert _bf_score_label(9.5, "STANDARD") == "PRIME"
    assert _bf_score_label(9.5, "EARLY_GROWTH") == "PROVEN"
    assert _bf_score_label(0.5, "STANDARD") == "FRAGILE"


def test_bf_score_color_tiers():
    assert _bf_score_color(9.5) == "#04e762"
    assert _bf_score_color(0.5) == "#D00000"


def test_render_bf_card_shape_and_footer_date_matches_pt():
    card = render_bf_card("NVDA", BF_ITEM_NVDA, TAG_DATA, in_watchlist=False, lang="EN")
    assert card["type"] == "bubble" and card["size"] == "kilo"
    assert "hero" not in card and "footer" not in card
    # footer is last body item; BF is date-only BY DESIGN (see render_bf_card:
    # "with fiscalPeriod + earning suffix the full timestamp makes the footer
    # too long") — shared DD-Mon-YY format, time part stripped. Test previously
    # asserted the full timestamp (stale vs the deliberate date-only change).
    footer = card["body"]["contents"][-1]
    footer_text = footer["contents"][0]["text"]
    assert footer_text.startswith("13-Jul-26 |"), footer_text
    assert "16:05" not in footer_text, footer_text
    assert "Q1/2027" in footer_text


def test_render_bf_card_2x2_pillar_grid():
    card = render_bf_card("NVDA", BF_ITEM_NVDA, TAG_DATA, in_watchlist=False, lang="EN")
    # pillar grid is the 5th body child (tags, header, stats, valuation, pillars, footer)
    pillar_block = card["body"]["contents"][4]
    assert len(pillar_block["contents"]) == 2  # two rows
    assert len(pillar_block["contents"][0]["contents"]) == 2  # 2 pillars/row


def test_render_bf_card_th_translates_pillar_names():
    card = render_bf_card("NVDA", BF_ITEM_NVDA, TAG_DATA, in_watchlist=False, lang="TH")
    txt = str(card)
    assert "การเติบโต" in txt  # GROWTH -> TH
    assert "GROWTH" not in txt


def test_bf_earning_suffix_upcoming():
    # nextDate far in future -> " | Q2:Nd"
    suffix = _bf_earning_suffix(BF_ITEM_NVDA, "Q1/2027")
    assert suffix.startswith(" | Q2:") and suffix.endswith("d")
