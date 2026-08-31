import tempfile
from pathlib import Path
import unittest

from codex_mode_switcher.errors import ProfileValidationError
from codex_mode_switcher.profiles import import_profile
from codex_mode_switcher.state import LocalState


TEMPLATE = '''[model_providers.example]
base_url = "https://api.example.test/v1"
'''


class LocalStateTests(unittest.TestCase):
    def test_stores_only_credential_free_template_and_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = LocalState(Path(temporary) / "state")
            stored = state.add_profile(import_profile("Example", TEMPLATE))
            self.assertEqual(stored.identifier, "example")
            self.assertEqual(state.list_profiles(), (stored,))
            self.assertEqual(state.profile("example").template, TEMPLATE)
            content = (Path(temporary) / "state" / "profiles.json").read_text()
            self.assertNotIn("api_key", content.lower())

    def test_rejects_duplicate_profile_identifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = LocalState(Path(temporary) / "state")
            state.add_profile(import_profile("Example", TEMPLATE))
            with self.assertRaises(ProfileValidationError):
                state.add_profile(import_profile("Example", TEMPLATE))

    def test_saves_account_configuration_separately_from_auth(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = LocalState(Path(temporary) / "state")
            state.save_account_config('model = "account"\n')
            self.assertEqual(state.account_config(), 'model = "account"\n')
            self.assertFalse((Path(temporary) / "state" / "auth.json").exists())
