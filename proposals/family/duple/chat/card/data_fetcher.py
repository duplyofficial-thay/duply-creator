"""
DRAFT — duples/{duple_id}/chat/card/data_fetcher.py for the family archetype.

Each function below is the data-access half of one card type. The actual
DB client (however the platform wraps Postgres access — not visible from
this creator-kit repo) needs to be wired in by whoever implements this
against the real schema; the TODO comment in each function states exactly
what to query. The return shapes are the CONTRACT card_renderer.py expects
— keep them stable even if the query implementation changes later.
"""

from datetime import date


def fetch_quests(duply_id: str) -> list[dict]:
    """TODO: SELECT id, title, xp_reward, coin_reward, status, due_date
    FROM quest_instances WHERE duply_id = %s AND due_date = CURRENT_DATE
    ORDER BY status, created_at."""
    return [
        {"id": "placeholder", "title": "เก็บของเล่นเข้าที่", "xp_reward": 10,
         "coin_reward": 10, "status": "assigned", "due_date": date.today().isoformat()},
    ]


def fetch_wallet(duply_id: str) -> dict:
    """TODO: SELECT coin_balance, total_xp, level FROM wallets WHERE duply_id = %s."""
    return {"coin_balance": 0, "total_xp": 0, "level": 1}


def fetch_leaderboard(duply_id: str, scope: str, limit: int = 20) -> list[dict]:
    """TODO:
    scope="global": SELECT w.duply_id, up.nickname, w.total_xp, w.level
      FROM wallets w JOIN user_profiles up ON up.duply_id = w.duply_id
      ORDER BY w.total_xp DESC LIMIT %s.
    scope="family": same, plus JOIN family_members fm ON fm.duply_id = w.duply_id
      WHERE fm.guild_id = (SELECT guild_id FROM family_members WHERE duply_id = %s).

    IMPORTANT: nickname only, never real name/photo, on the GLOBAL scope —
    see the plan's privacy note (global leaderboard exposes activity across
    unrelated families)."""
    return []


def fetch_family_members(duply_id: str) -> dict:
    """TODO: resolve the caller's guild_id via family_members, then
    SELECT fm.duply_id, fm.role, up.nickname, w.total_xp, w.level,
      (SELECT count(*) FROM quest_instances qi WHERE qi.duply_id = fm.duply_id
       AND qi.due_date = CURRENT_DATE AND qi.status = 'approved') AS done_today
    FROM family_members fm
    JOIN user_profiles up ON up.duply_id = fm.duply_id
    JOIN wallets w ON w.duply_id = fm.duply_id
    WHERE fm.guild_id = <resolved guild_id>."""
    return {"guild_name": "", "members": []}


def fetch_rewards(guild_id: str) -> list[dict]:
    """TODO: SELECT id, title, cost_coins FROM reward_catalog
    WHERE guild_id = %s AND is_active = true ORDER BY cost_coins."""
    return []
