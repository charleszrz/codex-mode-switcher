"""Privacy-first local profile switching primitives."""

from .activation import account_activation_changes, api_activation_changes
from .profiles import ImportedProfile, import_profile
from .platform_paths import PlatformPaths, resolve_platform_paths
from .switch_plan import ConfigSwitchPlan, plan_api_switch
from .transactions import PlannedDelete, PlannedWrite, apply_changes, apply_writes

__all__ = ["ConfigSwitchPlan", "ImportedProfile", "PlatformPaths", "PlannedDelete", "PlannedWrite", "account_activation_changes", "api_activation_changes", "apply_changes", "apply_writes", "import_profile", "plan_api_switch", "resolve_platform_paths"]
