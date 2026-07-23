"""
card/data_fetcher.py — resolve_target() + fetch_pt_batch()/fetch_ns_batch().

Reuses the batch-fetch layer in platform/fip_client/pt_util.py and
ns_util.py (also used by platform/tools/packs/finance/us/get_stock_us.py — the
AI-lane tools, via the _fip_util.py shim) rather than reimplementing
ticker resolution or PT/NS fetching. pt_util.py/ns_util.py were relocated
fip-engine/fip-client/ -> platform/fip_client/ on 2026-07-19: the
infra/platform vs infra/engine Docker split puts platform/ and fip-engine/
in separate containers with separate filesystems, so this sys.path hack
can only reach files inside its own image's build context. Not moved into
top-level shared/ — that's scoped to chat/agent-orchestration logic
(see shared/redis_contracts.py's docstring), while pt_util/ns_util are
fip-engine domain knowledge (SECTOR_ORDER, THEME_BENCHMARK, the
fip:tags:list namespace) that happens to be called from platform/duples
code, not the other way around. Named pt_util/ns_util, not
market_util/news_util (their original names) — pt/bf/ns is the vocabulary
already used everywhere else in this codebase, "market" was a vague label
that would only get more confusing once bf_util exists too.

DataFetcher does NOT touch the ctx-string caches (sector:ctx, macro:ctx:pt,
theme:ctx:{theme}, user:{duply_id}:wl:ctx) that the AI-lane tools use to
cache their *rendered LLM strings* — those are a different concern from card
rendering. batch_pt_us() itself always returns full structured `display`
data regardless of pt-us-service's own internal cache state, so there is
nothing extra for DataFetcher to cache here. (This corrects an assumption
in the original plan's §2 cache-strategy table, which assumed DataFetcher
needed to read/write those ctx-string keys directly — it doesn't.)
"""

import os
import sys

_FIP_CLIENT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..",
                 "platform", "fip_client")
)
if _FIP_CLIENT_DIR not in sys.path:
    sys.path.insert(0, _FIP_CLIENT_DIR)

from pt_util import (  # noqa: E402
    batch_pt_us, get_tag_data, get_universe, get_theme_tickers,
    SECTOR_ORDER, MACRO_ETFS, MACRO_ORDER, INVERT, THEME_BENCHMARK, redis_get,
)
from ns_util import batch_ns_us  # noqa: E402
from bf_util import batch_bf_us  # noqa: E402

# The real cap enforced below (watchlist limit parity). card_config.py's
# REPLY_OUTPUT_PROMPT/REACH_ALERT_OUTPUT_PROMPT import this instead of
# hardcoding "5" again in prose — a prompt claiming a different number
# than this would silently lie to the LLM (truncation still happens here,
# just not where the model was told it would).
PT_COMPARE_MAX_TICKERS = 5


class ResolvedTarget:
    __slots__ = ("tickers", "mode", "benchmarks", "invert", "label")

    def __init__(self, tickers: list[str], mode: str, benchmarks: list[str] | None = None,
                 invert: set[str] | None = None, label: str | None = None):
        self.tickers = tickers
        self.mode = mode  # "single" | "list"
        self.benchmarks = benchmarks or []
        self.invert = invert or set()
        self.label = label


def resolve_target(route, user_ctx: dict) -> ResolvedTarget | None:
    """route: thay/chat/router's RouteDecision (duck-typed here, not
    imported — router lives in its own directory since it's the front
    door for SERVICE/CARD/AI, not owned by card/). user_ctx: {"watchlist": [...]}.
    Returns None for target types this round doesn't cover (documented
    per-branch below) rather than guessing at a fetch shape."""
    card_type = route.card_type

    if card_type == "pt":
        # card_ticker accepts a comma list ("NVDA,AMD,TSM") — multi-ticker
        # list card: same list layout + SPY/QQQ summary line as WL, capped
        # at PT_COMPARE_MAX_TICKERS (watchlist limit parity). Single ticker
        # keeps the classic single-stock PT card. Label "Stocks"
        # (2026-07-15, was "Compare") — neutral header: the LLM also uses
        # this card for "check these 3" requests, not only explicit
        # comparisons.
        tickers = list(dict.fromkeys(
            t.strip().upper() for t in (route.ticker or "").split(",") if t.strip()
        ))
        if not tickers:
            return None
        if len(tickers) > 1:
            all_tickers = list(dict.fromkeys(["SPY", "QQQ"] + tickers[:PT_COMPARE_MAX_TICKERS]))
            return ResolvedTarget(tickers=all_tickers, mode="list",
                                   benchmarks=["SPY", "QQQ"], label="Stocks")
        return ResolvedTarget(tickers=[tickers[0]], mode="single", label=tickers[0])

    if card_type in ("ns", "bf"):
        # bf/ns cards are single-ticker only. If the LLM misuses the comma
        # list (documented for pt compare only) here, take the first ticker
        # instead of passing "NVDA,AMD" as one symbol to the engine (which
        # silently produced no card).
        first = next((t.strip().upper() for t in (route.ticker or "").split(",") if t.strip()), None)
        if not first:
            return None
        return ResolvedTarget(tickers=[first], mode="single", label=first)

    if card_type == "wl":
        # SPY/QQQ ride along as a summary line (RENDER_WL: "spyPct"/"qqqPct"
        # computed and excluded from `stocks`), not full rows — mark them
        # via `benchmarks` so CardRenderer can tell rows from summary.
        watchlist = user_ctx.get("watchlist") or []
        all_tickers = list(dict.fromkeys(["SPY", "QQQ"] + watchlist))
        return ResolvedTarget(tickers=all_tickers, mode="list", benchmarks=["SPY", "QQQ"], label="Watchlist")

    if card_type == "st":
        # SECTOR_ORDER includes SPY/QQQ (needed for the summary %) but
        # sector_meta in card_metadata.yaml has no SPY/QQQ entries — same
        # summary-line-not-a-row treatment as WL.
        return ResolvedTarget(tickers=list(SECTOR_ORDER), mode="list", benchmarks=["SPY", "QQQ"], label="Sector")

    if card_type == "mc":
        # MACRO_ETFS includes VT (needed for the "World" summary %) but
        # MACRO_ORDER — the actual display row order — excludes it
        # (RENDER_MC: "เรียง fixed order ตาม docs ไม่ sort", VT shown
        # separately as "World:X%"). Fetch the superset, render MACRO_ORDER.
        return ResolvedTarget(tickers=list(MACRO_ETFS), mode="list", benchmarks=["VT"],
                               invert=set(INVERT), label="Macro")

    if card_type == "theme":
        universe = get_universe()
        if not universe:
            return None
        tickers, benchmarks = get_theme_tickers(route.theme, universe)
        all_tickers = list(dict.fromkeys(benchmarks + tickers))
        return ResolvedTarget(tickers=all_tickers, mode="list", benchmarks=benchmarks, label=route.theme)

    if card_type == "mc_ns":
        # Not ticker-based (no ResolvedTarget applies) — handled directly
        # in pipeline.py via fetch_macro_ns(), same pattern as tag_info.
        # Earlier note here ("upstream inactive") was wrong: the n8n
        # workflow is inactive, but a separate Pi cronjob
        # (fip-engine/macro_ns_cron.py, every 4h) writes fresh
        # macro:raw:ns/macro:ctx:ns independently — confirmed live,
        # healthy runs every 4h.
        return None

    if card_type == "tag_info":
        # Static lookup (fip:tags:list), not a PT/NS ticker fetch — no
        # ResolvedTarget applies. Out of this round's CardRenderer scope
        # (PT, NS only per the approved plan); left to a future round.
        return None

    return None


def fetch_pt_batch(tickers: list[str]) -> dict[str, dict]:
    """Always batch. Single ticker is just a 1-element list — no special
    case. Thin pass-through to the existing, already-deployed batch_pt_us()."""
    return batch_pt_us(tickers)


def fetch_ns_batch(tickers: list[str]) -> dict[str, dict]:
    """Thin wrapper for naming symmetry with fetch_pt_batch. Real
    implementation lives in fip-client/news_util.py (batch_ns_us) — kept
    there, not here, so a future AI-lane NS tool can reuse it directly
    without routing through card/. Requires ns_engine.py's cache-hit fix
    (applied locally, not yet deployed) so structured `news` items are
    present on cache hits, not just fresh fetches."""
    return batch_ns_us(tickers)


def fetch_bf_batch(tickers: list[str]) -> dict[str, dict]:
    """Thin wrapper for naming symmetry with fetch_pt_batch/fetch_ns_batch.
    Real implementation is fip-client/bf_util.batch_bf_us -> bf-service
    :8010/bf/batch. Single-ticker BF card is just a 1-element batch."""
    return batch_bf_us(tickers)


def get_tags() -> dict:
    """Thin re-export of get_tag_data() so CardRenderer only imports from
    data_fetcher, not reaching into market_util directly."""
    return get_tag_data()


def fetch_macro_ns() -> dict | None:
    """Read macro:raw:ns (written by fip-engine/macro_ns_cron.py every 4h,
    TTL 60h) — {"driver": str, "sentiment": str, "news": [...]}. Matches
    n8n's Directory_MC_NS, minus the ai_context field (LLM-facing, not a
    render concern — lives in macro:ctx:ns instead, untouched here).
    Returns None if the key is missing/expired (cron down, or between the
    first deploy and its first successful run) — caller must handle it,
    same contract as every other None-returning branch in this module."""
    import json
    raw = redis_get("macro:raw:ns")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None
