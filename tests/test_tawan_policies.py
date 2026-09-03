import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from duples.tawan.domain.policies import (
    PolicyError,
    PriceRule,
    can_bot_reply,
    idempotency_key,
    reserve_stock,
    resolve_price,
    validate_capture_commands,
    validate_order_transition,
)


class TawanPolicyTests(unittest.TestCase):
    def test_staff_pause_blocks_bot_until_expiry(self):
        now = datetime.now(timezone.utc)
        self.assertFalse(can_bot_reply("paused_by_staff", None, now))
        self.assertFalse(can_bot_reply("paused_until", None, now))
        self.assertFalse(can_bot_reply("paused_until", now + timedelta(minutes=5), now))
        self.assertTrue(can_bot_reply("paused_until", now - timedelta(minutes=1), now))

    def test_idempotency_key_is_stable_and_action_specific(self):
        first = idempotency_key("LINE", "evt-1", "reply")
        self.assertEqual(first, idempotency_key("line", "evt-1", "reply"))
        self.assertNotEqual(first, idempotency_key("line", "evt-1", "task"))

    def test_capture_commands_reject_unsafe_model_writes(self):
        with self.assertRaises(PolicyError):
            validate_capture_commands([{"type": "order_update", "state": "paid", "idempotency_key": "x"}])
        with self.assertRaises(PolicyError):
            validate_capture_commands([{"type": "memory_candidate", "permanent": True, "idempotency_key": "x"}])

    def test_price_precedence_and_pro_gate(self):
        rules = [
            PriceRule("standard", Decimal("100")),
            PriceRule("tier", Decimal("90"), approved=True),
            PriceRule("campaign", Decimal("50"), approved=True),
        ]
        self.assertEqual(resolve_price(rules).amount, Decimal("90"))
        self.assertEqual(resolve_price(rules, plan="pro").amount, Decimal("50"))

    def test_stock_and_order_authority_rules(self):
        self.assertEqual(reserve_stock(Decimal("10"), Decimal("3"), Decimal("2")), Decimal("5"))
        with self.assertRaises(PolicyError):
            reserve_stock(Decimal("10"), Decimal("9"), Decimal("2"))
        with self.assertRaises(PolicyError):
            validate_order_transition("awaiting_payment", "paid", "store_staff")
        validate_order_transition("awaiting_payment", "paid", "store_owner")


if __name__ == "__main__":
    unittest.main()
