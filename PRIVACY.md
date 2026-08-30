# Privacy policy and data boundary

## Default posture

Codex Mode Switcher is designed as a local-only application. It must not operate a backend, create an account, transmit telemetry, upload configuration, or contact a provider on behalf of the user.

## Data categories

| Data | Tool behavior |
| --- | --- |
| API keys | Strict mode does not retain them. Opt-in convenience mode may retain an inactive profile's key only in the operating system credential store. |
| Active Codex authentication | The tool must not create an additional backup or export. If Codex itself requires an active credential in its own storage, the UI must disclose that before switching. |
| ChatGPT/OAuth authentication | Never read for migration, export, back up, restore, or transmit. |
| Provider configuration | Stored locally only after explicit user import. Endpoints may be sensitive and must never appear in logs, diagnostics, issues, examples, or telemetry. |
| Backups | Local, minimal, access-restricted, time-limited, and deletable by the user. They must exclude tool-managed credential copies. |
| Diagnostics | User-created and redacted by default. Automatic collection and upload are prohibited. |

## Non-negotiable rules

1. No file-based credential fallback.
2. No credential value in a command argument, environment variable, notification, exception, log, test fixture, or screenshot.
3. No network request is required for a switch.
4. Removal and uninstall must offer an explicit local-data cleanup path.
5. Any future data collection requires a separate public privacy-policy revision and an explicit opt-in.

## Scope of responsibility

The tool protects data it handles. It cannot change the storage, account, network, or data-retention behavior of Codex or a provider selected by the user. The UI must make this distinction clear.
