"""
tests/test_router.py — Fallthrough-contract checklist from the migration
audit (§1, §2), run as unit tests. Router has zero I/O so no mocks needed.

Fixtures/assertions here are tied to Thay's real router_config.yaml content
(this directory), even though router.py itself moved to platform/chat_core/
(2026-07-16, design session part 4) — kept colocated with the config it's
validating rather than following the mechanism to platform/.
"""

import os
import sys

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.normpath(os.path.join(_DIR, "..", "..", "..", ".."))
_CHAT_CORE_DIR = os.path.join(_ROOT, "platform", "chat_core")
if _CHAT_CORE_DIR not in sys.path:
    sys.path.insert(0, _CHAT_CORE_DIR)

from router import classify, RouteDecision, SERVICE, CARD, AI  # noqa: E402


def test_bare_ticker_defaults_to_pt():
    r = classify("AAPL")
    assert r.lane == CARD and r.card_type == "pt" and r.ticker == "AAPL"


def test_ticker_with_recognized_modifier():
    assert classify("AAPL bf").card_type == "bf"
    assert classify("AAPL พื้นฐาน").card_type == "bf"
    assert classify("AAPL pt").card_type == "pt"
    assert classify("AAPL price").card_type == "pt"
    assert classify("AAPL ns").card_type == "ns"
    assert classify("AAPL ข่าว").card_type == "ns"


def test_ticker_with_unrecognized_modifier_falls_through_to_AI():
    """The one rule most likely to get silently inverted during a port:
    unrecognized 2nd word -> AI, NOT a default to pt."""
    r = classify("AAPL xyz")
    assert r.lane == AI, "unrecognized modifier must fall through to AI, not default to pt"


def test_denylist_beats_ticker_shape():
    for word in ("HI", "OK", "TEST", "THAY"):
        r = classify(word)
        assert r.lane == AI, f"{word} is denylisted, must not route to CARD"


def test_alias_resolves_before_ticker_check():
    r = classify("APPLE")
    assert r.lane == CARD and r.card_type == "pt" and r.ticker == "AAPL"


def test_alias_scoped_to_ticker_path_only():
    """Alias must not leak into keyword_route_map matching (audit §2)."""
    r = classify("TESLA bf")
    assert r.card_type == "bf" and r.ticker == "TSLA"


def test_single_word_keyword_map():
    assert classify("WL").card_type == "wl"
    assert classify("พอร์ต").card_type == "wl"
    # Pre-2026-07-16 stale values (sector/macro/macro_ns) — router_config.yaml
    # already uses the unified short codes from the 2026-07-13 card-type
    # migration (chat-orchestration-findings.md §4); this test just wasn't
    # updated then. Unrelated to today's file reorg — fixed in passing.
    assert classify("SECTOR").card_type == "st"
    assert classify("MACRO").card_type == "mc"
    assert classify("NS").card_type == "mc_ns"


def test_two_word_keyword_exact_match():
    r = classify("AI POWER")
    assert r.lane == CARD and r.card_type == "theme" and r.theme == "AIPOWER"


def test_two_word_keyword_requires_exactly_two_words():
    """Deliberate tightening vs n8n — see router.py module docstring."""
    r = classify("AI POWER คืออะไร")
    assert r.lane != CARD or r.card_type != "theme" or r.theme != "AIPOWER", (
        "3+ word messages must not loosely match a 2-word keyword"
    )


def test_service_add_del():
    r = classify("ADD AAPL")
    assert r.lane == SERVICE and r.type == "WATCHLIST_ADD" and r.ticker == "AAPL"
    r = classify("DEL AAPL")
    assert r.lane == SERVICE and r.type == "WATCHLIST_DEL" and r.ticker == "AAPL"


def test_service_lang_variants():
    for variant, expected in (("TH", "TH"), ("EN", "EN"), ("TH LANG", "TH"), ("EN LANG", "EN")):
        r = classify(variant)
        assert r.lane == SERVICE and r.type == "LANG_UPDATE" and r.value == expected


def test_tag_postback():
    r = classify("TAG|abc123")
    assert r.lane == CARD and r.card_type == "tag_info" and r.tag_id == "abc123"


def test_tag_postback_checked_before_ticker_regex():
    """TAG| would not match TICKER_REGEX anyway (pipe char), but confirming
    precedence explicitly per the audit's documented order."""
    r = classify("TAG|SOME-LONG-TAG-ID")
    assert r.lane == CARD and r.card_type == "tag_info"


def test_free_text_goes_to_AI():
    assert classify("what do you think about the market today").lane == AI
    assert classify("ช่วยดูพอร์ตหน่อย").lane == AI


def test_empty_input():
    assert classify("").lane == AI
    assert classify("   ").lane == AI


def test_route_decision_equality():
    assert classify("WL") == RouteDecision(lane=CARD, card_type="wl")
