import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVISION_SCRIPT = REPO_ROOT / "scripts" / "provision_duple.py"


def load_provision_module():
    spec = importlib.util.spec_from_file_location("provision_duple", PROVISION_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProvisionDupleUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provision_duple = load_provision_module()

    def test_sql_string_escape_doubles_single_quotes(self):
        self.assertEqual(self.provision_duple.sq("Tawan's store"), "Tawan''s store")

    def test_commerce_settings_keep_cards_disabled_by_default(self):
        rendered = self.provision_duple._render_duple_settings("commerce", {}, [])

        self.assertIn('ARCHETYPE = "commerce"', rendered)
        self.assertIn('"cards_enabled": False', rendered)
        self.assertIn('"gate_roles": "creator"', rendered)

    def test_finance_memory_config_keeps_holding_topic(self):
        rendered = self.provision_duple._render_mem_config("finance", "thay")

        self.assertIn('"holding_thesis"', rendered)
        self.assertIn('holdings_topic="holding_thesis"', rendered)

    def test_non_finance_memory_config_has_no_holding_topic(self):
        rendered = self.provision_duple._render_mem_config("commerce", "tawan_demo")

        self.assertIn('default_topics=["personal_facts"]', rendered)
        self.assertIn("holdings_topic=None", rendered)

    def test_tawan_registration_config_is_validated_before_provisioning(self):
        archetype, persona = self.provision_duple.validate_registration_config(
            {
                "duple_id": "tawan",
                "archetype": "commerce",
                "owner": "owner@example.com",
                "description": "demo",
                "persona": {"name": "Tawan"},
            },
            "tawan",
        )
        self.assertEqual(archetype, "commerce")
        self.assertEqual(persona["name"], "Tawan")


if __name__ == "__main__":
    unittest.main()
