# Platform Tools

Tools the LLM can call during a conversation. Shared across Duples — not Duple-specific.

## Structure

```
platform/tools/packs/
  generic/          ← any Duple (search, memory, knowledge)
  commerce/         ← commerce-archetype Duples (Tawan)
  finance/          ← finance-archetype Duples (Thay, Khun)
  {new_archetype}/  ← create a new pack if none fits
```

## How to add a tool

1. Copy the template from the right pack folder
2. Rename + fill in the logic
3. Open a PR — team reviews and deploys to Pi
4. After deploy: enable in Supabase `agent_profiles.tools_enabled`

Full guide: [guide/05-extending.md](../../guide/05-extending.md)

## Templates

| File | Use when |
|---|---|
| `packs/generic/_template.py` | Tool useful to any Duple |
| `packs/commerce/_template.py` | Tool scoped to one store (requires `store_id` from context) |
