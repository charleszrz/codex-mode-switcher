from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codex_mode_switcher.cli import main


TEMPLATE = '''[model_providers.example]
base_url = "https://api.example.test/v1"
'''


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.state = self.root / "state"
        self.codex = self.root / "codex"
        self.codex.mkdir()
        (self.codex / "config.toml").write_text('model = "account"\n')
        self.template = self.root / "profile.toml"
        self.template.write_text(TEMPLATE)

    def tearDown(self):
        self.temporary.cleanup()

    def arguments(self, *command: str) -> list[str]:
        return ["--state-dir", str(self.state), "--codex-dir", str(self.codex), *command]

    def test_preview_does_not_display_provider_endpoint(self):
        self.assertEqual(main(self.arguments("add", "--label", "Example", "--config", str(self.template))), 0)
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(self.arguments("preview", "--profile", "example")), 0)
        self.assertIn("Will change", output.getvalue())
        self.assertNotIn("api.example.test", output.getvalue())

    def test_activate_api_requires_explicit_apply(self):
        main(self.arguments("add", "--label", "Example", "--config", str(self.template)))
        self.assertEqual(main(self.arguments("activate-api", "--profile", "example")), 1)
        self.assertFalse((self.codex / "auth.json").exists())

    def test_activate_api_uses_key_once_without_local_profile_copy(self):
        main(self.arguments("add", "--label", "Example", "--config", str(self.template)))
        with patch("codex_mode_switcher.cli.require_codex_stopped"), patch("codex_mode_switcher.cli.getpass.getpass", return_value="test-api-key"):
            self.assertEqual(main(self.arguments("activate-api", "--profile", "example", "--apply")), 0)
        self.assertTrue((self.codex / "auth.json").exists())
        self.assertNotIn("test-api-key", (self.state / "profiles.json").read_text())
