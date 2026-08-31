import json
import tempfile
from pathlib import Path
import unittest

from codex_mode_switcher.activation import account_activation_changes, api_activation_changes
from codex_mode_switcher.errors import ProfileValidationError
from codex_mode_switcher.profiles import import_profile
from codex_mode_switcher.switch_plan import plan_api_switch
from codex_mode_switcher.transactions import apply_changes


TEMPLATE = '''[model_providers.example]
base_url = "https://api.example.test/v1"
'''


class ActivationTests(unittest.TestCase):
    def setUp(self):
        profile = import_profile("Example", TEMPLATE)
        self.plan = plan_api_switch('model = "existing"\n', profile)

    def test_api_activation_writes_only_current_auth_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.toml"
            auth = root / "auth.json"
            apply_changes(api_activation_changes(config, auth, self.plan, "test-api-key"))
            self.assertIn('model_provider = "example"', config.read_text())
            self.assertEqual(json.loads(auth.read_text())["auth_mode"], "apikey")

    def test_empty_api_key_is_rejected_before_writing(self):
        with self.assertRaises(ProfileValidationError):
            api_activation_changes(Path("config.toml"), Path("auth.json"), self.plan, "  ")

    def test_account_activation_removes_active_api_auth(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.toml"
            auth = root / "auth.json"
            auth.write_text('{"auth_mode":"apikey"}\n')
            apply_changes(account_activation_changes(config, auth, 'model = "account"\n'))
            self.assertEqual(config.read_text(), 'model = "account"\n')
            self.assertFalse(auth.exists())
