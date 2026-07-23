#!/usr/bin/env python3
"""
provision_duple.py — Provision a new Duple: schema, role, tables, seed data, scaffold.

Usage (run from duply-creator/):
    python scripts/provision_duple.py <duple_id>
    python scripts/provision_duple.py <duple_id> --supabase-dir /path/to/duply-astro

Prerequisites:
    - supabase CLI logged in + linked (in --supabase-dir, default: ../duply-astro)
    - pyyaml installed: pip install pyyaml
    - register/{duple_id}.yaml filled out
"""

from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml  # pip install pyyaml

# ─── Paths ───────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
CREATOR_DIR = SCRIPT_DIR.parent
REGISTER_DIR = CREATOR_DIR / "register"
SCHEMA_TEMPLATE = SCRIPT_DIR / "schema_template.sql"
ENV_EXAMPLE_SRC = CREATOR_DIR / "duples" / ".env.example"
DEFAULT_SUPABASE_DIR = CREATOR_DIR.parent / "duply-astro"

# ─── Agent seed configuration ─────────────────────────────────────────────────

_AGENTS = [
    "chat.reply",
    "memory.dream",
    "memory.noter",
    "reach.alert",
    "knowledge.extract",
]

_TOOLS: dict[str, dict[str, list[str]]] = {
    "finance": {
        # finance.us / finance.set NOT included by default — team adds the right
        # market pack after provisioning based on the Duple's actual market focus.
        "chat.reply":        ["generic", "finance.generic"],
        "reach.alert":       ["generic", "finance.generic"],
        "memory.noter":      [],
        "memory.dream":      [],
        "knowledge.extract": ["generic"],
    },
    "lifestyle": {
        "chat.reply":        ["generic"],
        "reach.alert":       [],
        "memory.noter":      [],
        "memory.dream":      [],
        "knowledge.extract": ["generic"],
    },
    "commerce": {
        "chat.reply":        ["generic"],
        "reach.alert":       [],
        "memory.noter":      [],
        "memory.dream":      [],
        "knowledge.extract": ["generic"],
    },
}

# Default system_prompt templates — enough for the agent to run without crashing.
# Keys must match exactly what each agent's code reads. Team fills real content in Supabase.
# chat.reply: _build_system_prompt() reads bond, business, philosophy, coverage, tools,
#             platform, examples (list); "output" is code-locked — never put it here.
# reach.alert: reads coverage, stance, goal, philosophy, examples (list);
#              "output" is code-locked — never put it here.
_DEFAULT_PROMPTS: dict[str, dict] = {
    "chat.reply": {
        "philosophy": (
            "Be helpful, warm, and genuine. Match your persona's character. "
            "Don't lecture or add unnecessary caveats."
        ),
        "platform": (
            "You chat via LINE. Keep replies conversational and concise. "
            "Use line breaks for readability, not markdown headers."
        ),
        "tools": (
            "Use tools when you need current data. "
            "Call tools before answering questions about real-time information."
        ),
        "coverage": (
            "Focus on topics within your Duple's domain. "
            "Engage naturally on other topics but stay honest about your expertise."
        ),
        "bond": (
            "Match your tone to the user's closeness level. "
            "Warmer and more casual as the relationship grows."
        ),
        "business": "",
        "examples": [],
    },
    "reach.alert": {
        "coverage": "Send alerts about assets the user is tracking.",
        "stance": "Factual and concise. No recommendations, no speculation.",
        "goal": "Keep the user informed about significant price movements in their watchlist.",
        "philosophy": "Be direct and informative. State what triggered and why it matters.",
        "examples": [],
    },
    "memory.noter":      {"note": "Configure extraction rules in Supabase."},
    "memory.dream":      {"note": "Configure consolidation rules in Supabase."},
    "knowledge.extract": {"note": "Configure knowledge extraction rules in Supabase."},
}

# ─── SQL helpers ─────────────────────────────────────────────────────────────


def run_sql(sql: str, supabase_dir: Path) -> str:
    """Run SQL via supabase CLI (temp file → -f flag). Returns raw stdout."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
        f.write(sql)
        tmp = f.name
    try:
        result = subprocess.run(
            ["supabase", "db", "query", "--linked", "-f", tmp],
            cwd=supabase_dir,
            capture_output=True,
            text=True,
        )
    finally:
        os.unlink(tmp)
    if result.returncode != 0:
        raise RuntimeError(f"SQL failed:\n{result.stderr.strip()}")
    return result.stdout


def run_sql_rows(sql: str, supabase_dir: Path) -> list[dict]:
    """Run SQL and return parsed rows from the JSON output."""
    out = run_sql(sql, supabase_dir)
    try:
        data = json.loads(out)
        return data.get("rows", [])
    except (json.JSONDecodeError, AttributeError):
        return []


def sq(value: str) -> str:
    """Escape a string for SQL single-quote safety."""
    return value.replace("'", "''")


# ─── Provision ───────────────────────────────────────────────────────────────


def provision(duple_id: str, supabase_dir: Path) -> None:
    # 0. Validate duple_id format
    if not re.match(r"^[a-z][a-z0-9_]{1,29}$", duple_id):
        _die("duple_id must be 2–30 chars: lowercase letters, digits, underscores; start with a letter.")

    # 1. Parse + validate YAML
    reg_file = REGISTER_DIR / f"{duple_id}.yaml"
    if not reg_file.exists():
        _die(f"register/{duple_id}.yaml not found.")

    with open(reg_file) as f:
        cfg = yaml.safe_load(f)

    for field in ("duple_id", "archetype", "owner", "description", "persona"):
        if not cfg.get(field):
            _die(f"Missing required field in YAML: {field}")

    if cfg["duple_id"] != duple_id:
        _die(f"duple_id in YAML ({cfg['duple_id']!r}) must match filename ({duple_id!r}).")

    archetype = cfg["archetype"]
    if archetype not in ("finance", "lifestyle", "commerce"):
        _die(f"archetype must be finance | lifestyle | commerce, got: {archetype!r}")

    persona = cfg["persona"]
    if not isinstance(persona, dict) or not persona.get("name"):
        _die("persona must be a mapping with at least a 'name' key.")

    schema = f"{duple_id}_ai"
    role = f"{duple_id}_role"
    password = secrets.token_urlsafe(32)

    print(f"\n=== Provisioning {duple_id} ===")
    print(f"Schema: {schema}   Role: {role}   Archetype: {archetype}\n")

    # 2. Conflict check
    _step("Checking for conflicts")
    rows = run_sql_rows(
        f"SELECT COUNT(*)::int AS n FROM information_schema.schemata "
        f"WHERE schema_name = '{sq(schema)}';",
        supabase_dir,
    )
    if int((rows[0] if rows else {}).get("n", 0)) > 0:
        _die(f"Schema '{schema}' already exists.")

    rows = run_sql_rows(
        f"SELECT COUNT(*)::int AS n FROM pg_roles WHERE rolname = '{sq(role)}';",
        supabase_dir,
    )
    if int((rows[0] if rows else {}).get("n", 0)) > 0:
        _die(f"Role '{role}' already exists.")

    # 3. Create schema + role + grants
    _step("Creating schema and role")
    run_sql(f"CREATE SCHEMA {schema};", supabase_dir)
    run_sql(
        f"CREATE ROLE {role} WITH LOGIN PASSWORD '{password}' "
        f"NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;",
        supabase_dir,
    )
    run_sql(f"GRANT USAGE ON SCHEMA {schema} TO {role};", supabase_dir)
    run_sql(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role};",
        supabase_dir,
    )

    # 4. Create tables from template
    _step("Creating tables")
    sql = SCHEMA_TEMPLATE.read_text()
    sql = sql.replace("__SCHEMA__", schema).replace("__DUPLE_ID__", duple_id)

    if archetype != "finance":
        lines, in_block = [], False
        for line in sql.splitlines():
            if "-- BEGIN FINANCE" in line:
                in_block = True
            elif "-- END FINANCE" in line:
                in_block = False
            elif not in_block:
                lines.append(line)
        sql = "\n".join(lines)

    run_sql(sql, supabase_dir)

    # 5. Seed public.duply_duples
    _step("Seeding public.duply_duples")
    # persona column is TEXT — store the description string only, matching
    # how Thay's persona is stored (plain prose, not JSON blob).
    persona_text = sq(persona.get("description", "").strip())
    run_sql(
        f"INSERT INTO public.duply_duples "
        f"  (duple_id, schema_name, name, archetype, description, persona, is_active) "
        f"VALUES "
        f"  ('{sq(duple_id)}', '{schema}', '{sq(persona['name'])}', "
        f"   '{sq(archetype)}', '{sq(cfg['description'])}', "
        f"   '{persona_text}', true) "
        f"ON CONFLICT (duple_id) DO NOTHING;",
        supabase_dir,
    )

    # 6. Seed agent_profiles
    _step("Seeding agent_profiles")
    tools_map = _TOOLS.get(archetype, _TOOLS["lifestyle"])

    for agent_id in _AGENTS:
        domain, function = agent_id.split(".", 1)
        tools = tools_map.get(agent_id, [])
        prompt = _DEFAULT_PROMPTS.get(agent_id, {"note": "Configure in Supabase."})
        prompt_json = sq(json.dumps(prompt, ensure_ascii=False))
        run_sql(
            f"INSERT INTO {schema}.agent_profiles "
            f"  (agent_id, duple, domain, function, system_prompt, "
            f"   is_active, uses_tools, tools_enabled, status) "
            f"VALUES "
            f"  ('{sq(agent_id)}', '{sq(duple_id)}', '{sq(domain)}', '{sq(function)}', "
            f"   '{prompt_json}'::jsonb, true, {str(bool(tools)).lower()}, "
            f"   '{sq(json.dumps(tools))}'::jsonb, 'active');",
            supabase_dir,
        )

    # 7. Verify isolation
    _step("Verifying isolation")
    rows = run_sql_rows(
        f"SELECT has_schema_privilege('{sq(role)}', '{schema}', 'USAGE') AS own;",
        supabase_dir,
    )
    own_ok = bool((rows[0] if rows else {}).get("own", False))
    _check(own_ok, expect_true=True, label=f"{role} has USAGE on {schema}")

    rows = run_sql_rows(
        f"SELECT has_schema_privilege('{sq(role)}', 'thay_ai', 'USAGE') AS other;",
        supabase_dir,
    )
    other_ok = bool((rows[0] if rows else {}).get("other", False))
    _check(other_ok, expect_true=False, label=f"{role} is isolated from thay_ai")

    # 8. Generate scaffold
    _step("Generating scaffold")
    _generate_scaffold(duple_id, archetype, cfg)

    # 9. Print credentials
    _print_credentials(duple_id, schema, role, password, persona["name"], cfg["owner"])


# ─── Scaffold generator ──────────────────────────────────────────────────────


def _generate_scaffold(duple_id: str, archetype: str, cfg: dict) -> None:
    root = CREATOR_DIR / "duples" / duple_id
    root.mkdir(parents=True, exist_ok=True)

    persona = cfg["persona"]
    gates = cfg.get("gates", {})
    reach_triggers = cfg.get("reach", {}).get("enabled_triggers", ["price_above", "price_below"])

    # duple_settings.py
    _write(root / "duple_settings.py", _render_duple_settings(archetype, gates, reach_triggers))

    # .env.example
    _write(root / ".env.example", ENV_EXAMPLE_SRC.read_text().replace("{duple_id}", duple_id))

    # chat/router/router_config.yaml
    (root / "chat" / "router").mkdir(parents=True, exist_ok=True)
    _write(root / "chat" / "router" / "router_config.yaml", _render_router_config())

    # chat/reply/context_builder.py
    (root / "chat" / "reply").mkdir(parents=True, exist_ok=True)
    _write(root / "chat" / "reply" / "context_builder.py",
           _render_context_builder(duple_id, persona["name"]))

    print(f"  wrote duples/{duple_id}/ (4 files)")


def _render_duple_settings(archetype: str, gates: dict, reach_triggers: list) -> str:
    chat_gate = gates.get("chat", "all")
    reach_gate = gates.get("reach", "creator")
    memory_gate = gates.get("memory", "all")
    knowledge_gate = gates.get("knowledge", "all")
    reach_enabled = archetype == "finance" and bool(reach_triggers)
    cards_enabled = archetype == "finance"

    return (
        f'ARCHETYPE = "{archetype}"\n'
        f"\n"
        f"CHAT = {{\n"
        f'    "enabled": True,\n'
        f'    "gate_roles": "{chat_gate}",\n'
        f'    "cards_enabled": {cards_enabled},\n'
        f"}}\n"
        f"\n"
        f"REACH = {{\n"
        f'    "enabled": {reach_enabled},\n'
        f'    "gate_roles": "{reach_gate}",\n'
        f'    "enabled_triggers": {reach_triggers!r},\n'
        f"}}\n"
        f"\n"
        f"MEMORY = {{\n"
        f'    "enabled": True,\n'
        f'    "gate_roles": "{memory_gate}",\n'
        f"}}\n"
        f"\n"
        f"KNOWLEDGE = {{\n"
        f'    "enabled": False,\n'
        f'    "gate_roles": "{knowledge_gate}",\n'
        f"}}\n"
    )


def _render_router_config() -> str:
    return """\
# router_config.yaml — intent routing rules
# ticker_alias_map: map common misspellings to canonical tickers
# chat_word_denylist: short words that route to AI, never CARD
# NOTE: bare NO/YES must be quoted (PyYAML parses them as booleans otherwise)

ticker_alias_map: {}

chat_word_denylist:
  - HI
  - HEY
  - OK
  - "NO"
  - "YES"
  - WOW
  - LOL
  - THANKS
  - TEST
"""


def _render_context_builder(duple_id: str, persona_name: str) -> str:
    return f'''\
"""
context_builder.py — assembles the LLM context for {duple_id}.chat.reply.

Called once per AI-lane turn from reply_flow.py:
    ctx = build_context(duply_id, AGENT_ID)

Returns a dict with:
    system_prompt   str   — persona + agent_profiles.system_prompt blocks
    context_user    str   — formatted user profile
    context_memory  str   — active memory topics (from memory.noter)
    context_market  str   — real-time market data (empty until wired)
    context_history str   — empty string (history travels via `history` list)
    tools_enabled   list  — from agent_profiles.tools_enabled
    history         list  — {{role, content}} turns for prompt_builder
    watchlist       list  — raw user watchlist (for card dedup reuse)
    system_lang     str   — UI language (e.g. "TH")

Edit this file to customize how {persona_name} uses user data.
Persona character → edit public.duply_duples.persona in Supabase.
Operational config → edit {duple_id}_ai.agent_profiles.system_prompt in Supabase.
"""

import asyncio
import json
import logging
import os
import sys
import urllib.request

import redis.asyncio as aioredis

_DIR = os.path.dirname(os.path.abspath(__file__))
# 4 levels up: reply/ → chat/ → {duple_id}/ → duples/ → repo root (duply-agents/)
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
DUPLE_ID = os.environ.get("DUPLE_ID", "{duple_id}")
REDIS_URL = os.environ.get("PT_REDIS_URL", "redis://localhost:6379/0")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SCHEMA = os.environ.get("SCHEMA_NAME", "{duple_id}_ai")

_PROMPT_TTL = 300  # 5 min — matches Thay


# ─── Supabase helper ─────────────────────────────────────────────────────────


def _supabase_get(path: str, schema: str = SCHEMA) -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY not configured")
    req = urllib.request.Request(f"{{SUPABASE_URL}}{{path}}")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {{SUPABASE_KEY}}")
    req.add_header("Accept-Profile", schema)
    req.add_header("Content-Profile", schema)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


# ─── Agent prompt cache (TTL ~5 min, in-memory) ──────────────────────────────

_prompt_cache: TTLCache = TTLCache(ttl_seconds=_PROMPT_TTL)
_persona_cache: TTLCache = TTLCache(ttl_seconds=_PROMPT_TTL)


def _fetch_agent_prompt(agent_id: str) -> dict:
    rows = _supabase_get(
        f"/rest/v1/agent_profiles?agent_id=eq.{{agent_id}}&is_active=eq.true"
        f"&select=system_prompt,tools_enabled&limit=1"
    )
    row = rows[0] if rows else {{}}
    if not row.get("system_prompt"):
        raise ValueError(f"no active agent_profiles row for {{agent_id!r}}")
    return {{"system_prompt": row["system_prompt"], "tools_enabled": row.get("tools_enabled")}}


def get_agent_prompt(agent_id: str) -> dict:
    return _prompt_cache.get_or_refresh(agent_id, lambda: _fetch_agent_prompt(agent_id))


def _fetch_duple_persona(duple_id: str) -> str:
    rows = _supabase_get(
        f"/rest/v1/duply_duples?duple_id=eq.{{duple_id}}&select=persona&limit=1",
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
            f"?duply_id=eq.{{duply_id}}"
            f"&select=nickname,tier,system_lang,knowledge_level,closeness,goal,archetype_data"
            f"&limit=1"
        )
        return rows[0] if rows else {{}}
    except Exception as e:
        log.warning("user_profile fetch failed for %s: %s", duply_id, e)
        return {{}}


def _build_context_user(profile: dict) -> str:
    parts = []
    if profile.get("nickname"):
        parts.append(f"Name: {{profile['nickname']}}")
    if profile.get("tier") and profile["tier"] != "free":
        parts.append(f"Tier: {{profile['tier']}}")
    if profile.get("knowledge_level"):
        parts.append(f"Knowledge level: {{profile['knowledge_level']}}")
    if profile.get("closeness"):
        parts.append(f"Closeness: {{profile['closeness']:.1f}}")
    if profile.get("goal"):
        parts.append(f"Goal: {{profile['goal']}}")
    return "\\n".join(parts)


def _build_system_prompt(agent_blocks: dict, persona: str) -> str:
    parts = []
    if persona:
        parts.append(persona)
    for key, value in (agent_blocks or {{}}).items():
        if value:
            parts.append(f"[{{key.upper()}}]\\n{{value}}")
    return "\\n\\n".join(parts)


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

    watchlist = (profile.get("archetype_data") or {{}}).get("watchlist") or []

    return {{
        "system_prompt": _build_system_prompt(
            agent_prompt.get("system_prompt") or {{}}, duple_persona
        ),
        "tools_enabled": agent_prompt.get("tools_enabled") or [],
        "context_user": _build_context_user(profile),
        "context_memory": memory_topics,
        "context_market": "",   # TODO: wire market data (SET price feed) when ready
        "context_history": "",
        "history": history_raw,
        "watchlist": watchlist,
        "system_lang": profile.get("system_lang") or "TH",
    }}


def build_context(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    return asyncio.run(build_context_async(duply_id, agent_id))
'''


# ─── Output helpers ──────────────────────────────────────────────────────────


def _step(label: str) -> None:
    print(f"  {label}...")


def _check(value: bool, *, expect_true: bool, label: str) -> None:
    ok = value if expect_true else not value
    mark = "✓" if ok else "!"
    warn = "" if ok else " — check manually"
    print(f"    {mark} {label}{warn}")


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def _die(msg: str) -> None:
    print(f"Error: {msg}")
    sys.exit(1)


def _print_credentials(
    duple_id: str, schema: str, role: str, password: str,
    persona_name: str, owner: str,
) -> None:
    w = 56
    def row(label: str, value: str) -> str:
        content = f"  {label:<10} {value}"
        return f"║{content:<{w}}║"

    lines = [
        f"╔{'═' * w}╗",
        f"║{'  Provisioned: ' + duple_id:<{w}}║",
        f"║{'  Persona:     ' + persona_name:<{w}}║",
        f"╠{'═' * w}╣",
        row("Host:", "db.fpjevusrpausqunjhubk.supabase.co"),
        row("Database:", "postgres"),
        row("Schema:", schema),
        row("Role:", role),
        row("Password:", password),
        f"╚{'═' * w}╝",
    ]
    print("\n" + "\n".join(lines))
    print(f"""
Send credentials to {owner} via a secure channel.

Next steps:
  1. git add duples/{duple_id}/ && git commit -m "feat: scaffold {duple_id}" && git push
  2. Creator: git pull → copy duples/.env.example → duples/{duple_id}/.env → fill in password
  3. Fill in agent_profiles.system_prompt for {schema}.chat.reply in Supabase
  4. Add line-webhook-service entry to infra/platform/docker-compose.yml on Pi
""")


# ─── CLI entry point ─────────────────────────────────────────────────────────


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    duple_id = args[0].strip().lower()

    supabase_dir = DEFAULT_SUPABASE_DIR
    if "--supabase-dir" in args:
        idx = args.index("--supabase-dir")
        supabase_dir = Path(args[idx + 1]).resolve()

    if not supabase_dir.exists():
        _die(f"supabase directory not found: {supabase_dir}")

    provision(duple_id, supabase_dir)


if __name__ == "__main__":
    main()
