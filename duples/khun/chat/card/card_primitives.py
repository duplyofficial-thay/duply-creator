"""
card/card_primitives.py — Shared flex-card building blocks, reused across
PT/NS (and future engines) CardRenderers. Ported near-verbatim from the
audited Subflow A/B flex JSON (workflow Thay.fip, mFO5AuDuC9BAPPIV /
q9llBApw4G2mMOl5) — re-verified 2026-07-13 against the live n8n node code
pulled via REST API (RENDER_PT, RENDER_NS, RENDER_WL, RENDER_ST, RENDER_MC,
RENDER_THEME), not re-derived from memory.

Each primitive is a pure function: data in, flex-JSON fragment out. No
engine-specific branching lives here — a caller supplies whatever the
engine-specific choice is (e.g. footer_row's next_action/icon).

Naming correction vs the original plan: what the plan called `logo_header`
turned out, on inspecting the actual n8n flex JSON, to be a *per-ticker
company logo* (img.logo.dev, keyed by ticker) — not a fixed Thay/Duple
brand header. Renamed to `ticker_logo` to match what it actually is.
Further correction (2026-07-13): `ticker_logo` is never used as a bubble
`hero` slot in any real n8n card — RENDER_PT/RENDER_NS both embed it as a
small inline rounded box (18px/42px) next to the ticker text, not a
full-width hero banner. See card_renderer.py's single-ticker shells.
"""

ASSET_BASE = "https://raw.githubusercontent.com/duplyofficial-thay/duply.asset/main"
LOGO_DEV_TOKEN = "pk_BFk0A2nVTEGE5xbSi-vtUA"  # already public — embedded in every delivered flex card today

# next_action/icon per engine's footer nav button (tap -> jump to another
# card type for the same ticker). icon filenames copied byte-for-byte from
# the live n8n code, including NS's pre-encoded "%20(1)" — that is the
# actual raw.githubusercontent filename in production, not a typo to "fix".
FOOTER_TARGETS = {
    "pt": {"next_action": "bf", "icon": "bank-fill.png"},
    "ns": {"next_action": "bf", "icon": "chart-bar-fill%20(1).png"},
    "bf": {"next_action": None, "icon": "chart-bar-fill%20(1).png"},
}


def watchlist_star(ticker: str, in_watchlist: bool, **padding: str) -> dict:
    """Star icon box + ADD/DEL postback, for a single-ticker card's header
    row. Postback text is fed straight back through router.classify() —
    same SERVICE-lane contract as free-typed 'ADD AAPL' / 'DEL AAPL'.

    `padding` is the one placement difference between engines: RENDER_PT's
    header wraps this with paddingStart:5px, RENDER_NS's with
    paddingTop:6px (different header layouts) — pass e.g.
    watchlist_star(t, flag, paddingStart="5px")."""
    icon = "star-fill.png" if in_watchlist else "star.png"
    postback_data = f"DEL {ticker}" if in_watchlist else f"ADD {ticker}"
    box = {
        "type": "box", "layout": "vertical", "flex": 0,
        "alignItems": "center", "justifyContent": "center",
        "action": {"type": "postback", "data": postback_data},
        "contents": [{"type": "image", "url": f"{ASSET_BASE}/{icon}", "size": "13px", "aspectMode": "fit"}],
    }
    box.update(padding)
    return box


def footer_row(ticker: str, footer_text: str, next_action: str | None, icon: str) -> dict:
    """Single-ticker card's bottom row: centered timestamp text + an
    absolute-positioned nav-icon button. This is the LAST item of
    `body.contents` in the real n8n cards (RENDER_PT/RENDER_NS) — there is
    no separate bubble-level "footer" slot for single-ticker cards, unlike
    the list cards (WL/ST/MC/THEME), which do use bubble.footer for a
    plain centered text-only line (see card_renderer's list shells).

    postback.data is f'{ticker} {next_action}' or bare `ticker` — fed
    straight back through router.classify(), same contract as free-typed
    'AAPL bf'. next_action/icon are supplied by the calling engine's
    renderer via FOOTER_TARGETS, not inferred here (icon isn't a pure
    function of next_action — PT->bf and NS->bf use different icons)."""
    postback_data = f"{ticker} {next_action}" if next_action else str(ticker)
    return {
        "type": "box", "layout": "horizontal", "margin": "lg", "alignItems": "center",
        "contents": [
            {"type": "text", "text": footer_text, "size": "xxs", "color": "#CBD5E1", "align": "center", "flex": 1},
            {
                "type": "box", "layout": "vertical",
                "position": "absolute", "offsetEnd": "-6px",
                "width": "24px", "height": "24px",
                "justifyContent": "center", "alignItems": "center",
                "action": {"type": "postback", "data": postback_data},
                "contents": [{"type": "image", "url": f"{ASSET_BASE}/{icon}", "size": "14px", "aspectMode": "fit"}],
            },
        ],
    }


def list_footer_box(text: str, padding_bottom: str = "12px") -> dict:
    """Bubble-level footer for list cards (WL/ST/MC/THEME) — a plain
    centered 'date | market_state' line, no icon button. padding_bottom
    differs slightly per card in the real n8n code (WL/THEME: 15px, ST/MC:
    12px) — pass it through rather than normalizing away a real, if minor,
    difference."""
    return {
        "type": "box", "layout": "vertical", "paddingBottom": padding_bottom,
        "contents": [{"type": "text", "text": text, "size": "xxs", "color": "#CBD5E1", "align": "center"}],
    }


def tag_chip(tag_id: str, tag_info: dict, variant: str = "list", lang: str = "EN",
             action: bool = True) -> dict:
    """Gradient tag chip. tag_info is one value from fip:tags:list
    (Redis), shape: {th, c1, c2, tx, lv, sem, ...} — confirmed live against
    Redis, these are the real field names (n8n's `tag.label`/`tag.textColor`
    were names given by an n8n-only enrichment step that doesn't exist in
    the Python port; `th`/`tx` here are the direct, correct equivalents).

    Two real visual variants, confirmed structurally different in the live
    n8n code — not a single shared style:
    - "single" (RENDER_PT's per-ticker detail card, and RENDER_TAG_INFO's
      own tag pill — same box, see below): cornerRadius 20px, paddingAll
      4px + paddingStart/paddingEnd 8px, explicit height 20px, text size
      10px (TH) / 9px (EN).
    - "list" (RENDER_WL/RENDER_ST/RENDER_MC/RENDER_THEME's list rows):
      cornerRadius 100px, height 14px, paddingStart/paddingEnd 5px only
      (no paddingAll), fixed text size 7px.
    Both offset the label text -1px on TH (baseline correction for Thai
    script), 0px on EN.

    `action=False` drops the postback (RENDER_TAG_INFO's own pill has
    none — you're already viewing that tag's info, tapping it again to
    navigate to itself is pointless; every other usage taps through to
    the tag-info card, so defaults to True).

    EN label formatting: deliberately unified on dash->space
    ("STAR-STACKED" -> "STAR STACKED") everywhere, by explicit product
    call — the real n8n source is NOT consistent here (Directory_PT/WL/
    ST/MC/THEME show the raw id with dashes; Directory_TI, the tag-info
    card's own enrichment, converts dashes to spaces) and asking "does it
    match n8n" doesn't resolve which of the two real behaviors to copy.
    Chosen: space, since a chip is user-facing label text, not a raw
    identifier, and reads better as an English phrase.
    """
    is_thai = lang == "TH"
    offset_top = "-1px" if is_thai else "0px"
    # Every Directory_* node (PT/WL/ST/MC/THEME/TI) does
    # `label: system_lang === "TH" ? th_name : id` — EN mode shows the raw
    # tag id (not the Thai text) — see docstring above for the
    # dash-vs-space unification on top of that shared rule.
    label_text = tag_info.get("th", tag_id) if is_thai else tag_id.replace("-", " ")
    background = {
        "type": "linearGradient", "angle": "270deg",
        "startColor": tag_info.get("c1", "#64748B"),
        "endColor": tag_info.get("c2", "#94A3B8"),
    }
    text_content = {
        "type": "text", "text": label_text,
        "color": tag_info.get("tx", "#FFFFFF"), "weight": "bold",
        "align": "center", "offsetTop": offset_top,
    }
    postback = {"action": {"type": "postback", "data": f"TAG|{tag_id}"}} if action else {}

    if variant == "single":
        text_content["size"] = "10px" if is_thai else "9px"
        text_content["gravity"] = "center"  # RENDER_PT/RENDER_TAG_INFO have this; RENDER_WL's list variant doesn't
        return {
            "type": "box", "layout": "vertical", "cornerRadius": "20px",
            "paddingAll": "4px", "paddingStart": "8px", "paddingEnd": "8px",
            "flex": 0, "justifyContent": "center", "height": "20px",
            "background": background,
            **postback,
            "contents": [text_content],
        }

    # "list" variant (default)
    text_content["size"] = "7px"
    return {
        "type": "box", "layout": "vertical", "cornerRadius": "100px",
        "height": "14px", "justifyContent": "center",
        "paddingStart": "5px", "paddingEnd": "5px", "flex": 0,
        "background": background,
        **postback,
        "contents": [text_content],
    }


def ticker_logo(ticker: str) -> dict:
    """Per-ticker company logo (img.logo.dev). NOT a fixed app/brand
    header, and NOT a bubble.hero image — every real card embeds this as a
    small inline rounded box next to the ticker text. Caller supplies the
    box (width/height/cornerRadius), since PT uses 18px and NS uses 42px."""
    return {
        "type": "image",
        "url": f"https://img.logo.dev/ticker/{ticker}?token={LOGO_DEV_TOKEN}",
        "size": "full",
        "aspectMode": "cover",
    }
