"""
DRAFT — duples/{duple_id}/schedule/schedule_engine.py

New custom domain per guide/05-extending.md §3 ("Custom Domains"): stateless
engine, reads schedules/quest_instances/schedule_nudge_log, writes
schedule_nudge_log, pushes LINE messages. Deliberately NOT built by
repurposing reach.alert — reach_custom_rules/reach_alert_log are hard
finance-shaped (ticker/threshold), and reach_cron.py's documented cadence
is "every 15 min on market days," wrong for bedtime reminders that must
fire every day including weekends. This engine's cron (schedule_cron.py)
runs daily instead — see that file's docstring for the exact crontab ask.

TODO markers below are the platform-tier pieces this repo can't implement
directly (no DB client / LINE push client visible from the creator-kit
repo) — wire these against whatever the platform's shared helpers turn out
to be (likely mirroring however reach_cron.py does it).
"""

from datetime import datetime, timedelta


def get_due_schedule_nudges(now: datetime) -> list[dict]:
    """TODO: SELECT s.id, s.duply_id, s.label, s.message_override
    FROM schedules s
    WHERE s.is_active = true
      AND extract(dow from now) = ANY(s.days_of_week)
      AND s.time_of_day BETWEEN (now - interval '5 minutes')::time AND now()::time
      AND NOT EXISTS (
        SELECT 1 FROM schedule_nudge_log l
        WHERE l.schedule_id = s.id AND l.fired_at::date = now()::date
      )
    -- The 5-minute lookback window matches schedule_cron.py's run interval
    -- (see that file) so a slightly-late cron tick doesn't skip a nudge.
    """
    return []


def get_due_soon_quest_nudges(now: datetime, hours_before_due: int = 2) -> list[dict]:
    """TODO: quests still 'assigned' with due_date = today, where "due soon"
    means within `hours_before_due` of local end-of-day (quests don't have a
    due TIME, only a due DATE — end-of-day is the natural deadline).
    SELECT qi.id, qi.duply_id, qi.title
    FROM quest_instances qi
    WHERE qi.status = 'assigned' AND qi.due_date = CURRENT_DATE
      AND NOT EXISTS (
        SELECT 1 FROM schedule_nudge_log l
        WHERE l.duply_id = qi.duply_id AND l.message LIKE '%' || qi.id || '%'
          AND l.fired_at::date = CURRENT_DATE
      )
    -- Gate this on SCHEDULE.enabled_triggers-equivalent per duple_settings.py's
    -- SCHEDULE block if a creator wants to turn off due-soon nudges specifically
    -- while keeping routine (bedtime/wake) nudges on.
    """
    return []


def compose_nudge_message(label_or_title: str, message_override: str | None, persona_context: dict) -> str:
    """message_override wins if set (creator-authored fixed text via
    set_schedule). Otherwise fall back to a persona-driven default —
    TODO: call the same LLM-authoring path reach.alert already uses for
    its push messages, passing schedule.nudge's agent_profiles.system_prompt
    (coverage/stance/goal/philosophy/examples — see
    ../../prompts/schedule_nudge_system_prompt.json) plus persona_context
    (child's nickname, closeness/bond score) so tone matches chat.reply's.
    """
    if message_override:
        return message_override
    return f"เอ่อ ถึงเวลา {label_or_title} แล้วนะ!"


def fire_nudge(duply_id: str, schedule_id: str | None, message: str) -> None:
    """TODO: push `message` via LINE (platform's push helper — same one
    reach.alert uses), then INSERT INTO schedule_nudge_log
    (schedule_id, duply_id, fired_at, message, status) VALUES (%s, %s, now(), %s, 'sent').
    schedule_id is NULL for due-soon quest nudges (those aren't tied to a
    `schedules` row) — schema allows this only if schedule_id's FK is made
    nullable for that case, or a separate log table is used; flag this
    ambiguity to whoever wires this in."""
    pass


def run_once(now: datetime | None = None) -> int:
    """Entry point called by schedule_cron.py each tick. Returns count of
    nudges fired, for cron log visibility (mirrors reach_cron.py's pattern
    per the guide, though that file isn't visible from this repo)."""
    now = now or datetime.now()
    fired = 0

    for row in get_due_schedule_nudges(now):
        message = compose_nudge_message(row["label"], row.get("message_override"), persona_context={"duply_id": row["duply_id"]})
        fire_nudge(row["duply_id"], row["id"], message)
        fired += 1

    for row in get_due_soon_quest_nudges(now):
        message = compose_nudge_message(row["title"], None, persona_context={"duply_id": row["duply_id"]})
        fire_nudge(row["duply_id"], None, message)
        fired += 1

    return fired
