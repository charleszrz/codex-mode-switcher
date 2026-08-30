# Threat model

## Assets to protect

- API keys and any bearer credentials.
- ChatGPT and OAuth authentication state.
- Private provider endpoints, organization identifiers, local paths, and project names.
- The user's existing Codex configuration and ability to recover it.

## Primary threats and required controls

| Threat | Required control |
| --- | --- |
| Secret committed to Git | Local release audit, CI audit, `.gitignore`, GitHub secret scanning, and push protection. |
| Credential copied into tool state | Store only with explicit opt-in in the OS credential store; prohibit file fallbacks and backups. |
| Interrupted write corrupts Codex | Preflight, minimal backup, atomic replace, post-write validation, automatic rollback. |
| Unsupported Codex format is overwritten | Version/format detection; stop safely when compatibility is unknown. |
| Sensitive data appears in support request | Redacted diagnostics and issue templates that forbid keys, tokens, complete auth files, private URLs, and paths. |
| Malicious or malformed imported config | Strict schema/allowlist validation; no executable interpolation; display a change preview. |
| Linux lacks a secure key store | Disable convenience storage rather than persist a key in a file. |
| A release binary is replaced or modified | Publish checksums; add signed/notarized artifacts only after a documented signing process exists. |

## Out of scope for v0.1

- Cloud synchronization, multi-device profiles, account recovery, remote control, and automatic updates.
- Supporting an arbitrary Codex authentication format without an explicit compatibility test.
- Claiming that third-party providers retain no request data.
