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
        self.assertEqual([migration.version for migration in self.migrations], [10])
        self.assertTrue(self.migrations[0].up_sql)
        self.assertTrue(self.migrations[0].down_sql)

    def test_plan_applies_missing_and_rolls_back_above_target(self):
        self.assertEqual([action for action, _ in plan(self.migrations, set())], ["apply"])
        self.assertEqual([action for action, _ in plan(self.migrations, {10}, target=0)], ["rollback"])

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
