"""Privacy-first local profile switching primitives."""

from .activation import account_activation_changes, api_activation_changes
from .profiles import ImportedProfile, import_profile
from .platform_paths import PlatformPaths, resolve_platform_paths
from .process_guard import codex_is_running, require_codex_stopped
from .switch_plan import ConfigSwitchPlan, plan_api_switch
from .transactions import PlannedDelete, PlannedWrite, apply_changes, apply_writes

__all__ = ["ConfigSwitchPlan", "ImportedProfile", "PlatformPaths", "PlannedDelete", "PlannedWrite", "account_activation_changes", "api_activation_changes", "apply_changes", "apply_writes", "codex_is_running", "import_profile", "plan_api_switch", "require_codex_stopped", "resolve_platform_paths"]
