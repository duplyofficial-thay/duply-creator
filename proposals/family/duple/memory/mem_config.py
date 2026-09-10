"""
DRAFT — duples/dom/memory/mem_config.py

Per the 2026-07-28 platform update (commits 29cbbe3/3893ddb/dc3dc81), every
Duple gets a MemConfig declaring what memory.noter/memory.dream are allowed
to extract and observe. Non-finance archetypes default to an empty
observable_fields set (see provision_duple.py's _render_mem_config()) — this
draft customizes it for the family archetype instead of leaving the bare
default, since what Dom should notice about a kid (routine patterns, what
motivates them, what causes them to stall) is exactly the kind of thing
memory.dream should be consolidating over time.

A change to this file requires a Docker rebuild (docker compose build
dream-agent), per guide/03-domains.md — not a plain container restart like
duples/ config files normally get. Flag this to the Duply team as a
deploy-timing consideration, not something that takes effect on push alone.
"""

from archetypes import MemConfig

MEM_CONFIG = MemConfig(
    default_topics=["personal_facts", "habit_pattern", "family_dynamic"],
    observable_fields=frozenset({
        "focus_style",         # how this kid tends to approach tasks (e.g. needs short bursts, easily distracted, hyperfocuses)
        "motivation_triggers", # what actually gets them moving (competition, praise, specific rewards)
        "routine_challenges",  # recurring friction points (mornings, homework transitions, bedtime)
    }),
    holdings_topic=None,  # finance-only concept, not applicable here
)
