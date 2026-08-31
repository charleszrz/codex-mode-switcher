"""Import only credential-free API profile configuration."""

from __future__ import annotations

from dataclasses import dataclass
import re
import tomllib
from urllib.parse import parse_qsl, urlparse

from .errors import ProfileValidationError


SENSITIVE_KEY = re.compile(r"(?:^|[_-])(api[_-]?key|token|authorization|password|secret)(?:$|[_-])", re.I)
SENSITIVE_VALUE = re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]{10,})")
PROFILE_ID = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class ImportedProfile:
    """A validated local configuration template without a credential value."""

    identifier: str
    label: str
    provider_id: str
    template: str


def profile_identifier(label: str) -> str:
    identifier = PROFILE_ID.sub("_", label.lower()).strip("_")
    if not identifier:
        raise ProfileValidationError("Profile name must contain a letter or number.")
    return identifier


def _has_sensitive_value(value: object, key: str = "") -> bool:
    if SENSITIVE_KEY.search(key):
        return True
    if isinstance(value, str):
        return bool(SENSITIVE_VALUE.search(value))
    if isinstance(value, dict):
        return any(_has_sensitive_value(child, str(child_key)) for child_key, child in value.items())
    if isinstance(value, list):
        return any(_has_sensitive_value(child) for child in value)
    return False


def _provider_from(parsed: dict[str, object]) -> tuple[str, dict[str, object]]:
    providers = parsed.get("model_providers")
    if not isinstance(providers, dict) or len(providers) != 1:
        raise ProfileValidationError("Import exactly one model provider configuration.")
    provider_id, provider = next(iter(providers.items()))
    if not isinstance(provider_id, str) or not isinstance(provider, dict):
        raise ProfileValidationError("The model provider configuration is invalid.")
    base_url = provider.get("base_url")
    if not isinstance(base_url, str):
        raise ProfileValidationError("The model provider must include a base_url.")
    parsed_url = urlparse(base_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ProfileValidationError("The model provider base_url must be an HTTP(S) URL.")
    if parsed_url.username or parsed_url.password or parsed_url.fragment:
        raise ProfileValidationError("The model provider base_url must not contain credentials or a fragment.")
    if any(SENSITIVE_KEY.fullmatch(key) for key, _ in parse_qsl(parsed_url.query, keep_blank_values=True)):
        raise ProfileValidationError("The model provider base_url must not contain a credential query parameter.")
    return provider_id, provider


def import_profile(label: str, template: str) -> ImportedProfile:
    """Validate a user-imported TOML template without persisting or logging it."""
    if not label.strip() or not template.strip():
        raise ProfileValidationError("A profile name and configuration are required.")
    try:
        parsed = tomllib.loads(template)
    except tomllib.TOMLDecodeError as error:
        raise ProfileValidationError("The imported configuration is not valid TOML.") from error
    if _has_sensitive_value(parsed):
        raise ProfileValidationError("Remove credentials, tokens, and secrets before importing a configuration.")
    provider_id, _ = _provider_from(parsed)
    return ImportedProfile(
        identifier=profile_identifier(label),
        label=label.strip(),
        provider_id=provider_id,
        template=template if template.endswith("\n") else f"{template}\n",
    )
