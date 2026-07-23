# Stub — no card dedup needed when cards are disabled.
# When you add cards: implement suppression logic here.


def suppress_if_recently_shown(history, card_type, card_subject, window=6):
    return card_type, card_subject
