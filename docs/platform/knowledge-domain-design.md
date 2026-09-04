# Knowledge Domain — Design

Scope: `knowledge.extract` + the `get_knowledge` query tool — Thay's fourth
context source (alongside PT/BF/NS), distilled analyst reasoning instead of
raw data. For current schema/config/pipeline-step facts see
`knowledge-domain-reference.md`. Supersedes `docs/archive/kb-engine-design.md`
(the pre-build draft — kept for its still-valid legal-posture rationale;
this doc describes decisions made while actually building it).

---

## Why this exists

Thay currently answers from PT/BF/NS ctx (price, fundamentals, news) — all
*data*, no *opinion of its own*. Knowledge adds reasoning (thesis,
structural risk, industry context) paraphrased from public analyst
write-ups, so Thay can form an original point of view instead of only
reporting numbers.

## Domain placement: its own domain, not a tool

Originally scaffolded as a single tool under `platform/tools/generic/` —
reclassified to its own domain (`platform/knowledge/`) once it became clear
this is a real pipeline (extract → validate → anonymize → embed → store),
not a single function call. `get_knowledge.py` (the tool the LLM calls to
*query* this domain) still lives in `platform/tools/generic/` — that split
mirrors how `pt-service`/`bf-service` (data engines) are separate from
`get_stock.py` (the tool that calls them): the engine owns the pipeline, the
tool owns the LLM-facing query surface.

## Legal posture (non-negotiable, unchanged from the original plan)

- **"Public" ≠ "no copyright."** Never store raw article text — extract,
  then discard the original immediately. No field, table, or cache holds
  source text past the extraction step (`ingest.py`'s own docstring states
  this explicitly as a "Legal invariant").
- **Never store real analyst names/article titles.** `source_id` is a
  one-way `HMAC-SHA256(canonical_url, KNOWLEDGE_SOURCE_SALT)` hash, not a
  name.
- **Extraction is validated, not just prompted** — an n-gram overlap check
  against the raw source hard-fails any chunk too close to source wording
  (numbers/tickers/dates exempted).
- Thay never attributes a view to a named real person — reasoning is folded
  into Thay's own voice.
- Not legal advice — flag for actual counsel review before scaling revenue
  on this feature.

## Architecture: in-process module, not a standalone service

The original plan proposed a separate `knowledge-engine/` service with its
own systemd unit and port (same pattern as `pt-engine-set/`). Built instead
as a plain module (`platform/knowledge/`), called directly by the ingest CLI
and by `get_knowledge.py` at query time — no HTTP hop, no separate deploy.
Justified by call pattern: ingestion is manual/batch (a human runs a CLI),
and query happens inside a process that already has the embedding client
loaded — there was no concurrent-scaling or separate-deploy-cadence reason
to pay the HTTP tax pt/bf/ns pay for being genuinely shared, high-frequency
engines.

## Schema: per-Duple table, not a shared table with a tenant column

Went through two revisions before landing here: first a single
`public.knowledge_entries` with a `duple_id` scoping column, then moved to a
per-Duple table — matching the schema-per-Duple pattern the rest of the
platform uses (`{duple}_ai.*`). The RPC (`public.match_knowledge`) has to
live in `public` regardless — PostgREST can't resolve functions via
`Accept-Profile` the way it does for table reads — but it routes to the
right schema dynamically via `format('... FROM %I.knowledge_entries ...',
p_duple_id || '_ai')`. **No `DEFAULT` on `p_duple_id`** — every caller must
supply it explicitly, the same "explicit over silently-defaulting-to-thay"
discipline as `CardConfig`/`ArchetypeConfig` elsewhere in the platform. This
means a second Duple's KB needs zero RPC changes — just her own
`{duple}_ai.knowledge_entries` table and ingested content.

## Agent registration follows the dream/noter two-part pattern

`ingest.py`'s extraction step is itself an LLM agent (`agent_id =
"knowledge.extract"`), registered exactly like `memory.dream`/`memory.noter`:
locked platform template in `public.agent_profiles.system_prompt` (with a
`{categories}` placeholder), Duple-owned fill-in content in
`{duple}_ai.agent_profiles.duple_prompt.categories`. Reusing this pattern
instead of inventing a new prompt-storage shape for knowledge kept the
"platform template + Duple override" model uniform across every
LLM-calling agent in the platform, not knowledge-specific.

## Retrieval floor: tuned empirically, not guessed

`MIN_SIMILARITY` was set via `eval_retrieval.py` against a real test corpus
rather than picked arbitrarily: EN-relevant queries scored 0.55-0.66,
TH-relevant 0.40-0.49 (cross-lingual penalty ~0.15, still cleanly separated
from noise), adjacent-irrelevant ceiling 0.347, off-topic ~0.0. The floor
sits between the adjacent-irrelevant ceiling and the TH-relevant floor —
this needs re-tuning once the corpus grows past this test set's size, since
a floor tuned on ~10 chunks is not guaranteed to hold at real volume. Every
returned chunk carries `published_date` so the model can communicate age
naturally ("this view is from ~2 months ago") — the model never decides
exclusion; that's `expiry_date` (hard cut, SQL) and `min_similarity` (hard
floor, SQL), both deterministic, not left to LLM judgment.

## Gap vs. the original plan — not silently carried forward

The original draft specified a **two-mechanism freshness model**:
`expiry_date` (hard cut, implemented) plus a **soft-decay rerank** in Python
(`HALF_LIFE` by `validity_type`, blending similarity + decay). **The
soft-decay half was never built** — checked directly against the current
code, no decay/rerank logic exists anywhere. Today's ranking is
similarity-only past the `expiry_date`/`min_similarity` cuts. Not a bug —
the original plan itself said this needs "a few real examples from
friend-test logs" before it's worth building — but worth stating explicitly
rather than letting the old plan doc imply it shipped.

## Deferred / explicitly not built

- Soft-decay reranking (see gap above)
- Contradiction/supersede detection between entries — revisit once entry
  volume per ticker is high enough to actually collide
- Automated crawler ingestion — manual curation (`ingest.py` CLI) only, for
  now
- A second Duple's knowledge base — RPC is ready (dynamic `p_duple_id`
  routing), but no `grace_ai.knowledge_entries` table or content exists yet
