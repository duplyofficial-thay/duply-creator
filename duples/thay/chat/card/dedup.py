"""
card/dedup.py — AI-lane card dedup, ported from n8n's `AI_Output` node
(workflow `Thay.ai (subflow D)`, id vaznMbxHBIjuBba8, "CARD DEDUP" block).
Not previously ported to Python — confirmed missing by reading the live
n8n workflow directly (2026-07-14) and grepping the whole Python port for
any equivalent, found none.

What it does: if the LLM is about to show the same card (type + ticker)
that was already shown earlier in the current session (since the last
"[resumed after Xh]" marker — see reply/context_builder.py's
_apply_resume_gaps), suppress it. The user gets text only, not a
redundant repeat of a card they already saw. CARD lane never calls this —
it's an AI-lane-only guard against the LLM re-emitting a card it doesn't
know it already showed.

Format compatibility, load-bearing: parse_history_card() must read BOTH
n8n's historical "[Card:...]" wording (multiple eras exist in real
history — confirmed against live Supabase interact_log rows) and
end_of_turn.py's Python-written rows, since during parallel-run both are
mixed in the same history. end_of_turn.py's docstring explains the one
place (theme) where the writer had to match n8n's literal wording rather
than its own generic one, specifically so this parser doesn't need two
code paths.
"""

import re

CARD_NAME_MAP = {
    "macro news": "mc_ns",
    "macro": "mc",
    "sectors": "st",
    "watchlist": "wl",
}

_OVERVIEW_MAP = {
    "watchlist": "wl",
    "sector": "st",
    "sectors": "st",
    "macro": "mc",
}

_CARD_BRACKET_RE = re.compile(r"\[Card:?\s*([^\]]+)\]", re.IGNORECASE)
_LANE_A_RE = re.compile(r"^([A-Z0-9]+(?:\s*,\s*[A-Z0-9]+)*)\s+(pt|bf|ns)$", re.IGNORECASE)
_TECHNICALS_RE = re.compile(r"^([A-Z0-9]+)\s+Technicals$", re.IGNORECASE)
_OVERVIEW_RE = re.compile(r"^(\w+)\s+Overview$", re.IGNORECASE)


def _norm_ticker(ticker: str | None) -> str:
    """Normalize a card_ticker for dedup keys. Multi-ticker PT compare
    (2026-07-15) writes comma lists ("NVDA,AMD") into the placeholder;
    normalize to a sorted, deduped, upper set so "AMD, nvda" and
    "NVDA,AMD" produce the same key. Single tickers pass through unchanged
    (sorted set of one)."""
    if not ticker:
        return ""
    parts = sorted({t.strip().upper() for t in str(ticker).split(",") if t.strip()})
    return ",".join(parts)


def parse_history_card(content: str) -> dict:
    """content -> {"ticker": str|None, "type": str}. Faithful port of
    n8n's parseHistoryCard — same branch order, same fallback. Extended
    2026-07-15: lane-A tickers may be a comma list (multi-ticker PT
    compare) — normalized via _norm_ticker for order-insensitive dedup."""
    m = _CARD_BRACKET_RE.search(content or "")
    raw = m.group(1).strip() if m else ""

    lane_a = _LANE_A_RE.match(raw)
    if lane_a:
        return {"ticker": _norm_ticker(lane_a.group(1)), "type": lane_a.group(2).lower()}

    technicals = _TECHNICALS_RE.match(raw)
    if technicals:
        return {"ticker": technicals.group(1).upper(), "type": "pt"}

    overview = _OVERVIEW_RE.match(raw)
    if overview:
        key = overview.group(1).lower()
        return {"ticker": None, "type": _OVERVIEW_MAP.get(key, key)}

    card_type = CARD_NAME_MAP.get(raw.lower()) or ("theme" if raw.startswith("Theme_") else raw.lower())
    ticker = raw[len("Theme_"):].upper() if raw.startswith("Theme_") else None
    return {"ticker": ticker, "type": card_type}


def suppress_if_recently_shown(
    history: list[dict],
    card_type: str | None,
    card_ticker: str | None,
    window: int = 6,
) -> tuple[str | None, str | None]:
    """(card_type, card_ticker) -> (card_type, card_ticker) or (None, None)
    if that exact card was already shown in the last `window` messages of
    the current session. `history` must be the structured list
    (context_builder.build_context()["history"]), not the flattened
    context_history string — the session boundary and per-message role
    can't be recovered from that string.
    """
    if not card_type:
        return card_type, card_ticker

    last_resume_idx = -1
    for i, h in enumerate(history):
        if h.get("role") == "system" and str(h.get("content") or "").startswith("[resumed"):
            last_resume_idx = i

    session_history = history[last_resume_idx + 1:]
    recent_history = session_history[-window:] if window else session_history

    shown_keys = set()
    for h in recent_history:
        content = h.get("content")
        if h.get("role") == "assistant" and isinstance(content, str) and content.startswith("[Card"):
            parsed = parse_history_card(content)
            shown_keys.add(f"{parsed['type']}:{parsed['ticker'] or ''}")

    current_key = f"{card_type}:{_norm_ticker(card_ticker)}"
    if current_key in shown_keys:
        return None, None
    return card_type, card_ticker
