# card/card_primitives.py — stub.
#
# Pure helper functions that build LINE Flex Message JSON fragments.
# No engine-specific logic here — card_renderer.py calls these.
#
# See duples/thay/chat/card/card_primitives.py for the full set of primitives:
#   header_box(title, subtitle, color)    -> flex box dict
#   price_row(label, value, change_pct)   -> flex row dict
#   tag_chip(label, color)                -> flex component
#   footer_row(action_label, action_data) -> flex box dict
#   bubble(header, body, footer)          -> Flex bubble dict
#   carousel(bubbles)                     -> Flex carousel dict
#
# All primitives are pure functions: data in, Flex JSON fragment out.
