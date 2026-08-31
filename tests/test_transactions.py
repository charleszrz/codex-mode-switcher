import tempfile
from pathlib import Path
import unittest

from codex_mode_switcher.errors import TransactionError
from codex_mode_switcher.transactions import PlannedWrite, apply_writes


class TransactionTests(unittest.TestCase):
    def test_writes_all_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            apply_writes((PlannedWrite(root / "first", b"one"), PlannedWrite(root / "second", b"two")))
            self.assertEqual((root / "first").read_bytes(), b"one")
            self.assertEqual((root / "second").read_bytes(), b"two")

    def test_rolls_back_completed_writes_after_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            first.write_bytes(b"original")

            def fail_on_second(path: Path, content: bytes) -> None:
                if path == second:
                    raise OSError("simulated failure")
                path.write_bytes(content)

            with self.assertRaises(TransactionError):
                apply_writes((PlannedWrite(first, b"changed"), PlannedWrite(second, b"new")), fail_on_second)
            self.assertEqual(first.read_bytes(), b"original")
            self.assertFalse(second.exists())

    def test_rejects_duplicate_target(self):
        target = Path("duplicate")
        with self.assertRaises(TransactionError):
            apply_writes((PlannedWrite(target, b"one"), PlannedWrite(target, b"two")))

    def test_rolls_back_a_write_that_fails_after_replacing_the_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.write_bytes(b"original")

            def replace_then_fail(path: Path, content: bytes) -> None:
                path.write_bytes(content)
                raise OSError("simulated failure after write")

            with self.assertRaises(TransactionError):
                apply_writes((PlannedWrite(target, b"changed"),), replace_then_fail)
            self.assertEqual(target.read_bytes(), b"original")
