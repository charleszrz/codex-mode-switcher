"""Build strict-privacy activation transactions without retaining credentials."""

from __future__ import annotations

import json
from pathlib import Path

from .errors import ProfileValidationError
from .switch_plan import ConfigSwitchPlan
from .transactions import PlannedChange, PlannedDelete, PlannedWrite


def api_activation_changes(
    config_path: Path,
    auth_path: Path,
    switch_plan: ConfigSwitchPlan,
    api_key: str,
) -> tuple[PlannedChange, ...]:
    """Prepare active API config/auth without retaining a profile credential copy."""
    if not api_key.strip():
        raise ProfileValidationError("An API key is required to activate an API profile.")
    auth = json.dumps({"auth_mode": "apikey", "OPENAI_API_KEY": api_key}, ensure_ascii=False).encode("utf-8") + b"\n"
    return (
        PlannedWrite(config_path, switch_plan.content.encode("utf-8")),
        PlannedWrite(auth_path, auth),
    )


def account_activation_changes(
    config_path: Path,
    auth_path: Path,
    account_config: str,
) -> tuple[PlannedChange, ...]:
    """Restore a non-auth account config and remove the active API credential."""
    if not account_config.strip():
        raise ProfileValidationError("An account configuration is required to return to account mode.")
    return (
        PlannedWrite(config_path, account_config.encode("utf-8")),
        PlannedDelete(auth_path),
    )
