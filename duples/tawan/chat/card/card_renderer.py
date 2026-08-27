# card/card_renderer.py — stub.
#
# Implement render_pt_card first — it handles single-ticker and compare cards.
# Each function receives data from data_fetcher + user_ctx and returns a
# LINE Flex Message dict {"contents": {...}, "altText": "..."} or None.
# Use card_primitives.py for reusable Flex building blocks.
#
# pipeline.py imports these by name — keep function signatures stable.
# See duples/thay/chat/card/card_renderer.py for a full reference implementation.
#
# Do NOT load card_metadata.yaml at module level unless you need it —
# an import-time crash breaks the entire webhook service.


def render_pt_card(items: dict, mode: str = "single", tag_data: dict = None,
                   watchlist: list = None, label: str = None,
                   card_type: str = "pt", lang: str = "TH",
                   benchmarks: list = None) -> dict | None:
    raise NotImplementedError("render_pt_card not implemented yet")


def render_ns_card(items: dict, mode: str = "single",
                   label: str = None, watchlist: list = None) -> dict | None:
    raise NotImplementedError("render_ns_card not implemented yet")


def render_bf_card(ticker: str, data: dict, tag_data: dict,
                   in_watchlist: bool = False, lang: str = "TH") -> dict | None:
    raise NotImplementedError("render_bf_card not implemented yet")


def render_macro_ns_card(data: dict) -> dict | None:
    raise NotImplementedError("render_macro_ns_card not implemented yet")


def render_tag_info_card(tag_id: str, tag_info: dict, lang: str = "TH") -> dict | None:
    raise NotImplementedError("render_tag_info_card not implemented yet")
