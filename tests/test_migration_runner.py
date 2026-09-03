import json
import unittest
from pathlib import Path

from scripts.migration_runner import load_migrations, plan, render_sql


REPO_ROOT = Path(__file__).resolve().parents[1]


class MigrationRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.migrations = load_migrations(REPO_ROOT / "scripts" / "migrations")

    def test_manifest_is_ordered_and_reversible(self):
        self.assertEqual([migration.version for migration in self.migrations], [10, 20, 30])
        self.assertTrue(all(migration.up_sql and migration.down_sql for migration in self.migrations))

    def test_commerce_migration_contains_all_owned_data_layers(self):
        rendered = render_sql(self.migrations[1].up_sql, "tawan_demo_ai", "tawan_demo")
        for table in (
            "store_settings", "customers", "customer_memories", "consent_records",
            "interaction_events", "sales_journeys", "tasks", "approvals",
            "catalog_items", "inventory_balances", "price_rules", "transactions",
            "payments", "payment_evidence", "knowledge_candidates",
            "analytics_events", "audit_events",
        ):
            self.assertIn(f"tawan_demo_ai.{table}", rendered)
        self.assertNotIn("__SCHEMA__", rendered)

    def test_plan_applies_missing_and_rolls_back_above_target(self):
        self.assertEqual([action for action, _ in plan(self.migrations, set())], ["apply", "apply", "apply"])
        self.assertEqual([action for action, _ in plan(self.migrations, {10, 20, 30}, target=0)], ["rollback", "rollback", "rollback"])

    def test_plan_rejects_skipping_a_migration(self):
        with self.assertRaises(ValueError):
            plan(self.migrations, {20})

    def test_operational_migration_contains_pilot_safety_records(self):
        rendered = render_sql(self.migrations[2].up_sql, "tawan_demo_ai", "tawan_demo")
        for table in (
            "conversation_controls", "outbound_messages", "usage_ledger",
            "customer_contact_controls", "transaction_amendments", "shipments",
            "returns", "schema_migration_history", "job_runs", "store_entitlements",
            "tax_configs", "processing_activities",
        ):
            self.assertIn(f"tawan_demo_ai.{table}", rendered)

    def test_render_sql_rejects_unsafe_identifiers(self):
        with self.assertRaises(ValueError):
            render_sql("select 1", "tawan_ai; drop schema public", "tawan")

    def test_fixture_covers_isolated_demo_businesses(self):
        fixture = REPO_ROOT / "tests" / "fixtures" / "tawan_stores.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))
        stores = data["stores"]
        self.assertEqual(len(stores), 6)
        self.assertEqual(len({store["store_id"] for store in stores}), 6)
        self.assertEqual(len({store["schema"] for store in stores}), 6)
        self.assertIn("construction", {store["business"] for store in stores})


if __name__ == "__main__":
    unittest.main()
