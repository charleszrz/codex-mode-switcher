"""Small, testable atomic writes with in-process rollback."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
from typing import Union

from .errors import TransactionError


@dataclass(frozen=True)
class PlannedWrite:
    path: Path
    content: bytes


@dataclass(frozen=True)
class PlannedDelete:
    path: Path


PlannedChange = Union[PlannedWrite, PlannedDelete]


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
    """Apply writes, restoring original bytes after any failure."""
    apply_changes(tuple(writes), writer)


def apply_changes(changes: Iterable[PlannedChange], writer: Writer = atomic_write) -> None:
    """Apply writes/deletes, restoring original bytes after any failure."""
    planned = tuple(changes)
    paths = [change.path.resolve() for change in planned]
    if len(paths) != len(set(paths)):
        raise TransactionError("A transaction cannot write the same path twice.")

    originals = {path: path.read_bytes() if path.exists() else None for path in paths}
    attempted: list[Path] = []
    try:
        for change in planned:
            attempted.append(change.path)
            if isinstance(change, PlannedWrite):
                writer(change.path, change.content)
                if change.path.read_bytes() != change.content:
                    raise OSError("Post-write verification failed.")
            else:
                change.path.unlink(missing_ok=True)
                if change.path.exists():
                    raise OSError("Post-delete verification failed.")
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
