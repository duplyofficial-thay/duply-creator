"""
context_builder.py — assembles the LLM context for khun.chat.reply.

Called once per AI-lane turn from reply_flow.py:
    ctx = build_context(duply_id, AGENT_ID)

Returns a dict with:
    system_prompt   str   — persona + agent_profiles.system_prompt blocks
    context_user    str   — formatted user profile
    context_memory  str   — active memory topics (from memory.noter)
    context_market  str   — real-time market data (empty until wired)
    context_history str   — legacy empty string (history via `history` list)
    tools_enabled   list  — from agent_profiles.tools_enabled
    history         list  — {role, content} turns for prompt_builder
    watchlist       list  — raw user watchlist (for card dedup reuse)
    system_lang     str   — UI language (e.g. "TH")

Edit this file to customize how Khun uses user data.
Persona character → edit public.duply_duples.persona in Supabase.
Operational config → edit khun_ai.agent_profiles.system_prompt in Supabase.
"""

import asyncio
import json
import logging
import os
import sys

import redis.asyncio as aioredis

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_DIR, "..", "..", "..", "..", ".."))
_SHARED = os.path.join(_ROOT, "shared")
_PLATFORM = os.path.join(_ROOT, "platform", "chat")
for _p in (_SHARED, _PLATFORM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from agent_prompt_cache import get_agent_prompt, get_duple_persona  # noqa: E402
from redis_contracts import (  # noqa: E402
    USER_HISTORY_KEY_FMT,
    MEMORY_TOPICS_LIVE_KEY_FMT,
)

log = logging.getLogger(__name__)

AGENT_ID = "chat.reply"
DUPLE_ID = os.environ.get("DUPLE_ID", "khun")
REDIS_URL = os.environ.get("PT_REDIS_URL", "redis://localhost:6379/0")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SCHEMA = os.environ.get("SCHEMA_NAME", "khun_ai")


# ─── Redis-backed reads ───────────────────────────────────────────────────────


async def _fetch_memory_topics(r: aioredis.Redis, duply_id: str) -> str:
    key = MEMORY_TOPICS_LIVE_KEY_FMT.format(duple_id=DUPLE_ID, duply_id=duply_id)
    raw = await r.get(key)
    return raw or ""


async def _fetch_history(r: aioredis.Redis, duply_id: str) -> list[dict]:
    key = USER_HISTORY_KEY_FMT.format(duple_id=DUPLE_ID, duply_id=duply_id)
    raw = await r.get(key)
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


# ─── Supabase reads ───────────────────────────────────────────────────────────


def _fetch_user_profile(duply_id: str) -> dict:
    import urllib.request
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {}
    try:
        url = (
            f"{SUPABASE_URL}/rest/v1/user_profiles"
            f"?duply_id=eq.{duply_id}&select=nickname,tier,system_lang,"
            f"knowledge_level,closeness,goal,archetype_data&limit=1"
        )
        req = urllib.request.Request(url)
        req.add_header("apikey", SUPABASE_KEY)
        req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
        req.add_header("Accept-Profile", SCHEMA)
        with urllib.request.urlopen(req, timeout=5) as resp:
            rows = json.loads(resp.read())
            return rows[0] if rows else {}
    except Exception as e:
        log.warning("user_profile fetch failed: %s", e)
        return {}


def _build_context_user(profile: dict) -> str:
    parts = []
    if profile.get("nickname"):
        parts.append(f"Name: {profile['nickname']}")
    if profile.get("tier") and profile["tier"] != "free":
        parts.append(f"Tier: {profile['tier']}")
    if profile.get("knowledge_level"):
        parts.append(f"Knowledge level: {profile['knowledge_level']}")
    if profile.get("closeness"):
        parts.append(f"Closeness: {profile['closeness']:.1f}")
    if profile.get("goal"):
        parts.append(f"Goal: {profile['goal']}")
    return "\n".join(parts)


def _build_system_prompt(agent_blocks: dict, persona: str) -> str:
    parts = []
    if persona:
        parts.append(persona)
    for key, value in (agent_blocks or {}).items():
        if value:
            parts.append(f"[{key.upper()}]\n{value}")
    return "\n\n".join(parts)


# ─── Main build ───────────────────────────────────────────────────────────────


async def build_context_async(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    r = aioredis.from_url(REDIS_URL, decode_responses=True,
                          socket_connect_timeout=3, socket_timeout=3)
    try:
        memory_topics, history_raw = await asyncio.gather(
            _fetch_memory_topics(r, duply_id),
            _fetch_history(r, duply_id),
        )
    finally:
        await r.aclose()

    profile = await asyncio.to_thread(_fetch_user_profile, duply_id)
    agent_prompt = get_agent_prompt(agent_id)
    duple_persona = get_duple_persona(DUPLE_ID)

    watchlist = (profile.get("archetype_data") or {}).get("watchlist") or []

    return {
        "system_prompt": _build_system_prompt(
            agent_prompt.get("system_prompt") or {}, duple_persona
        ),
        "tools_enabled": agent_prompt.get("tools_enabled") or [],
        "context_user": _build_context_user(profile),
        "context_memory": memory_topics,
        "context_market": "",   # wire market data here when ready
        "context_history": "",
        "history": history_raw,
        "watchlist": watchlist,
        "system_lang": profile.get("system_lang") or "TH",
    }


def build_context(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    return asyncio.run(build_context_async(duply_id, agent_id))
