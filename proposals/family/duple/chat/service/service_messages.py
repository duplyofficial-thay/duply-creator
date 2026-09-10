"""
DRAFT — duples/dom/chat/service/service_messages.py

New SERVICE-lane wording file per the 2026-07-28 platform update
(v0.3.0, commit 23376f1) — render_service_messages(result) turns a
run_service() result dict into user-facing LINE message strings.

Only LANG_UPDATE is wired in router_config.yaml's service_routes for this
Duple (see that file's comments on why PROFILE_UPDATE was omitted, and the
open question on whether quest-approval postback actions belong here too).
Wording kept in Dom's voice: brief, calm, no exclamation-mark enthusiasm.
"""


def render_service_messages(result: dict) -> list[str]:
    if result.get("status") != "ok":
        return ["ตอนนี้ทำไม่ได้ ลองใหม่อีกทีนะ"]

    action = result.get("action")

    if action == "LANG_UPDATE":
        lang = result.get("system_lang")
        if lang == "TH":
            return ["โอเค คุยไทยต่อนะ"]
        if lang == "EN":
            return ["Alright, switching to English."]
        return ["เปลี่ยนภาษาเรียบร้อย"]

    return ["เรียบร้อย"]
