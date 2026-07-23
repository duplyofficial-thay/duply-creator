"""
tests/test_pipeline.py — render_card() dispatch correctness. Mocks the
fetch layer only (network I/O) — real Router + real CardRenderer run, so
these tests catch wiring bugs (wrong tickers reaching fetch, wrong mode/
label reaching render) that per-module unit tests can't.

Rewritten 2026-07-13 alongside card_renderer.py's rewrite against the real
n8n node code — list cards now use header/footer (not title-in-body), single
mode has no "hero" key, and MC's has_tag:false no longer flips the percent
sign (confirmed that was never real n8n behavior).
"""

import os
import sys
from unittest.mock import patch

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
_ROUTER_DIR = os.path.normpath(os.path.join(_DIR, "..", "router"))
if _ROUTER_DIR not in sys.path:
    sys.path.insert(0, _ROUTER_DIR)

import pipeline as pl  # noqa: E402
from router import classify, RouteDecision, CARD  # noqa: E402

PT_ITEM = lambda price, pct: {"status": "SUCCESS", "display": {  # noqa: E731
    "marketState": "REGULAR", "regular": {"price": price, "percent": pct},
    "extended": None, "analysis": {"tags": []},
}}


def test_render_card_returns_none_for_unresolvable_types():
    for text in ("AAPL bf", "NS", "TAG|abc"):
        route = classify(text)
        assert route.lane == "CARD", f"{text!r} should still classify as CARD"
        assert pl.render_card(route, user_ctx={}) is None, f"{text!r} should render to None this round"


def test_render_card_single_ticker_pt():
    route = classify("AAPL")
    with patch.object(pl, "fetch_pt_batch", return_value={"AAPL": PT_ITEM(213.5, 1.2)}) as m_fetch, \
         patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={"watchlist": ["AAPL"]})
    m_fetch.assert_called_once_with(["AAPL"])
    assert card["type"] == "bubble"
    assert "hero" not in card, "real RENDER_PT has no bubble.hero — logo is an inline 18px box"


def test_render_card_pt_multi_ticker_compare_list():
    # multi-ticker PT comes from the AI lane (LLM card_ticker="NVDA,AMD,TSM"),
    # never from router.classify() — construct the RouteDecision directly.
    route = RouteDecision(lane=CARD, card_type="pt", ticker="nvda, AMD,TSM,NVDA")
    with patch.object(pl, "fetch_pt_batch", return_value={
        "SPY": PT_ITEM(550, 0.5), "QQQ": PT_ITEM(480, 0.8),
        "NVDA": PT_ITEM(120, 2.1), "AMD": PT_ITEM(160, -0.4), "TSM": PT_ITEM(190, 1.0),
    }) as m_fetch, patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={"watchlist": []})
    m_fetch.assert_called_once_with(["SPY", "QQQ", "NVDA", "AMD", "TSM"])  # dedup + upper + benchmarks first
    assert card["header"]["contents"][0]["text"] == "Stocks"
    rows = card["body"]["contents"]
    assert len(rows) == 3  # NVDA/AMD/TSM — SPY/QQQ are header summary, not rows


def test_render_card_pt_multi_ticker_caps_at_five():
    route = RouteDecision(lane=CARD, card_type="pt", ticker="A,B,C,D,E,F,G")
    with patch.object(pl, "fetch_pt_batch", return_value={}) as m_fetch, \
         patch.object(pl, "get_tags", return_value={}):
        pl.render_card(route, user_ctx={"watchlist": []})
    called = m_fetch.call_args[0][0]
    assert called == ["SPY", "QQQ", "A", "B", "C", "D", "E"]


def test_render_card_wl_excludes_benchmarks_from_rows():
    route = classify("WL")
    with patch.object(pl, "fetch_pt_batch", return_value={
        "SPY": PT_ITEM(550, 0.5), "QQQ": PT_ITEM(480, 0.8), "NVDA": PT_ITEM(120, 2.1),
    }) as m_fetch, patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={"watchlist": ["NVDA"]})
    m_fetch.assert_called_once_with(["SPY", "QQQ", "NVDA"])
    assert card["header"]["contents"][0]["text"] == "WATCHLIST"
    rows = card["body"]["contents"]
    assert len(rows) == 1  # NVDA only — SPY/QQQ are the header summary, not rows
    inner = rows[0]["contents"][0]
    assert inner["action"] == {"type": "postback", "data": "NVDA"}, "tap-to-navigate, confirmed against RENDER_WL"


def test_render_card_sector_dispatches_full_sector_order():
    route = classify("SECTOR")
    with patch.object(pl, "fetch_pt_batch", return_value={}) as m_fetch, \
         patch.object(pl, "get_tags", return_value={}):
        pl.render_card(route, user_ctx={})
    called_tickers = m_fetch.call_args[0][0]
    assert called_tickers[0] == "SPY" and "XLK" in called_tickers


def test_render_card_sector_sorts_by_percent_desc_with_icon_rows():
    route = classify("SECTOR")
    with patch.object(pl, "fetch_pt_batch", return_value={
        "SPY": PT_ITEM(550, 0.1), "QQQ": PT_ITEM(480, 0.1),
        "XLK": PT_ITEM(200, 0.5), "XLE": PT_ITEM(90, 2.0), "XLF": PT_ITEM(40, -1.0),
    }), patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={})
    assert card["header"]["contents"][0]["text"] == "SECTORS"
    rows = [r for r in card["body"]["contents"] if r.get("type") != "separator"]
    names = [r["contents"][1]["contents"][0]["text"] for r in rows]
    assert names == ["Energy", "Technology", "Financials"], "must sort by % desc: XLE(2.0) > XLK(0.5) > XLF(-1.0)"
    assert rows[0]["contents"][0]["backgroundColor"] == "#EF4444", "icon color from sector_meta"
    assert rows[0]["action"]["data"] == "ENERGY", "row postback -> theme keyword, not bare ticker"


def test_render_card_macro_fixed_order_and_invert_through_full_pipeline():
    """Confirmed against Directory_MC (runs before RENDER_MC, missed in an
    earlier pass): TLT/LQD's REGULAR percent is flipped upstream (* -1)
    before the render node ever sees it. Icon/color box never changes."""
    route = classify("MACRO")
    with patch.object(pl, "fetch_pt_batch", return_value={
        "VT": PT_ITEM(110, 0.3), "SPY": PT_ITEM(550, 1.0), "QQQ": PT_ITEM(480, 0.8),
        "IWM": PT_ITEM(210, 0.2), "TLT": PT_ITEM(91, -0.4), "LQD": PT_ITEM(108, -0.1),
        "GLD": PT_ITEM(240, 0.6),
    }), patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={})
    assert card["header"]["contents"][1]["contents"][1]["text"] == "+0.30%"  # World: VT
    rows = [r for r in card["body"]["contents"] if r.get("type") != "separator"]
    names = [r["contents"][1]["contents"][0]["text"] for r in rows]
    assert names == ["Market", "Growth", "Small Cap", "Rates", "Credit", "Gold"], "fixed order, not sorted"
    pct_texts = [r["contents"][2]["contents"][0]["text"] for r in rows]
    assert pct_texts[3] == "+0.40%", "TLT's raw -0.4% must arrive inverted through the full pipeline"


def test_render_card_macro_thai_names():
    route = classify("MACRO")
    with patch.object(pl, "fetch_pt_batch", return_value={"SPY": PT_ITEM(550, 1.0)}), \
         patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={"system_lang": "TH"})
    rows = card["body"]["contents"]
    assert rows[0]["contents"][1]["contents"][0]["text"] == "ภาพรวมตลาด"


def test_render_card_theme_resolves_via_universe():
    route = classify("TECH")
    with patch("data_fetcher.get_universe", return_value={
        "tickerMap": {"AAPL": {"themes": ["TECH"]}, "MSFT": {"themes": ["TECH"]}}
    }), patch.object(pl, "fetch_pt_batch", return_value={}) as m_fetch, \
         patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={})
    assert card is not None
    called_tickers = m_fetch.call_args[0][0]
    assert "AAPL" in called_tickers and "SPY" in called_tickers  # SPY/XLK benchmarks


def test_render_card_ns_single_ticker():
    route = classify("AAPL ns")
    ns_item = {"ticker": "AAPL", "short": "...", "news": [{"title": "x", "source": "Reuters", "date": "2026-07-13"}]}
    with patch.object(pl, "fetch_ns_batch", return_value={"AAPL": ns_item}) as m_fetch:
        card = pl.render_card(route, user_ctx={})
    m_fetch.assert_called_once_with(["AAPL"])
    assert "hero" not in card


def test_render_card_macro_ns_bypasses_resolve_target():
    """mc_ns is intercepted before resolve_target(), same as tag_info —
    not a ticker fetch."""
    route = classify("NS")
    assert route.card_type == "mc_ns"
    data = {"driver": "Oil shock", "sentiment": "RISK-OFF", "news": [{"title": "x", "source": "Reuters", "date": "d"}]}
    with patch.object(pl, "fetch_macro_ns", return_value=data):
        card = pl.render_card(route, user_ctx={})
    assert card["header"]["contents"][0]["text"] == "US MACRO"


def test_render_card_macro_ns_none_when_redis_empty():
    route = classify("NS")
    with patch.object(pl, "fetch_macro_ns", return_value=None):
        assert pl.render_card(route, user_ctx={}) is None


def test_render_card_theme_returns_none_on_universe_failure():
    route = classify("TECH")
    with patch("data_fetcher.get_universe", return_value=None):
        assert pl.render_card(route, user_ctx={}) is None


def test_render_card_theme_translates_labels():
    route = classify("ROBOTIC")  # THEME_LABELS: ROBOTIC -> "PHYSICAL AI"
    with patch("data_fetcher.get_universe", return_value={
        "tickerMap": {"NVDA": {"themes": ["ROBOTIC"]}}
    }), patch.object(pl, "fetch_pt_batch", return_value={
        "NVDA": PT_ITEM(120, 2.1), "SPY": PT_ITEM(550, 0.5), "QQQ": PT_ITEM(480, 0.8),
    }), patch.object(pl, "get_tags", return_value={}):
        card = pl.render_card(route, user_ctx={})
    assert card["header"]["contents"][0]["text"] == "PHYSICAL AI"
