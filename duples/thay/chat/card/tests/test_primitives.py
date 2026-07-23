import os
import sys

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from card_primitives import watchlist_star, footer_row, list_footer_box, tag_chip, ticker_logo, FOOTER_TARGETS  # noqa: E402


def test_watchlist_star_not_in_wl():
    box = watchlist_star("AAPL", in_watchlist=False, paddingStart="5px")
    img = box["contents"][0]
    assert box["action"]["data"] == "ADD AAPL"
    assert img["url"].endswith("star.png")
    assert box["paddingStart"] == "5px"


def test_watchlist_star_in_wl():
    box = watchlist_star("AAPL", in_watchlist=True, paddingTop="6px")
    img = box["contents"][0]
    assert box["action"]["data"] == "DEL AAPL"
    assert img["url"].endswith("star-fill.png")
    assert box["paddingTop"] == "6px"


def test_footer_row_pt_to_bf():
    c = footer_row("AAPL", footer_text="13/07 18:00", **FOOTER_TARGETS["pt"])
    icon_box = c["contents"][1]
    assert icon_box["action"]["data"] == "AAPL bf"
    assert icon_box["contents"][0]["url"].endswith("bank-fill.png")
    assert c["contents"][0]["text"] == "13/07 18:00"


def test_footer_row_ns_to_bf_different_icon_and_filename():
    c = footer_row("AAPL", footer_text="-", **FOOTER_TARGETS["ns"])
    icon_box = c["contents"][1]
    assert icon_box["action"]["data"] == "AAPL bf"
    # real n8n filename, pre-encoded space — not "chart-bar-fill.png"
    assert icon_box["contents"][0]["url"].endswith("chart-bar-fill%20(1).png")
    pt = footer_row("AAPL", footer_text="-", **FOOTER_TARGETS["pt"])
    assert pt["contents"][1]["contents"][0]["url"] != icon_box["contents"][0]["url"]


def test_footer_row_no_next_action_bare_ticker():
    c = footer_row("AAPL", footer_text="-", next_action=None, icon="chart-bar-fill.png")
    assert c["contents"][1]["action"]["data"] == "AAPL"


def test_list_footer_box():
    b = list_footer_box("13-Jul-26 18:00 | CLOSED", padding_bottom="15px")
    assert b["contents"][0]["text"] == "13-Jul-26 18:00 | CLOSED"
    assert b["paddingBottom"] == "15px"


def test_tag_chip_single_variant_is_bigger_and_two_tag_capable():
    tag_info = {"th": "ดาวเรียงตัว", "c1": "#134e4a", "c2": "#7c3aed", "tx": "#ffffff"}
    c = tag_chip("STAR-STACKED", tag_info, variant="single", lang="TH")
    assert c["action"]["data"] == "TAG|STAR-STACKED"
    assert c["contents"][0]["text"] == "ดาวเรียงตัว"  # TH mode shows the Thai label
    assert c["cornerRadius"] == "20px" and c["height"] == "20px"
    assert c["contents"][0]["size"] == "10px"  # TH


def test_tag_chip_list_variant_is_smaller():
    tag_info = {"th": "ดาวเรียงตัว", "c1": "#134e4a", "c2": "#7c3aed", "tx": "#ffffff"}
    c = tag_chip("STAR-STACKED", tag_info, variant="list", lang="TH")
    assert c["cornerRadius"] == "100px" and c["height"] == "14px"
    assert c["contents"][0]["size"] == "7px"
    assert c["contents"][0]["offsetTop"] == "-1px"  # TH baseline correction


def test_tag_chip_en_shows_spaced_id_not_thai_text():
    """Every Directory_* node: `label: system_lang === "TH" ? th_name : id`
    — EN mode must show the tag id, not the Thai label (an earlier draft
    ignored `lang` entirely and always showed the Thai text). EN id is
    dash->space ("STAR-STACKED" -> "STAR STACKED") — a deliberate product
    call to unify on one EN label format everywhere (real n8n itself is
    inconsistent: Directory_TI converts dashes to spaces, Directory_PT/WL/
    ST/MC/THEME don't)."""
    tag_info = {"th": "ดาวเรียงตัว", "c1": "#134e4a", "c2": "#7c3aed", "tx": "#ffffff"}
    en_chip = tag_chip("STAR-STACKED", tag_info, variant="list", lang="EN")
    th_chip = tag_chip("STAR-STACKED", tag_info, variant="list", lang="TH")
    assert en_chip["contents"][0]["text"] == "STAR STACKED"
    assert th_chip["contents"][0]["text"] == "ดาวเรียงตัว"


def test_tag_chip_action_false_omits_postback():
    """RENDER_TAG_INFO's own tag pill has no postback — you're already
    viewing this tag's info. Every other usage (RENDER_PT chips, list-row
    chips) taps through to the tag-info card, so action defaults True."""
    tag_info = {"th": "ดาวเรียงตัว", "c1": "#134e4a", "c2": "#7c3aed", "tx": "#ffffff"}
    c = tag_chip("STAR-STACKED", tag_info, variant="single", action=False)
    assert "action" not in c
    c_default = tag_chip("STAR-STACKED", tag_info, variant="single")
    assert c_default["action"]["data"] == "TAG|STAR-STACKED"


def test_tag_chip_single_variant_has_gravity_center():
    """RENDER_PT/RENDER_TAG_INFO's tag text has gravity:center; RENDER_WL's
    list variant doesn't (confirmed against both live node sources)."""
    tag_info = {"th": "x", "c1": "#134e4a", "c2": "#7c3aed", "tx": "#ffffff"}
    single = tag_chip("X", tag_info, variant="single")
    listv = tag_chip("X", tag_info, variant="list")
    assert single["contents"][0]["gravity"] == "center"
    assert "gravity" not in listv["contents"][0]


def test_ticker_logo():
    c = ticker_logo("AAPL")
    assert "img.logo.dev/ticker/AAPL" in c["url"]
