# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-02

### Added

- Visual dork builder with all Google operators, boolean logic, sites, file types,
  and live query preview.
- Multi-engine support: Google, DuckDuckGo, and Bing adapters behind a common interface.
- Token-bucket rate limiter with jitter, rotating User-Agents, retries with backoff,
  and CAPTCHA/bot-check detection.
- Rotating proxy pool with round-robin rotation, failure cooldown, and validation.
- SQLite persistence for jobs and results, deduplicated across engines.
- Result filter: domain whitelist/blacklist and URL regex keep-filters.
- Exporters: JSON, CSV, Markdown, and self-contained HTML report.
- Saved dork library with name/save/load/delete.
- Live URL re-checking that annotates status code, content type, and title.
- Recurring scheduled dorks via a background scheduler.
- Regex row highlighting in the results grid.
- Plugin system with `setup`, `on_result`, and `on_export` hooks.
- Automatic SQLite schema migration for older databases.
- Cross-platform PySide6 UI (Windows / macOS / Linux).
- README translated into 11 additional languages.
