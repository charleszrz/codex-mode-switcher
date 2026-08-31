import subprocess
import unittest

from codex_mode_switcher.errors import ProfileValidationError
from codex_mode_switcher.process_guard import codex_is_running, require_codex_stopped


def result(code: int, output: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], code, output, "")


class ProcessGuardTests(unittest.TestCase):
    def test_detects_windows_chatgpt_process(self):
        running = codex_is_running("Windows", lambda *args, **kwargs: result(0, "ChatGPT.exe 123 Console"))
        self.assertTrue(running)

    def test_detects_unix_client_process(self):
        def runner(command, **kwargs):
            return result(0, "123\n") if command[-1] == "Codex" else result(1)

        self.assertTrue(codex_is_running("Darwin", runner))

    def test_allows_when_no_supported_process_exists(self):
        self.assertFalse(codex_is_running("Linux", lambda *args, **kwargs: result(1)))

    def test_blocks_activation_when_client_is_running(self):
        with self.assertRaises(ProfileValidationError):
            require_codex_stopped("Darwin", lambda *args, **kwargs: result(0))
