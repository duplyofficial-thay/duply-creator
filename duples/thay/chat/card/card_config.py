"""
duples/thay/chat/card/card_config.py — Thay's card vocabulary, the
Duple-owned data agent_loop.py needs to validate/describe card output in
its LLM contract.

Phase 5-A of squishy-marinating-moore.md: agent_loop.py used to hardcode
these values as module-level constants (VALID_CARD_TYPES,
TICKER_REQUIRED_CARD_TYPES, FALLBACK_RESPONSE) — one of the "leaks in
things billed as generic" the platform-vs-tenant-taxonomy research found.
Platform code now defines the CardConfig shape (agent_loop.CardConfig);
only the Duple owns the actual values.

This is a single instance, not an archetype/Duple-keyed registry —
deliberately deferred until a second card-bearing Duple (Grace) exists to
prove out whether card vocabularies are archetype-level or duple-level.
Guessing that now would repeat the mistake the plan explicitly avoided for
lifestyle's ArchetypeConfig content. See squishy-marinating-moore.md
Phase 5-A / Phase 5-C.

Exported as CARD_CONFIG (not THAY_CARD_CONFIG) — matches the convention
already used by context_builder.py's AGENT_ID/build_context: the directory
a caller resolves onto sys.path (via DUPLE_ID) disambiguates which Duple's
module got imported, so the symbol name itself doesn't need a Duple prefix
(Phase 5-A½, squishy-marinating-moore.md).

2026-07-19: also owns the "output" prompt block for chat.reply
(REPLY_OUTPUT_PROMPT) and reach.alert (REACH_ALERT_OUTPUT_PROMPT) — moved
out of Supabase agent_profiles.system_prompt, same rule already applied to
memory.noter/memory.dream/knowledge.extract's platform-locked blocks: if a
Python parser depends on the exact text (here, _parse_and_validate()'s JSON
keys), it's code, not a creator-editable block. Every card-type semantic
and the "up to 5 tickers" convention below is a direct description of
card/data_fetcher.py's resolve_target() branches (real code behavior, not
persona/business content) — verified against that file before moving.

reach.alert shares this SAME CARD_CONFIG (2026-07-19, revised same day —
an earlier pass here gave it its own narrower REACH_ALERT_CARD_CONFIG,
{None, "pt"} only, reasoning that reach's prompt only ever taught pt|null
so the validator shouldn't accept more. Reverted after owner input: reach's
near-term roadmap adds alert rules (market-condition, news) that map onto
card types already in this same set (mc/st for market condition, mc_ns/ns
for news) — maintaining a second CardConfig would mean widening it again,
piecemeal, for every new alert rule, which is exactly the
two-places-to-keep-in-sync problem this file exists to avoid. One shared
object means when those alert rules ship, only REACH_ALERT_OUTPUT_PROMPT's
text needs updating — no code/validator change.

This does mean the validator currently accepts more than reach.alert's
prompt text teaches (bf/ns/mc/mc_ns/st/theme have no real alert-rule use
case yet) — a deliberate, documented gap, not the accidental one from
before: REACH_ALERT_OUTPUT_PROMPT says outright which values are reserved
for not-yet-built alert rules. Risk is low (temperature=0, and the model
has no reason to reach for an unexplained enum value), and the failure
mode if it ever did is a mildly-wrong-but-still-legitimate card attached to
a push, not a crash or bad data.

The multi-ticker cap in both OUTPUT_PROMPTs below (PT_COMPARE_MAX_TICKERS)
is imported from data_fetcher.py, not a second hardcoded "5" — that number
is only real where data_fetcher.resolve_target() slices the ticker list;
a prose copy that drifted from it would tell the LLM a cap that isn't the
one actually enforced.
"""

from agent_loop import CardConfig, build_json_shape_hint
from data_fetcher import PT_COMPARE_MAX_TICKERS

CARD_CONFIG = CardConfig(
    valid_card_types=frozenset({None, "pt", "bf", "ns", "mc", "mc_ns", "st", "wl", "theme"}),
    # Card types whose card_ticker field carries real data: pt/bf/ns = stock
    # ticker, theme = theme keyword. wl/st/mc/mc_ns are ticker-less (rendered
    # from watchlist/SECTOR_ORDER/MACRO_ETFS — see card/data_fetcher.resolve_target).
    ticker_required_card_types=frozenset({"pt", "bf", "ns", "theme"}),
    # The JSON key Thay's LLM uses for that ticker/theme string. Kept as
    # "card_ticker" — Thay's live system prompt (agent_profiles) already
    # teaches this exact key via real examples; changing it would need a
    # prompt retune for zero benefit to Thay. A future Duple whose cards
    # aren't ticker-shaped sets its own word here instead.
    subject_field_name="card_ticker",
    fallback_message="ขออภัยครับ ระบบขัดข้อง",
)

REPLY_OUTPUT_PROMPT = (
    f"JSON only, no markdown fence: {build_json_shape_hint(CARD_CONFIG)}\n"
    "card types: pt/bf/ns=stock, st=sectors, mc=macro overview, mc_ns=macro news, "
    "wl=watchlist. For pt, card_ticker may be a comma-separated list of up to "
    f'{PT_COMPARE_MAX_TICKERS} tickers (e.g. "NVDA,AMD,TSM") to show a '
    "side-by-side compare card when the user asks to compare multiple stocks "
    "technically; single ticker shows the full single-stock card. card_type: "
    "null by default."
)

REACH_ALERT_OUTPUT_PROMPT = (
    f"Return a JSON object exactly: {build_json_shape_hint(CARD_CONFIG)}\n"
    'No markdown fence (no ```json) — raw JSON only. Today, only ever choose '
    '"pt" or "wl" — the other card_type values in the schema above are '
    "reserved for alert rules that don't exist yet (market-condition/news "
    "alerts, coming later); do not use them until told otherwise.\n"
    'If ONE ticker moved and the user tracks it, attach a pt card '
    '(card_type="pt", card_ticker="SYMBOL"). If several tickers moved '
    'together, card_ticker may instead be a comma-separated list (e.g. '
    f'"NVDA,AMD,TSM", up to {PT_COMPARE_MAX_TICKERS}) for a side-by-side '
    'compare card — or attach a wl card (card_type="wl", card_ticker=null) '
    "to show the user's full watchlist instead. Otherwise, no card "
    "(card_type=null, card_ticker=null)."
)
