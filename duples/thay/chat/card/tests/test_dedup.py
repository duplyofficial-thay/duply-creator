"""
tests/test_dedup.py — card/dedup.py correctness.

Two things must both hold, or dedup silently does nothing (no exception —
just never suppresses):
  1. parse_history_card() must correctly read every real n8n wording still
     alive in production history (pulled from live Supabase interact_log,
     2026-07-14 — not invented).
  2. It must also correctly read whatever end_of_turn.py writes going
     forward, for every one of the 8 card types agent_loop.VALID_CARD_TYPES
     allows — this is the roundtrip table.
"""

import os
import sys
from unittest.mock import patch

_CARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _CARD_DIR not in sys.path:
    sys.path.insert(0, _CARD_DIR)
# 2026-07-16 reorg: end_of_turn.py moved thay/chat/ -> platform/chat_core/
# (Duple-agnostic — see docs/platform-vs-tenant-taxonomy.md); card/ moved
# thay/chat/card/ -> duples/thay/chat/card/ (design session part 4, same
# day). No longer parent/child, so this is a cross-tree lookup instead of
# dirname(_CARD_DIR).
_CHAT_CORE_DIR = os.path.normpath(os.path.join(_CARD_DIR, "..", "..", "..", "..", "platform", "chat_core"))
if _CHAT_CORE_DIR not in sys.path:
    sys.path.insert(0, _CHAT_CORE_DIR)

import dedup as dd  # noqa: E402

# end_of_turn.py sets up its own sys.path (shared/, noter/) at import time —
# don't duplicate that here. Doing so previously put noter/'s prompt_builder.py
# ahead of reply/'s same-named-but-different module in global sys.path,
# breaking reply_flow.py's import in any test collected afterward — sys.path
# is process-global across the whole pytest run, not scoped per test file.
import end_of_turn as eot  # noqa: E402


# ── 1. Real n8n wording, pulled from live thay_ai.interact_log 2026-07-14 ──

def test_parses_real_n8n_lane_a_format():
    assert dd.parse_history_card("[Card:ARM pt]") == {"ticker": "ARM", "type": "pt"}


def test_parses_real_n8n_watchlist_format():
    assert dd.parse_history_card("[Card: Watchlist]") == {"ticker": None, "type": "wl"}


def test_parses_n8n_technicals_format():
    assert dd.parse_history_card("[Card: AAPL Technicals]") == {"ticker": "AAPL", "type": "pt"}


def test_parses_n8n_overview_formats():
    assert dd.parse_history_card("[Card: Sector Overview]") == {"ticker": None, "type": "st"}
    assert dd.parse_history_card("[Card: Macro Overview]") == {"ticker": None, "type": "mc"}


def test_parses_n8n_theme_format():
    assert dd.parse_history_card("[Card: Theme_ROBOTIC]") == {"ticker": "ROBOTIC", "type": "theme"}


def test_non_card_content_returns_empty_type():
    assert dd.parse_history_card("just chatting, no card here") == {"ticker": None, "type": ""}


# ── 2. Roundtrip: every type end_of_turn.py can write, dedup must read back ─

ROUNDTRIP_CASES = [
    # (card_type, card_ticker) -> expected {ticker, type} after roundtrip
    ("pt", "AAPL", {"ticker": "AAPL", "type": "pt"}),
    ("bf", "AAPL", {"ticker": "AAPL", "type": "bf"}),
    ("ns", "AAPL", {"ticker": "AAPL", "type": "ns"}),
    ("mc", None, {"ticker": None, "type": "mc"}),
    ("mc_ns", None, {"ticker": None, "type": "mc_ns"}),
    ("st", None, {"ticker": None, "type": "st"}),
    ("wl", None, {"ticker": None, "type": "wl"}),
    ("theme", "ROBOTIC", {"ticker": "ROBOTIC", "type": "theme"}),
    # multi-ticker PT (2026-07-15): parses back normalized (sorted set)
    ("pt", "NVDA,AMD", {"ticker": "AMD,NVDA", "type": "pt"}),
    ("pt", "nvda, AMD,TSM,NVDA", {"ticker": "AMD,NVDA,TSM", "type": "pt"}),
]


def test_multi_ticker_dedup_is_order_insensitive():
    # "AMD,NVDA" shown earlier must suppress a new "NVDA, amd" card
    history = [{"role": "assistant", "content": "[Card:AMD,NVDA pt]"}]
    assert dd.suppress_if_recently_shown(history, "pt", "NVDA, amd") == (None, None)
    # different ticker set must NOT be suppressed
    assert dd.suppress_if_recently_shown(history, "pt", "NVDA,TSM") == ("pt", "NVDA,TSM")


def test_multi_ticker_dedup_does_not_block_solo_and_vice_versa():
    # exact-set match only — never subset matching:
    # multi shown → solo of a member ticker must still show
    hist = [{"role": "assistant", "content": "[Card:NVDA,TSLA pt]"}]
    assert dd.suppress_if_recently_shown(hist, "pt", "NVDA") == ("pt", "NVDA")
    assert dd.suppress_if_recently_shown(hist, "pt", "TSLA") == ("pt", "TSLA")
    # solo shown → multi containing it must still show
    hist2 = [{"role": "assistant", "content": "[Card:NVDA pt]"}]
    assert dd.suppress_if_recently_shown(hist2, "pt", "NVDA,TSLA") == ("pt", "NVDA,TSLA")
    # same ticker, different card type — not affected
    assert dd.suppress_if_recently_shown(hist2, "bf", "NVDA") == ("bf", "NVDA")


def test_every_card_type_roundtrips_through_end_of_turn_and_dedup():
    for card_type, card_ticker, expected in ROUNDTRIP_CASES:
        written = eot._card_placeholder(card_type, card_ticker)
        parsed = dd.parse_history_card(written)
        assert parsed == expected, f"{card_type}/{card_ticker} wrote {written!r}, parsed back as {parsed}, expected {expected}"


# ── 3. suppress_if_recently_shown: session boundary + window + suppression ──

def _assistant_card(content):
    return {"role": "assistant", "content": content}


def _user(content):
    return {"role": "user", "content": content}


def test_suppresses_exact_repeat_within_session():
    history = [_user("AAPL"), _assistant_card("[Card:AAPL pt]")]
    result = dd.suppress_if_recently_shown(history, "pt", "AAPL")
    assert result == (None, None)


def test_does_not_suppress_different_ticker():
    history = [_user("AAPL"), _assistant_card("[Card:AAPL pt]")]
    result = dd.suppress_if_recently_shown(history, "pt", "NVDA")
    assert result == ("pt", "NVDA")


def test_does_not_suppress_different_type_same_ticker():
    history = [_user("AAPL"), _assistant_card("[Card:AAPL pt]")]
    result = dd.suppress_if_recently_shown(history, "ns", "AAPL")
    assert result == ("ns", "AAPL")


def test_resume_marker_resets_the_window():
    history = [
        _user("AAPL"), _assistant_card("[Card:AAPL pt]"),
        {"role": "system", "content": "[resumed after 3h]"},
    ]
    result = dd.suppress_if_recently_shown(history, "pt", "AAPL")
    assert result == ("pt", "AAPL"), "a new session must not carry the old card forward"


def test_window_only_looks_at_last_6_messages_of_session():
    old_card = [_assistant_card("[Card:AAPL pt]")]
    filler = [_user("x"), _assistant_card("ok")] * 3  # 6 filler messages
    history = old_card + filler
    result = dd.suppress_if_recently_shown(history, "pt", "AAPL")
    assert result == ("pt", "AAPL"), "card outside the 6-message window must not suppress"


def test_theme_dedup_uses_the_real_theme_keyword_not_the_ticker_field():
    history = [_user("ROBOTIC"), _assistant_card("[Card: Theme_ROBOTIC]")]
    assert dd.suppress_if_recently_shown(history, "theme", "ROBOTIC") == (None, None)
    assert dd.suppress_if_recently_shown(history, "theme", "PHOTONICS") == ("theme", "PHOTONICS")


def test_no_card_type_passes_through_untouched():
    assert dd.suppress_if_recently_shown([], None, None) == (None, None)
