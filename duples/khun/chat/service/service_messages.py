"""
service_messages.py — Khun per-Duple wording for SERVICE lane confirmations.

render_service_messages(result) takes the dict returned by run_service()
and returns a list of user-facing strings to send back on LINE.

Future: move wording to Supabase (agent_profiles) for live editing.
"""


def render_service_messages(result: dict) -> list[str]:
    if result.get("status") != "ok":
        return ["ขออภัยครับ ไม่สามารถดำเนินการได้ในขณะนี้"]

    action = result.get("action")

    if action == "PROFILE_UPDATE":
        op = result.get("op")
        n = result.get("count", 0)
        mx = result.get("max", 5)
        lines = []

        if op == "add":
            added = result.get("added") or []
            skipped = result.get("skipped") or []
            rejected = result.get("rejected") or []
            if added:
                lines.append(f"เพิ่ม {', '.join(added)} เรียบร้อยครับ ({n}/{mx})")
            if skipped:
                lines.append(f"{', '.join(skipped)} มีอยู่ใน Watchlist อยู่แล้วครับ")
            if rejected:
                lines.append(f"ไม่สามารถเพิ่ม {', '.join(rejected)} ได้ครับ "
                             f"Watchlist เต็มแล้ว (สูงสุด {mx} ตัว)")

        elif op == "remove":
            removed = result.get("removed") or []
            not_found = result.get("not_found") or []
            if removed:
                lines.append(f"ลบ {', '.join(removed)} เรียบร้อยครับ (เหลือ {n}/{mx})")
            if not_found:
                lines.append(f"{', '.join(not_found)} ไม่อยู่ใน Watchlist ครับ")

        return ["\n".join(lines)] if lines else ["ดำเนินการเรียบร้อยครับ"]

    if action == "LANG_UPDATE":
        lang = result.get("system_lang", "TH")
        return ["ตั้งค่าเป็นภาษาไทยเรียบร้อยครับ" if lang == "TH"
                else "Language set to English."]

    if action == "WATCHLIST_GET":
        wl = result.get("watchlist") or []
        n = result.get("watchlist_count", 0)
        mx = result.get("max", 5)
        if not wl:
            return [f"Watchlist ยังว่างอยู่ครับ (0/{mx})"]
        return [f"Watchlist ตอนนี้: {', '.join(wl)} ({n}/{mx})"]

    return ["ดำเนินการเรียบร้อยครับ"]
