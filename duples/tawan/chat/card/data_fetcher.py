# card/data_fetcher.py — stub.
#
# Implement these when cards_enabled is set to True in duple_settings.py.
#
# resolve_target(route) -> target
#   Maps a RouteDecision to a fetch target (ticker, list of tickers, keyword…).
#   Called by pipeline.py before any fetch. See duples/thay/chat/card/data_fetcher.py.
#
# fetch_*_batch(target, user_ctx) -> data | None
#   One function per card family (pt, ns, bf…). Returns raw data dict or None on failure.
#   pipeline.py calls the right fetch function based on route.card_type.


def resolve_target(route):
    raise NotImplementedError("data_fetcher.resolve_target not implemented yet")
