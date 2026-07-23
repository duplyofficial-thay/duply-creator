# Onboarding — From Zero to Live Duple

## Who Does What

| Step | Creator | Duply Team |
|---|---|---|
| 1 | Add registration file, push | — |
| 2 | — | Provision schema + scaffold + push back |
| 3 | Pull, edit `duples/{id}/` locally | — |
| 4 | Push changes | Deploy on Pi → test via LINE |
| 5 | Edit prompts directly in DB | (no deploy needed) |

---

## Step 1 — Register Your Duple

Inside the `register/` folder:

1. Copy `_template.yaml` → rename to `{your_duple_id}.yaml`  
   (Use `thay.yaml` as a real reference — it's a live, working Duple)
2. Fill in every field
3. Commit and push
4. Notify the Duply team

The Duply team handles LINE setup end-to-end — you don't need a LINE account or tokens.

---

## Step 2 — Provisioning (Duply Team)

After receiving your registration file, the Duply team runs `scripts/provision_duple.py`, which does everything in one shot:

**Database (fully automated):**
- Creates Postgres schema `{duple_id}_ai` in the shared Supabase project
- Creates a native Postgres role scoped to that schema only
- Creates all tables (`user_profiles`, `interact_log`, `agent_profiles`, etc.)
- Seeds `{schema}.agent_profiles` with all 5 agents (correct `tools_enabled` per archetype)
- Seeds `public.duply_duples` with your Duple's metadata and persona
- Verifies isolation: confirms your role cannot read `thay_ai` or any other schema

**Scaffold (fully automated):**
- Generates `duples/{duple_id}/` in this repo and pushes it back

**Pi infrastructure (manual, done by team):**
- Creates LINE Official Account for your Duple (integrated with the Duply LIFF auth system)
- Configures Cloudflare tunnel → new hostname e.g. `webhook-{duple_id}.duply.org`
- Adds a new `line-webhook-service` entry to `infra/platform/docker-compose.yml`
- Registers the webhook URL in LINE Console

**You receive:**
- Postgres credentials (role name + password) — see below

**Save credentials immediately** — copy `duples/.env.example` to `duples/{your_id}/.env` and fill in:

```bash
cp duples/.env.example duples/{your_id}/.env
# then edit the file with your credentials
```

```
POSTGRES_HOST=db.fpjevusrpausqunjhubk.supabase.co
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_SCHEMA={your_id}_ai
POSTGRES_ROLE={your_id}_role
POSTGRES_PASSWORD=<the password the Duply team sent you>
```

This file is git-ignored — it will never be committed. Keep it only on your machine.

---

## Step 3 — Pull and Edit

```bash
git pull
```

You now have `duples/{your_id}/` with these files:

```
duples/{your_id}/
  duple_settings.py       ← domain gates, archetype, enabled triggers
  router_config.yaml      ← intent routing rules
  .env.example            ← env var reference (no real secrets here)
  chat/
    reply/
      context_builder.py  ← how your Duple assembles context for the LLM
```

Edit these files locally with Claude Code. Key files:

### `duple_settings.py`

Controls which domains are active and who can access them:

```python
ARCHETYPE = "finance"   # or "lifestyle", "commerce"

CHAT    = {"enabled": True, "gate_roles": "all"}
REACH   = {"enabled": True, "gate_roles": "creator", "enabled_triggers": ["price_above", "price_below"]}
MEMORY  = {"enabled": True, "gate_roles": "all"}
KNOWLEDGE = {"enabled": False, "gate_roles": "all"}
```

Role options: `"all"` (everyone), `"creator"` (you only), `"tester"` (beta users), `"pro"` (paid users)

### `router_config.yaml`

Routing rules — which messages trigger a card response vs go to AI. Claude Code can help you tune this after you describe your Duple's main use cases.

### `context_builder.py`

How your Duple assembles the LLM's context (user profile, memory, market data, etc.). This is the main file you'll iterate on as your Duple evolves.

---

## Step 4 — Deploy

Push your changes:

```bash
git add duples/{your_id}/
git commit -m "feat: update context and routing for {your_id}"
git push
```

Notify the Duply team → we pull → rebuild Docker image → redeploy → test via LINE.

---

## Step 5 — Edit Prompts (no redeploy needed)

Once your Duple is live, most tuning happens in Supabase — not code. Connect to your schema with the Postgres credentials from Step 2 and edit `{schema}.agent_profiles`.

See [04-prompts.md](04-prompts.md) for the exact table, columns, and safe edit patterns.

Changes to prompts are **live immediately** after a Redis cache expiry (~24h) or manual flush by the Duply team.

---

## After Launch

- **Expand access:** change `gate_roles` in `duple_settings.py` → push → team redeploys
- **Add users to a role:** update `{schema}.user_profiles.roles` (TEXT[]) directly in your schema
- **Ingest knowledge docs:** send content to the Duply team — they run `knowledge/ingest.py`
- **Enable broadcast:** contact Duply team to enable `reach.broadcast` once you have a use case
