"""A deliberately small CLI for strict-privacy local profile switching."""

from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import platform
import sys
import tomllib

from .activation import account_activation_changes, api_activation_changes
from .errors import ProfileValidationError, TransactionError
from .platform_paths import resolve_platform_paths
from .process_guard import require_codex_stopped
from .profiles import import_profile
from .state import LocalState
from .switch_plan import plan_api_switch
from .transactions import apply_changes


def _paths(arguments: argparse.Namespace) -> tuple[Path, Path]:
    defaults = resolve_platform_paths(platform.system(), Path.home(), os.environ)
    return (
        Path(arguments.state_dir) if arguments.state_dir else defaults.state_home,
        Path(arguments.codex_dir) if arguments.codex_dir else defaults.codex_home,
    )


def _state(arguments: argparse.Namespace) -> tuple[LocalState, Path]:
    state_dir, codex_dir = _paths(arguments)
    state = LocalState(state_dir)
    state.initialize()
    return state, codex_dir


def _require_apply(arguments: argparse.Namespace) -> None:
    if not arguments.apply:
        raise ProfileValidationError("Preview only. Run again with --apply after closing Codex to make this change.")


def _current_config(codex_dir: Path) -> tuple[Path, str]:
    path = codex_dir / "config.toml"
    try:
        return path, path.read_text(encoding="utf-8")
    except OSError as error:
        raise ProfileValidationError("No readable Codex configuration was found.") from error


def command_add(arguments: argparse.Namespace) -> None:
    state, _ = _state(arguments)
    template = Path(arguments.config).read_text(encoding="utf-8")
    stored = state.add_profile(import_profile(arguments.label, template))
    print(f"Added profile: {stored.label} ({stored.identifier})")


def command_list(arguments: argparse.Namespace) -> None:
    state, _ = _state(arguments)
    for profile in state.list_profiles():
        print(f"{profile.identifier}\t{profile.label}\t{profile.provider_id}")


def command_capture_account(arguments: argparse.Namespace) -> None:
    state, codex_dir = _state(arguments)
    _, content = _current_config(codex_dir)
    try:
        parsed = tomllib.loads(content)
    except tomllib.TOMLDecodeError as error:
        raise ProfileValidationError("The current Codex configuration is not valid TOML.") from error
    if "model_provider" in parsed:
        raise ProfileValidationError("Do not capture an API configuration as the account baseline.")
    _require_apply(arguments)
    state.save_account_config(content)
    print("Saved the local account configuration. Authentication was not read or copied.")


def command_preview(arguments: argparse.Namespace) -> None:
    state, codex_dir = _state(arguments)
    config_path, current = _current_config(codex_dir)
    profile = state.profile(arguments.profile)
    plan = plan_api_switch(current, profile)
    print(f"Profile: {profile.label}")
    print(f"Config: {config_path.name}")
    print("Will change: " + ", ".join(plan.touched))
    print("No credential is read, stored, or displayed during preview.")


def command_activate_api(arguments: argparse.Namespace) -> None:
    state, codex_dir = _state(arguments)
    config_path, current = _current_config(codex_dir)
    profile = state.profile(arguments.profile)
    plan = plan_api_switch(current, profile)
    _require_apply(arguments)
    require_codex_stopped()
    api_key = getpass.getpass("API key (used once; not retained by this tool): ")
    apply_changes(api_activation_changes(config_path, codex_dir / "auth.json", plan, api_key))
    print("API profile activated. Start Codex manually after confirming it was fully closed.")


def command_activate_account(arguments: argparse.Namespace) -> None:
    state, codex_dir = _state(arguments)
    _require_apply(arguments)
    require_codex_stopped()
    apply_changes(account_activation_changes(codex_dir / "config.toml", codex_dir / "auth.json", state.account_config()))
    print("Account configuration restored. Sign in directly in Codex; no account authentication was restored.")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(prog="codex-mode-switcher", description="Privacy-first local Codex profile switching")
    value.add_argument("--state-dir", help="Override local state location for testing or portable use.")
    value.add_argument("--codex-dir", help="Override the Codex configuration directory for testing or portable use.")
    commands = value.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="Import one credential-free API profile.")
    add.add_argument("--label", required=True)
    add.add_argument("--config", required=True, help="A TOML file that does not contain a credential.")
    add.set_defaults(handler=command_add)

    listing = commands.add_parser("list", help="List local API profiles without displaying endpoints.")
    listing.set_defaults(handler=command_list)

    capture = commands.add_parser("capture-account", help="Save the current non-API config as the local account baseline.")
    capture.add_argument("--apply", action="store_true")
    capture.set_defaults(handler=command_capture_account)

    preview = commands.add_parser("preview", help="Preview an API profile switch without writing files.")
    preview.add_argument("--profile", required=True)
    preview.set_defaults(handler=command_preview)

    api = commands.add_parser("activate-api", help="Activate an API profile after explicit confirmation.")
    api.add_argument("--profile", required=True)
    api.add_argument("--apply", action="store_true")
    api.set_defaults(handler=command_activate_api)

    account = commands.add_parser("activate-account", help="Restore account config and remove active API authentication.")
    account.add_argument("--apply", action="store_true")
    account.set_defaults(handler=command_activate_account)
    return value


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        arguments.handler(arguments)
    except (OSError, ProfileValidationError, TransactionError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0
