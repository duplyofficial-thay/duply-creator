# Onboarding — From Zero to Live Duple

## Who Does What

| Step | Creator | Duply Team |
|---|---|---|
| 0 | Fill in `duple_config.yaml` | — |
| 1 | — | Provision schema + DB role, return credentials |
| 2 | Connect to DB, write persona/prompts | — |
| 3 | — | Generate code scaffold, open PR for review |
| 4 | Edit router config + Duple settings | — |
| 5 | Push to repo, open PR | Review + merge + deploy on Pi |
| 6 | Create LINE Official Account, send token/secret | Wire LINE OA + Cloudflare route → Duple goes live |

---

## Step 0 — Fill in `duple_config.yaml`

Fill in every field in [`templates/duple_config.yaml`](../templates/duple_config.yaml).

Key decisions:
- **`duple_id`** — lowercase, no spaces, unique. Becomes your schema name (`{duple_id}_ai`) and the mention keyword in LINE (`@{Duple_id}`)
- **`archetype`** — determines which tool packs your Duple can use (see [03-domains.md](03-domains.md))
- **`persona.description`** — 2–4 sentences. This seeds your initial `chat.reply` prompt; you'll refine it in Step 2

Send the filled-in config to the Duply team. **Do not include LINE tokens in this file** — send those separately via a secure channel.

---

## Step 1 — Provisioning (Duply Team)

The Duply team runs `provision_duple.py` with your config. This:

1. Creates Postgres schema `{duple_id}_ai` in the shared Supabase project
2. Creates a native Postgres role scoped to that schema only (read + write, no other schemas)
3. Seeds `{schema}.agent_profiles` with default prompt blocks for all agents
4. Seeds `public.duply_duples` with your Duple's metadata row
5. Verifies isolation: confirms the new role cannot query `thay_ai` or any other schema
6. Returns credentials (role name + password) to you

You'll receive a Postgres connection string. Keep it secret.

---

## Step 2 — Write Your Persona and Prompts

Connect to your schema using the credentials from Step 1 (psql, DBeaver, TablePlus, or any Postgres client — or ask Claude Code to do it for you).

Edit `{schema}.agent_profiles` — specifically the `duple_prompt` JSONB column for each `agent_id`. This is the layer you own. See [04-prompts.md](04-prompts.md) for the exact keys and how to edit safely.

Start with `chat.reply` — it's what users hit first. You can refine the others later.

---

## Step 3 — Code Scaffold (Duply Team)

The Duply team runs the scaffold generator with your config. This creates:

```
duples/<duple_id>/
  duple_settings.py       ← domain gates, archetype, enabled triggers
  router_config.yaml      ← intent routing rules
  .env.example            ← env var template (no real secrets)
  chat/
    reply/
      context_builder.py  ← context assembly (persona, memory, market data)
    card/
      card_config.py      ← card types your Duple serves (if archetype=finance)
```

This scaffold is opened as a PR in the shared `duply-thay` repo for the Duply team to review before merging.

---

## Step 4 — Edit Your Config

Once you have the scaffold, your main files to edit:

### `duple_settings.py`

Controls which domains are active and who can access them:

```python
ARCHETYPE = "finance"   # or "lifestyle", "commerce"

CHAT = {"enabled": True, "gate_roles": "all"}
REACH = {"enabled": True, "gate_roles": "creator", "enabled_triggers": ["price_above", "price_below"]}
MEMORY = {"enabled": True, "gate_roles": "all"}
KNOWLEDGE = {"enabled": False, "gate_roles": "all"}
```

Role options: `"all"` (everyone), `"creator"` (you only), `"tester"` (beta users), `"pro"` (paid users)

### `router_config.yaml`

Controls how incoming messages are classified — which messages go to AI, which trigger a card, which hit a service. The Duply team can help tune this after you describe your Duple's main use cases.

---

## Step 5 — PR and Deploy

Push your `duples/<duple_id>/` changes to the repo and open a PR. The Duply team reviews, merges, then:
- Rebuilds the Docker image
- Starts your Duple's `line-webhook-service` process on the Pi
- Confirms it's healthy

---

## Step 6 — LINE OA + Go Live

1. Create a LINE Official Account for your Duple at [developers.line.biz](https://developers.line.biz)
2. Send `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_CHANNEL_SECRET` to the Duply team via secure channel
3. The Duply team adds them to `duples/<duple_id>/.env` on the Pi and sets the webhook URL
4. Your Duple is live — add yourself as a friend on LINE and test

---

## After Launch

- **Edit prompts anytime** — connect to your schema, update `agent_profiles.duple_prompt`. No redeploy needed
- **Change gate_roles** — edit `duple_settings.py` + rebuild (Duply team does the rebuild)
- **Add users to roles** — update `{schema}.user_profiles.roles` column (TEXT[]) in your schema
- **Ingest knowledge docs** — send content to the Duply team; they run `knowledge/ingest.py`
