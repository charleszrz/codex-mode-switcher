"""Small local-only desktop UI for the strict-privacy workflow."""

from __future__ import annotations

from pathlib import Path
import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import tomllib

from .activation import account_activation_changes, api_activation_changes
from .errors import ProfileValidationError, TransactionError
from .platform_paths import resolve_platform_paths
from .process_guard import require_codex_stopped
from .profiles import import_profile
from .state import LocalState, StoredProfile
from .switch_plan import plan_api_switch
from .transactions import apply_changes


class SwitcherApp:
    def __init__(self, root: tk.Tk, state: LocalState, codex_dir: Path):
        self.root = root
        self.state = state
        self.codex_dir = codex_dir
        root.title("Codex Mode Switcher")
        root.minsize(620, 410)

        tk.Label(root, text="Codex Mode Switcher", font=("TkDefaultFont", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 4))
        tk.Label(root, text="Local only · No telemetry · No account authentication backup", foreground="#356859").pack(anchor="w", padx=20)

        body = tk.Frame(root)
        body.pack(fill="both", expand=True, padx=20, pady=18)
        self.profiles = tk.Listbox(body, height=10, exportselection=False)
        self.profiles.pack(side="left", fill="both", expand=True)
        actions = tk.Frame(body)
        actions.pack(side="right", fill="y", padx=(16, 0))
        for label, command in (
            ("Import API profile", self.import_profile),
            ("Preview selected", self.preview),
            ("Activate selected API", self.activate_api),
            ("Capture account config", self.capture_account),
            ("Return to account", self.activate_account),
        ):
            tk.Button(actions, text=label, command=command, width=24).pack(fill="x", pady=3)

        self.status = tk.StringVar(value="Choose or import a credential-free API profile.")
        tk.Label(root, textvariable=self.status, anchor="w", wraplength=560).pack(fill="x", padx=20, pady=(0, 20))
        self.reload_profiles()

    def reload_profiles(self) -> None:
        self.profiles.delete(0, tk.END)
        for profile in self.state.list_profiles():
            self.profiles.insert(tk.END, f"{profile.label}  ·  {profile.identifier}")

    def selected_profile(self) -> StoredProfile:
        selection = self.profiles.curselection()
        if not selection:
            raise ProfileValidationError("Select an API profile first.")
        return self.state.list_profiles()[selection[0]]

    def current_config(self) -> tuple[Path, str]:
        path = self.codex_dir / "config.toml"
        try:
            return path, path.read_text(encoding="utf-8")
        except OSError as error:
            raise ProfileValidationError("No readable Codex configuration was found.") from error

    def run_action(self, action) -> None:
        try:
            action()
        except (OSError, ProfileValidationError, TransactionError) as error:
            messagebox.showerror("Codex Mode Switcher", str(error), parent=self.root)

    def import_profile(self) -> None:
        def action() -> None:
            source = filedialog.askopenfilename(parent=self.root, title="Choose a credential-free TOML configuration", filetypes=[("TOML", "*.toml"), ("All files", "*")])
            if not source:
                return
            label = simpledialog.askstring("Profile name", "Name this API profile:", parent=self.root)
            if label is None:
                return
            template = Path(source).read_text(encoding="utf-8")
            stored = self.state.add_profile(import_profile(label, template))
            self.reload_profiles()
            self.status.set(f"Imported {stored.label}. No credential was stored.")

        self.run_action(action)

    def preview(self) -> None:
        def action() -> None:
            stored = self.selected_profile()
            _, current = self.current_config()
            plan = plan_api_switch(current, self.state.profile(stored.identifier))
            messagebox.showinfo("Preview", "Will change:\n\n" + "\n".join(plan.touched) + "\n\nNo credential has been read or displayed.", parent=self.root)

        self.run_action(action)

    def capture_account(self) -> None:
        def action() -> None:
            _, content = self.current_config()
            try:
                parsed = tomllib.loads(content)
            except tomllib.TOMLDecodeError as error:
                raise ProfileValidationError("The current Codex configuration is not valid TOML.") from error
            if "model_provider" in parsed:
                raise ProfileValidationError("Do not capture an API configuration as the account baseline.")
            if not messagebox.askyesno("Capture account config", "Save the current non-API configuration locally? Account authentication will not be read or copied.", parent=self.root):
                return
            self.state.save_account_config(content)
            self.status.set("Saved account configuration. Authentication was not read or copied.")

        self.run_action(action)

    def activate_api(self) -> None:
        def action() -> None:
            stored = self.selected_profile()
            config_path, current = self.current_config()
            plan = plan_api_switch(current, self.state.profile(stored.identifier))
            if not messagebox.askyesno("Activate API profile", "Close Codex first. This will update the active configuration and prompt for a one-time API key. The tool will not retain the key.", parent=self.root):
                return
            require_codex_stopped()
            key = simpledialog.askstring("API key", "API key (used once and not retained by this tool):", show="*", parent=self.root)
            if key is None:
                return
            apply_changes(api_activation_changes(config_path, self.codex_dir / "auth.json", plan, key))
            self.status.set(f"Activated {stored.label}. Start Codex manually.")

        self.run_action(action)

    def activate_account(self) -> None:
        def action() -> None:
            if not messagebox.askyesno("Return to account", "Close Codex first. This restores the account configuration and removes the active API authentication. You will sign in directly in Codex.", parent=self.root):
                return
            require_codex_stopped()
            apply_changes(account_activation_changes(self.codex_dir / "config.toml", self.codex_dir / "auth.json", self.state.account_config()))
            self.status.set("Account configuration restored. Sign in directly in Codex.")

        self.run_action(action)


def run() -> None:
    paths = resolve_platform_paths(platform.system(), Path.home(), os.environ)
    state = LocalState(paths.state_home)
    state.initialize()
    root = tk.Tk()
    SwitcherApp(root, state, paths.codex_home)
    root.mainloop()
