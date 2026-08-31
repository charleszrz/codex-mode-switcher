"""Conservative process checks before modifying Codex configuration."""

from __future__ import annotations

from collections.abc import Callable
import platform
import subprocess

from .errors import ProfileValidationError


Runner = Callable[..., subprocess.CompletedProcess[str]]


def codex_is_running(system: str, runner: Runner = subprocess.run) -> bool:
    """Detect supported desktop clients without inspecting their process arguments."""
    if system == "Windows":
        result = runner(["tasklist", "/FI", "IMAGENAME eq ChatGPT.exe", "/NH"], capture_output=True, text=True, check=False)
        return "ChatGPT.exe".lower() in result.stdout.lower()
    if system in {"Darwin", "Linux"}:
        for name in ("ChatGPT", "Codex", "chatgpt", "codex"):
            result = runner(["pgrep", "-x", name], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return True
        return False
    raise ProfileValidationError(f"Unsupported desktop platform: {system}.")


def require_codex_stopped(system: str | None = None, runner: Runner = subprocess.run) -> None:
    if codex_is_running(system or platform.system(), runner):
        raise ProfileValidationError("Close Codex completely before switching profiles.")
