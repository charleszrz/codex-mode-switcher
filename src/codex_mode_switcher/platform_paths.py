"""Resolve only documented per-user state locations for supported desktops."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .errors import ProfileValidationError


@dataclass(frozen=True)
class PlatformPaths:
    """User-owned locations; no global or administrator-owned paths are used."""

    codex_home: Path
    state_home: Path


def resolve_platform_paths(system: str, home: Path, environment: Mapping[str, str]) -> PlatformPaths:
    """Resolve paths deterministically so every platform rule can be tested."""
    if system == "Darwin":
        return PlatformPaths(
            codex_home=home / ".codex",
            state_home=home / "Library" / "Application Support" / "Codex Mode Switcher",
        )
    if system == "Windows":
        local_app_data = environment.get("LOCALAPPDATA")
        if not local_app_data:
            raise ProfileValidationError("LOCALAPPDATA is required on Windows.")
        return PlatformPaths(
            codex_home=home / ".codex",
            state_home=Path(local_app_data) / "Codex Mode Switcher",
        )
    if system == "Linux":
        xdg_state = environment.get("XDG_STATE_HOME")
        return PlatformPaths(
            codex_home=home / ".codex",
            state_home=Path(xdg_state) / "codex-mode-switcher" if xdg_state else home / ".local" / "state" / "codex-mode-switcher",
        )
    raise ProfileValidationError(f"Unsupported desktop platform: {system}.")
