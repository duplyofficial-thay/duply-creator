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

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - exercised by local environments without PyYAML
    yaml = None

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
        "knowledge.extract": [],
    },
    "lifestyle": {
        "chat.reply":        ["generic"],
        "reach.alert":       [],
        "memory.noter":      [],
        "memory.dream":      [],
        "knowledge.extract": [],
    },
    "commerce": {
        "chat.reply":        ["generic"],
        "reach.alert":       [],
        "memory.noter":      [],
        "memory.dream":      [],
        "knowledge.extract": [],
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
        "coverage": "Send proactive alerts about topics the user is tracking.",
        "stance": "Factual and concise. State what triggered and why it matters.",
        "goal": "Keep the user informed when significant events occur.",
        "philosophy": "Be direct. No filler, no speculation.",
        "examples": [],
    },
    # memory.noter reads: output_format, instructions, importance_guide, bond_rules (all required),
    # focus_areas (optional — Duple-specific extraction guidance).
    # Fill these in Supabase after provisioning. Platform template handles the rest.
    "memory.noter": {
        "focus_areas": "",
    },
    # memory.dream reads: instructions, output_format (required), focus_areas (optional).
    # Platform template in public.agent_profiles is self-sufficient — only add
    # focus_areas here if you need Duple-specific consolidation guidance.
    "memory.dream": {
        "focus_areas": "",
    },
    "knowledge.extract": {},
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
    if yaml is None:
        _die("pyyaml is required to provision a Duple. Install it with: python3 -m pip install pyyaml")

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
    run_sql(f"GRANT USAGE, CREATE ON SCHEMA {schema} TO {role};", supabase_dir)
    run_sql(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role};",
        supabase_dir,
    )

    # 3b. Grant PostgREST roles access + expose schema
    _step("Granting PostgREST access + exposing schema")
    run_sql(
        f"GRANT USAGE ON SCHEMA {schema} TO anon, authenticated, service_role;",
        supabase_dir,
    )
    run_sql(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
        f"GRANT ALL ON TABLES TO service_role;",
        supabase_dir,
    )
    run_sql(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
        f"GRANT SELECT ON TABLES TO anon, authenticated;",
        supabase_dir,
    )
    # Auto-grant service_role/anon on tables created by the duple role itself
    run_sql(
        f"""CREATE OR REPLACE FUNCTION {schema}.auto_grant_on_create()
RETURNS event_trigger LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE obj record;
BEGIN
  FOR obj IN
    SELECT schema_name, object_identity
    FROM pg_event_trigger_ddl_commands()
    WHERE schema_name = '{schema}' AND object_type = 'table'
  LOOP
    EXECUTE format('GRANT ALL ON %s TO service_role', obj.object_identity);
    EXECUTE format('GRANT SELECT ON %s TO anon, authenticated', obj.object_identity);
  END LOOP;
END;
$$;
CREATE EVENT TRIGGER {schema}_auto_grant
  ON ddl_command_end WHEN TAG IN ('CREATE TABLE')
  EXECUTE FUNCTION {schema}.auto_grant_on_create();""",
        supabase_dir,
    )
    # Append schema to pgrst.db_schemas (idempotent — skips if already present)
    # Must read from pg_db_role_setting, not current_setting() which returns the session value
    run_sql(
        f"""DO $$
DECLARE
  cur text := 'public';
  cfg text;
BEGIN
  FOR cfg IN
    SELECT unnest(setconfig)
    FROM pg_db_role_setting
    WHERE setrole = (SELECT oid FROM pg_roles WHERE rolname = 'authenticator')
  LOOP
    IF cfg LIKE 'pgrst.db_schemas=%%' THEN
      cur := substring(cfg FROM 'pgrst\\.db_schemas=(.+)');
    END IF;
  END LOOP;
  IF position('{schema}' IN cur) = 0 THEN
    EXECUTE 'ALTER ROLE authenticator SET pgrst.db_schemas TO ' || quote_literal(cur || ',{schema}');
  END IF;
END $$;
NOTIFY pgrst, 'reload config';
NOTIFY pgrst, 'reload schema';""",
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

    # 4b. Grant on existing tables/sequences (DEFAULT PRIVILEGES only covers future objects)
    run_sql(f"GRANT ALL ON ALL TABLES IN SCHEMA {schema} TO service_role;", supabase_dir)
    run_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO anon, authenticated;", supabase_dir)
    run_sql(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {schema} TO service_role;", supabase_dir)
    run_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} GRANT USAGE, SELECT ON SEQUENCES TO service_role;", supabase_dir)
    run_sql(f"GRANT ALL ON ALL FUNCTIONS IN SCHEMA {schema} TO service_role;", supabase_dir)

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
    reach_triggers = cfg.get("reach", {}).get("enabled_triggers", [])

    # __init__.py (makes duples/{duple_id}/ a package for importlib)
    _write(root / "__init__.py", "")

    # memory/mem_config.py
    (root / "memory").mkdir(parents=True, exist_ok=True)
    _write(root / "memory" / "__init__.py", "")
    _write(root / "memory" / "mem_config.py", _render_mem_config(archetype, duple_id))

    # duple_settings.py
    _write(root / "duple_settings.py", _render_duple_settings(archetype, gates, reach_triggers))

    # .env.example
    _write(root / ".env.example", ENV_EXAMPLE_SRC.read_text().replace("{duple_id}", duple_id))

    # chat/router/router_config.yaml
    (root / "chat" / "router").mkdir(parents=True, exist_ok=True)
    _write(root / "chat" / "router" / "router_config.yaml", _render_router_config(archetype))

    # chat/reply/context_builder.py
    (root / "chat" / "reply").mkdir(parents=True, exist_ok=True)
    _write(root / "chat" / "reply" / "context_builder.py",
           _render_context_builder(duple_id, persona["name"]))

    # chat/service/service_messages.py — per-Duple wording for SERVICE lane replies
    (root / "chat" / "service").mkdir(parents=True, exist_ok=True)
    _write(root / "chat" / "service" / "service_messages.py",
           _render_service_messages(persona.get("language", "TH")))

    # chat/card/ — stubs; always generated so reply_flow.py can import them
    # and so future card authors know the required interface.
    (root / "chat" / "card").mkdir(parents=True, exist_ok=True)
    is_thai = persona.get("language", "").upper() == "TH"
    fallback_msg = "ขออภัยครับ ระบบขัดข้อง" if is_thai else "Sorry, something went wrong."
    _write(root / "chat" / "card" / "card_config.py",    _render_card_config(fallback_msg))
    _write(root / "chat" / "card" / "pipeline.py",       _render_card_pipeline())
    _write(root / "chat" / "card" / "dedup.py",          _render_card_dedup())
    _write(root / "chat" / "card" / "data_fetcher.py",   _render_card_data_fetcher())
    _write(root / "chat" / "card" / "card_renderer.py",  _render_card_renderer())
    _write(root / "chat" / "card" / "card_primitives.py",_render_card_primitives())
    _write(root / "chat" / "card" / "card_metadata.yaml",_render_card_metadata(duple_id))

    # reach/hooks.py — per-Duple reach trigger stub
    (root / "reach").mkdir(parents=True, exist_ok=True)
    _write(root / "reach" / "hooks.py", _render_reach_hooks_stub(duple_id))

    print(f"  wrote duples/{duple_id}/ (16 files)")


def _render_reach_hooks_stub(duple_id: str) -> str:
    return (
        '"""\n'
        f'hooks.py — {duple_id} reach triggers.\n'
        '\n'
        'Add EVENT_TRIGGERS (subclass EventTrigger from reach_engine) for\n'
        'event-based pushes, or SCHEDULE_TRIGGERS (ScheduleTrigger) for\n'
        'time-based recurring pushes. Both lists are empty by default.\n'
        '"""\n'
        '\n'
        'EVENT_TRIGGERS = []\n'
        'SCHEDULE_TRIGGERS = []\n'
        '\n'
        '\n'
        'def generate_message(duply_id, fires, profile, system_lang):\n'
        '    """Called by reach_engine._deliver when fires have no pre-built messages.\n'
        '    Return (list[str], card_dict|None) or (None, None) on failure.\n'
        '    Import LLM helpers from reach_engine or implement inline."""\n'
        '    return None, None\n'
        '\n'
        '\n'
        'def fallback_message(fires):\n'
        '    """Cheap no-LLM text for capped/quiet-hours logging. Never pushed."""\n'
        '    return ["\\U0001f514"]\n'
    )


def _render_mem_config(archetype: str, duple_id: str) -> str:
    if archetype == "finance":
        return (
            'from archetypes import MemConfig\n'
            '\n'
            'MEM_CONFIG = MemConfig(\n'
            '    default_topics=["personal_facts", "investment_pattern", "holding_thesis"],\n'
            '    observable_fields=frozenset({\n'
            '        "risk_appetite",\n'
            '        "trading_style",\n'
            '        "time_horizon",\n'
            '        "investment_style",\n'
            '    }),\n'
            '    holdings_topic="holding_thesis",  # finance only\n'
            ')\n'
        )
    return (
        'from archetypes import MemConfig\n'
        '\n'
        '# observable_fields: add archetype-specific JSONB fields from user_profiles.archetype_data\n'
        '# that dream/noter should be allowed to observe and update.\n'
        'MEM_CONFIG = MemConfig(\n'
        '    default_topics=["personal_facts"],\n'
        '    observable_fields=frozenset(),\n'
        '    holdings_topic=None,\n'
        ')\n'
    )


def _render_duple_settings(archetype: str, gates: dict, reach_triggers: list) -> str:
    chat_gate = gates.get("chat", "creator")
    reach_gate = gates.get("reach", "creator")
    memory_gate = gates.get("memory", "creator")
    knowledge_gate = gates.get("knowledge", "creator")
    return (
        f'ARCHETYPE = "{archetype}"\n'
        f"\n"
        f"CHAT = {{\n"
        f'    "gate_roles": "{chat_gate}",\n'
        f'    "cards_enabled": False,\n'
        f'    "dump_prompt": False,\n'
        f"}}\n"
        f"\n"
        f"REACH = {{\n"
        f'    "enabled": True,\n'
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


def _render_service_messages(language: str) -> str:
    # Generate Thai wording by default; edit the file for EN-only Duples.
    del language  # reserved for future use
    return (
        '"""\n'
        'service_messages.py — per-Duple wording for SERVICE lane confirmations.\n'
        '\n'
        'render_service_messages(result) takes the dict returned by run_service()\n'
        'and returns a list of user-facing strings to send back on LINE.\n'
        '\n'
        'Future: move wording to Supabase (agent_profiles) for live editing.\n'
        '"""\n'
        '\n'
        '\n'
        'def render_service_messages(result: dict) -> list[str]:\n'
        '    if result.get("status") != "ok":\n'
        '        return ["ขออภัยครับ ไม่สามารถดำเนินการได้ในขณะนี้"]\n'
        '\n'
        '    action = result.get("action")\n'
        '\n'
        '    if action == "PROFILE_UPDATE":\n'
        '        op = result.get("op")\n'
        '        n = result.get("count", 0)\n'
        '        mx = result.get("max", 5)\n'
        '        lines = []\n'
        '\n'
        '        if op == "add":\n'
        '            added = result.get("added") or []\n'
        '            skipped = result.get("skipped") or []\n'
        '            rejected = result.get("rejected") or []\n'
        '            if added:\n'
        '                lines.append(f"เพิ่ม {\', \'.join(added)} เรียบร้อยครับ ({n}/{mx})")\n'
        '            if skipped:\n'
        '                lines.append(f"{\', \'.join(skipped)} มีอยู่ใน Watchlist อยู่แล้วครับ")\n'
        '            if rejected:\n'
        '                lines.append(f"ไม่สามารถเพิ่ม {\', \'.join(rejected)} ได้ครับ "\n'
        '                             f"Watchlist เต็มแล้ว (สูงสุด {mx} ตัว)")\n'
        '\n'
        '        elif op == "remove":\n'
        '            removed = result.get("removed") or []\n'
        '            not_found = result.get("not_found") or []\n'
        '            if removed:\n'
        '                lines.append(f"ลบ {\', \'.join(removed)} เรียบร้อยครับ (เหลือ {n}/{mx})")\n'
        '            if not_found:\n'
        '                lines.append(f"{\', \'.join(not_found)} ไม่อยู่ใน Watchlist ครับ")\n'
        '\n'
        '        return ["\\n".join(lines)] if lines else ["ดำเนินการเรียบร้อยครับ"]\n'
        '\n'
        '    if action == "LANG_UPDATE":\n'
        '        lang = result.get("system_lang", "TH")\n'
        '        return ["ตั้งค่าเป็นภาษาไทยเรียบร้อยครับ" if lang == "TH"\n'
        '                else "Language set to English."]\n'
        '\n'
        '    if action == "WATCHLIST_GET":\n'
        '        wl = result.get("watchlist") or []\n'
        '        n = result.get("watchlist_count", 0)\n'
        '        mx = result.get("max", 5)\n'
        '        if not wl:\n'
        '            return [f"Watchlist ยังว่างอยู่ครับ (0/{mx})"]\n'
        '        return [f"Watchlist ตอนนี้: {\', \'.join(wl)} ({n}/{mx})"]\n'
        '\n'
        '    return ["ดำเนินการเรียบร้อยครับ"]\n'
    )


def _render_router_config(archetype: str) -> str:
    postback_block = ""
    if archetype == "finance":
        postback_block = """
# ─── POSTBACK ROUTES ───────────────────────────────────────────────────────────
postback_routes:
  - patterns: ["TAG|"]
    match: prefix
    card_type: tag_info
    payload: rest
"""
    return f"""\
# router_config.yaml — intent routing rules
# ticker_regex:       optional — omit for non-finance Duples (defaults to no ticker routing)
# ticker_alias_map:   misspellings → canonical tickers
# chat_word_denylist: short words that always fall to AI even if they match ticker_regex
# NOTE: bare NO/YES must be quoted (PyYAML parses them as booleans otherwise)

ticker_alias_map: {{}}

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

# ─── SERVICE ROUTES ────────────────────────────────────────────────────────────
service_routes:
  - patterns: ["TH", "EN", "TH LANG", "EN LANG"]
    match: exact
    type: LANG_UPDATE
    payload: self

  # Uncomment to enable watchlist add/remove:
  # - patterns: ["ADD "]
  #   match: prefix
  #   type: PROFILE_UPDATE
  #   op: add
  #   field: watchlist
  #   max: 5
  #   payload: rest_words
  #
  # - patterns: ["DEL "]
  #   match: prefix
  #   type: PROFILE_UPDATE
  #   op: remove
  #   field: watchlist
  #   max: 5
  #   payload: rest_words
{postback_block}
# ─── CARD KEYWORD ROUTES ───────────────────────────────────────────────────────
mode_words: {{}}   # add keyword groups here if your Duple has analysis modes

keyword_route_map: {{}}
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
    watchlist       list  — [] by default; extend in this file if needed
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
            f"&select=nickname,tier,system_lang,knowledge_level,closeness,goal"
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

    return {{
        "system_prompt": _build_system_prompt(
            agent_prompt.get("system_prompt") or {{}}, duple_persona
        ),
        "tools_enabled": agent_prompt.get("tools_enabled") or [],
        "context_user": _build_context_user(profile),
        "context_memory": memory_topics,
        "context_market": "",   # TODO: wire real-time context here (price, events, etc.)
        "context_history": "",
        "history": history_raw,
        "watchlist": [],        # TODO: fetch from profile if your Duple needs it
        "system_lang": profile.get("system_lang") or "TH",
    }}


def build_context(duply_id: str, agent_id: str = AGENT_ID) -> dict:
    return asyncio.run(build_context_async(duply_id, agent_id))
'''


def _render_card_config(fallback_msg: str) -> str:
    return f'''\
from agent_loop import CardConfig, build_json_shape_hint

# Minimal stub — cards not configured yet.
# When you add card types: extend valid_card_types and ticker_required_card_types.
CARD_CONFIG = CardConfig(
    valid_card_types=frozenset({{None}}),
    ticker_required_card_types=frozenset(),
    subject_field_name="card_subject",
    fallback_message="{fallback_msg}",
)

REPLY_OUTPUT_PROMPT = (
    f"JSON only, no markdown fence: {{build_json_shape_hint(CARD_CONFIG)}}\\n"
    "card_type: null (plain text reply only — no cards configured yet)."
)

REACH_ALERT_OUTPUT_PROMPT = (
    f"Return a JSON object exactly: {{build_json_shape_hint(CARD_CONFIG)}}\\n"
    "No markdown fence. card_type: null only."
)
'''


def _render_card_pipeline() -> str:
    return '''\
# Stub — no cards configured yet.
# When you add card types: implement render_card_with_status and render_card here.


def render_card_with_status(route, user_ctx: dict):
    return None, "no_cards"


def render_card(route, user_ctx: dict):
    return None
'''


def _render_card_dedup() -> str:
    return '''\
# Stub — no card dedup needed when cards are disabled.
# When you add cards: implement suppression logic here.


def suppress_if_recently_shown(history, card_type, card_subject, window=6):
    return card_type, card_subject
'''


def _render_card_data_fetcher() -> str:
    return '''\
# card/data_fetcher.py — stub.
#
# Implement these when cards_enabled is set to True in duple_settings.py.
#
# resolve_target(route) -> target
#   Maps a RouteDecision to a fetch target (ticker, list of tickers, keyword…).
#   Called by pipeline.py before any fetch. See duples/thay/chat/card/data_fetcher.py.
#
# fetch_*_batch(target, user_ctx) -> data | None
#   One function per card family (pt, ns, bf…). Returns raw data dict or None on failure.
#   pipeline.py calls the right fetch function based on route.card_type.


def resolve_target(route):
    raise NotImplementedError("data_fetcher.resolve_target not implemented yet")
'''


def _render_card_renderer() -> str:
    return '''\
# card/card_renderer.py — stub.
#
# Implement render_pt_card first — it handles single-ticker and compare cards.
# Each function receives data from data_fetcher + user_ctx and returns a
# LINE Flex Message dict {"contents": {...}, "altText": "..."} or None.
# Use card_primitives.py for reusable Flex building blocks.
#
# pipeline.py imports these by name — keep function signatures stable.
# See duples/thay/chat/card/card_renderer.py for a full reference implementation.
#
# Do NOT load card_metadata.yaml at module level unless you need it —
# an import-time crash breaks the entire webhook service.


def render_pt_card(items: dict, mode: str = "single", tag_data: dict = None,
                   watchlist: list = None, label: str = None,
                   card_type: str = "pt", lang: str = "TH",
                   benchmarks: list = None) -> dict | None:
    raise NotImplementedError("render_pt_card not implemented yet")


def render_ns_card(items: dict, mode: str = "single",
                   label: str = None, watchlist: list = None) -> dict | None:
    raise NotImplementedError("render_ns_card not implemented yet")


def render_bf_card(ticker: str, data: dict, tag_data: dict,
                   in_watchlist: bool = False, lang: str = "TH") -> dict | None:
    raise NotImplementedError("render_bf_card not implemented yet")


def render_macro_ns_card(data: dict) -> dict | None:
    raise NotImplementedError("render_macro_ns_card not implemented yet")


def render_tag_info_card(tag_id: str, tag_info: dict, lang: str = "TH") -> dict | None:
    raise NotImplementedError("render_tag_info_card not implemented yet")
'''


def _render_card_primitives() -> str:
    return '''\
# card/card_primitives.py — stub.
#
# Pure helper functions that build LINE Flex Message JSON fragments.
# No engine-specific logic here — card_renderer.py calls these.
#
# See duples/thay/chat/card/card_primitives.py for the full set of primitives:
#   header_box(title, subtitle, color)    -> flex box dict
#   price_row(label, value, change_pct)   -> flex row dict
#   tag_chip(label, color)                -> flex component
#   footer_row(action_label, action_data) -> flex box dict
#   bubble(header, body, footer)          -> Flex bubble dict
#   carousel(bubbles)                     -> Flex carousel dict
#
# All primitives are pure functions: data in, Flex JSON fragment out.
'''


def _render_card_metadata(duple_id: str) -> str:
    return f'''\
# card/card_metadata.yaml — display metadata for cards (icons, colors, labels).
#
# Add entries here when implementing card types in card_renderer.py.
# See duples/thay/chat/card/card_metadata.yaml for the full reference format.
#
# Example structure:
#
# sector_meta:
#   XLK: {{name_en: Technology, name_th: "เทคโนโลยี", icon: XLK.png, color: "#6366F1"}}
#
# macro_meta:
#   SPY: {{name_en: Market, name_th: "ภาพรวมตลาด", icon: macro_market.png, color: "#1D4ED8", has_tag: true}}
#
# theme_labels:
#   TECH: TECHNOLOGY
#
# This file is intentionally empty until cards are configured for {duple_id}.
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

── Creator steps ─────────────────────────────────────────────
  1. git push (scaffold committed above)
  2. Creator: git pull → copy duples/.env.example → duples/{duple_id}/.env → fill in creds
  3. Edit duples/{duple_id}/ scaffold (router, duple_settings, context_builder)
  4. Fill system_prompt for {schema}.chat.reply in Supabase (see guide/04-prompts.md)

── Team infra steps ───────────────────────────────────────────
  5. Assign port: (thay=8020, khun=8021 → pick next) and fill into duples/{duple_id}/.env
  6. On Pi — add to infra/platform/docker-compose.yml:

     {duple_id}-line-webhook-service:
       image: duply-platform:latest
       container_name: {duple_id}-line-webhook-service
       restart: always
       network_mode: host
       working_dir: /app/platform/chat
       command: ["python3", "line_webhook_service.py"]
       env_file:
         - ../../.env.platform
         - ../../.env.archetype.finance
         - ../../duples/{duple_id}/.env
       environment:
         AGENT_LOOP_DEBUG_LOG: /app/logs/debug_parse_failures.jsonl
       volumes:
         - ../../duples:/app/duples:ro
         - ../../platform/chat/logs:/app/logs:rw

  7. Cloudflare Zero Trust → Tunnels → Edit → Public Hostnames → Add:
       webhook-{duple_id}.duply.org → http://localhost:<PORT>
  8. LINE Console → Messaging API → Webhook URL:
       https://webhook-{duple_id}.duply.org/webhook  (enable + verify)
  9. docker compose -f infra/platform/docker-compose.yml up -d {duple_id}-line-webhook-service
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
