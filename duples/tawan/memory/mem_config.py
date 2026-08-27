from archetypes import MemConfig

# observable_fields: add archetype-specific JSONB fields from user_profiles.archetype_data
# that dream/noter should be allowed to observe and update.
MEM_CONFIG = MemConfig(
    default_topics=["personal_facts"],
    observable_fields=frozenset(),
    holdings_topic=None,
)
