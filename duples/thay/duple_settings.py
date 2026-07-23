ARCHETYPE = "finance"

CHAT = {
    "gate_roles": "all",
}

REACH = {
    "enabled": True,
    "gate_roles": "creator",
    "enabled_triggers": ["price_above", "price_below", "reminder"],
}

MEMORY = {
    "enabled": True,
    "gate_roles": "all",
}

KNOWLEDGE = {
    "enabled": False,
    "gate_roles": "creator",
}
