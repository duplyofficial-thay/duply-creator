"""
tests/test_golden_replay.py — replay real production turns from
thay_ai.interact_log through router.classify(), offline. No shadow-calls
to n8n or any live service; fixtures are a one-time pull (see
tests/fixtures/*.json) of the exact CARD-lane and AI-lane user turns that
already happened in production, per the migration audit's golden-set
recommendation.

SERVICE lane is NOT covered here — interact_log's own logging code
excludes it by design (confirmed in the earlier audit), so there is
nothing to replay it against from this source. That gap is tracked
separately (audit §7 — pull from n8n execution history before it prunes).
"""

import json
import os
import sys

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.normpath(os.path.join(_DIR, "..", "..", "..", ".."))
_CHAT_CORE_DIR = os.path.join(_ROOT, "platform", "chat_core")
if _CHAT_CORE_DIR not in sys.path:
    sys.path.insert(0, _CHAT_CORE_DIR)

from router import classify, CARD, AI  # noqa: E402

_FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load(name):
    with open(os.path.join(_FIXTURES, name), encoding="utf-8") as f:
        return json.load(f)


def test_card_lane_golden_set_all_route_to_card():
    """940 real production messages that n8n routed to FAST_A/FAST_B
    (type=card in interact_log). Every one must classify as CARD lane."""
    rows = _load("golden_card_rows.json")
    mismatches = []
    for row in rows:
        content = row.get("content") or ""
        r = classify(content)
        if r.lane != CARD:
            mismatches.append((content, r.lane, r.card_type))

    total = len(rows)
    mismatch_rate = len(mismatches) / total if total else 0
    # Report, don't silently pass/fail on an arbitrary threshold — a golden
    # set replay is diagnostic. Print mismatches so real divergences are
    # visible in test output, not just a pass/fail count.
    if mismatches:
        print(f"\n{len(mismatches)}/{total} card-lane messages did NOT classify as CARD:")
        for content, lane, card_type in mismatches[:30]:
            print(f"  {content!r} -> lane={lane} card_type={card_type}")

    # Allow a small tolerance: TAG| ids referencing tags that have since
    # been renamed/retired, and pre-alias-map company names typed in ways
    # the current alias map doesn't cover, are expected sources of noise
    # in a 5.5-week-old log, not necessarily router bugs. Anything above a
    # few percent is a real signal to investigate before cutover.
    assert mismatch_rate < 0.05, f"{mismatch_rate:.1%} mismatch rate — see printed diffs above"


def test_chat_lane_golden_set_mostly_routes_to_AI():
    """440 real production messages that went to the AI lane (type=chat).
    These are natural-language messages — should overwhelmingly classify
    as AI, though a few may legitimately be CARD (e.g. a user typed 'WL'
    mid-conversation and the LLM handled it anyway under the old n8n
    routing quirks) — same tolerance reasoning as above."""
    rows = _load("golden_chat_rows.json")
    mismatches = []
    for row in rows:
        content = row.get("content") or ""
        r = classify(content)
        if r.lane != AI:
            mismatches.append((content, r.lane, r.card_type))

    total = len(rows)
    mismatch_rate = len(mismatches) / total if total else 0
    if mismatches:
        print(f"\n{len(mismatches)}/{total} chat-lane messages classified as non-AI:")
        for content, lane, card_type in mismatches[:30]:
            print(f"  {content!r} -> lane={lane} card_type={card_type}")

    assert mismatch_rate < 0.05, f"{mismatch_rate:.1%} mismatch rate — see printed diffs above"
