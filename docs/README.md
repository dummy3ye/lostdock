# LostDock Documentation

Everything you need to use, extend, and ship LostDock. The [README](../README.md) is the
quick-start; these docs go deeper.

## Using the app

- [Usage guide](usage.md) — the full workflow: building a dork, running a search,
  re-checking URLs, filters, and export.
- [Search engines](engines.md) — how the engine adapters work, rate limiting,
  anti-block, proxies, and the Chrome "pipe" and "all" modes.
- [Scheduled dorks](scheduler.md) — running saved dorks on a timer in the background.

## Extending LostDock

- [Plugins](plugins.md) — the plugin system: hooks, lifecycle, and an example.

## Building and shipping

- [Packaging](packaging.md) — PyInstaller builds for Windows, macOS, and Linux, the
  Windows installer/updater, and the Arch Linux package.
- [Development](development.md) — environment setup, tests, project layout, and the
  release process.

## Quick reference

| Where | What |
|-------|------|
| Data | SQLite at `~/.lostdock/lostdock.db` |
| Plugins | `~/.lostdock/plugins/` (or the bundled `plugins/` dir) |
| Engines | `src/lostdock/adapters/` |
| Entry point | `src/lostdock/main.py` |
| Windows installer | `src/installer/windows/main.py` |
