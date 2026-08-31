# Usage

<p align="right"><a href="./使用说明.md">🇨🇳 简体中文</a> · <a href="./USAGE.md">🇺🇸 English</a></p>

This is pre-release software. Use it only after backing up your own Codex configuration through your normal device backup process.

## Install from source

Requirements:

- Codex installed for the current desktop user.
- Python 3.11 or later.
- Codex fully closed before any activation.

```bash
python -m pip install .
codex-mode-switcher gui
```

To use the CLI instead, run `codex-mode-switcher --help`.

## Strict privacy workflow

1. While signed into your personal account, use **Capture account config** once. The application stores only the non-authentication configuration and does not read or copy account authentication.
2. Prepare a TOML file with exactly one provider table and no credential. Import it as an API profile.
3. Choose **Preview selected**. Only the names of the settings to be changed are displayed; the provider endpoint is not displayed.
4. Fully close Codex, choose **Activate selected API**, and enter the API key in the one-time dialog.
5. The key is written only to Codex's active authentication location when that client requires it. This application does not retain a profile copy, make a backup of it, or send it over the network.
6. To return, fully close Codex and choose **Return to account**. The active API authentication is removed; sign in directly in Codex.

## Safe API profile example

```toml
model = "your-model"

[model_providers.example]
base_url = "https://api.example.invalid/v1"
wire_api = "responses"
```

Do not put an API key, token, authorization header, password, credential-bearing URL, or query parameter in this file. Import is rejected if common secret fields or formats are detected.

## What the tool changes

During API activation, it changes the active Codex `config.toml` and, only when required for API mode, its active authentication file. During account activation, it restores the captured non-authentication configuration and removes the active API authentication file.

The tool does not automatically start Codex. This is intentional: users can inspect the result before starting the client.

## Remove local state

Delete the application state directory only after returning to account mode:

- macOS: `~/Library/Application Support/Codex Mode Switcher`
- Windows: `%LOCALAPPDATA%\Codex Mode Switcher`
- Linux: `$XDG_STATE_HOME/codex-mode-switcher`, or `~/.local/state/codex-mode-switcher`

This removes stored profile templates and the captured account configuration. It does not remove Codex itself or change a provider's data retention practices.
