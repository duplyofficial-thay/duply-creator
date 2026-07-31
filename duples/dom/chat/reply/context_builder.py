"""
context_builder.py — assembles the LLM context for dom.chat.reply.

Called once per AI-lane turn from reply_flow.py:
    ctx = build_context(duply_id, AGENT_ID)

Returns a dict with:
    system_prompt   str   — persona + agent_profiles.system_prompt blocks
    context_user    str   — formatted user profile
    context_memory  str   — active memory topics (from memory.noter)
    context_market  str   — real-time market data (empty until wired)
    context_history str   — empty string (history travels via `history` list)
    tools_enabled   list  — from agent_profiles.tools_enabled
    history         list  — {role, content} turns for prompt_builder
    watchlist       list  — [] by default; extend in this file if needed
    system_lang     str   — UI language (e.g. "TH")

Edit this file to customize how Dom uses user data.
Persona character → edit public.duply_duples.persona in Supabase.
Operational config → edit dom_ai.agent_profiles.system_prompt in Supabase.
"""

import asyncio
import json
import logging
import os
import sys
import urllib.request

import redis.asyncio as aioredis

_DIR = os.path.dirname(os.path.abspath(__file__))
# 4 levels up: reply/ → chat/ → dom/ → duples/ → repo root (duply-agents/)
_REPO_ROOT = os.path.normpath(os.path.join(_DIR, "..", "..", "..", ".."))
_SHARED = os.path.join(_REPO_ROOT, "shared")
for _p in (_SHARED,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from agent_prompt_cache import TTLCache  # noqa: E402
from redis_contracts import (  # noqa: E402
    USER_HISTORY_KEY_FMT,
    MEMORY_TOPICS_LIVE_KEY_FMT,
)

log = logging.getLogger(__name__)

AGENT_ID = "chat.reply"
DUPLE_ID = os.environ["DUPLE_ID"]
REDIS_URL = os.environ.get("PT_REDIS_URL", "redis://localhost:6379/0")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SCHEMA = os.environ["SCHEMA_NAME"]

_PROMPT_TTL = 300  # 5 min — matches Thay


# ─── Supabase helper ─────────────────────────────────────────────────────────


def _supabase_get(path: str, schema: str = SCHEMA) -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY not configured")
    req = urllib.request.Request(f"{SUPABASE_URL}{path}")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Accept-Profile", schema)
    req.add_header("Content-Profile", schema)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


# ─── Agent prompt cache (TTL ~5 min, in-memory) ──────────────────────────────

_prompt_cache: TTLCache = TTLCache(ttl_seconds=_PROMPT_TTL)
_persona_cache: TTLCache = TTLCache(ttl_seconds=_PROMPT_TTL)


def _fetch_agent_prompt(agent_id: str) -> dict:
    rows = _supabase_get(
        f"/rest/v1/agent_profiles?agent_id=eq.{agent_id}&is_active=eq.true"
        f"&select=system_prompt,tools_enabled&limit=1"
    )
    row = rows[0] if rows else {}
    if not row.get("system_prompt"):
        raise ValueError(f"no active agent_profiles row for {agent_id!r}")
    return {"system_prompt": row["system_prompt"], "tools_enabled": row.get("tools_enabled")}


def get_agent_prompt(agent_id: str) -> dict:
    return _prompt_cache.get_or_refresh(agent_id, lambda: _fetch_agent_prompt(agent_id))


def _fetch_duple_persona(duple_id: str) -> str:
    rows = _supabase_get(
        f"/rest/v1/duply_duples?duple_id=eq.{duple_id}&select=persona&limit=1",
        schema="public",
    )
    persona = (rows[0].get("persona") or "") if rows else ""
    return persona.strip() if isinstance(persona, str) else ""


def get_duple_persona(duple_id: str = DUPLE_ID) -> str:
    try:
        return _persona_cache.get_or_refresh(duple_id, lambda: _fetch_duple_persona(duple_id))
    except Exception:
        log.warning("get_duple_persona failed for %s, using empty persona", duple_id)
        return ""


# ─── Redis-backed reads ───────────────────────────────────────────────────────


async def _fetch_memory_topics(r: aioredis.Redis, duply_id: str) -> str:
    key = MEMORY_TOPICS_LIVE_KEY_FMT.format(duple_id=DUPLE_ID, duply_id=duply_id)
    try:
        raw = await r.get(key)
    except Exception as e:
        log.warning("memory_topics redis get failed: %s", e)
        return ""
    if not raw:
        return ""
    try:
        parsed = json.loads(raw)
        return ", ".join(parsed) if isinstance(parsed, list) else str(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def _fetch_history(r: aioredis.Redis, duply_id: str) -> list:
    key = USER_HISTORY_KEY_FMT.format(duple_id=DUPLE_ID, duply_id=duply_id)
    try:
        raw = await r.get(key)
    except Exception as e:
        log.warning("history redis get failed: %s", e)
        return []
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


# ─── User profile ─────────────────────────────────────────────────────────────


def _fetch_user_profile(duply_id: str) -> dict:
    try:
        rows = _supabase_get(
            f"/rest/v1/user_profiles"
            f"?duply_id=eq.{duply_id}"
            f"&select=nickname,tier,system_lang,knowledge_level,closeness,goal"
            f"&limit=1"
        )
        return rows[0] if rows else {}
    except Exception as e:
        log.warning("user_profile fetch failed for %s: %s", duply_id, e)
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

    return {
        "system_prompt": _build_system_prompt(
            agent_prompt.get("system_prompt") or {}, duple_persona
        ),
        "tools_enabled": agent_prompt.get("tools_enabled") or [],
        "context_user": _build_context_user(profile),
        "context_memory": memory_topics,
        "context_market": "",   # TODO: wire real-time context here (price, events, etc.)
        "context_history": "",
        "history": history_raw,
        "watchlist": [],        # TODO: fetch from profile if your Duple needs it
        "system_lang": profile.get("system_lang") or "TH",
    }


def build_context(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    return asyncio.run(build_context_async(duply_id, agent_id))
