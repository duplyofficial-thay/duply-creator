"""
Commerce tool template — available to any commerce-archetype Duple (e.g. Tawan).
Copy this file, rename it, fill in the logic.

File naming: platform/tools/packs/commerce/get_{thing}.py
                                           or action_{thing}.py for write tools

Key difference from generic tools: you MUST read store_id from **context.
Never accept store_id as an LLM argument — that would allow prompt injection
to switch stores.
"""
import os

# 1. Define the schema
GET_STORE_THING_SCHEMA = {
    "name": "get_store_thing",
    "description": "One sentence: what this tool returns and when to call it. Do not mention store_id — the platform resolves it automatically.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What the user is asking about.",
            },
        },
        "required": ["query"],
        # Note: store_id is NOT a parameter — never expose it to the LLM
    },
}


# 2. Implement the function
def get_store_thing(query: str, **context) -> str:
    """
    Fetch store-scoped data and return a plain string for the LLM.

    Rules (same as generic, plus):
    - store_id comes from context ONLY — never from tool arguments
    - All queries must include WHERE store_id = ? — never return another store's data
    - On failure: return "[ERROR] get_store_thing: <reason>"
    """
    try:
        store_id = context.get("store_id")
        if not store_id:
            return "[ERROR] get_store_thing: missing store_id in context"

        # lang = context.get("lang", "TH")
        # customer_id = context.get("customer_id")

        result = "..."  # your logic here — always scope to store_id

        return f"[STORE_THING] {result}"

    except Exception as e:
        return f"[ERROR] get_store_thing: {str(e)[:120]}"


# 3. After writing this file:
#    - Open a PR
#    - Team adds to platform/tools/registry.py on Pi:
#
#    TOOL_REGISTRY["get_store_thing"] = {
#        "func": get_store_thing,
#        "schema": GET_STORE_THING_SCHEMA,
#        "owner_tier": "archetype",
#        "owner_scope": "commerce",
#    }
#    _PACK_MAP["commerce"].append("get_store_thing")
#
#    - After deploy: enable in Supabase agent_profiles.tools_enabled
