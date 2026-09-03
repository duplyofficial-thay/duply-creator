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
| `docs/tawan/TASK_BREAKDOWN.md` | Atomic Tawan tasks, dependencies, status, and acceptance evidence |
| `docs/tawan/CURRENT_TASK_STATUS.md` | Current status of all 149 Tawan cards, blockers, help needed, and next order |
| `docs/tawan/PHASE_1_ROADBLOCKS.md` | Duply platform blockers and phase-by-phase feature plan |
| `docs/tawan/TESTING.md` | Supported local test commands and current Tawan test scope |
| `docs/tawan/notion-import/` | Validated Tawan task and Sprint CSV package for safe Notion synchronization |
| `.agents/skills/tawan-project-handoff/` | Portable AI handoff workflow for resuming Tawan work from Git |

---

## Testing

Run the current local test baseline from the repository root:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
PYTHONPYCACHEPREFIX=/tmp/duply-creator-pycache python3 -m compileall scripts duples
```

See [docs/tawan/TESTING.md](docs/tawan/TESTING.md) for scope, dependency notes, and the next migration-test milestones.
