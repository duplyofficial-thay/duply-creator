from agent_loop import CardConfig, build_json_shape_hint

# Minimal stub — cards not configured yet.
# When you add card types: extend valid_card_types and ticker_required_card_types.
CARD_CONFIG = CardConfig(
    valid_card_types=frozenset({None}),
    ticker_required_card_types=frozenset(),
    subject_field_name="card_subject",
    fallback_message="ขออภัยครับ ระบบขัดข้อง",
)

REPLY_OUTPUT_PROMPT = (
    f"JSON only, no markdown fence: {build_json_shape_hint(CARD_CONFIG)}\n"
    "card_type: null (plain text reply only — no cards configured yet)."
)

REACH_ALERT_OUTPUT_PROMPT = (
    f"Return a JSON object exactly: {build_json_shape_hint(CARD_CONFIG)}\n"
    "No markdown fence. card_type: null only."
)
