"""
Generic tool template — available to any Duple.
Copy this file, rename it, fill in the logic.

File naming: platform/tools/packs/generic/get_{thing}.py
"""
import os

# 1. Define the schema — tells the LLM what this tool does and when to call it
GET_THING_SCHEMA = {
    "name": "get_thing",
    "description": "One sentence: what this tool returns and when the LLM should call it.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What the user is asking about.",
            },
        },
        "required": ["query"],
    },
}


# 2. Implement the function
def get_thing(query: str, **context) -> str:
    """
    Fetch data and return a plain string for the LLM to read.

    Rules:
    - Always returns a string — never raise, never return None
    - On failure: return "[ERROR] get_thing: <reason>"
    - Prefix output with [TAG] so the LLM knows the source
    - context: injected by the platform (duply_id, lang, etc.) — read from here, not from args
    """
    try:
        # duply_id = context.get("duply_id")   # who is asking
        # lang = context.get("lang", "TH")      # TH or EN

        result = "..."  # your logic here

        return f"[THING] {result}"

    except Exception as e:
        return f"[ERROR] get_thing: {str(e)[:120]}"


# 3. After writing this file:
#    - Open a PR
#    - Team adds to platform/tools/registry.py on Pi:
#
#    TOOL_REGISTRY["get_thing"] = {
#        "func": get_thing,
#        "schema": GET_THING_SCHEMA,
#        "owner_tier": "platform",
#        "owner_scope": None,
#    }
#    _PACK_MAP["generic"].append("get_thing")
#
#    - After deploy: enable in Supabase agent_profiles.tools_enabled
