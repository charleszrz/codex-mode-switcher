"""Local, access-restricted storage for credential-free profile templates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path

from .errors import ProfileValidationError
from .profiles import ImportedProfile
from .transactions import PlannedWrite, apply_writes


@dataclass(frozen=True)
class StoredProfile:
    identifier: str
    label: str
    provider_id: str
    template_file: str


class LocalState:
    """Persist non-secret templates locally; API keys are intentionally absent."""

    def __init__(self, root: Path):
        self.root = root
        self.registry_path = root / "profiles.json"
        self.templates_path = root / "profiles"
        self.account_config_path = root / "account.toml"

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)
        if os.name != "nt":
            os.chmod(self.root, 0o700)
            os.chmod(self.templates_path, 0o700)
        if not self.registry_path.exists():
            self._write_registry(())

    def _read_registry(self) -> tuple[StoredProfile, ...]:
        self.initialize()
        try:
            value = json.loads(self.registry_path.read_text(encoding="utf-8"))
            profiles = value.get("profiles", []) if isinstance(value, dict) else []
            return tuple(StoredProfile(**item) for item in profiles if isinstance(item, dict))
        except (OSError, ValueError, TypeError) as error:
            raise ProfileValidationError("The local profile registry is invalid.") from error

    def _write_registry(self, profiles: tuple[StoredProfile, ...]) -> None:
        content = json.dumps({"version": 1, "profiles": [asdict(profile) for profile in profiles]}, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        apply_writes((PlannedWrite(self.registry_path, content),))

    def list_profiles(self) -> tuple[StoredProfile, ...]:
        return self._read_registry()

    def add_profile(self, profile: ImportedProfile) -> StoredProfile:
        existing = self._read_registry()
        if any(item.identifier == profile.identifier for item in existing):
            raise ProfileValidationError("A profile with this name already exists.")
        stored = StoredProfile(
            identifier=profile.identifier,
            label=profile.label,
            provider_id=profile.provider_id,
            template_file=f"{profile.identifier}.toml",
        )
        template_path = self.templates_path / stored.template_file
        registry = existing + (stored,)
        registry_content = json.dumps({"version": 1, "profiles": [asdict(item) for item in registry]}, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        apply_writes((
            PlannedWrite(template_path, profile.template.encode("utf-8")),
            PlannedWrite(self.registry_path, registry_content),
        ))
        return stored

    def profile(self, identifier: str) -> ImportedProfile:
        stored = next((item for item in self._read_registry() if item.identifier == identifier), None)
        if stored is None:
            raise ProfileValidationError("The selected profile does not exist.")
        template_path = self.templates_path / stored.template_file
        try:
            template = template_path.read_text(encoding="utf-8")
        except OSError as error:
            raise ProfileValidationError("The selected profile template is unavailable.") from error
        return ImportedProfile(stored.identifier, stored.label, stored.provider_id, template)

    def save_account_config(self, content: str) -> None:
        if not content.strip():
            raise ProfileValidationError("The account configuration cannot be empty.")
        apply_writes((PlannedWrite(self.account_config_path, content.encode("utf-8")),))

    def account_config(self) -> str:
        try:
            return self.account_config_path.read_text(encoding="utf-8")
        except OSError as error:
            raise ProfileValidationError("No local account configuration has been captured.") from error
