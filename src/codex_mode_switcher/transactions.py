"""Small, testable atomic writes with in-process rollback."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import os
from pathlib import Path
import tempfile

from .errors import TransactionError


@dataclass(frozen=True)
class PlannedWrite:
    path: Path
    content: bytes


Writer = Callable[[Path, bytes], None]


def atomic_write(path: Path, content: bytes) -> None:
    """Replace a file without exposing a partial write at its final path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        if os.name != "nt":
            os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def apply_writes(writes: Iterable[PlannedWrite], writer: Writer = atomic_write) -> None:
    """Apply a small set of writes, restoring original bytes after any failure."""
    planned = tuple(writes)
    paths = [write.path.resolve() for write in planned]
    if len(paths) != len(set(paths)):
        raise TransactionError("A transaction cannot write the same path twice.")

    originals = {path: path.read_bytes() if path.exists() else None for path in paths}
    attempted: list[Path] = []
    try:
        for write in planned:
            attempted.append(write.path)
            writer(write.path, write.content)
            if write.path.read_bytes() != write.content:
                raise OSError("Post-write verification failed.")
    except Exception as error:
        restore_error: Exception | None = None
        for path in reversed(attempted):
            try:
                original = originals[path.resolve()]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, original)
            except Exception as rollback_failure:
                restore_error = rollback_failure
        detail = "Configuration write failed and was rolled back."
        if restore_error is not None:
            detail = "Configuration write failed and rollback was incomplete."
        raise TransactionError(detail) from error
