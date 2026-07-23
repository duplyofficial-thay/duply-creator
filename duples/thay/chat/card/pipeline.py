"""
card/pipeline.py — wires data_fetcher -> card_renderer into one callable
for the CARD lane. Does NOT import or call router.classify() itself —
router lives in thay/chat/router/, a sibling to card/reply/service/, since
it's the front door for all three lanes (SERVICE/CARD/AI), not owned by
card/ specifically. The caller (eventually the unified /chat endpoint —
not built yet) runs router.classify() first, then passes the resulting
RouteDecision in here once it already knows lane=CARD. render_card()
duck-types `route` (reads .card_type/.ticker/.theme/etc.) rather than
importing the RouteDecision class, so card/ has zero import-time
dependency on router/ at all — confirmed by grep before this file existed
in its current form: nothing in card/ ever imported router.py in
production code, only test fixtures did.

Everything this calls already exists and is independently tested
(DataFetcher, CardRenderer) — this file is pure dispatch/glue, no new
fetch or render logic.

This is also where the 3-layer architecture pays off concretely: wl,
st, mc, theme, and single-ticker pt ALL go through the exact same
fetch_pt_batch() + render_pt_card() call — render_pt_card already branches
on mode ("single" vs "list") and card_type (generic/st/mc row
style) internally, so there's nothing card-type-specific to add here
beyond picking PT-family vs NS-family and passing target.benchmarks through.
"""

from card_renderer import render_pt_card, render_ns_card, render_tag_info_card, render_macro_ns_card, render_bf_card
from data_fetcher import resolve_target, fetch_pt_batch, fetch_ns_batch, fetch_bf_batch, fetch_macro_ns, get_tags


def render_card(route, user_ctx: dict) -> dict | None:
    """route: router.RouteDecision (lane must be CARD). user_ctx:
    {"watchlist": [...], "system_lang": "TH"|"EN"}.

    Returns {"contents": flex_json, "altText": per_card_label} or None.
    Callers must handle None explicitly rather than assume every CARD-lane
    RouteDecision produces a card. Callers that need to phrase the failure
    (reply_flow CARD lane) use render_card_with_status()."""
    return render_card_with_status(route, user_ctx)[0]


def _card_alt_text(route, target=None, tag_id=None) -> str:
    """Per-card-type altText for LINE notification preview. Single-ticker
    format matches n8n RETURN-TO-MAIN_A replyMap; list-card wording follows
    the same pattern."""
    ct = route.card_type
    if ct == "pt":
        if target and getattr(target, "mode", None) != "single":
            bench_n = len(target.benchmarks) if target.benchmarks else 0
            user_tickers = target.tickers[bench_n:bench_n + 3]
            tickers_str = ", ".join(t.upper() for t in user_tickers)
            return f"Stocks: {tickers_str}"
        ticker = (target.tickers[0] if target and target.tickers else route.ticker or "Stock").upper()
        return f"{ticker} Technicals"
    if ct == "bf":
        ticker = (target.tickers[0] if target and target.tickers else route.ticker or "Stock").upper()
        return f"{ticker} Fundamentals"
    if ct == "ns":
        if target and getattr(target, "mode", None) == "single":
            return f"{target.tickers[0].upper()} News"
        return "News"
    if ct == "tag_info":
        return f"Tag: {tag_id or route.tag_id or 'Unknown'}"
    if ct == "wl":
        return "Watchlist"
    if ct == "theme":
        label = (getattr(target, "label", None) if target else None) or route.theme or "Unknown"
        return f"Theme: {label}"
    if ct == "st":
        return "Sectors"
    if ct == "mc":
        return "Macro"
    if ct == "mc_ns":
        return "Macro News"
    return "\u0e21\u0e32\u0e41\u0e25\u0e49\u0e27\u0e04\u0e23\u0e31\u0e1a"


def render_card_with_status(route, user_ctx: dict) -> tuple[dict | None, str | None]:
    """(card, fail_status). fail_status is the engine's CLEAN OUTPUT status
    (TICKER_NOT_FOUND | NOT_SUPPORTED | FAILED — docs/thay.md → Engine Status
    Contract) when a ticker card dead-ends, or None for generic
    unavailability (mc_ns cache empty, theme universe missing, ...). Lets the
    caller mirror n8n RETURN-TO-MAIN_A's per-status reply wording."""
    lang = (user_ctx.get("system_lang") or "EN").upper()

    # tag_info: static fip:tags:list lookup, not a PT/NS ticker fetch —
    # handled here (like ns) rather than through resolve_target/ResolvedTarget,
    # which only models ticker-batch fetches.
    if route.card_type == "tag_info":
        tag_id = (route.tag_id or "").strip()
        if not tag_id:
            return None, None
        tag_info = get_tags().get(tag_id)
        if not tag_info:
            return None, None
        card = render_tag_info_card(tag_id, tag_info, lang=lang)
        return {"contents": card, "altText": _card_alt_text(route, tag_id=tag_id)}, None

    # mc_ns: same reasoning as tag_info — a single pre-fetched Redis blob
    # (macro:raw:ns, written by fip-engine/macro_ns_cron.py every 4h), not
    # a ticker batch. No ResolvedTarget applies.
    if route.card_type == "mc_ns":
        data = fetch_macro_ns()
        if data is None:
            return None, None
        card = render_macro_ns_card(data)
        return {"contents": card, "altText": _card_alt_text(route)}, None

    target = resolve_target(route, user_ctx)
    if target is None:
        return None, None

    watchlist = user_ctx.get("watchlist") or []

    if route.card_type == "ns":
        items = fetch_ns_batch(target.tickers)
        if target.mode == "single":
            data = items.get(target.tickers[0])
            if not data or data.get("error") or data.get("status") == "FAILED":
                return None, (data or {}).get("status") or "FAILED"
        card = render_ns_card(items, mode=target.mode, label=target.label, watchlist=watchlist)
        return {"contents": card, "altText": _card_alt_text(route, target=target)}, None

    if route.card_type == "bf":
        items = fetch_bf_batch(target.tickers)
        data = items.get(target.tickers[0])
        if not data or data.get("status") != "SUCCESS":
            return None, (data or {}).get("status")
        tag_data = get_tags()
        card = render_bf_card(target.tickers[0], data, tag_data,
                              in_watchlist=target.tickers[0] in watchlist, lang=lang)
        return {"contents": card, "altText": _card_alt_text(route, target=target)}, None

    # pt, wl, st, mc, theme all share one fetch+render path
    items = fetch_pt_batch(target.tickers)

    # Single-ticker card with a non-renderable item (TICKER_NOT_FOUND /
    # FAILED clean shapes from pt-us-service) → None, same contract as the
    # bf branch above — caller renders the "ticker not found" reply. List
    # cards keep going: bad tickers simply drop out of the rows.
    if target.mode == "single":
        data = items.get(target.tickers[0])
        if not data or data.get("status") not in ("SUCCESS", "IPO_LIMITED"):
            return None, (data or {}).get("status")

    tag_data = get_tags()
    card = render_pt_card(
        items,
        mode=target.mode,
        tag_data=tag_data,
        watchlist=watchlist,
        label=target.label,
        card_type=route.card_type,
        lang=lang,
        benchmarks=target.benchmarks,
    )
    return {"contents": card, "altText": _card_alt_text(route, target=target)}, None
