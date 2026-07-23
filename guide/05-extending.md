# Extending Your Duple

Three ways to add new capabilities:

| What | Complexity | Requires team? |
|---|---|---|
| **Custom tool** | Write one Python function + schema | Team wires + redeploys |
| **Custom card** | Write renderer + metadata | Team wires + redeploys |
| **Custom domain** | New background service | Team deploys |

All of these need a code deploy — write the code in your `duples/{duple_id}/` folder, then coordinate with the Duply team.

---

## 1. Custom Tools

A tool is a Python function the LLM can call mid-conversation to get real-time data or perform an action.

### Contract

```python
# duples/{duple_id}/tools/my_tool.py

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


def my_tool(query: str) -> str:
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
- **Never raises** — catch exceptions, return `"[ERROR] ..."` string
- **Args come from JSON** — use basic types (str, int, float, bool, list)
- **No side effects by default** — tools are for reading, not writing (unless it's a deliberate action tool like `update_watchlist`)
- **Env vars** — read API keys from `os.environ.get(...)`. Add new keys to your `duples/{duple_id}/.env` and tell the team to include them in the container

### What to send the team

Once your tool is ready:
1. Push `duples/{duple_id}/tools/my_tool.py` to the repo
2. Tell the team: "add `my_tool` to the registry as `owner_tier=duple`, `owner_scope={duple_id}`"
3. The team adds it to `platform/tools/registry.py` + rebuilds the Docker image

### After the team deploys

Add your tool to `tools_enabled` in Supabase:
```sql
UPDATE {schema}.agent_profiles
SET tools_enabled = tools_enabled || '["my_tool"]'
WHERE agent_id = 'chat.reply';
```

Then update your `tools` block in `system_prompt` to tell the LLM when to use it:
```sql
UPDATE {schema}.agent_profiles
SET system_prompt = jsonb_set(system_prompt, '{tools}', '"Use my_tool when the user asks about X. Combine with get_memories to personalise the result."')
WHERE agent_id = 'chat.reply';
```

---

## 2. Custom Cards

A card is a structured LINE flex message — a rich visual layout with data, buttons, and images instead of plain text.

Cards can be triggered two ways:
- **Router-triggered**: a specific phrase or pattern → card sent directly, no LLM involved
- **LLM-triggered**: the LLM decides mid-turn to attach a card (returns a JSON response with `card_type` set)

### Files you write

**`duples/{duple_id}/chat/card/card_renderer.py`** — add your render function:

```python
def render_my_card(data: dict, lang: str = "TH") -> dict:
    """Returns a LINE flex message dict.
    data: whatever your data_fetcher returns for this card type.
    lang: "TH" or "EN" — use for localised labels.
    Returns: {"type": "flex", "altText": "...", "contents": {...}}
    """
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

**`duples/{duple_id}/chat/card/card_metadata.yaml`** — display metadata:

```yaml
my_card_meta:
  MY_TYPE:
    name_en: My Card
    name_th: "การ์ดของฉัน"
    icon: my_icon.png
    color: "#6366F1"
```

**`duples/{duple_id}/chat/card/data_fetcher.py`** — add a branch for your card type if it needs its own data source:

```python
elif card_type == "my_type":
    return fetch_my_data(data.get("card_subject"))
```

### What to do

1. Add your new `card_type` string to `valid_card_types` in `duples/{duple_id}/chat/card/card_config.py`
2. If the LLM needs a subject value (like a ticker, product name, etc.), it will pass it as `card_subject` — update `REPLY_OUTPUT_PROMPT` in `card_config.py` to tell the LLM when to use the new type and what to put in `card_subject`
3. Push your changes — the container picks them up on next restart (no rebuild needed)
4. If router-triggered: add the keyword pattern to `router_config.yaml`

---

## 3. Custom Domains

A domain is a completely new capability with its own lifecycle — a background service, batch job, or event processor. Examples:

| Domain idea | Pattern | Runs when |
|---|---|---|
| `social.publish` | Webhook + queue | On demand |
| `report.weekly` | Batch + cron | Scheduled |
| `market.signal` | Event-driven + cron | On market event |
| `coach.daily` | Push + cron | Daily |

### Structure

Put everything in `duples/{duple_id}/{domain}/`:

```
duples/{duple_id}/
  reach/
    alert/           ← reach.alert — cron-based price push (built-in)
  my_domain/
    my_engine.py     ← core logic
    my_cron.py       ← entry point for scheduled runs
    my_service.py    ← HTTP wrapper if it needs to be called from chat
```

### Typical process

1. **Write the engine** (`my_engine.py`) — stateless pure logic, reads from DB/Redis, writes to DB
2. **Write the entry point** (`my_cron.py` or `my_service.py`)
3. **If you need new tables** — describe them to the Duply team (column names, types, indexes). Team adds the migration
4. **If you need new env vars** — add them to your `duples/{duple_id}/.env` and tell the team
5. **Push the code** — the team adds the Docker service entry or cron entry and deploys

### Hook new domain into chat (optional)

If users should be able to interact with your domain via chat:
- Add a tool (`get_my_domain_data`, `trigger_my_domain`) following the custom tool pattern above
- Or add card types for domain output (custom card pattern above)
- Gate access via `duple_settings.py`:

```python
MY_DOMAIN = {
    "enabled": True,
    "gate_roles": "creator",   # test with yourself first
}
```

### What to tell the team

- What the service is (cron / webhook / on-demand)
- What schedule (if cron)
- What port (if HTTP service — team assigns to avoid conflicts)
- What new tables are needed
- What new env vars are needed
