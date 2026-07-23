"""
context_builder.py — reply-service's own context assembly, replacing its
dependency on n8n's "Master_data" (Thay.chat main workflow) and "Context
Builder" (Thay.ai subflow D) nodes for the AI lane. n8n's fast-lane still
uses Master_data independently — untouched by this module, expected to stay
that way until the fast-lane itself migrates to Python later.

Five data pieces, five different caching rules — see build_context_async().

Deployment note: this service is Per-Duple (currently Thay only), so duple_id/
schema_name are fixed per deployment (env-overridable), not per-request.
"""

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime

import redis.asyncio as aioredis

_DIR = os.path.dirname(os.path.abspath(__file__))
_SHARED_DIR = os.path.normpath(os.path.join(_DIR, "..", "..", "..", "..", "shared"))
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)
# 2026-07-16 reorg: this file moved thay/chat/reply/ -> duples/thay/reply/
# (Thay-specific — Per-Duple context assembly, see
# docs/platform-vs-tenant-taxonomy.md); user_profile.py moved
# thay/chat/context/ -> platform/chat/context/ (Duple-agnostic). No
# longer siblings-of-siblings, so this is a cross-tree lookup now.
_CONTEXT_DIR = os.path.normpath(os.path.join(_DIR, "..", "..", "..", "..", "platform", "chat", "context"))
if _CONTEXT_DIR not in sys.path:
    sys.path.insert(0, _CONTEXT_DIR)
# 2026-07-19: card_config.py owns REPLY_OUTPUT_PROMPT (the "output" system-
# prompt block, moved out of Supabase — see that module's docstring). It's
# a sibling dir (duples/thay/chat/card/), and it in turn imports agent_loop
# (platform/chat/) for CardConfig/build_json_shape_hint, so both need to be
# reachable here too — same cross-tree pattern as _CONTEXT_DIR above.
_CARD_DIR = os.path.normpath(os.path.join(_DIR, "..", "card"))
if _CARD_DIR not in sys.path:
    sys.path.insert(0, _CARD_DIR)
_CHAT_DIR = os.path.normpath(os.path.join(_DIR, "..", "..", "..", "..", "platform", "chat"))
if _CHAT_DIR not in sys.path:
    sys.path.insert(0, _CHAT_DIR)

from redis_contracts import (
    USER_HISTORY_KEY_FMT, MEMORY_TOPICS_LIVE_KEY_FMT, MARKET_CTX_KEY,
)
from agent_prompt_cache import TTLCache
from user_profile import fetch_profile as _fetch_profile_shared
from card_config import REPLY_OUTPUT_PROMPT

log = logging.getLogger(__name__)

REDIS_URL = os.environ.get("PT_REDIS_URL", "redis://localhost:6379/0")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

DUPLE_ID = os.environ.get("DUPLE_ID", "thay")
SCHEMA_NAME = os.environ.get("SCHEMA_NAME", "thay_ai")
AGENT_ID = "chat.reply"  # this deployment's own agent — passed explicitly
                         # into get_agent_prompt(), never hardcoded inside it

PROMPT_CACHE_TTL_SECONDS = 300  # 5 min

# ── Agent prompt: in-memory cache, keyed by agent_id (not Redis anymore) ───
# Cache behavior lives in shared/agent_prompt_cache.py (TTLCache), reused by
# memory.noter/chat.dream too — this module only supplies the fetch_fn.

_prompt_cache: TTLCache = TTLCache(ttl_seconds=PROMPT_CACHE_TTL_SECONDS)


def _supabase_query(path: str, schema: str = SCHEMA_NAME):
    """Synchronous Supabase REST GET. Raises on network/HTTP error — callers
    decide how to handle it (warn+continue for read fallbacks, raise for
    agent_prompt when no cache exists yet)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY not configured")
    req = urllib.request.Request(f"{SUPABASE_URL}{path}")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Accept-Profile", schema)
    req.add_header("Content-Profile", schema)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


def _fetch_agent_prompt(agent_id: str) -> dict:
    rows = _supabase_query(
        f"/rest/v1/agent_profiles?agent_id=eq.{agent_id}&is_active=eq.true"
        f"&select=system_prompt,tools_enabled&limit=1"
    )
    row = rows[0] if rows else {}
    prompt = row.get("system_prompt")
    if not prompt:
        raise ValueError(f"no active agent_profiles row for agent_id={agent_id!r}")
    return {"system_prompt": prompt, "tools_enabled": row.get("tools_enabled")}


def get_agent_prompt(agent_id: str) -> dict:
    """In-memory cache, TTL ~5min, keyed by agent_id. Returns
    {system_prompt, tools_enabled}. tools_enabled is None, [], or a list of
    tool/pack names (pack names expand in registry.get_enabled_tools)."""
    return _prompt_cache.get_or_refresh(agent_id, lambda: _fetch_agent_prompt(agent_id))


_persona_cache: TTLCache = TTLCache(ttl_seconds=PROMPT_CACHE_TTL_SECONDS)


def _fetch_duple_persona(duple_id: str) -> str:
    """public.duply_duples.persona — the one shared prompt block across a
    Duple's agents (2026-07-16, design session part 4: chat.reply and
    reach.alert previously each carried their own hand-authored persona
    text, already drifted after one edit cycle — see
    docs/platform-vs-tenant-taxonomy.md). schema="public" overrides this
    module's default Accept-Profile (thay_ai) — _supabase_query already
    supports this per-call."""
    rows = _supabase_query(
        f"/rest/v1/duply_duples?duple_id=eq.{duple_id}&select=persona&limit=1",
        schema="public",
    )
    return (rows[0].get("persona") or "").strip() if rows else ""


def get_duple_persona(duple_id: str = DUPLE_ID) -> str:
    """In-memory cache, TTL ~5min, keyed by duple_id. Same stale-cache-on-error
    behavior as get_agent_prompt(), except empty string (not an exception) on
    a cold cache with no persona set yet — a missing persona should degrade
    to no persona block, not break the whole prompt build."""
    try:
        return _persona_cache.get_or_refresh(duple_id, lambda: _fetch_duple_persona(duple_id))
    except Exception:
        logging.warning("get_duple_persona: fetch failed for %s, using empty persona", duple_id)
        return ""


# ── Redis-backed reads (async, gathered together per request) ─────────────

async def _fetch_market_ctx(r: aioredis.Redis) -> str:
    """Redis-only, no fallback — owned by the price-feed cron."""
    try:
        raw = await r.get(MARKET_CTX_KEY)
    except Exception as e:
        log.warning("market_ctx redis get failed: %s", e)
        return ""
    if not raw:
        return ""
    try:
        parsed = json.loads(raw)
        return parsed.get("market_ctx", raw) if isinstance(parsed, dict) else str(parsed)
    except (json.JSONDecodeError, TypeError):
        return raw


async def _fetch_memory_topics_live(r: aioredis.Redis, duply_id: str) -> str:
    """Redis-only, no fallback — owned by memory.noter."""
    key = MEMORY_TOPICS_LIVE_KEY_FMT.format(duple_id=DUPLE_ID, duply_id=duply_id)
    try:
        raw = await r.get(key)
    except Exception as e:
        log.warning("memory_topics_live redis get failed for %s: %s", duply_id, e)
        return ""
    if not raw:
        return ""
    try:
        parsed = json.loads(raw)
        return ", ".join(parsed) if isinstance(parsed, list) else str(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def _fetch_history_raw(r: aioredis.Redis, duply_id: str) -> list[dict]:
    """Redis-first, Supabase-fallback (last 40 interact_log rows, trimmed to
    the last 10 turn_ids), warm-write-back with NO TTL — this key is fully
    rewritten by the existing end-of-turn system on every real turn; this
    module's write-back is only a safety net for a cold/missing cache and
    must never add a TTL that system doesn't already set.

    Deviation from Master_data, called out explicitly: Master_data computes
    `trimmed` (last 10 turn_ids) for the Redis write-back, but then formats
    the CURRENT request's own history from the untrimmed 40-row `logs`
    variable — it never reassigns `logs = trimmed`. That means its immediate
    response and what it caches for next time are inconsistent. Here, the
    trimmed set is used for BOTH the response and the write-back, matching
    what the Redis-cache-hit path already effectively returns (only ever the
    trimmed data). This was a deliberate call — flag if the original
    untrimmed-response quirk should be preserved instead."""
    key = USER_HISTORY_KEY_FMT.format(duple_id=DUPLE_ID, duply_id=duply_id)
    raw = None
    try:
        raw = await r.get(key)
    except Exception as e:
        log.warning("history redis get failed for %s: %s", duply_id, e)

    if raw:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            log.warning("history redis value malformed for %s, refetching from supabase", duply_id)

    try:
        rows = await asyncio.to_thread(
            _supabase_query,
            f"/rest/v1/interact_log?duply_id=eq.{duply_id}&order=created_at.desc&limit=40",
        )
        logs = list(reversed(rows)) if isinstance(rows, list) else []
    except Exception as e:
        log.warning("history supabase fallback failed for %s: %s", duply_id, e)
        return []

    if not logs:
        return []

    turn_ids = list(dict.fromkeys(row.get("turn_id") for row in logs))  # unique, first-occurrence order
    recent_turn_ids = set(turn_ids[-10:])
    trimmed = [row for row in logs if row.get("turn_id") in recent_turn_ids]

    try:
        await r.set(key, json.dumps(trimmed))  # no TTL — see docstring
    except Exception as e:
        log.warning("history redis write-back failed for %s: %s", duply_id, e)

    return trimmed


def _parse_created_at_ms(created_at: str) -> float | None:
    if not created_at:
        return None
    try:
        return datetime.fromisoformat(created_at).timestamp() * 1000
    except ValueError:
        return None


def _apply_resume_gaps(logs: list[dict]) -> list[dict]:
    """Ported verbatim from Master_data's 'Build history' step: insert a
    system message whenever consecutive turns are >2h apart."""
    TWO_HOURS_MS = 2 * 60 * 60 * 1000
    history = []
    last_time = None
    for m in logs:
        msg_time = _parse_created_at_ms(m.get("created_at"))
        if last_time is not None and msg_time is not None and (msg_time - last_time) > TWO_HOURS_MS:
            hours = int((msg_time - last_time) // (1000 * 60 * 60))
            history.append({"role": "system", "content": f"[resumed after {hours}h]"})
        history.append({"role": m.get("role"), "content": m.get("content")})
        if msg_time is not None:
            last_time = msg_time
    return history


# ── String assembly, ported from n8n's "Context Builder" node ─────────────

def _section(title: str, value) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    return f"\n# {title}\n{s}" if s else ""


def _build_system_prompt(p: dict, persona: str = "") -> str:
    """persona is now the Duple-level shared block (public.duply_duples.persona,
    see get_duple_persona()), passed in by the caller — not read from p
    anymore. p['persona'] (the old per-agent copy in agent_profiles) is
    intentionally ignored here even if still present in the row; it isn't
    deleted from Supabase (harmless leftover), just no longer consulted.

    Output is REPLY_OUTPUT_PROMPT (card_config.py), not p['output'], as of
    2026-07-19 — it's a description of agent_loop._parse_and_validate()'s
    JSON contract, which a creator editing Supabase can't safely change
    anyway (wrong key names there silently break every reply). Same rule
    already applied to memory.noter/memory.dream/knowledge.extract's
    platform-locked blocks. Old p['output'] rows are harmless leftovers,
    same treatment as p['persona'] above."""
    examples = p.get("examples")
    examples_block = ""
    if isinstance(examples, list) and examples:
        lines = "\n".join(f"User: {e.get('user')}\nThay: {e.get('thay')}" for e in examples)
        examples_block = f"\n# Examples\n{lines}"

    persona_block = str(persona).strip() if persona else ""

    parts = [
        persona_block,
        _section("Bond", p.get("bond")),
        _section("Business", p.get("business")),
        _section("Philosophy", p.get("philosophy")),
        _section("Coverage", p.get("coverage")),
        _section("Tools", p.get("tools")),
        _section("Platform", p.get("platform")),
        _section("Output", REPLY_OUTPUT_PROMPT),
        examples_block,
    ]
    return "\n".join(part for part in parts if part)


def _build_context_user(profile: dict) -> str:
    u = profile or {}
    archetype_data = u.get("archetype_data") or {}

    holdings_raw = archetype_data.get("holdings")
    if isinstance(holdings_raw, list) and holdings_raw:
        mapped = [
            h if isinstance(h, str) else (h.get("ticker") if isinstance(h, dict) else None)
            for h in holdings_raw
        ]
        holdings = ", ".join(filter(None, mapped))
    else:
        holdings = "none"

    watchlist_raw = archetype_data.get("watchlist")
    watchlist = ", ".join(watchlist_raw) if watchlist_raw else "none"

    behavior_tags = (u.get("behavior") or {}).get("tags")
    behavior = ", ".join(behavior_tags) if behavior_tags else "none"

    closeness = u.get("closeness")
    is_number = isinstance(closeness, (int, float)) and not isinstance(closeness, bool)
    bond = f"{closeness:.2f}" if is_number else "0.00"

    nickname = u.get("nickname") or "ไม่ทราบชื่อ"
    chat_lang = u.get("chat_lang") or "TH"
    trading_style = archetype_data.get("trading_style") or "unknown"
    time_horizon = archetype_data.get("time_horizon") or "unknown"
    risk_appetite = archetype_data.get("risk_appetite") or "unknown"
    knowledge_level = u.get("knowledge_level") or "unknown"

    return (
        f"nickname: {nickname} | bond: {bond} | lang: {chat_lang}\n"
        f"style: {trading_style} | horizon: {time_horizon} | risk: {risk_appetite} | level: {knowledge_level}\n"
        f"behavior: {behavior}\n"
        f"holdings: {holdings}\n"
        f"watchlist: {watchlist}"
    )


def _build_context_memory(memory_topics_live: str) -> str:
    live_topics = [t.strip() for t in (memory_topics_live or "").split(",") if t.strip()]
    if not live_topics:
        return ""
    return f"{', '.join(live_topics)}\n→ call get_memories(topic) for details"


def _build_context_market(market_ctx: str) -> str:
    return market_ctx if market_ctx else ""


def _build_context_history(history_annotated: list[dict]) -> str:
    lines = []
    for m in history_annotated:
        role = m.get("role")
        content = m.get("content")
        if role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Thay: {content}")
        else:
            lines.append(f"[{content}]")
    history_text = "\n".join(lines)
    return f"[HISTORY]\n{history_text}" if history_text else ""


# ── Orchestrator ────────────────────────────────────────────────────────

async def build_context_async(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    """Fetch profile/market_ctx/memory_topics_live/history concurrently over
    one Redis connection (fresh per call — avoids reusing an async client
    across event loops when called via asyncio.run() per request), then
    assemble the same 5 strings n8n's Master_data + Context Builder used to
    hand reply-service over HTTP.

    Never writes the current turn's user message or model reply into
    history — that stays owned by the existing end-of-turn system, untouched.
    """
    r = aioredis.from_url(REDIS_URL, decode_responses=True,
                           socket_connect_timeout=3, socket_timeout=3)
    try:
        profile, market_ctx, memory_topics_live, history_raw = await asyncio.gather(
            asyncio.to_thread(_fetch_profile_shared, duply_id),
            _fetch_market_ctx(r),
            _fetch_memory_topics_live(r, duply_id),
            _fetch_history_raw(r, duply_id),
        )
    finally:
        await r.aclose()

    agent_prompt = get_agent_prompt(agent_id)  # {system_prompt, tools_enabled}
    duple_persona = get_duple_persona(DUPLE_ID)  # synchronous, in-memory (or Supabase on cold/expired)
    history_annotated = _apply_resume_gaps(history_raw)

    return {
        "system_prompt": _build_system_prompt(agent_prompt["system_prompt"], duple_persona),
        "tools_enabled": agent_prompt.get("tools_enabled"),
        "context_user": _build_context_user(profile),
        "context_memory": _build_context_memory(memory_topics_live),
        "context_history": _build_context_history(history_annotated),
        "context_market": _build_context_market(market_ctx),
        # Structured history (list of {role, content}, resume-gap markers
        # already applied by _apply_resume_gaps) — the source of truth
        # context_history's string is rendered FROM. Callers that need to
        # reason about individual turns (e.g. card/dedup.py, which can't
        # parse that back out of a flattened string) should use this, not
        # re-derive it. Matches n8n's ctx.history shape (list of
        # {role, content}), not a Python invention.
        "history": history_annotated,
        # Raw fields (not formatted-string context) for callers that need to
        # render a card off the same profile fetch — e.g. reply_flow.py's
        # AI lane, which must NOT call user_profile.card_user_ctx() again for
        # the same turn (see that module's DOUBLE-FETCH GUARDRAIL docstring).
        # system_lang (card/UI language) is distinct from chat_lang (AI
        # persona language, already folded into context_user) — do not swap.
        "watchlist": (profile.get("archetype_data") or {}).get("watchlist") or [],
        "system_lang": profile.get("system_lang") or "EN",
    }


def build_context(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    """Synchronous entry point for reply_service.py's stdlib http.server
    handler (not asyncio-based) — wraps the async gather in its own fresh
    event loop per call."""
    return asyncio.run(build_context_async(duply_id, agent_id))
