import unittest

from codex_mode_switcher.errors import ProfileValidationError
from codex_mode_switcher.profiles import import_profile
from codex_mode_switcher.switch_plan import plan_api_switch


TEMPLATE = '''model = "example-model"

[model_providers.example]
base_url = "https://api.example.test/v1"
wire_api = "responses"
'''


class SwitchPlanTests(unittest.TestCase):
    def setUp(self):
        self.profile = import_profile("Example API", TEMPLATE)

    def test_adds_only_expected_api_settings(self):
        plan = plan_api_switch('model = "existing"\n[features]\nmemories = true\n', self.profile)
        self.assertEqual(plan.touched, ("model_provider", "forced_login_method", "disable_response_storage", "model_providers.example"))
        self.assertIn('model_provider = "example"', plan.content)
        self.assertIn('forced_login_method = "api"', plan.content)
        self.assertIn("disable_response_storage = true", plan.content)
        self.assertIn("[features]\nmemories = true", plan.content)
        self.assertIn("[model_providers.example]", plan.content)

    def test_replaces_an_existing_provider_table_without_duplicates(self):
        current = '''model_provider = "example"

[model_providers.example]
base_url = "https://old.example.test/v1"
'''
        plan = plan_api_switch(current, self.profile)
        self.assertEqual(plan.content.count("[model_providers.example]"), 1)
        self.assertIn("https://api.example.test/v1", plan.content)
        self.assertNotIn("https://old.example.test/v1", plan.content)

    def test_rejects_invalid_current_config(self):
        with self.assertRaises(ProfileValidationError):
            plan_api_switch("[broken", self.profile)
