"""Build an API switch preview without reading or writing authentication state."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import tomllib

from .errors import ProfileValidationError
from .profiles import ImportedProfile


TABLE_HEADER = re.compile(r"^\s*\[([^]]+)]\s*$")


@dataclass(frozen=True)
class ConfigSwitchPlan:
    """A candidate config and the deliberately small set of touched settings."""

    content: str
    touched: tuple[str, ...]


def _top_level_value(content: str, key: str, value: object) -> str:
    lines = content.splitlines(keepends=True)
    end = next((index for index, line in enumerate(lines) if TABLE_HEADER.match(line)), len(lines))
    replacement = f"{key} = {json.dumps(value)}\n" if isinstance(value, str) else f"{key} = {str(value).lower()}\n"
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
    for index in range(end):
        if pattern.match(lines[index]):
            lines[index] = replacement
            return "".join(lines)
    lines.insert(end, replacement)
    return "".join(lines)


def _section(content: str, name: str) -> str:
    lines = content.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line.strip() == f"[{name}]"), None)
    if start is None:
        raise ProfileValidationError("The imported provider table is missing.")
    end = next((index for index in range(start + 1, len(lines)) if TABLE_HEADER.match(lines[index])), len(lines))
    return "".join(lines[start:end]).rstrip() + "\n"


def _replace_section(content: str, name: str, replacement: str) -> str:
    lines = content.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line.strip() == f"[{name}]"), None)
    replacement_lines = replacement.rstrip().splitlines(keepends=True)
    if replacement_lines and not replacement_lines[-1].endswith("\n"):
        replacement_lines[-1] += "\n"
    if start is None:
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.extend(replacement_lines)
        return "".join(lines)
    end = next((index for index in range(start + 1, len(lines)) if TABLE_HEADER.match(lines[index])), len(lines))
    lines[start:end] = replacement_lines
    return "".join(lines)


def plan_api_switch(current_config: str, profile: ImportedProfile) -> ConfigSwitchPlan:
    """Return a validated API-mode config candidate without persisting it."""
    try:
        tomllib.loads(current_config)
    except tomllib.TOMLDecodeError as error:
        raise ProfileValidationError("The current Codex configuration is not valid TOML.") from error

    provider_table = f"model_providers.{profile.provider_id}"
    provider_fragment = _section(profile.template, provider_table)
    candidate = _top_level_value(current_config, "model_provider", profile.provider_id)
    candidate = _top_level_value(candidate, "forced_login_method", "api")
    candidate = _top_level_value(candidate, "disable_response_storage", True)
    candidate = _replace_section(candidate, provider_table, provider_fragment)
    try:
        tomllib.loads(candidate)
    except tomllib.TOMLDecodeError as error:
        raise ProfileValidationError("The generated configuration is not valid TOML.") from error
    return ConfigSwitchPlan(
        content=candidate if candidate.endswith("\n") else f"{candidate}\n",
        touched=("model_provider", "forced_login_method", "disable_response_storage", provider_table),
    )
