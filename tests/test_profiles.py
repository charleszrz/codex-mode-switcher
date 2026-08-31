import unittest

from codex_mode_switcher.errors import ProfileValidationError
from codex_mode_switcher.profiles import import_profile


VALID = '''model = "example-model"

[model_providers.example]
base_url = "https://api.example.test/v1"
wire_api = "responses"
'''


class ImportProfileTests(unittest.TestCase):
    def test_imports_one_credential_free_provider(self):
        profile = import_profile("Example API", VALID)
        self.assertEqual(profile.identifier, "example_api")
        self.assertEqual(profile.provider_id, "example")
        self.assertTrue(profile.template.endswith("\n"))

    def test_rejects_secret_key(self):
        with self.assertRaises(ProfileValidationError):
            import_profile("Example", VALID + '\napi_key = "redacted"\n')

    def test_rejects_multiple_providers(self):
        with self.assertRaises(ProfileValidationError):
            import_profile("Example", VALID + '\n[model_providers.other]\nbase_url = "https://other.example.test/v1"\n')

    def test_rejects_non_http_provider_url(self):
        with self.assertRaises(ProfileValidationError):
            import_profile("Example", VALID.replace("https://api.example.test/v1", "file:///tmp/provider"))

    def test_rejects_credential_in_provider_url(self):
        with self.assertRaises(ProfileValidationError):
            import_profile("Example", VALID.replace("https://api.example.test/v1", "https://user:pass@api.example.test/v1"))

    def test_rejects_credential_query_parameter(self):
        with self.assertRaises(ProfileValidationError):
            import_profile("Example", VALID.replace("https://api.example.test/v1", "https://api.example.test/v1?api_key=redacted"))
