"""
hooks.py — tawan reach triggers.

Add EVENT_TRIGGERS (subclass EventTrigger from reach_engine) for
event-based pushes, or SCHEDULE_TRIGGERS (ScheduleTrigger) for
time-based recurring pushes. Both lists are empty by default.
"""

EVENT_TRIGGERS = []
SCHEDULE_TRIGGERS = []


def generate_message(duply_id, fires, profile, system_lang):
    """Called by reach_engine._deliver when fires have no pre-built messages.
    Return (list[str], card_dict|None) or (None, None) on failure.
    Import LLM helpers from reach_engine or implement inline."""
    return None, None


def fallback_message(fires):
    """Cheap no-LLM text for capped/quiet-hours logging. Never pushed."""
    return ["\U0001f514"]
