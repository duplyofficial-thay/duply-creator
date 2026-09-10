"""
DRAFT — duples/{duple_id}/schedule/schedule_cron.py

Entry point for the new schedule.nudge domain. Ask for the Duply team (per
guide/05-extending.md §3's "what to tell the team" checklist):
  - service type: cron (not webhook/on-demand)
  - schedule: every 5 minutes, EVERY day (not "market days only" — that's
    reach_cron.py's cadence, wrong for bedtime/routine reminders which need
    weekends too)
  - new env vars: none beyond what every duple already has in .env
  - new tables: schedules, schedule_nudge_log (see ../../schema/family_block.sql)

Crontab line shape (mirroring guide/03-domains.md's reach_cron example, but
every 5 min / every day instead of market-hours slots):
  */5 * * * *  set -a; . /home/duply/duply-agents/.env; . /home/duply/duply-agents/duples/{duple_id}/.env; set +a; /usr/bin/python3 /home/duply/duply-agents/duples/{duple_id}/schedule/schedule_cron.py >> /home/duply/duply-agents/duples/{duple_id}/schedule/schedule_{duple_id}.log 2>&1
"""

import logging

from schedule_engine import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("schedule_cron")


def main() -> None:
    fired = run_once()
    logger.info("schedule_cron: fired %d nudge(s)", fired)


if __name__ == "__main__":
    main()
