from archetypes import MemConfig

MEM_CONFIG = MemConfig(
    default_topics=["personal_facts", "investment_pattern", "holding_thesis"],
    observable_fields=frozenset({
        "risk_appetite",
        "trading_style",
        "time_horizon",
        "investment_style",
    }),
    holdings_topic="holding_thesis",  # finance only — create/update actions on this topic may include "tickers": [...]
)
