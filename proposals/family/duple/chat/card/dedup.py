"""
DRAFT — duples/{duple_id}/chat/card/dedup.py for the family archetype.

Deliberately closer to khun's simple pass-through than thay's full recency-
suppression port: recency-suppression matters a lot for thay (a stock ticker
card repeated seconds apart is noise) but much less here — a kid asking for
their wallet or quest list twice in a row usually means "show me again",
not "you already told me this." No-op for now; revisit only if real usage
shows a specific card type getting spammy (candidate: leaderboard, if it
gets asked every message during a competitive streak).
"""


def suppress_if_recently_shown(history, card_type, card_subject, window=6):
    return card_type, card_subject
