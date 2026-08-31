from pathlib import Path
import unittest

from codex_mode_switcher.errors import ProfileValidationError
from codex_mode_switcher.platform_paths import resolve_platform_paths


class PlatformPathTests(unittest.TestCase):
    def test_macos_paths(self):
        paths = resolve_platform_paths("Darwin", Path("/home/tester"), {})
        self.assertEqual(paths.codex_home, Path("/home/tester/.codex"))
        self.assertEqual(paths.state_home, Path("/home/tester/Library/Application Support/Codex Mode Switcher"))

    def test_windows_paths_require_local_app_data(self):
        with self.assertRaises(ProfileValidationError):
            resolve_platform_paths("Windows", Path("D:/test-home"), {})
        paths = resolve_platform_paths("Windows", Path("D:/test-home"), {"LOCALAPPDATA": "D:/test-state"})
        self.assertEqual(paths.codex_home, Path("D:/test-home/.codex"))
        self.assertEqual(paths.state_home, Path("D:/test-state/Codex Mode Switcher"))

    def test_linux_paths_prefer_xdg_state_home(self):
        paths = resolve_platform_paths("Linux", Path("/home/tester"), {"XDG_STATE_HOME": "/var/state/tester"})
        self.assertEqual(paths.state_home, Path("/var/state/tester/codex-mode-switcher"))

    def test_linux_has_a_user_owned_fallback(self):
        paths = resolve_platform_paths("Linux", Path("/home/tester"), {})
        self.assertEqual(paths.state_home, Path("/home/tester/.local/state/codex-mode-switcher"))
