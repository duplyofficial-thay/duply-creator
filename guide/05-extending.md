# Extending Your Duple

Three ways to add new capabilities:

| What | Where you write | How it ships |
|---|---|---|
| **Tool** | `platform/tools/packs/{pack}/` | PR → team review → Pi deploy |
| **Card** | `duples/{duple_id}/chat/card/` | PR → Pi restart (no rebuild) |
| **Domain** | `duples/{duple_id}/{domain}/` | PR → team deploys |

---

## 1. Tools

A tool is a Python function the LLM can call mid-conversation to fetch data or perform an action.

### Where tools live

Tools are **platform-level** — shared across any Duple that enables them. They do not live inside your `duples/` folder.

```
platform/tools/packs/{pack_name}/
  my_tool.py        ← your tool here
```

Pick or create a pack that matches the tool's scope:

| Pack | Use for |
|---|---|
| `generic/` | tools useful to any Duple (search, memory, knowledge) |
| `packs/finance/` | tools for finance-archetype Duples |
| `packs/commerce/` | tools for commerce-archetype Duples (Tawan) |
| `packs/{new}/` | create a new pack if no existing one fits |

### Contribution process

```
1. Write your tool in platform/tools/packs/{pack}/
2. Register it in platform/tools/registry.py
3. Open a PR → team reviews against the checklist below
4. Team merges + deploys to Pi
5. You enable the tool in Supabase
```

You own steps 1–3. The team owns 4. You own 5.

### Tool contract

```python
# platform/tools/packs/{pack}/my_tool.py

MY_TOOL_SCHEMA = {
    "name": "my_tool",
    "description": "One sentence: what this tool does and when to call it.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What the user is asking about",
            },
        },
        "required": ["query"],
    },
}


def my_tool(query: str, **context) -> str:
    """Fetch data and return a plain string for the LLM.
    Never raises — always return '[ERROR] ...' on failure.
    """
    try:
        result = ...  # your logic here
        return f"[MY_TOOL] {result}"
    except Exception as e:
        return f"[ERROR] my_tool: {str(e)[:100]}"
```

Rules:
- **Always returns a string** — the LLM reads your return value directly
- **Never raises** — catch all exceptions, return `"[ERROR] ..."` string
- **Auth comes from context** — never accept `store_id`, `user_id`, or role as an LLM argument; read them from `**context` which the platform injects
- **No hardcoded secrets** — read from `os.environ.get(...)`
- **No direct DB writes** — tools read and propose; validated Python code writes

### Register in registry.py

```python
# platform/tools/registry.py

from platform.tools.packs.my_pack.my_tool import my_tool, MY_TOOL_SCHEMA

TOOL_REGISTRY["my_tool"] = {
    "func": my_tool,
    "schema": MY_TOOL_SCHEMA,
    "owner_tier": "archetype",   # or "platform"
    "owner_scope": "commerce",   # or None for generic
}

_PACK_MAP["my_pack"] = [..., "my_tool"]
```

### Team review checklist

Before the team merges your PR, they check:

- [ ] Tool returns a string in all code paths
- [ ] No unhandled exceptions (bare `except` or specific + fallback)
- [ ] `store_id` / auth read from `**context`, not from tool arguments
- [ ] No hardcoded API keys or credentials
- [ ] Tool name is unique across the whole registry
- [ ] Pack placement makes sense (generic vs archetype-specific)
- [ ] Description tells the LLM clearly when to call it

### Enable after deploy

```sql
-- Enable the tool for your agent in Supabase
UPDATE {schema}.agent_profiles
SET tools_enabled = tools_enabled || '["my_tool"]'
WHERE agent_id = 'chat.reply';
```

Then add guidance in your `system_prompt` tools block so the LLM knows when to use it.

---

## 2. Cards

A card is a structured LINE flex message — rich layout with data, buttons, and images.

Cards live in your Duple folder (not platform-level) because their layout and data are Duple-specific.

Cards trigger two ways:
- **Router-triggered**: keyword/pattern → card sent directly, no LLM
- **LLM-triggered**: LLM decides mid-turn to attach a card

### Files you write

**`duples/{duple_id}/chat/card/card_renderer.py`** — add your render function:

```python
def render_my_card(data: dict, lang: str = "TH") -> dict:
    return {
        "type": "flex",
        "altText": "My card",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": data.get("title", ""), "weight": "bold"},
                ],
            },
        },
    }
```

**`duples/{duple_id}/chat/card/card_metadata.yaml`**:

```yaml
my_card_meta:
  MY_TYPE:
    name_en: My Card
    name_th: "การ์ดของฉัน"
    icon: my_icon.png
    color: "#6366F1"
```

**`duples/{duple_id}/chat/card/data_fetcher.py`** — add a branch for your card type:

```python
elif card_type == "my_type":
    return fetch_my_data(data.get("card_subject"))
```

### Steps

1. Add your `card_type` to `valid_card_types` in `card_config.py`
2. If LLM-triggered: update `REPLY_OUTPUT_PROMPT` to tell the LLM when to use it
3. If router-triggered: add the keyword pattern to `router_config.yaml`
4. Open a PR → team restarts the container (no rebuild needed)

---

## 3. Custom Domains

A domain is a new background capability with its own lifecycle — a service, batch job, or event processor.

| Example | Pattern | Runs when |
|---|---|---|
| `social.publish` | Webhook + queue | On demand |
| `report.weekly` | Batch + cron | Scheduled |
| `market.signal` | Event-driven + cron | On market event |
| `coach.daily` | Push + cron | Daily |

### Structure

```
duples/{duple_id}/
  my_domain/
    my_engine.py     ← core logic (stateless, reads DB/Redis, writes DB)
    my_cron.py       ← entry point for scheduled runs
    my_service.py    ← HTTP wrapper if callable from chat
```

### Steps

1. Write `my_engine.py` — pure logic, no network side effects in the module body
2. Write the entry point (`my_cron.py` or `my_service.py`)
3. If you need new tables — describe them in the PR (column names, types, indexes)
4. If you need new env vars — add to your `duples/{duple_id}/.env.example`
5. Open a PR → team adds the Docker service or cron entry and deploys

### Gate access during development

```python
# duples/{duple_id}/duple_settings.py
MY_DOMAIN = {
    "enabled": True,
    "gate_roles": "creator",   # test with yourself first
}
```

### Connect to chat (optional)

- Add a tool following the tool pattern above (`get_my_domain_data`, `trigger_my_domain`)
- Or add card types for domain output
