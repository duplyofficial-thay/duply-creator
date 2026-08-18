# Duply Creator Kit

Everything you need to build and launch a Duple on the Duply platform.

---

## What is a Duple?

**Duply** = the platform layer (identity, auth, routing, shared infra)  
**Duple** = one AI product built on Duply (e.g. Thay — finance assistant)  
**Agent** = a named component inside a Duple (e.g. `chat.reply`, `memory.dream`, `reach.alert`)

Users talk to Duples via **LINE**. Each Duple has its own persona, tools, and memory — isolated from every other Duple at the database level.

---

## Getting Started

1. Read [guide/01-concepts.md](guide/01-concepts.md) — vocabulary and mental model
2. Read [guide/02-onboarding.md](guide/02-onboarding.md) — step-by-step from zero to live
3. Go to [register/](register/) — copy `_template.yaml`, rename, fill in, push

---

## Files

| Path | What it is |
|---|---|
| `register/_template.yaml` | Blank registration config |
| `register/thay.yaml` | Real example — Thay (finance Duple) |
| `register/{your_id}.yaml` | Your registration file — add it here |
| `duples/{your_id}/` | Your Duple's code — scaffolded by Duply team after registration |
| `guide/01-concepts.md` | Core vocabulary and how the platform works |
| `guide/02-onboarding.md` | Full onboarding walkthrough |
| `guide/03-domains.md` | What each domain does and what you can configure |
| `guide/04-prompts.md` | How to edit your Duple's persona and prompts |
| `PATCH-NOTES.md` | Platform changelog |
| `docs/tawan/PRODUCT_SPEC.md` | Approved Tawan commerce product baseline and related design documents |
| `.agents/skills/tawan-project-handoff/` | Portable AI handoff workflow for resuming Tawan work from Git |
