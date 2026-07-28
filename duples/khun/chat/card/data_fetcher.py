"""
card/data_fetcher.py -- Khun (SET market).
PT cards only -- calls pt-service :8001 (Settrade, SET).
"""

import os
import sys

_FIP_CLIENT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..",
                 "platform", "fip_client")
)
if _FIP_CLIENT_DIR not in sys.path:
    sys.path.insert(0, _FIP_CLIENT_DIR)

from pt_util import batch_pt_set, get_tag_data  # noqa: E402

PT_COMPARE_MAX_TICKERS = 5


class ResolvedTarget:
    __slots__ = ("tickers", "mode", "benchmarks", "invert", "label")

    def __init__(self, tickers, mode, benchmarks=None, invert=None, label=None):
        self.tickers = tickers
        self.mode = mode
        self.benchmarks = benchmarks or []
        self.invert = invert or set()
        self.label = label


def resolve_target(route, user_ctx: dict):
    card_type = route.card_type

    if card_type == "pt":
        tickers = list(dict.fromkeys(
            t.strip().upper() for t in (route.ticker or "").split(",") if t.strip()
        ))
        if not tickers:
            return None
        if len(tickers) > 1:
            return ResolvedTarget(tickers=tickers[:PT_COMPARE_MAX_TICKERS],
                                  mode="list", benchmarks=[], label="Stocks")
        return ResolvedTarget(tickers=[tickers[0]], mode="single", label=tickers[0])

    if card_type == "wl":
        watchlist = user_ctx.get("watchlist") or []
        if not watchlist:
            return None
        return ResolvedTarget(tickers=list(watchlist), mode="list",
                              benchmarks=[], label="Watchlist")

    return None


def fetch_pt_batch(tickers: list[str]) -> dict[str, dict]:
    return batch_pt_set(tickers)


def get_tags() -> dict:
    return get_tag_data()
