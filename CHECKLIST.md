# Duple Launch Checklist

Quick reference for the Duply team. Detail for each step → `guide/02-onboarding.md`, `guide/03-domains.md`.

---

## Creator → Team

- [ ] `register/{duple_id}.yaml` filled and pushed

## Team — Provision

- [ ] `python scripts/provision_duple.py {duple_id}` (run from `duply-creator/`)
- [ ] Verify schema + role in Supabase
- [ ] Push creator repo — scaffold now in `duples/{duple_id}/`
- [ ] Send DB credentials to creator

## Creator — Content (can start here, no infra needed)

- [ ] Fill `chat.reply` system_prompt in `{schema}.agent_profiles` (Supabase)
- [ ] Review `context_builder.py` — wire any real-time context the Duple needs
- [ ] Edit `router_config.yaml` for Duple-specific keywords / service routes

## Team — Deploy infra (needs LINE OA creds from creator first)

- [ ] Add `{duple_id}-line-webhook-service` to `infra/platform/docker-compose.yml` on Pi
- [ ] Create `duples/{duple_id}/.env` on Pi with LINE creds
- [ ] `scp duples/{duple_id}/` to Pi
- [ ] `docker compose up -d {duple_id}-line-webhook-service`
- [ ] Add reach cron entry (if `REACH.enabled = True` and Duple has triggers)
- [ ] Cloudflare: `webhook-{duple_id}.duply.org` → `http://localhost:{PORT}`
- [ ] LINE Console: set webhook URL → verify

## Team + Creator — Test

- [ ] Send a message via LINE → confirm AI reply
- [ ] Check `{schema}.interact_log` — rows written correctly
- [ ] Check `{schema}.agent_call_log` — LLM call logged

## Open to users

- [ ] Set `CHAT.gate_roles = "all"` in `duple_settings.py`
- [ ] Container restart (contact Duply team)
