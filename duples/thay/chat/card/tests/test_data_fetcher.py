"""
tests/test_data_fetcher.py — resolve_target() (mostly pure) + fetch_*_batch()
(I/O, mocked — no live services required, matches the "offline only, no
service spin-up" testing constraint).
"""

import json
import os
import sys
from unittest.mock import patch, MagicMock

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
_ROUTER_DIR = os.path.normpath(os.path.join(_DIR, "..", "router"))
if _ROUTER_DIR not in sys.path:
    sys.path.insert(0, _ROUTER_DIR)

import data_fetcher as df  # noqa: E402
from router import classify  # noqa: E402


def test_resolve_bf_single_ticker():
    """BF now resolves to a single-ticker target (bf-service :8010 live) —
    same shape as pt/ns."""
    route = classify("AAPL bf")
    assert route.card_type == "bf"
    t = df.resolve_target(route, user_ctx={})
    assert t.tickers == ["AAPL"] and t.mode == "single"


def test_resolve_single_ticker():
    route = classify("AAPL")
    t = df.resolve_target(route, user_ctx={})
    assert t.tickers == ["AAPL"] and t.mode == "single"


def test_resolve_wl_dedupes_and_leads_with_benchmarks():
    route = classify("WL")
    t = df.resolve_target(route, user_ctx={"watchlist": ["SPY", "AAPL", "NVDA"]})
    assert t.tickers == ["SPY", "QQQ", "AAPL", "NVDA"], "SPY/QQQ lead, no dup SPY"


def test_resolve_wl_empty_watchlist():
    route = classify("WL")
    t = df.resolve_target(route, user_ctx={})
    assert t.tickers == ["SPY", "QQQ"]


def test_resolve_sector():
    route = classify("SECTOR")
    t = df.resolve_target(route, user_ctx={})
    assert t.tickers[0] == "SPY" and "XLK" in t.tickers


def test_resolve_macro_carries_invert_set():
    route = classify("MACRO")
    t = df.resolve_target(route, user_ctx={})
    assert "TLT" in t.invert and "LQD" in t.invert
    assert "SPY" in t.tickers


def test_resolve_theme_uses_universe():
    route = classify("TECH")
    with patch.object(df, "get_universe", return_value={
        "tickerMap": {"AAPL": {"themes": ["TECH"]}, "MSFT": {"themes": ["TECH"]}, "XOM": {"themes": ["ENERGY"]}}
    }):
        t = df.resolve_target(route, user_ctx={})
    assert set(t.tickers) >= {"AAPL", "MSFT", "SPY", "XLK"}
    assert "XOM" not in t.tickers


def test_resolve_theme_returns_none_on_universe_failure():
    route = classify("TECH")
    with patch.object(df, "get_universe", return_value=None):
        assert df.resolve_target(route, user_ctx={}) is None


def test_resolve_macro_ns_not_ticker_based():
    """mc_ns is a single pre-fetched Redis blob (macro:raw:ns), not a
    ticker batch — no ResolvedTarget applies. Handled directly in
    pipeline.py via fetch_macro_ns(), same pattern as tag_info."""
    route = classify("NS")
    assert route.card_type == "mc_ns"
    assert df.resolve_target(route, user_ctx={}) is None


def test_fetch_macro_ns_parses_redis_json():
    with patch.object(df, "redis_get", return_value=json.dumps(
        {"driver": "Oil shock", "sentiment": "RISK-OFF", "news": [{"title": "x"}]}
    )):
        data = df.fetch_macro_ns()
    assert data == {"driver": "Oil shock", "sentiment": "RISK-OFF", "news": [{"title": "x"}]}


def test_fetch_macro_ns_missing_key_returns_none():
    with patch.object(df, "redis_get", return_value=None):
        assert df.fetch_macro_ns() is None


def test_fetch_macro_ns_malformed_json_returns_none():
    with patch.object(df, "redis_get", return_value="not json"):
        assert df.fetch_macro_ns() is None


def test_resolve_tag_info_not_supported_this_round():
    route = classify("TAG|abc")
    assert df.resolve_target(route, user_ctx={}) is None


def test_fetch_pt_batch_reuses_batch_pt_us():
    with patch.object(df, "batch_pt_us", return_value={"AAPL": {"ticker": "AAPL"}}) as mock_fn:
        result = df.fetch_pt_batch(["AAPL"])
    mock_fn.assert_called_once_with(["AAPL"])
    assert result == {"AAPL": {"ticker": "AAPL"}}


def test_fetch_ns_batch_keys_by_self_describing_ticker_field():
    """ns_service.py's /ns/batch now stamps a 'ticker' field onto every
    result item server-side (fixed at the source since /ns/batch had zero
    other consumers) — keying is by that field, not by response order."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([
        {"ticker": "AAPL", "short": "(NS) AAPL ...", "news": [{"title": "A"}]},
        {"ticker": "NVDA", "short": "(NS) NVDA ...", "news": [{"title": "B"}]},
    ]).encode()
    mock_resp.__enter__ = lambda s: mock_resp
    mock_resp.__exit__ = lambda *a: None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = df.fetch_ns_batch(["AAPL", "NVDA"])

    assert result["AAPL"]["short"] == "(NS) AAPL ..."
    assert result["NVDA"]["short"] == "(NS) NVDA ..."


def test_fetch_ns_batch_keys_correctly_even_if_response_order_differs():
    """The whole point of keying by field instead of position: an
    out-of-order response (e.g. ns-service returns whichever finishes
    first from its ThreadPoolExecutor) must still map to the right
    ticker — this would silently mis-key under positional zipping."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([
        {"ticker": "NVDA", "short": "(NS) NVDA ..."},  # NVDA finished first
        {"ticker": "AAPL", "short": "(NS) AAPL ..."},
    ]).encode()
    mock_resp.__enter__ = lambda s: mock_resp
    mock_resp.__exit__ = lambda *a: None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = df.fetch_ns_batch(["AAPL", "NVDA"])  # requested in this order

    assert result["AAPL"]["short"] == "(NS) AAPL ..."
    assert result["NVDA"]["short"] == "(NS) NVDA ..."


def test_fetch_ns_batch_drops_items_missing_ticker_defensively():
    """Belt-and-suspenders: if a malformed item without 'ticker' ever
    slips through, drop it rather than crash or mis-key."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([
        {"ticker": "AAPL", "short": "ok"},
        {"short": "no ticker field"},
    ]).encode()
    mock_resp.__enter__ = lambda s: mock_resp
    mock_resp.__exit__ = lambda *a: None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = df.fetch_ns_batch(["AAPL"])

    assert result == {"AAPL": {"ticker": "AAPL", "short": "ok"}}


def test_fetch_ns_batch_dedupes_request_list():
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([{"ticker": "AAPL", "short": "x"}]).encode()
    mock_resp.__enter__ = lambda s: mock_resp
    mock_resp.__exit__ = lambda *a: None

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = df.fetch_ns_batch(["AAPL", "AAPL"])

    called_url = mock_open.call_args[0][0].full_url
    assert called_url.count("AAPL") == 1
    assert result == {"AAPL": {"ticker": "AAPL", "short": "x"}}


def test_fetch_ns_batch_empty_input():
    assert df.fetch_ns_batch([]) == {}


def test_fetch_ns_batch_swallows_errors():
    with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
        assert df.fetch_ns_batch(["AAPL"]) == {}
