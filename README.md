# Codex Mode Switcher

A privacy-first, local profile switcher for Codex on macOS, Windows, and Linux.

> This repository is under private pre-release development. It is not affiliated with or endorsed by OpenAI.

## Product principles

- No accounts, cloud sync, telemetry, analytics, or automatic updates.
- Never export, back up, or restore ChatGPT or OAuth authentication state.
- Never commit credentials, local configuration, backups, logs, or machine paths.
- Do not fall back to plain-text key storage when a platform secure credential store is unavailable.
- Preview changes, back up only what is necessary, write atomically, verify, and roll back on failure.

## Planned platform support

| Platform | Credential store | Release status |
| --- | --- | --- |
| macOS | Keychain | Planned stable |
| Windows | Credential Manager / DPAPI | Planned stable |
| Linux | Secret Service only | Planned preview |

Linux convenience storage is unavailable when a secure Secret Service implementation cannot be detected. The tool will not replace it with a file-based key store.

## Data handling

See [PRIVACY.md](PRIVACY.md) and [THREAT_MODEL.md](THREAT_MODEL.md) before testing or contributing. The implementation has not been migrated into this repository yet.

## Status

The repository currently contains only release-safety documentation and auditing infrastructure. No user-ready executable has been released.

## Development requirement

The development core requires Python 3.11 or later. This does not mean that a future end user must replace their operating system's bundled Python: distributed applications will use an isolated runtime.
