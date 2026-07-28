"""
card/card_renderer.py — render_pt_card() / render_ns_card().

Rewritten 2026-07-13 against the live n8n node code (pulled via REST API
from workflow Thay.fip, mFO5AuDuC9BAPPIV / q9llBApw4G2mMOl5: RENDER_PT,
RENDER_NS, RENDER_WL, RENDER_ST, RENDER_MC, RENDER_THEME, plus the
Directory_PT enrichment node) rather than re-derived from memory — LINE
flex JSON is unforgiving of drift, so every box/color/threshold below is a
verified port, not an approximation. Two findings from that pass worth
flagging for future readers:

1. RENDER_PT's `enrichedAnalysis` (translated structure/zone/trend labels
   + up/down/flat arrow per indicator) is computed by a separate n8n node,
   Directory_PT, that runs BEFORE RENDER_PT — not inside RENDER_PT itself.
   The Python pt-us-service display.analysis block has none of that: raw
   EN-only strings (structure="Above", zone="Neutral", trend/histTrend/
   Trend rather than "arrow"). That whole enrichment step (_PT_TRANS_*,
   _to_arrow below) is ported here, inline, since it's presentation-layer
   translation, not a data-fetching concern — it stays out of
   data_fetcher.py on purpose.
2. RENDER_MC's TLT/LQD `hasTag:false` only suppresses the tag chip — the
   REGULAR percent flip is real, but happens one step earlier, in
   Directory_MC (the enrichment node before RENDER_MC): `percent:
   (d.regular?.percent ?? 0) * sign`, sign=-1 for TLT/LQD. The extended
   (after-hours) percent is deliberately left unflipped in that same
   node. Missing Directory_MC on a first pass (checking only RENDER_MC
   itself) briefly led to concluding there was no inversion at all —
   fixed via MC_INVERT / build_meta_row's `invert` param below.

One function per engine, `mode` ("single"|"list") branches internally for
PT — not one function per card type. List mode further branches per
`card_type` (st/mc/wl/theme) because each has a genuinely different
header/footer/row shape in the real cards (confirmed line-by-line, not
assumed parity).
"""

import os
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlsplit

import yaml

from card_primitives import (
    watchlist_star, footer_row, list_footer_box, tag_chip, ticker_logo, FOOTER_TARGETS,
)

_METADATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card_metadata.yaml")
with open(_METADATA_PATH, encoding="utf-8") as f:
    _METADATA = yaml.safe_load(f) or {}

SECTOR_META: dict = _METADATA.get("sector_meta") or {}
SECTOR_TO_THEME_KEYWORD: dict = _METADATA.get("sector_to_theme_keyword") or {}
MACRO_ORDER: list = _METADATA.get("macro_order") or []
MACRO_META: dict = _METADATA.get("macro_meta") or {}
# Directory_MC's `INVERT = new Set(["TLT", "LQD"])` — flips REGULAR percent
# sign only (not extended-hours) before RENDER_MC ever runs. Kept as its
# own constant rather than derived from MACRO_META's has_tag field: they
# coincide today, but the invert rule is a fact about Directory_MC, not
# a consequence of the tag-visibility flag.
MC_INVERT = {"TLT", "LQD"}
THEME_LABELS: dict = _METADATA.get("theme_labels") or {}
BENCHMARK_LABELS: dict = _METADATA.get("benchmark_labels") or {}

ASSET_BASE = "https://raw.githubusercontent.com/duplyofficial-thay/duply.asset/main"
BKK_TZ = timezone(timedelta(hours=7))
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

UP_COLOR = "#10B981"
DOWN_COLOR = "#E63946"

# RENDER_TAG_INFO group accents — split by tag.type (pt vs bf), ported
# verbatim from the live n8n node. Unknown group falls back to slate.
_PT_ACCENT = {
    "Buy Zone": "#10b981", "Profit Run": "#6366f1", "Standby": "#f59e0b",
    "Sell Zone": "#f97316", "Stay Out": "#ef4444", "Events": "#64748b",
}
_BF_ACCENT = {
    "Top Picks": "#f59e0b", "Growth Bets": "#6366f1", "Value Plays": "#10b981",
    "Safe Picks": "#0ea5e9", "Warning": "#f97316", "Red Flags": "#ef4444",
    "Characters": "#8b5cf6",
}


# ─────────────────────────── formatting helpers ────────────────────────────

def fmt_pct(v) -> str:
    """'+X.XX%' / '-X.XX%' / '-' — used for ST/MC row percents and the
    wl/sector/macro/theme benchmark summary line (all share this 2dp
    convention; only RENDER_PT's own price-detail card uses a different
    abs>=10 -> 1dp threshold, see _fmt_pt_pct)."""
    if v is None:
        return "-"
    try:
        val = float(v)
        return f"{'+' if val >= 0 else ''}{val:.2f}%"
    except (TypeError, ValueError):
        return "-"


def _fmt_pt_pct(pct_val) -> str:
    pct_val = pct_val or 0
    sign = "+" if pct_val >= 0 else ""
    if abs(pct_val) >= 10:
        return f"{sign}{pct_val:.1f}%"
    return f"{sign}{pct_val:.2f}%"


def _fmt_bar_price(val) -> str:
    """RENDER_PT's fmtPrice — position-bar price labels only."""
    if not val:
        return "-"
    n = float(val)
    if n >= 1000:
        return str(round(n))
    if n >= 100:
        return f"{n:.0f}"
    if n >= 10:
        return f"{n:.1f}"
    return f"{n:.2f}"


def _fmt_price_wl(v) -> str:
    """toLocaleString(2dp, thousands-separated) — WL/theme row price/pct
    text and ST/MC's benchmark-less summary line do NOT use this; only
    WL/theme per-row numbers do."""
    if v is None:
        return "0.00"
    return f"{float(v):,.2f}"


def _fmt_bkk_dt(dt: datetime) -> str:
    """'DD-Mon-YY HH:MM' — the one shared footer date/time format across
    every card (PT/NS/WL/ST/MC/THEME). No pipe between date and time —
    that would collide visually with the "| market_state" suffix that
    ST/MC/WL/THEME already append. Each card keeps its own suffix around
    this string (the market-state suffix, PT's "(NEW IPO)") — only the
    date/time rendering itself is unified; WL's old "Updated: " prefix
    was dropped for consistency with the other list cards."""
    return f"{dt.day:02d}-{_MONTHS[dt.month - 1]}-{str(dt.year)[2:]} {dt.hour:02d}:{dt.minute:02d}"


def _bkk_now_str() -> str:
    """Bangkok time, computed at render time — used by WL/ST/MC/THEME
    footers (n8n's `new Date()`, not data's updateTime)."""
    return _fmt_bkk_dt(datetime.now(BKK_TZ))


def _bkk_ts_str(ts_ms) -> str:
    """Bangkok time, from an epoch-ms timestamp — NS footer (`ts`, already
    milliseconds — matches ns_engine's ts convention, same as pt/bf)."""
    if not ts_ms:
        return "-"
    return _fmt_bkk_dt(datetime.fromtimestamp(ts_ms / 1000, tz=BKK_TZ))


def _fmt_footer_dt_from_engine(raw_time: str) -> str:
    """Parse pt-us-service's raw `updateTime` ('DD/MM/YYYY HH:MM') and
    reformat to the same shared convention as every other footer — PT
    used to just pass the raw engine string through with a naive
    space->pipe replace, which is why its footer looked different from
    NS/WL/ST/MC/THEME even though all five show the same kind of
    timestamp. Falls back to the raw string if it's ever a shape we don't
    recognize, rather than breaking the footer entirely."""
    try:
        dt = datetime.strptime(raw_time, "%d/%m/%Y %H:%M")
        return _fmt_bkk_dt(dt)
    except (ValueError, TypeError):
        return raw_time


def _pct_of(item: dict) -> float | None:
    return (item.get("display", {}) or {}).get("regular", {}).get("percent")


def _benchmark_summary_text(items: dict[str, dict], benchmark_tickers: list[str],
                             labels: dict[str, str] | None = None) -> str:
    """'SPY:+0.52% QQQ:+0.31%' (sector, no labels) or 'World:+0.35%'
    (macro, labels={'VT': 'World'}) or 'S&P500:+0.5% Tech:+0.3%' (theme,
    labels=BENCHMARK_LABELS). Used only by ST/THEME's header line — WL and
    MC build their (differently-shaped) header inline instead, so this
    helper is not shared by all four list cards."""
    labels = labels or {}
    parts = []
    for t in benchmark_tickers:
        item = items.get(t)
        pct = _pct_of(item) if item else None
        parts.append(f"{labels.get(t, t)}:{fmt_pct(pct)}")
    return " ".join(parts)


# ─────────────── PT single-ticker indicator translation (Directory_PT) ─────

_PT_TRANS_EN = {
    "structure": {"Above": "Above", "Below": "Below", "At": "At"},
    "zone": {"Overbought": "Overbought", "Oversold": "Oversold", "Neutral": "Neutral"},
    "macd_trend": {"Bullish": "Bullish", "Bearish": "Bearish"},
    "vol": {"Active": "Active", "Moderate": "Moderate", "Inactive": "Inactive"},
    "rr": {"Lower Risk": "Lower Risk", "Moderate": "Moderate", "Higher Risk": "Higher Risk"},
}
_PT_TRANS_TH = {
    "structure": {"Above": "เหนือเส้น", "Below": "ใต้เส้น", "At": "กลางเส้น"},
    "zone": {"Overbought": "ซื้อมากเกินไป", "Oversold": "ขายมากเกินไป", "Neutral": "เป็นกลาง"},
    "macd_trend": {"Bullish": "ขาขึ้น", "Bearish": "ขาลง"},
    "vol": {"Active": "แอคทีฟ", "Moderate": "ปานกลาง", "Inactive": "ไม่แอคทีฟ"},
    "rr": {"Lower Risk": "เสี่ยงต่ำ", "Moderate": "ปานกลาง", "Higher Risk": "เสี่ยงสูง",
           "Setup Complete": "ถึงเป้าหมาย", "Setup Invalid": "หลุดจากแผน"},
}

_UP_KEYWORDS = ("bullish", "rising", "oversold", "lower risk", "complete", "above",
                "ขาขึ้น", "กำลังขึ้น", "ขายมากเกินไป", "เสี่ยงต่ำ", "เหนือเส้น")
_DOWN_KEYWORDS = ("bearish", "falling", "overbought", "higher risk", "invalid", "below",
                  "ขาลง", "กำลังลง", "ซื้อมากเกินไป", "เสี่ยงสูง", "ใต้เส้น")


def _tr(table: dict, value):
    return table.get(value, value)


def _to_arrow(v) -> str:
    if v in ("Rising", "Bullish", "Expanding"):
        return "up"
    if v in ("Falling", "Bearish", "Shrinking"):
        return "down"
    return "flat"


def _get_trend_color(text, theme_sub_color: str) -> str:
    t = str(text or "").lower()
    if any(k in t for k in _UP_KEYWORDS):
        return UP_COLOR
    if any(k in t for k in _DOWN_KEYWORDS):
        return DOWN_COLOR
    return theme_sub_color


def _arrow_char(v: str) -> str:
    return "↗" if v == "up" else "↘" if v == "down" else "→"


def _arrow_color(v: str, active_color: str, theme_sub_color: str) -> str:
    if v == "flat":
        return theme_sub_color
    if v == "up":
        return UP_COLOR
    if v == "down":
        return DOWN_COLOR
    return active_color


def _pt_theme(is_penny: bool) -> dict:
    if is_penny:
        return {"bg": "#0F172A", "textMain": "#F8FAFC", "textSec": "#F1F5F9",
                "textSub": "#94A3B8", "border": "#334155", "barBg": "#334155", "dot": "#F8FAFC"}
    return {"bg": "#FFFFFF", "textMain": "#111111", "textSec": "#1E293B",
            "textSub": "#64748B", "border": "#EEEEEE", "barBg": "#F1F5F9", "dot": "#2d3142"}


# ───────────────────────────── PT single-ticker card ────────────────────────

def _build_position_bar(vis: dict, theme: dict) -> dict:
    prices = vis.get("prices", {}) or {}
    positions = vis.get("positions", {}) or {}
    cw = 240

    def px(pct):
        return f"{round(pct / 100 * cw)}px"

    cur_pos = positions.get("cur", 48)
    cur_pos = min(97, max(0, cur_pos))
    prev_pct = positions.get("prev")

    contents = [
        {"type": "text", "text": "SL", "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetStart": "0px", "offsetTop": "0px"},
        {"type": "text", "text": "SUP", "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetStart": "23%", "offsetTop": "0px"},
        {"type": "text", "text": "RES", "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetEnd": "20%", "offsetTop": "0px"},
        {"type": "text", "text": "TP", "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetEnd": "0px", "offsetTop": "0px", "align": "end"},
        {"type": "box", "layout": "vertical", "backgroundColor": theme["barBg"],
         "cornerRadius": "2px", "position": "absolute",
         "offsetStart": "0px", "offsetEnd": "0px", "offsetTop": "22px", "height": "4px",
         "contents": [{"type": "filler"}]},
    ]

    if prev_pct is not None:
        from_pct = min(prev_pct, cur_pos)
        to_pct = max(prev_pct, cur_pos)
        bar_start_px = round(from_pct / 100 * cw)
        bar_end_px = round(to_pct / 100 * cw)
        bar_width_px = max(6, bar_end_px - bar_start_px)
        contents.append({
            "type": "box", "layout": "vertical", "backgroundColor": "#7161ef",
            "cornerRadius": "2px", "position": "absolute", "offsetTop": "22px", "height": "4px",
            "offsetStart": f"{bar_start_px}px", "width": f"{bar_width_px}px",
            "contents": [{"type": "filler"}],
        })

    contents.extend([
        {"type": "text", "text": _fmt_bar_price(prices.get("sl")), "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetTop": "33px", "offsetStart": px(0), "align": "start"},
        {"type": "text", "text": _fmt_bar_price(prices.get("sup")), "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetTop": "33px", "offsetStart": px(22), "align": "start"},
        {"type": "text", "text": _fmt_bar_price(prices.get("res")), "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetTop": "33px", "offsetStart": px(65), "align": "start"},
        {"type": "text", "text": _fmt_bar_price(prices.get("tp")), "size": "xxs", "color": theme["textSub"],
         "position": "absolute", "offsetTop": "33px", "offsetEnd": "0px", "align": "end"},
    ])

    for dot in [{"pct": 0, "color": theme["dot"]}, {"pct": 24, "color": theme["textSub"]},
                {"pct": 46, "color": theme["dot"]}, {"pct": 68, "color": theme["textSub"]}]:
        contents.append({
            "type": "box", "layout": "vertical", "width": "6px", "height": "6px",
            "backgroundColor": dot["color"], "cornerRadius": "10px", "position": "absolute",
            "offsetTop": "21px", "offsetStart": px(dot["pct"]), "contents": [{"type": "filler"}],
        })

    contents.append({
        "type": "box", "layout": "vertical", "width": "6px", "height": "6px",
        "backgroundColor": theme["dot"], "cornerRadius": "10px", "position": "absolute",
        "offsetTop": "21px", "offsetEnd": "0px", "contents": [{"type": "filler"}],
    })

    contents.append({
        "type": "box", "layout": "vertical", "width": "12px", "height": "12px",
        "backgroundColor": theme["bg"], "borderColor": "#7161ef", "borderWidth": "3px",
        "cornerRadius": "10px", "position": "absolute", "offsetTop": "18px",
        "offsetStart": f"{round(cur_pos / 100 * cw) - 6}px", "contents": [{"type": "filler"}],
    })

    return {
        "type": "box", "layout": "vertical", "margin": "lg", "height": "55px",
        "contents": contents,
    }


def _indicator_row(label: str, theme: dict, value_text: str, trend_text: str,
                    trend_color: str, arrow: str, th_offset: str) -> dict:
    return {
        "type": "box", "layout": "horizontal", "alignItems": "center",
        "contents": [
            {"type": "text", "text": label, "size": "xs", "color": theme["textSub"], "flex": 0},
            {"type": "filler"},
            {"type": "text", "text": value_text, "size": "12px", "color": theme["textMain"],
             "weight": "regular", "flex": 0},
            {"type": "text", "text": "|", "margin": "md", "color": theme["border"], "flex": 0, "gravity": "center"},
            {"type": "text", "text": trend_text, "size": "12px", "color": trend_color, "weight": "bold",
             "margin": "md", "flex": 0, "offsetTop": th_offset},
            {"type": "text", "text": "|", "margin": "md", "color": theme["border"], "flex": 0, "gravity": "center"},
            {"type": "text", "text": _arrow_char(arrow), "size": "12px",
             "color": _arrow_color(arrow, trend_color, theme["textSub"]), "weight": "bold", "margin": "md", "flex": 0},
        ],
    }


def _build_indicator_block(a: dict, tRaw: dict, lang: str, theme: dict) -> dict:
    """tRaw (technicalRaw) is required, not optional decoration — EMA50's
    trend color is a raw currentPrice-vs-ema50 comparison in the real
    n8n code (`tRaw.currentPrice > tRaw.ema50`), NOT derived from the
    translated structure text like RSI/MACD/RR's colors are. MACD value
    and volume pace also fall back to tRaw when `a` lacks them."""
    is_thai = lang == "TH"
    th_offset = "-2px" if is_thai else "0px"
    trans = _PT_TRANS_TH if is_thai else _PT_TRANS_EN

    ema = a.get("EMA50") or {}
    ema_structure = _tr(trans["structure"], ema.get("structure"))
    ema_arrow = _to_arrow(ema.get("Trend"))
    ema_dist = ema.get("distPct") or 0
    ema_dist_str = f"{'+' if ema_dist > 0 else ''}{ema_dist}%"
    ema_structure_color = UP_COLOR if (tRaw.get("currentPrice") or 0) > (tRaw.get("ema50") or 0) else DOWN_COLOR

    rsi = a.get("rsi") or {}
    rsi_zone = _tr(trans["zone"], rsi.get("zone"))
    rsi_arrow = _to_arrow(rsi.get("trend"))
    rsi_val = rsi.get("value")

    macd = a.get("macd") or {}
    macd_trend = _tr(trans["macd_trend"], macd.get("trend"))
    macd_arrow = _to_arrow(macd.get("histTrend"))
    macd_val = macd.get("value")
    if not isinstance(macd_val, (int, float)):
        macd_val = tRaw.get("macd")
    macd_val_str = f"{macd_val:.3f}" if isinstance(macd_val, (int, float)) else "-"

    vol = a.get("volume") or {}
    vol_label = _tr(trans["vol"], vol.get("label"))
    vol_pace = vol.get("pace")
    if vol_pace is None:
        vol_pace = tRaw.get("vol_pace") or 0
    vol_color = UP_COLOR if vol.get("label") in ("Active", "แอคทีฟ") else theme["textSub"]

    rr = a.get("rr") or {}
    rr_status = _tr(trans["rr"], rr.get("status"))
    rr_ratio = rr.get("ratio")
    rr_str = f"1:{rr_ratio}" if rr_ratio is not None else "-"

    return {
        "type": "box", "layout": "vertical", "margin": "md", "spacing": "xs",
        "action": {"type": "uri", "label": "Card Guide",
                   "uri": "https://duply.org/collections/reference/finance/pt-card/#indicators"},
        "contents": [
            _indicator_row("EMA50:", theme, ema_dist_str, ema_structure, ema_structure_color, ema_arrow, th_offset),
            _indicator_row("RSI:", theme, f"{rsi_val:.1f}" if isinstance(rsi_val, (int, float)) else "-",
                            rsi_zone, _get_trend_color(rsi_zone, theme["textSub"]), rsi_arrow, th_offset),
            _indicator_row("MACD:", theme, macd_val_str, macd_trend,
                            _get_trend_color(macd_trend, theme["textSub"]), macd_arrow, th_offset),
            {
                "type": "box", "layout": "horizontal", "alignItems": "center",
                "contents": [
                    {"type": "text", "text": "VOL:", "size": "xs", "color": theme["textSub"], "flex": 0},
                    {"type": "filler"},
                    {"type": "text", "text": f"{vol_pace:.2f}x", "size": "12px", "color": theme["textMain"], "flex": 0},
                    {"type": "text", "text": "|", "margin": "md", "color": theme["border"], "flex": 0, "gravity": "center"},
                    {"type": "text", "text": vol_label, "size": "12px", "color": vol_color, "weight": "bold",
                     "margin": "md", "flex": 0, "offsetTop": th_offset},
                ],
            },
            {
                "type": "box", "layout": "horizontal", "alignItems": "center",
                "contents": [
                    {"type": "text", "text": "RR:", "size": "xs", "color": theme["textSub"], "flex": 0},
                    {"type": "filler"},
                    {"type": "text", "text": rr_str, "size": "12px", "color": theme["textMain"], "flex": 0},
                    {"type": "text", "text": "|", "margin": "md", "color": theme["border"], "flex": 0, "gravity": "center"},
                    {"type": "text", "text": rr_status, "size": "12px", "color": _get_trend_color(rr_status, theme["textSub"]),
                     "weight": "bold", "margin": "md", "flex": 0, "offsetTop": th_offset},
                ],
            },
        ],
    }


def build_pt_single_card(ticker: str, item: dict, tag_data: dict, in_watchlist: bool, lang: str = "EN") -> dict:
    """Full single-ticker PT bubble — near-verbatim port of RENDER_PT (V.4).
    Not a generic row; this is its own rich layout (position bar, penny
    theme, extended-hours row, translated+arrowed indicators)."""
    d = item.get("display", {}) or {}
    a = d.get("analysis", {}) or {}
    vis = d.get("visualData") or {}
    tRaw = item.get("technicalRaw") or {}
    is_ipo_limited = item.get("status") == "IPO_LIMITED"

    reg = d.get("regular") or {}
    current_price = reg.get("price") or 0
    is_penny_mode = current_price < 5.0
    theme = _pt_theme(is_penny_mode)

    pct_val = reg.get("percent") or 0
    pct_str = _fmt_pt_pct(pct_val)
    price_color = UP_COLOR if pct_val >= 0 else DOWN_COLOR
    price_str = f"{reg['price']:.2f}" if reg.get("price") is not None else "-"
    price_font_size = "30px" if len(price_str) >= 9 else "36px" if len(price_str) >= 7 else "42px"

    ext = d.get("extended")
    market_state = d.get("marketState", "CLOSED")
    extended_row = {"type": "filler"}
    if market_state == "LIVE":
        extended_row = {
            "type": "box", "layout": "horizontal", "spacing": "sm", "margin": "none", "offsetBottom": "2px",
            "contents": [{
                "type": "box", "layout": "vertical", "cornerRadius": "5px", "backgroundColor": "#fee2e2",
                "paddingAll": "2px", "paddingStart": "6px", "paddingEnd": "6px", "flex": 0,
                "contents": [{"type": "text", "text": "● LIVE", "size": "10px", "color": "#dc2626",
                              "weight": "bold", "align": "center"}],
            }],
        }
    elif ext and isinstance(ext.get("price"), (int, float)):
        is_up = (ext.get("percent") or 0) >= 0
        moon_icon = "moon-fill.png" if is_penny_mode else "moon-fill-black.png"
        extended_row = {
            "type": "box", "layout": "baseline", "spacing": "xs", "margin": "none", "offsetBottom": "2px",
            "contents": [
                {"type": "icon", "url": f"{ASSET_BASE}/{moon_icon}", "size": "xxs", "offsetTop": "1px"},
                {"type": "text", "text": f"{ext['price']:.2f}", "size": "13px",
                 "color": UP_COLOR if is_up else DOWN_COLOR, "flex": 0},
                {"type": "text", "text": f"({'+' if is_up else ''}{ext.get('percent', 0):.2f}%)",
                 "size": "13px", "color": UP_COLOR if is_up else DOWN_COLOR},
            ],
        }

    tags = (a.get("tags") or [])[:2]
    tag_boxes = [tag_chip(t, tag_data[t], variant="single", lang=lang) for t in tags if tag_data.get(t)]

    raw_time = d.get("updateTime") or "-"
    footer_text = _fmt_footer_dt_from_engine(raw_time) if raw_time != "-" else raw_time
    footer_label = f"{footer_text}  (NEW IPO)" if is_ipo_limited else footer_text

    body_contents = [
        {"type": "box", "layout": "horizontal", "spacing": "xs",
         "contents": tag_boxes if tag_boxes else [{"type": "filler"}]},
        {
            "type": "box", "layout": "vertical", "margin": "lg", "spacing": "none",
            "contents": [
                {
                    "type": "box", "layout": "horizontal", "spacing": "sm", "alignItems": "center", "offsetTop": "4px",
                    "contents": [
                        {"type": "box", "layout": "vertical", "width": "18px", "height": "18px", "cornerRadius": "5px",
                         "contents": [ticker_logo(ticker + ".BK")]},
                        {"type": "text", "text": ticker or "STOCK", "weight": "bold", "size": "md",
                         "color": theme["textSec"], "flex": 0},
                        watchlist_star(ticker, in_watchlist, paddingStart="5px"),
                        {"type": "filler"},
                    ],
                },
                {
                    "type": "box", "layout": "baseline", "spacing": "xs", "margin": "xs",
                    "contents": [
                        {"type": "text", "text": price_str, "size": price_font_size, "weight": "bold",
                         "color": theme["textMain"], "flex": 0},
                        {"type": "text", "text": pct_str, "size": "md", "weight": "bold", "color": price_color},
                    ],
                },
                extended_row,
            ],
        },
        footer_row(ticker, footer_text=footer_label, **FOOTER_TARGETS["pt"]),
    ]

    if not is_ipo_limited:
        body_contents[2:2] = [
            {"type": "separator", "margin": "md", "color": theme["border"]},
            _build_position_bar(vis, theme),
            _build_indicator_block(a, tRaw, lang, theme),
        ]

    return {
        "type": "bubble", "size": "kilo",
        "body": {"type": "box", "layout": "vertical", "backgroundColor": theme["bg"],
                 "paddingAll": "20px", "contents": body_contents},
    }


# ──────────────────────── list-mode row builders (ST/MC) ───────────────────

def build_meta_row(ticker: str, item: dict, meta_entry: dict, tag_data: dict,
                    postback_data: str, lang: str = "EN", invert: bool = False) -> dict:
    """Icon+color+localized-name row — RENDER_ST/RENDER_MC pattern.

    `has_tag` (absent=True for sector, explicit for macro) controls tag
    visibility. `invert` is a separate, MC-only concern: confirmed against
    Directory_MC (the enrichment node that runs BEFORE RENDER_MC, missed
    in an earlier pass of this port) that TLT/LQD's REGULAR percent is
    multiplied by -1 upstream before RENDER_MC ever sees it —
    `percent: (d.regular?.percent ?? 0) * sign`. The icon/color box never
    changes, and — confirmed in the same node — the EXTENDED (after-hours)
    percent is left unflipped (`...d` spread preserves the original
    `extended` object untouched). Sector never inverts (no INVERT set in
    Directory_ST) — that's why this is a caller-supplied flag, not derived
    from `has_tag` (they coincide for today's MACRO_META entries, but
    that's a fact about the data, not a logic dependency worth hard-wiring)."""
    name = meta_entry.get("name_th" if lang == "TH" else "name_en", ticker)
    show_tag = meta_entry.get("has_tag", True)
    d = item.get("display", {}) or {}
    reg = d.get("regular") or {}
    ext = d.get("extended")
    pct = reg.get("percent")
    if invert and pct is not None:
        pct = pct * -1

    tags = (d.get("analysis", {}) or {}).get("tags") or []
    tag_id = tags[0] if (show_tag and tags) else None
    tag_info = tag_data.get(tag_id) if tag_id else None
    name_col_tag = (
        {"type": "box", "layout": "horizontal",
         "contents": [tag_chip(tag_id, tag_info, variant="list", lang=lang)]}
        if tag_info
        else {"type": "box", "layout": "vertical", "height": "14px", "contents": []}
    )

    ext_col = {"type": "box", "layout": "vertical", "height": "14px", "contents": []}
    if ext:
        ext_pct = ext.get("percent")
        ext_col = {
            "type": "box", "layout": "horizontal", "spacing": "xs", "justifyContent": "flex-end",
            "contents": [
                {"type": "text", "text": "☾", "size": "xxs", "color": "#94A3B8", "flex": 0},
                {"type": "text", "text": fmt_pct(ext_pct), "size": "xxs",
                 "color": UP_COLOR if (ext_pct or 0) >= 0 else DOWN_COLOR, "flex": 0},
            ],
        }

    return {
        "type": "box", "layout": "horizontal", "alignItems": "center", "spacing": "md",
        "paddingTop": "10px", "paddingBottom": "10px",
        "action": {"type": "postback", "data": postback_data},
        "contents": [
            {
                "type": "box", "layout": "vertical", "width": "36px", "height": "36px",
                "cornerRadius": "18px", "flex": 0, "backgroundColor": meta_entry.get("color", "#64748B"),
                "paddingAll": "4px",
                "contents": [{"type": "image", "url": f"{ASSET_BASE}/{meta_entry['icon']}",
                              "size": "full", "aspectMode": "cover"}],
            },
            {"type": "box", "layout": "vertical", "flex": 1, "spacing": "xs",
             "contents": [
                 {"type": "text", "text": name, "size": "sm", "weight": "bold", "color": "#1E293B"},
                 name_col_tag,
             ]},
            {"type": "box", "layout": "vertical", "flex": 0, "alignItems": "flex-end", "spacing": "xs",
             "contents": [
                 {"type": "text", "text": fmt_pct(pct), "size": "sm", "weight": "bold",
                  "color": UP_COLOR if (pct or 0) >= 0 else DOWN_COLOR, "align": "end"},
                 ext_col,
             ]},
        ],
    }


def _rows_with_separators(rows: list[dict]) -> list[dict]:
    """ST/MC: separator between rows, none after the last."""
    out = []
    for i, row in enumerate(rows):
        out.append(row)
        if i != len(rows) - 1:
            out.append({"type": "separator", "color": "#F1F5F9"})
    return out


def _st_card(items: dict, tag_data: dict, lang: str) -> dict:
    spy_pct = _pct_of(items.get("SPY", {})) or 0
    qqq_pct = _pct_of(items.get("QQQ", {})) or 0
    m_state = next(iter(items.values()), {}).get("display", {}).get("marketState", "CLOSED") if items else "CLOSED"

    row_tickers = [t for t in items if t in SECTOR_META and items[t].get("display", {}).get("regular")]
    row_tickers.sort(key=lambda t: (_pct_of(items[t]) or 0), reverse=True)
    rows = _rows_with_separators([
        build_meta_row(t, items[t], SECTOR_META[t], tag_data,
                       postback_data=SECTOR_TO_THEME_KEYWORD.get(t, t), lang=lang)
        for t in row_tickers
    ])

    return {
        "type": "bubble", "size": "mega",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#FFFFFF",
            "paddingAll": "16px", "paddingBottom": "4px",
            "contents": [
                {"type": "text", "text": "SECTORS", "weight": "bold", "size": "xl", "color": "#1A1A1A"},
                {"type": "box", "layout": "horizontal", "margin": "sm", "spacing": "xs",
                 "contents": [
                     {"type": "text", "text": "S&P500:", "size": "xxs", "color": "#94A3B8", "flex": 0},
                     {"type": "text", "text": fmt_pct(spy_pct), "size": "xxs",
                      "color": UP_COLOR if spy_pct >= 0 else DOWN_COLOR, "flex": 0},
                     {"type": "text", "text": "|", "size": "xxs", "color": "#E2E8F0", "flex": 0, "margin": "sm"},
                     {"type": "text", "text": "Nasdaq:", "size": "xxs", "color": "#94A3B8", "flex": 0, "margin": "sm"},
                     {"type": "text", "text": fmt_pct(qqq_pct), "size": "xxs",
                      "color": UP_COLOR if qqq_pct >= 0 else DOWN_COLOR, "flex": 0},
                 ]},
            ],
        },
        "body": {"type": "box", "layout": "vertical", "paddingAll": "16px", "paddingTop": "8px",
                 "paddingBottom": "0px", "contents": rows},
        "footer": list_footer_box(f"{_bkk_now_str()} | {m_state}", padding_bottom="12px"),
    }


def _mc_card(items: dict, tag_data: dict, lang: str) -> dict:
    vt_pct = _pct_of(items.get("VT", {})) or 0
    m_state = next(iter(items.values()), {}).get("display", {}).get("marketState", "CLOSED") if items else "CLOSED"

    rows = _rows_with_separators([
        build_meta_row(t, items[t], MACRO_META[t], tag_data, postback_data=t, lang=lang,
                       invert=t in MC_INVERT)
        for t in MACRO_ORDER if t in items and t in MACRO_META
    ])

    return {
        "type": "bubble", "size": "mega",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#FFFFFF",
            "paddingAll": "16px", "paddingBottom": "4px",
            "contents": [
                {"type": "text", "text": "US MACRO", "weight": "bold", "size": "xl", "color": "#1A1A1A"},
                {"type": "box", "layout": "horizontal", "margin": "sm", "spacing": "xs",
                 "contents": [
                     {"type": "text", "text": "World:", "size": "xxs", "color": "#94A3B8", "flex": 0},
                     {"type": "text", "text": fmt_pct(vt_pct), "size": "xxs",
                      "color": UP_COLOR if vt_pct >= 0 else DOWN_COLOR, "flex": 0},
                 ]},
            ],
        },
        "body": {"type": "box", "layout": "vertical", "paddingAll": "16px", "paddingTop": "8px",
                 "paddingBottom": "0px", "contents": rows},
        "footer": list_footer_box(f"{_bkk_now_str()} | {m_state}", padding_bottom="12px"),
    }


# ──────────────────────── list-mode row builders (WL/THEME) ────────────────

def _wl_theme_row(ticker: str, item: dict, tag_data: dict, lang: str = "EN") -> dict:
    """Shared row body for WL and THEME (confirmed identical structure in
    the live node code) — logo box + ticker/tag column + 140px price
    column with a day%/ext% sub-row. Only the wrapping (separator vs.
    last-row filler) differs between the two, handled by the caller.

    `lang` matters here even though WL/THEME's own header titles are
    hardcoded English in the real n8n cards — Directory_WL/Directory_THEME
    both translate each row's tag label the same way Directory_PT/ST/MC do
    (`system_lang === "TH" ? th_name : id`)."""
    d = item.get("display", {}) or {}
    reg = d.get("regular") or {"price": 0, "percent": 0}
    ext = d.get("extended")
    tags = (d.get("analysis", {}) or {}).get("tags") or []
    tag_id = tags[0] if tags else None
    tag_info = tag_data.get(tag_id) if tag_id else None

    tag_col = (
        {"type": "box", "layout": "horizontal", "contents": [tag_chip(tag_id, tag_info, variant="list", lang=lang)]}
        if tag_info else {"type": "filler"}
    )

    pct = reg.get("percent") or 0
    price_row = {
        "type": "box", "layout": "horizontal", "justifyContent": "flex-end", "alignItems": "center",
        "contents": [
            {"type": "text", "text": _fmt_price_wl(reg.get("price")), "size": "sm", "weight": "bold",
             "color": "#1e293b", "align": "end", "flex": 0},
            {"type": "box", "layout": "vertical", "width": "75px", "contents": [
                {"type": "text", "text": f"{'+' if pct >= 0 else ''}{_fmt_price_wl(pct)}%", "size": "sm",
                 "weight": "bold", "color": UP_COLOR if pct >= 0 else DOWN_COLOR, "align": "end"},
            ]},
        ],
    }
    ext_row = {"type": "filler"}
    if ext:
        ext_pct = ext.get("percent") or 0
        ext_row = {
            "type": "box", "layout": "horizontal", "margin": "xs", "justifyContent": "flex-end", "alignItems": "center",
            "contents": [
                {"type": "text", "text": f"☾ {_fmt_price_wl(ext.get('price'))}", "size": "xxs",
                 "color": "#94a3b8", "align": "end", "flex": 0},
                {"type": "box", "layout": "vertical", "width": "75px", "contents": [
                    {"type": "text", "text": f"{'+' if ext_pct >= 0 else ''}{_fmt_price_wl(ext_pct)}%",
                     "size": "xxs", "color": UP_COLOR if ext_pct >= 0 else DOWN_COLOR, "align": "end"},
                ]},
            ],
        }

    return {
        "type": "box", "layout": "vertical", "paddingTop": "lg", "paddingBottom": "lg",
        "action": {"type": "postback", "data": ticker},
        "contents": [
            {
                "type": "box", "layout": "horizontal", "alignItems": "flex-start",
                "contents": [
                    {"type": "box", "layout": "vertical", "width": "32px", "height": "32px", "cornerRadius": "16px",
                     "backgroundColor": "#F1F5F9", "contents": [ticker_logo(ticker + ".BK")]},
                    {"type": "box", "layout": "vertical", "margin": "md", "flex": 1, "spacing": "xs",
                     "contents": [
                         {"type": "text", "text": ticker, "size": "sm", "weight": "bold", "color": "#1e293b"},
                         tag_col,
                     ]},
                    {"type": "box", "layout": "vertical", "flex": 0, "width": "140px",
                     "contents": [price_row, ext_row]},
                ],
            },
        ],
    }


def _wl_card(items: dict, tag_data: dict, lang: str = "EN") -> dict:
    spy_pct = _pct_of(items.get("SPY", {})) or 0
    qqq_pct = _pct_of(items.get("QQQ", {})) or 0
    stocks = [t for t in items if t not in ("SPY", "QQQ") and items[t].get("display", {}).get("regular")]
    m_state = next(iter(items.values()), {}).get("display", {}).get("marketState", "CLOSED") if items else "CLOSED"

    if stocks:
        rows = [
            {"type": "box", "layout": "vertical",
             "contents": [_wl_theme_row(t, items[t], tag_data, lang=lang), {"type": "separator", "color": "#f1f5f9"}]}
            for t in stocks
        ]
    else:
        rows = [{"type": "box", "layout": "vertical", "paddingAll": "xl",
                 "contents": [{"type": "text", "text": "No active watchlist data.", "align": "center",
                               "color": "#94a3b8", "size": "sm"}]}]

    return {
        "type": "bubble", "size": "mega",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#ffffff",
            "paddingAll": "15px", "paddingBottom": "5px",
            "contents": [
                {"type": "text", "text": "WATCHLIST", "color": "#000000", "weight": "bold", "size": "xl", "align": "start"},
                {"type": "box", "layout": "horizontal", "justifyContent": "flex-start", "margin": "sm",
                 "contents": [
                     {"type": "box", "layout": "baseline", "spacing": "xs", "flex": 0, "contents": [
                         {"type": "text", "text": "S&P500:", "color": "#94A3B8", "size": "xxs", "flex": 0},
                         {"type": "text", "text": fmt_pct(spy_pct), "color": UP_COLOR if spy_pct >= 0 else DOWN_COLOR,
                          "size": "xxs", "flex": 0},
                     ]},
                     {"type": "text", "text": "|", "color": "#e2e8f0", "size": "xxs", "flex": 0, "margin": "md"},
                     {"type": "box", "layout": "baseline", "spacing": "xs", "flex": 0, "margin": "md", "contents": [
                         {"type": "text", "text": "Nasdaq:", "color": "#94A3B8", "size": "xxs", "flex": 0},
                         {"type": "text", "text": fmt_pct(qqq_pct), "color": UP_COLOR if qqq_pct >= 0 else DOWN_COLOR,
                          "size": "xxs", "flex": 0},
                     ]},
                 ]},
            ],
        },
        "body": {"type": "box", "layout": "vertical", "paddingAll": "16px", "paddingTop": "0px",
                 "paddingBottom": "0px", "contents": rows},
        "footer": list_footer_box(f"{_bkk_now_str()} | {m_state.upper()}", padding_bottom="15px"),
    }


def _theme_card(items: dict, tag_data: dict, theme_key: str, benchmarks: list[str], lang: str = "EN") -> dict:
    b0_key = benchmarks[0] if benchmarks else "SPY"
    b1_key = benchmarks[1] if len(benchmarks) > 1 else "SPY"
    b0_pct = _pct_of(items.get(b0_key, {})) or 0
    b1_pct = _pct_of(items.get(b1_key, {})) or 0
    b0_label = BENCHMARK_LABELS.get(b0_key, b0_key)
    b1_label = BENCHMARK_LABELS.get(b1_key, b1_key)
    theme_label = THEME_LABELS.get(theme_key, theme_key)
    m_state = next(iter(items.values()), {}).get("display", {}).get("marketState", "CLOSED") if items else "CLOSED"

    stock_tickers = [t for t in items if t not in benchmarks and items[t].get("display", {}).get("regular")]
    n = len(stock_tickers)
    if n:
        rows = []
        for idx, t in enumerate(stock_tickers):
            is_last = idx == n - 1
            tail = (
                {"type": "box", "layout": "vertical", "height": "1px", "contents": [{"type": "filler"}]}
                if is_last else {"type": "separator", "color": "#f1f5f9"}
            )
            rows.append({"type": "box", "layout": "vertical",
                         "contents": [_wl_theme_row(t, items[t], tag_data, lang=lang), tail]})
    else:
        rows = [{"type": "box", "layout": "vertical", "paddingAll": "xl",
                 "contents": [{"type": "text", "text": "No data available.", "align": "center",
                               "color": "#94a3b8", "size": "sm"}]}]

    return {
        "type": "bubble", "size": "mega",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#ffffff",
            "paddingAll": "15px", "paddingBottom": "5px",
            "contents": [
                {"type": "text", "text": theme_label, "weight": "bold", "size": "xl", "color": "#1A1A1A"},
                {"type": "box", "layout": "horizontal", "margin": "sm", "spacing": "xs",
                 "contents": [
                     {"type": "text", "text": f"{b0_label}:", "color": "#94A3B8", "size": "xxs", "flex": 0},
                     {"type": "text", "text": fmt_pct(b0_pct), "color": UP_COLOR if b0_pct >= 0 else DOWN_COLOR,
                      "size": "xxs", "flex": 0},
                     {"type": "text", "text": "|", "color": "#e2e8f0", "size": "xxs", "flex": 0, "margin": "md"},
                     {"type": "text", "text": f"{b1_label}:", "color": "#94A3B8", "size": "xxs", "flex": 0, "margin": "md"},
                     {"type": "text", "text": fmt_pct(b1_pct), "color": UP_COLOR if b1_pct >= 0 else DOWN_COLOR,
                      "size": "xxs", "flex": 0},
                 ]},
            ],
        },
        "body": {"type": "box", "layout": "vertical", "paddingAll": "16px", "paddingTop": "0px",
                 "paddingBottom": "0px", "contents": rows},
        "footer": list_footer_box(f"{_bkk_now_str()} | {m_state.upper()}", padding_bottom="15px"),
    }


# ───────────────────────────── public entry point ───────────────────────────

def render_pt_card(items: dict[str, dict], mode: str, tag_data: dict,
                    watchlist: list[str] | None = None, label: str = "",
                    card_type: str = "generic",
                    lang: str = "EN", benchmarks: list[str] | None = None) -> dict:
    """card_type: "pt" (single-ticker) | "st" | "mc" | "wl" | "theme".
    Each list card_type has a genuinely different bubble shape (confirmed
    against live n8n node code) — dispatched to its own builder rather
    than a single shared generic layout."""
    watchlist = watchlist or []
    benchmarks = benchmarks or []

    if mode == "single":
        tickers = list(items.keys())
        if not tickers:
            return {"type": "bubble", "body": {"type": "box", "layout": "vertical",
                    "contents": [{"type": "text", "text": f"No data for {label or tickers}"}]}}
        ticker = tickers[0]
        return build_pt_single_card(ticker, items[ticker], tag_data,
                                     in_watchlist=ticker in watchlist, lang=lang)

    if card_type == "st":
        return _st_card(items, tag_data, lang)
    if card_type == "mc":
        return _mc_card(items, tag_data, lang)
    if card_type == "wl":
        return _wl_card(items, tag_data, lang)
    if card_type == "theme":
        return _theme_card(items, tag_data, label, benchmarks, lang)
    if card_type == "pt":
        # multi-ticker PT compare ("NVDA,AMD,TSM") — same list shape as
        # theme/wl (SPY/QQQ header line, _wl_theme_row rows), title = label
        # ("Stocks") from resolve_target.
        return _theme_card(items, tag_data, label, benchmarks, lang)

    # no other list card_type is expected; fall back to theme's shape
    # (closest generic match) rather than silently guessing further.
    return _theme_card(items, tag_data, label, benchmarks, lang)


# ───────────────────────────────── NS card ───────────────────────────────────

_NS_SOURCE_COLORS = {
    "reuters": "#FF8000", "bloomberg": "#1A73E8", "bloomberg technology": "#1A73E8",
    "the wall street journal": "#333333", "financial times": "#CC0000", "barrons": "#8B0000",
    "cnbc": "#004A97", "ft": "#CC0000",
    "seeking alpha": "#16A34A", "investors business daily": "#0369A1", "marketbeat": "#059669",
    "zacks investment research": "#D97706", "the motley fool": "#C2410C", "fool - investing news": "#C2410C",
    "benzinga": "#FF6B35", "investopedia": "#0284C7",
    "business insider": "#7C3AED", "new york post": "#7C3AED", "market watch": "#7C3AED",
    "24/7 wall street": "#7C3AED", "pymnts": "#7C3AED", "fxempire": "#7C3AED",
    "accesswire": "#7C3AED", "business wire": "#7C3AED", "prnewswire": "#7C3AED",
}


def _ns_source_color(source: str) -> str:
    return _NS_SOURCE_COLORS.get((source or "").lower(), "#94A3B8")


_URI_ACTION_SAFE_CHARS = "%/:?&=@!$'()*+,;#"


def _safe_uri(url: str | None) -> str | None:
    """Re-encode a raw external URL (FMP news `url` field) for a LINE Flex
    `uri` action. External APIs sometimes return URLs with unescaped
    reserved characters — confirmed live 2026-07-20: a literal `|` in a
    TDY news query string caused LINE's reply API to reject the ENTIRE
    Flex message with 400, silently dropping the whole card (not just that
    one row) with no user-visible error. `%` stays in the safe set so
    already-percent-encoded sequences aren't double-escaped. Returns None
    (row gets no action, same as a missing url) rather than risk sending a
    still-malformed URL — a card with a dead link beats a card that never
    arrives."""
    if not url:
        return None
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return quote(url, safe=_URI_ACTION_SAFE_CHARS)


def build_ns_single_card(ticker: str, ns_item: dict, in_watchlist: bool) -> dict:
    """Full single-ticker NS bubble — port of RENDER_NS. Renders ALL news
    items (no cap), each row clickable, source names color-coded."""
    news = ns_item.get("news") or []
    company_name = ns_item.get("companyName") or ticker

    news_rows = []
    for i, n in enumerate(news):
        if i > 0:
            news_rows.append({"type": "separator", "margin": "none", "color": "#F1F5F9"})
        row = {
            "type": "box", "layout": "horizontal", "spacing": "sm",
            "paddingTop": "10px", "paddingBottom": "0px" if i == len(news) - 1 else "10px",
            "alignItems": "center",
            "contents": [
                {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                    {"type": "text", "text": n.get("title", ""), "size": "xxs", "color": "#1E293B",
                     "wrap": True, "maxLines": 2, "weight": "bold"},
                    {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm", "contents": [
                        {"type": "text", "text": n.get("source", ""), "size": "9px",
                         "color": _ns_source_color(n.get("source")), "weight": "bold", "flex": 0},
                        {"type": "text", "text": "·", "size": "9px", "color": "#CBD5E1", "flex": 0},
                        {"type": "text", "text": n.get("date", ""), "size": "9px", "color": "#94A3B8"},
                    ]},
                ]},
                {"type": "text", "text": "›", "size": "xl", "color": "#CBD5E1", "flex": 0, "gravity": "center"},
            ],
        }
        safe_url = _safe_uri(n.get("url"))
        if safe_url:
            row["action"] = {"type": "uri", "uri": safe_url}
        news_rows.append(row)
    news_rows.append({"type": "separator", "margin": "lg", "color": "#F1F5F9"})

    footer_text = _bkk_ts_str(ns_item.get("ts"))

    return {
        "type": "bubble", "size": "kilo",
        "body": {
            "type": "box", "layout": "vertical", "backgroundColor": "#FFFFFF", "paddingAll": "20px",
            "contents": [
                {
                    "type": "box", "layout": "horizontal", "spacing": "md", "alignItems": "center",
                    "contents": [
                        {"type": "box", "layout": "vertical", "width": "42px", "height": "42px", "cornerRadius": "12px",
                         "contents": [ticker_logo(ticker + ".BK")]},
                        {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                            {"type": "box", "layout": "horizontal", "alignItems": "flex-start", "spacing": "sm",
                             "contents": [
                                 {"type": "text", "text": ticker, "weight": "bold", "size": "xxl", "color": "#1E293B", "flex": 0},
                                 watchlist_star(ticker, in_watchlist, paddingTop="6px"),
                             ]},
                            {"type": "text", "text": company_name, "size": "xxs", "color": "#64748B",
                             "wrap": True, "maxLines": 1},
                        ]},
                    ],
                },
                {"type": "separator", "margin": "lg", "color": "#F1F5F9"},
                {"type": "text", "text": "News Drivers", "size": "xs", "color": "#64748B", "weight": "bold", "margin": "lg"},
                *news_rows,
                footer_row(ticker, footer_text=footer_text, **FOOTER_TARGETS["ns"]),
            ],
        },
    }


def render_ns_card(items: dict[str, dict], mode: str, label: str = "",
                    watchlist: list[str] | None = None) -> dict:
    """No tag_chip call here — NS has no tagging logic built yet (docs/
    thay.md NS Card Status: 'NS tag — no tagging logic built')."""
    watchlist = watchlist or []
    tickers = list(items.keys())

    if mode == "single":
        if not tickers:
            return {"type": "bubble", "body": {"type": "box", "layout": "vertical",
                    "contents": [{"type": "text", "text": f"No news for {label or tickers}"}]}}
        ticker = tickers[0]
        return build_ns_single_card(ticker, items[ticker], in_watchlist=ticker in watchlist)

    # list mode: no real n8n precedent exists for a multi-ticker NS card
    # (mc_ns was pre-rendered upstream, never a per-ticker list) — keep a
    # minimal fallback rather than inventing a layout with no source to verify against.
    rows = [{"type": "text", "text": f"{t}: {items[t].get('short', '')}"} for t in tickers]
    return {"type": "bubble", "body": {"type": "box", "layout": "vertical",
            "contents": [{"type": "text", "text": label, "weight": "bold", "size": "lg"}, *rows]}}


_MC_NS_SENTIMENT_THEME = {
    "RISK-ON": {"bg1": "#DCFCE7", "bg2": "#BBF7D0", "text": "#16A34A"},
    "RISK-OFF": {"bg1": "#FEE2E2", "bg2": "#FECACA", "text": "#DC2626"},
    "TENSE": {"bg1": "#FEF9C3", "bg2": "#FEF08A", "text": "#CA8A04"},
    "NEUTRAL": {"bg1": "#F1F5F9", "bg2": "#E2E8F0", "text": "#64748B"},
}

# RENDER_MC_NS's own SOURCE_COLORS — a real, separate (slightly shorter)
# list from RENDER_NS's, not the same map reused. Ported as its own dict
# rather than sharing _NS_SOURCE_COLORS with the per-ticker NS card, since
# the two n8n nodes genuinely differ (RENDER_MC_NS is missing several
# tier-3 outlets RENDER_NS has) — confirmed by reading both live.
_MC_NS_SOURCE_COLORS = {
    "reuters": "#FF8000", "bloomberg": "#1A73E8", "bloomberg technology": "#1A73E8",
    "the wall street journal": "#333333", "financial times": "#CC0000", "barrons": "#8B0000",
    "cnbc": "#004A97", "ft": "#CC0000",
    "seeking alpha": "#16A34A", "investors business daily": "#0369A1", "marketbeat": "#059669",
    "zacks investment research": "#D97706", "the motley fool": "#C2410C", "fool - investing news": "#C2410C",
    "benzinga": "#FF6B35", "investopedia": "#0284C7",
    "business insider": "#7C3AED", "market watch": "#7C3AED",
}


def _mc_ns_source_color(source: str) -> str:
    return _MC_NS_SOURCE_COLORS.get((source or "").lower(), "#94A3B8")


def render_macro_ns_card(data: dict) -> dict:
    """Macro-news bubble — ported from RENDER_MC_NS. `data` is
    fetch_macro_ns()'s return shape: {"driver": str, "sentiment": str,
    "news": [...]}. Not per-ticker (no lang-dependent translation anywhere
    in the real node — news content is English-only, same as the
    per-ticker NS card); footer uses "now" (Bangkok time), matching
    Directory_MC_NS's own `ts: Date.now()` — the raw data has no fetch
    timestamp of its own to show instead."""
    news = data.get("news") or []
    driver = data.get("driver") or ""
    sentiment = (data.get("sentiment") or "NEUTRAL").upper().strip()
    theme = _MC_NS_SENTIMENT_THEME.get(sentiment, _MC_NS_SENTIMENT_THEME["NEUTRAL"])

    news_rows = []
    for i, n in enumerate(news):
        if i > 0:
            news_rows.append({"type": "separator", "margin": "none", "color": "#F1F5F9"})
        news_rows.append({
            "type": "box", "layout": "horizontal", "spacing": "sm",
            "paddingTop": "10px", "paddingBottom": "0px" if i == len(news) - 1 else "10px",
            "alignItems": "center",
            "action": {"type": "uri", "uri": _safe_uri(n.get("url")) or "https://finance.yahoo.com"},
            "contents": [
                {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                    {"type": "text", "text": n.get("title", ""), "size": "xxs", "color": "#1E293B",
                     "wrap": True, "maxLines": 2, "weight": "bold"},
                    {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm", "contents": [
                        {"type": "text", "text": n.get("source", ""), "size": "9px",
                         "color": _mc_ns_source_color(n.get("source")), "weight": "bold", "flex": 0},
                        {"type": "text", "text": "·", "size": "9px", "color": "#CBD5E1", "flex": 0},
                        {"type": "text", "text": n.get("date", ""), "size": "9px", "color": "#94A3B8"},
                    ]},
                ]},
                {"type": "text", "text": "›", "size": "xl", "color": "#CBD5E1", "flex": 0, "gravity": "center"},
            ],
        })

    return {
        "type": "bubble", "size": "mega",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#FFFFFF",
            "paddingAll": "16px", "paddingBottom": "4px",
            "contents": [
                {"type": "text", "text": "US MACRO", "weight": "bold", "size": "xl", "color": "#1A1A1A"},
                {"type": "box", "layout": "horizontal", "margin": "sm", "contents": [
                    {"type": "text", "text": "Market News", "size": "xxs", "color": "#94A3B8", "flex": 0},
                ]},
            ],
        },
        "body": {
            "type": "box", "layout": "vertical", "backgroundColor": "#FFFFFF",
            "paddingAll": "16px", "paddingTop": "8px",
            "contents": [
                {
                    "type": "box", "layout": "vertical", "backgroundColor": "#F8FAFC",
                    "cornerRadius": "10px", "paddingAll": "12px",
                    "contents": [
                        {"type": "box", "layout": "horizontal", "contents": [
                            {"type": "box", "layout": "vertical", "paddingEnd": "60px", "contents": [
                                {"type": "text", "text": "DRIVERS", "size": "xs", "color": "#64748B", "weight": "bold"},
                                {"type": "text", "text": driver, "size": "xxs", "color": "#1E293B", "wrap": True, "margin": "sm"},
                            ]},
                            {
                                "type": "box", "layout": "vertical", "cornerRadius": "7px", "paddingAll": "4px",
                                "position": "absolute", "offsetEnd": "0px",
                                "background": {"type": "linearGradient", "angle": "45deg",
                                               "startColor": theme["bg1"], "endColor": theme["bg2"]},
                                "contents": [{"type": "text", "text": sentiment, "size": "xxs",
                                              "weight": "bold", "color": theme["text"]}],
                            },
                        ]},
                    ],
                },
                {"type": "text", "text": "TOP HEADLINES", "size": "xs", "color": "#7C3AED",
                 "weight": "bold", "margin": "lg"},
                *news_rows,
            ],
        },
        "footer": list_footer_box(_bkk_now_str(), padding_bottom="12px"),
    }


def render_tag_info_card(tag_id: str, tag_info: dict, lang: str = "EN") -> dict:
    """Tag mini card (micro bubble) — ported from n8n RENDER_TAG_INFO.

    Field mapping n8n `tag.*` (built by Directory_TI) -> Redis `fip:tags:list`:
      label    -> tag_chip()'s own lang rule (th / EN dash->space id — see
                  tag_chip's docstring for why EN is unified on spaces
                  everywhere rather than matching Directory_TI's dash->space
                  vs Directory_PT/WL/ST/MC/THEME's raw-dash split)
      desc     -> `desc_en` (EN, fallback `desc`) / `desc` (TH)
      textColor-> `tx`
      group    -> `group` (fallback "General"); c1/c2/lv/type -> direct
    Drivers exist in the data but RENDER_TAG_INFO does not render them
    (n8n builds driverBoxes then never places them in the bubble) — omitted
    here to match the real card, not the dead code.

    The tag pill itself is `tag_chip(..., variant="single", action=False)`
    — structurally the exact same box RENDER_PT's per-ticker tag chips
    use, minus the postback (you're already viewing this tag's own info).
    An earlier draft rebuilt this box inline, duplicating tag_chip().
    """
    is_thai = lang == "TH"
    tag = tag_info or {}
    group = tag.get("group", "General")
    tag_type = tag.get("type", "pt")
    accent_map = _BF_ACCENT if tag_type == "bf" else _PT_ACCENT
    accent = accent_map.get(group, "#64748b")
    lib_page = "bf-tag-lib" if tag_type == "bf" else "pt-tag-lib"
    desc = (tag.get("desc_en") or tag.get("desc") or "No description available.") if not is_thai \
        else (tag.get("desc") or "ไม่มีคำอธิบายสำหรับแท็กนี้")

    # weight dots — lv 1-3 = that many on; lv>=4 = platinum (3 green dots)
    lv = tag.get("lv", 1)
    is_platinum = lv >= 4
    dots_on = 3 if (is_platinum or lv >= 3) else (2 if lv == 2 else 1)
    dot_color = "#10b981" if is_platinum else "#94A3B8"
    dot_boxes = [
        {"type": "box", "layout": "vertical", "width": "6px", "height": "6px",
         "cornerRadius": "10px", "backgroundColor": dot_color if i <= dots_on else "#334155",
         "flex": 0, "contents": [{"type": "filler"}]}
        for i in (1, 2, 3)
    ]

    flex_container = {
        "type": "bubble", "size": "micro",
        "styles": {"body": {"backgroundColor": "#0F172A"}},
        "body": {
            "type": "box", "layout": "vertical", "paddingAll": "20px", "spacing": "sm",
            "contents": [
                # 1. TAG PILL — shared with RENDER_PT's per-ticker chip
                # (tag_chip), minus the postback: you're already viewing
                # this tag's own info card.
                {"type": "box", "layout": "horizontal", "margin": "none",
                 "contents": [
                     tag_chip(tag_id, tag, variant="single", lang=lang, action=False),
                     {"type": "filler"},
                 ]},
                # 2. GROUP LABEL
                {"type": "box", "layout": "baseline", "spacing": "xs", "margin": "md",
                 "contents": [
                     {"type": "text", "text": "▎", "size": "xxs", "color": accent, "flex": 0},
                     {"type": "text", "text": group.upper(), "size": "8px", "color": accent,
                      "weight": "bold", "flex": 0, "offsetTop": "-0.6px", "offsetStart": "-2px"},
                 ]},
                # 3. DESC
                {"type": "text", "text": desc, "wrap": True, "size": "xxs",
                 "color": "#CBD5E1", "margin": "xs", "lineSpacing": "1px"},
                # 4. WEIGHT DOTS
                {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "lg",
                 "contents": dot_boxes},
                # 5. READ MORE
                {"type": "box", "layout": "horizontal", "margin": "md",
                 "contents": [
                     {"type": "filler"},
                     {"type": "box", "layout": "horizontal", "flex": 0, "spacing": "xs",
                      "alignItems": "center",
                      "action": {"type": "uri",
                                 "uri": f"https://duply.org/collections/library/finance/{lib_page}#{tag_id}"},
                      "contents": [
                          {"type": "text", "text": "ⓘ", "size": "11px", "color": "#334155", "flex": 0},
                          {"type": "text", "text": "Read More", "size": "10px", "color": "#334155", "flex": 0},
                      ]},
                     {"type": "filler"},
                 ]},
            ],
        },
    }
    return flex_container


# ─────────────────────────────── BF card ───────────────────────────────
# Ported from n8n DIRECTORY_BF (enrich) + RENDER_BF (layout). bf-service
# returns raw pillars/tags/valuation; the enrich step (score->label->color,
# TH translation) lives inline here — same pattern as PT's inline
# analysis-translation in _build_indicator_block, kept out of data_fetcher.

_BF_PILLAR_TH = {"GROWTH": "การเติบโต", "QUALITY": "คุณภาพ",
                 "REALITY": "สภาพคล่อง", "SURVIVAL": "ความมั่นคง"}
_BF_SCORE_TH = {
    "PRIME": "ยอดเยี่ยม", "PROVEN": "พิสูจน์แล้ว", "HEALTHY": "สุขภาพดี",
    "VALIDATED": "เริ่มพิสูจน์", "STABLE": "มั่นคง", "DEVELOPING": "กำลังพัฒนา",
    "WEAK": "อ่อนแอ", "UNPROVEN": "ยังพิสูจน์ไม่ได้", "FRAGILE": "เปราะบาง",
    "NASCENT": "น่าห่วง", "DISTRESSED": "วิกฤต",
}
_BF_VAL_TH = {"FAIR": "แฟร์", "PREMIUM": "พรีเมี่ยม", "DISCOUNT": "ส่วนลด",
              "EXPENSIVE": "แพง", "CHEAP": "ถูก"}


def _bf_safe(val, fallback="-") -> str:
    if val is None or val == "" or val in ("undefined", "NaN"):
        return fallback
    return str(val).strip()


def _bf_score_label(score, model_type) -> str:
    try:
        sc = float(score or 0)
    except (TypeError, ValueError):
        sc = 0.0
    is_early = str(model_type).upper() == "EARLY_GROWTH"
    if sc >= 9.0:
        return "PROVEN" if is_early else "PRIME"
    if sc >= 7.0:
        return "VALIDATED" if is_early else "HEALTHY"
    if sc >= 5.0:
        return "DEVELOPING" if is_early else "STABLE"
    if sc >= 1.0:
        return "UNPROVEN" if is_early else "WEAK"
    return "NASCENT" if is_early else "FRAGILE"


def _bf_score_color(score) -> str:
    try:
        sc = float(score or 0)
    except (TypeError, ValueError):
        sc = 0.0
    if sc >= 9.0:
        return "#04e762"
    if sc >= 7.0:
        return "#80B918"
    if sc >= 5.0:
        return "#68b0ab"
    if sc >= 1.0:
        return "#FF9E00"
    return "#D00000"


def _bf_valuation_color(status: str) -> dict:
    s = _bf_safe(status).upper()
    if s in ("PREMIUM", "EXPENSIVE"):
        return {"bg1": "#F3E8FF", "bg2": "#E9D5FF", "text": "#7E22CE"}
    if s in ("DISCOUNT", "CHEAP"):
        return {"bg1": "#E0F2FE", "bg2": "#BAE6FD", "text": "#0369A1"}
    return {"bg1": "#FFFBEB", "bg2": "#FEF3C7", "text": "#D97706"}


def _bf_theme(model_type: str) -> dict:
    is_early = model_type == "EARLY_GROWTH"
    is_degraded = model_type == "DEGRADED"
    return {
        "bg": "#0F172A" if is_early else "#EFF1F1" if is_degraded else "#FFFFFF",
        "textMain": "#F8FAFC" if is_early else "#1E293B",
        "textSub": "#94A3B8" if is_early else "#64748B",
        "sep": "#334155" if is_early else "#EBEBEA" if is_degraded else "#F1F5F9",
        "box": "#1E293B" if is_early else "#FDFDFD",
        "border": "#334155" if is_early else "#EBEBEA" if is_degraded else "#F1F5F9",
        "valBoxBg": "#1E293B" if is_early else "#FFFFFF" if is_degraded else "#F8FAFC",
        "valLabelColor": "#94A3B8" if is_early else "#64748B",
        "valValueColor": "#F8FAFC" if is_early else "#334155",
        "valSubColor": "#64748B" if is_early else "#94A3B8",
        "is_early": is_early,
    }


def _bf_pillar_box(p: dict, theme: dict, lang: str, th_offset: str) -> dict:
    if not p or not p.get("name"):
        return {"type": "box", "layout": "vertical", "flex": 1}
    name = p["name"]
    display_name = (_BF_PILLAR_TH.get(name, name) if lang == "TH" else name)
    score_label = _bf_score_label(p.get("score"), p.get("_model_type"))
    display_score = (_BF_SCORE_TH.get(score_label, score_label) if lang == "TH" else score_label)
    score_color = _bf_score_color(p.get("score"))
    return {
        "type": "box", "layout": "vertical", "flex": 1,
        "backgroundColor": theme["box"], "paddingAll": "10px",
        "cornerRadius": "10px", "borderColor": theme["border"], "borderWidth": "1px", "height": "90px",
        "contents": [
            {"type": "text", "text": display_name, "size": "xxs", "color": theme["textSub"],
             "weight": "bold", "offsetTop": th_offset},
            {"type": "text", "text": _bf_safe(p.get("metric")), "size": "9px", "color": theme["textSub"], "margin": "xs"},
            {"type": "text", "text": _bf_safe(p.get("value")), "size": "sm", "color": theme["textMain"], "weight": "bold"},
            {"type": "filler"},
            {"type": "text", "text": display_score.upper(), "size": "13px", "weight": "bold",
             "color": score_color, "align": "center", "offsetTop": th_offset},
        ],
    }


def _bf_earning_suffix(item: dict, fiscal_period: str) -> str:
    """Footer earning-status suffix — ` | Qx:Nd` / ` | Qx-Day` / ` | Qx: Updating`
    / ` | Qx: Nd ago`. Ported from RENDER_BF's earning logic."""
    ed = item.get("earningData") or {}
    meta_as_of = (item.get("meta") or {}).get("dataAsOf") or {}
    pending_q = meta_as_of.get("pendingPeriod")
    is_post_earning = meta_as_of.get("isPostEarning")

    last_eps = (ed.get("lastEps") or {}).get("date")
    days_since = None
    if last_eps:
        try:
            days_since = (datetime.now(BKK_TZ).date()
                          - datetime.strptime(last_eps, "%Y-%m-%d").date()).days
        except (ValueError, TypeError):
            days_since = None

    # current quarter -> next quarter label
    try:
        cur_q = int(fiscal_period.replace("Q", "").split("/")[0])
    except (ValueError, IndexError):
        cur_q = 0
    auto_next_q = "Q1" if cur_q == 4 else f"Q{cur_q + 1}"

    if pending_q:
        return f" | {pending_q}: Updating"
    if is_post_earning and days_since is not None and days_since <= 3:
        return f" | {fiscal_period.split('/')[0]}: {days_since}d ago"
    next_date = ed.get("nextDate")
    if next_date:
        try:
            diff = (datetime.strptime(next_date, "%Y-%m-%d").date() - datetime.now(BKK_TZ).date()).days
        except (ValueError, TypeError):
            diff = None
        if diff == 0:
            return f" | {auto_next_q}-Day"
        if diff is not None and diff > 0:
            return f" | {auto_next_q}:{diff}d"
    return ""


def render_bf_card(ticker: str, item: dict, tag_data: dict, in_watchlist: bool, lang: str = "EN") -> dict:
    """Full single-ticker BF bubble — port of RENDER_BF + inline DIRECTORY_BF
    enrich. Reuses tag_chip (single variant), ticker_logo, watchlist_star,
    footer_row + FOOTER_TARGETS['bf'], and the shared engine-time footer
    formatter (_fmt_footer_dt_from_engine) so the footer date matches PT/NS."""
    is_thai = lang == "TH"
    th_offset = "-1px" if is_thai else "0px"
    th_offset_val = "-3px" if is_thai else "0px"

    d = item.get("display", {}) or {}
    valuation = d.get("valuation", {}) or {}
    pillars = list(d.get("pillars", []) or [])
    model_type = (item.get("meta") or {}).get("modelType") or d.get("state") or "STANDARD"
    theme = _bf_theme(model_type)

    # enriched tags (top 2) — tag_chip single variant handles label/color/lang
    raw_tags = (d.get("tags") or [])[:2]
    tag_boxes = [tag_chip(t, tag_data[t], variant="single", lang=lang) for t in raw_tags if tag_data.get(t)]

    logo_ticker = ticker + ".BK"
    company_name = _bf_safe(d.get("companyName"))
    industry_text = _bf_safe(d.get("groupName") or d.get("industry"))
    industry_size = "8px" if len(industry_text) > 23 else "xxs"
    val_theme = _bf_valuation_color(valuation.get("status"))
    val_badge_text = _bf_safe(valuation.get("displayStatus") or valuation.get("status"), "N/A")
    if lang == "TH" and valuation.get("status"):
        val_badge_text = _BF_VAL_TH.get(_bf_safe(valuation.get("status")).upper(), val_badge_text)
    val_label = "มูลค่า" if is_thai else "VALUATION"

    # valuation sub-text: "P/E | Ind. Avg: X | Fwd: Y"
    v_type = re.sub(r" \(.*\)| Ratio", "", _bf_safe(valuation.get("type"))).strip()
    v_bench = _bf_safe(valuation.get("industryAvg")).strip()
    raw_fwd = _bf_safe(valuation.get("forwardVal"))
    v_fwd = ""
    if raw_fwd and "N/A" not in raw_fwd and raw_fwd != "-":
        v_fwd = " | " + re.sub(r"Fwd (P/E|P/S): ", "Fwd: ", raw_fwd).strip()
    valuation_sub = f"{v_type} | {v_bench}{v_fwd}"

    # footer: date-only (matches RENDER_BF's `dateOnly` — with fiscalPeriod +
    # earning suffix the full timestamp makes the footer too long) + earning suffix
    raw_time = item.get("updateTime") or d.get("updateTime") or "-"
    footer_date = (_fmt_footer_dt_from_engine(raw_time) if raw_time != "-" else raw_time).split(" ")[0]
    fiscal_period = _bf_safe(d.get("fiscalPeriod"), "Q-")
    earning_suffix = _bf_earning_suffix(item, fiscal_period)
    footer_text = f"{footer_date} | {fiscal_period}{earning_suffix}"

    for p in pillars:
        p["_model_type"] = model_type

    def beta_tag(v):
        try:
            return "LOW" if float(v) < 1.0 else "HIGH"
        except (TypeError, ValueError):
            return "-"

    body_contents = [
        {"type": "box", "layout": "horizontal", "spacing": "xs",
         "contents": tag_boxes if tag_boxes else [{"type": "filler"}]},
        # header: logo + ticker + star + company
        {"type": "box", "layout": "horizontal", "margin": "lg", "spacing": "md", "alignItems": "center",
         "contents": [
             {"type": "box", "layout": "vertical", "width": "42px", "height": "42px", "cornerRadius": "12px",
              "contents": [ticker_logo(logo_ticker)]},
             {"type": "box", "layout": "vertical", "contents": [
                 {"type": "box", "layout": "horizontal", "alignItems": "flex-start", "spacing": "sm", "contents": [
                     {"type": "text", "text": ticker, "weight": "bold", "size": "xxl",
                      "color": theme["textMain"], "flex": 0},
                     watchlist_star(ticker, in_watchlist, paddingTop="6px"),
                 ]},
                 {"type": "text", "text": company_name, "size": "xxs", "color": theme["textSub"],
                  "wrap": True, "maxLines": 1},
             ]},
         ]},
        # mkt cap / beta / industry
        {"type": "box", "layout": "horizontal", "margin": "md", "contents": [
            {"type": "box", "layout": "vertical", "flex": 1, "alignItems": "center", "spacing": "xs", "contents": [
                {"type": "text", "text": "Mkt Cap", "size": "xxs", "color": theme["textSub"]},
                {"type": "text", "text": _bf_safe(d.get("mktCapVal")), "size": "xxs", "color": theme["textMain"], "weight": "bold"},
                {"type": "box", "layout": "vertical", "backgroundColor": theme["sep"], "cornerRadius": "4px",
                 "paddingStart": "4px", "paddingEnd": "4px",
                 "contents": [{"type": "text", "text": _bf_safe(d.get("mktCapSize")), "size": "9px", "color": theme["textMain"], "weight": "bold"}]},
            ]},
            {"type": "separator", "color": theme["sep"]},
            {"type": "box", "layout": "vertical", "flex": 1, "alignItems": "center", "spacing": "xs", "contents": [
                {"type": "text", "text": "BETA", "size": "xxs", "color": theme["textSub"]},
                {"type": "text", "text": _bf_safe(d.get("betaVal")), "size": "xxs", "color": theme["textMain"], "weight": "bold"},
                {"type": "box", "layout": "vertical", "backgroundColor": theme["sep"], "cornerRadius": "4px",
                 "paddingStart": "4px", "paddingEnd": "4px",
                 "contents": [{"type": "text", "text": beta_tag(d.get("betaVal")), "size": "9px", "color": theme["textMain"], "weight": "bold"}]},
            ]},
            {"type": "separator", "color": theme["sep"]},
            {"type": "box", "layout": "vertical", "flex": 1, "alignItems": "center", "spacing": "xs", "paddingStart": "8px", "contents": [
                {"type": "text", "text": _bf_safe(d.get("groupLabel")), "size": "xxs", "color": theme["textSub"]},
                {"type": "text", "text": industry_text, "size": industry_size, "color": theme["textMain"],
                 "weight": "bold", "wrap": True, "align": "center", "maxLines": 3},
            ]},
        ]},
        # valuation box
        {"type": "box", "layout": "vertical", "margin": "lg", "backgroundColor": theme["valBoxBg"],
         "cornerRadius": "10px", "paddingAll": "12px", "contents": [
            {"type": "box", "layout": "horizontal", "contents": [
                {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": val_label, "size": "xxs", "color": theme["valLabelColor"],
                     "weight": "bold", "offsetTop": th_offset_val},
                    {"type": "text", "text": _bf_safe(valuation.get("value")), "size": "lg", "weight": "bold",
                     "color": theme["valValueColor"], "margin": "xs"},
                    {"type": "text", "text": valuation_sub, "size": "9px", "color": theme["valSubColor"],
                     "margin": "xs", "wrap": True},
                ]},
                {"type": "box", "layout": "vertical", "cornerRadius": "7px", "paddingAll": "4px",
                 "paddingStart": "10px", "paddingEnd": "10px", "position": "absolute", "offsetEnd": "0px",
                 "background": {"type": "linearGradient", "angle": "45deg",
                                "startColor": val_theme["bg1"], "endColor": val_theme["bg2"]},
                 "contents": [{"type": "text", "text": val_badge_text, "size": "xs", "weight": "bold",
                               "color": val_theme["text"], "offsetTop": th_offset}]},
            ]},
        ]},
        # 2x2 pillar grid
        {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "md", "contents": [
            {"type": "box", "layout": "horizontal", "spacing": "md",
             "contents": [_bf_pillar_box(pillars[0] if len(pillars) > 0 else None, theme, lang, th_offset),
                          _bf_pillar_box(pillars[1] if len(pillars) > 1 else None, theme, lang, th_offset)]},
            {"type": "box", "layout": "horizontal", "spacing": "md",
             "contents": [_bf_pillar_box(pillars[2] if len(pillars) > 2 else None, theme, lang, th_offset),
                          _bf_pillar_box(pillars[3] if len(pillars) > 3 else None, theme, lang, th_offset)]},
        ]},
        footer_row(ticker, footer_text=footer_text, **FOOTER_TARGETS["bf"]),
    ]

    return {
        "type": "bubble", "size": "kilo",
        "body": {"type": "box", "layout": "vertical", "backgroundColor": theme["bg"],
                 "paddingAll": "20px", "contents": body_contents},
    }
