"""Pure business rules used by Tawan's reply and commerce handlers.

These functions do not call Supabase, LINE, or an LLM. They are deliberately
small so the runtime adapter can enforce the same rules before any write or
outbound message.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Mapping


class PolicyError(ValueError):
    """Raised when a proposed action violates a Tawan business rule."""


def can_bot_reply(state: str, paused_until: datetime | None, now: datetime) -> bool:
    """Return whether Tawan may answer a conversation at this instant."""
    if state == "bot_active":
        return True
    if state == "paused_until":
        return paused_until is not None and now >= paused_until
    return False


def idempotency_key(channel: str, event_id: str, action: str) -> str:
    """Create a stable, non-secret key for one inbound event action."""
    if not all((channel.strip(), event_id.strip(), action.strip())):
        raise PolicyError("channel, event_id, and action are required")
    raw = "|".join((channel.strip().lower(), event_id.strip(), action.strip().lower()))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_capture_commands(commands: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Validate model-proposed structured writes before execution."""
    allowed = {"interaction_event", "memory_candidate", "task", "approval", "order_update"}
    validated: list[dict[str, object]] = []
    for command in commands:
        command_type = command.get("type")
        if command_type not in allowed:
            raise PolicyError(f"unsupported capture command: {command_type!r}")
        if not command.get("idempotency_key"):
            raise PolicyError(f"{command_type} requires an idempotency_key")
        if command_type == "order_update" and command.get("state") == "paid":
            raise PolicyError("model output cannot mark an order paid")
        if command_type == "memory_candidate" and command.get("permanent") is True:
            raise PolicyError("permanent knowledge requires owner approval")
        validated.append(dict(command))
    return validated


@dataclass(frozen=True)
class PriceRule:
    kind: str
    amount: Decimal
    approved: bool = False
    active: bool = True
    priority: int = 0


PRICE_PRECEDENCE = {
    "customer": 0,
    "campaign": 1,
    "tier": 2,
    "quantity": 3,
    "wholesale": 3,
    "standard": 4,
}


def resolve_price(rules: Iterable[PriceRule], plan: str = "standard") -> PriceRule:
    """Choose the highest-precedence active, authorized price rule."""
    candidates = []
    for rule in rules:
        if rule.kind not in PRICE_PRECEDENCE:
            raise PolicyError(f"unknown price rule: {rule.kind!r}")
        if rule.amount < 0:
            raise PolicyError("price cannot be negative")
        if not rule.active:
            continue
        if rule.kind == "campaign" and plan != "pro":
            continue
        if rule.kind != "standard" and not rule.approved:
            continue
        candidates.append(rule)
    if not candidates:
        raise PolicyError("no authorized active price rule")
    return min(candidates, key=lambda rule: (PRICE_PRECEDENCE[rule.kind], -rule.priority))


def reserve_stock(on_hand: Decimal, reserved: Decimal, requested: Decimal) -> Decimal:
    """Return the new reserved quantity or reject an oversell."""
    if min(on_hand, reserved, requested) < 0:
        raise PolicyError("stock quantities cannot be negative")
    new_reserved = reserved + requested
    if new_reserved > on_hand:
        raise PolicyError("insufficient available stock")
    return new_reserved


ORDER_TRANSITIONS = {
    "draft": {"pending_confirmation", "cancelled", "expired"},
    "pending_confirmation": {"confirmed", "cancelled", "expired"},
    "confirmed": {"awaiting_payment", "cancelled", "expired"},
    "awaiting_payment": {"paid", "cancelled", "expired", "disputed"},
    "paid": {"in_progress", "refunded", "disputed"},
    "in_progress": {"completed", "refunded", "disputed"},
    "completed": {"refunded", "disputed"},
    "cancelled": set(),
    "expired": set(),
    "refunded": set(),
    "disputed": {"refunded"},
}


def validate_order_transition(current: str, requested: str, actor: str) -> None:
    """Validate an order transition and its minimum authority."""
    if requested not in ORDER_TRANSITIONS.get(current, set()):
        raise PolicyError(f"invalid order transition: {current} -> {requested}")
    if requested == "paid" and actor not in {"store_owner", "platform_admin"}:
        raise PolicyError("only an owner may mark an order paid in Phase 1")
