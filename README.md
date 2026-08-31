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
| macOS | Strict privacy mode (no retained inactive key) | In development |
| Windows | Strict privacy mode (no retained inactive key) | In development |
| Linux | Strict privacy mode (no retained inactive key) | In development |

An optional system-credential-store convenience mode is a future feature, not part of the current implementation. It will never fall back to a file-based key store.

## Data handling

See [PRIVACY.md](PRIVACY.md) and [THREAT_MODEL.md](THREAT_MODEL.md) before testing or contributing. The implementation has not been migrated into this repository yet.

## Status

The current pre-release includes a local desktop interface and CLI, but it has not completed real-device acceptance testing or public-release audit.

## Development requirement

The development core requires Python 3.11 or later. This does not mean that a future end user must replace their operating system's bundled Python: distributed applications will use an isolated runtime.

## Pre-release usage

Read [English usage](docs/USAGE.md) or [中文使用说明](docs/使用说明.md) before trying the software. In particular, close Codex before applying a change and never paste a key into a profile configuration file.
