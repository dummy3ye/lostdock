# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)

**LostDock** is a desktop tool for Google dorking and OSINT research. It pairs a
visual dork builder with multi-engine search, rate limiting, proxy rotation, and
persistent result storage — all in a native PySide6 (Qt) interface that runs on
**Windows, macOS, and Linux**.

> **Read this README in:** [中文](README.zh-CN.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [Deutsch](i18n/README.de.md) · [हिन्दी](i18n/README.hi.md) · [Português](i18n/README.pt-BR.md) · [Русский](i18n/README.ru.md) · [日本語](README.ja.md) · [한국어](i18n/README.ko.md) · [Italiano](i18n/README.it.md) · [العربية](i18n/README.ar.md)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Supported Operators](#supported-operators)
- [Search Engines](#search-engines)
- [Proxies](#proxies)
- [Scheduled Dorks](#scheduled-dorks)
- [URL Re-checking](#url-re-checking)
- [Plugins](#plugins)
- [Export](#export)
- [Data Storage](#data-storage)
- [Packaging](#packaging)
- [Releases](#releases)
- [Development](#development)
- [Documentation](#documentation)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Features

- **Visual dork builder** — compose searches from keywords, exact phrases, boolean
  logic (`AND`/`OR`/`NOT`), exclusions, required terms, sites, file types, and every
  Google operator, with a live query preview.
- **Multi-engine search** — Google, DuckDuckGo, and Bing behind one interface, plus a
  Chrome "pipe" mode that runs the search in your own browser. Or run all three at once
  and merge the results.
- **Rate limiting & anti-block** — token-bucket limiter with jitter, rotating
  User-Agents, exponential backoff, and CAPTCHA/bot-check detection. Google falls back
  to a headless Chromium renderer when plain HTTP is blocked.
- **Proxy rotation** — a proxy pool with round-robin rotation, failure cooldown, and
  validation.
- **Persistent storage** — every job and result stored in SQLite, deduplicated across
  engines.
- **Live URL re-checking** — re-fetch stored URLs and annotate status code, content
  type, and title.
- **Scheduled dorks** — run saved dorks on a recurring interval in the background.
- **Regex highlighting** — instantly highlight rows matching a pattern.
- **Filters** — domain whitelist/blacklist and URL-regex keep-filters applied on export.
- **Export** — JSON, CSV, Markdown, and a styled, self-contained HTML report.
- **Saved dork library** — save, load, and manage dorks by name.
- **Plugin system** — drop Python modules with `setup`, `on_result`, and `on_export`
  hooks.
- **Themes** — dark, light, and classic Win98 GDI styles.
- **Cross-platform** — one codebase packaged for Windows, macOS, and Linux, with a
  Windows installer/updater.

## Architecture

```
┌─ UI Layer (PySide6/Qt) ───────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings    │
│  Themes (dark / light / win98)                        │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  Service Layer                                          │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │    │
│  Exporter │ Plugins                                     │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  Core Engine                                            │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)         │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool         │
│  Compiler │ Operators                                    │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  SQLite (jobs, results, saved dorks, schedules, config) │
└─────────────────────────────────────────────────────────┘
```

## Installation

> Installation instructions are intentionally provided in English only.

### Prerequisites

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (fast package manager) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. Create a virtual environment and install
uv venv
uv pip install -e ".[dev]"

# 3. Install the headless Chromium used by the Google engine's anti-block fallback
uv run python -m playwright install chromium

# 4. Run
uv run lostdock
```

If you do not have `uv`, you can use plain `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### Alternative: run from the repository root without installing

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen for headless testing
```

## Usage

1. **Build a query** — type keywords, add an exact phrase, exclusions, `AND`/`OR`
   terms, sites (`site:`), file types, and inline operators. The compiled query
   updates live.
2. **Pick an engine** — Google, DuckDuckGo, Bing, Chrome, or "all" — and the number
   of pages.
3. Click **Run Search**. Results stream into the table; every result is persisted to
   SQLite.
4. Use **Re-check URLs** to fetch each result and annotate its live status.
5. Set a **Highlight** regex to spotlight interesting rows.
6. Click **Export...** to save as JSON, CSV, Markdown, or an HTML report.

## Supported Operators

The builder supports the full Google operator set:

| Operator | Meaning |
|----------|---------|
| `site:` | Restrict results to a domain |
| `inurl:` / `allinurl:` | Words in the URL |
| `intitle:` / `allintitle:` | Words in the title |
| `intext:` / `allintext:` | Words in the body text |
| `inanchor:` | Words in link anchor text |
| `filetype:` / `ext:` | Restrict to a file type |
| `cache:` | Google's cached version |
| `link:` | Pages linking to a URL |
| `related:` | Similar pages |
| `info:` | Page overview |
| `define:` | Definition of a term |
| `author:` | Author of a result |
| `daterange:` / `numrange:` | Numeric ranges |
| `loc:` | Location |
| `after:` / `before:` | Date filters (`YYYY-MM-DD`) |
| `lang:` | Language restriction |
| `"phrase"` | Exact phrase |
| `-term` | Exclude a term |
| `~term` | Include synonyms |
| `*` | Wildcard |
| `term1 OR term2` | Either term |

## Search Engines

All engines share the same interface (`SearchEngine` in `adapters/base.py`) and are
rate-limited by default. Add a new engine by subclassing `SearchEngine` and registering
it in `adapters/__init__.py`.

- **Google** — scrapes the SERP over HTTP first. If Google responds with a CAPTCHA or
  rate-limit block, it re-renders the page in a real headless Chromium (via Playwright),
  which defeats behavioral bot-detection on most residential networks. On datacenter
  IPs Google may block at the IP level regardless — add proxies in Tools → Settings, or
  use another engine. Requires the Chromium binary once
  (`python -m playwright install chromium`). For fully compliant production use,
  integrate the Google Custom Search JSON API (100 free queries/day).
- **DuckDuckGo** — lightweight HTML endpoint, generally tolerant of automated access at
  modest rates.
- **Bing** — SERP scraping; rate-limited and may hit bot-checks at scale.
- **Chrome (pipe)** — opens the search directly in your own Chrome/Chromium browser and
  lets you review it there. No results are captured back into LostDock; it is the
  simplest way to search when Google blocks everything else. Set `LOSTDOCK_CHROME` to
  point at a specific binary if needed.
- **All** — runs Google, DuckDuckGo, and Bing for the same query and merges the
  results. One blocked engine never aborts the search; results are deduplicated by URL.

## Proxies

Set proxies in **Tools → Settings**. One per line:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

Proxies rotate per request; failed proxies go into a cooldown period. Run the
"validate" path (in code, `ProxyPool.validate()`) to drop dead proxies.

## Scheduled Dorks

1. Save a dork (name it in the "Dork name" field).
2. In **Tools → Settings**, select the dork, set an interval in minutes, and save.
3. A background scheduler runs due dorks, stores results as new jobs, and bumps the
   next run.

## URL Re-checking

The **Re-check URLs** button fetches every URL in the current results off the UI
thread sequentially, annotates each row with `status code`, `content type`,
and a live `<title>`, and persists the results back to the database. Failures are
annotated inline and never crash the UI.

## Plugins

Drop `*.py` files into `~/.lostdock/plugins/` (or the bundled `plugins/` directory).
A plugin module may export any subset of:

```python
NAME = "my_plugin"

def setup(app): ...                    # once at startup
def on_result(result): return result   # return None to drop the result
def on_export(results, fmt, path): ... # before export
```

See `plugins/example_skip_tracking.py` for a working example.

## Export

| Format | Extension | Notes |
|--------|-----------|-------|
| JSON | `.json` | Full structured results |
| CSV | `.csv` | Spreadsheet-ready (UTF-8 BOM) |
| Markdown | `.md` | Human-readable |
| HTML | `.html` | Self-contained report, clickable links |

## Data Storage

- **Database:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins:** `~/.lostdock/plugins/`
- Tables: `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. Old databases
  migrate automatically.

## Packaging

The project includes a `lostdock.spec` for PyInstaller. Build per-platform:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # creates dist/lostdock
```

- **Windows:** `dist/lostdock.exe`, plus a one-file `lostdock-installer.exe` that acts
  as installer, updater, and uninstaller without admin rights
  (`src/installer/windows/main.py`).
- **macOS:** bundle into `dist/LostDock.app` (sign with `codesign` for distribution).
- **Linux:** `dist/lostdock` binary, or wrap in an AppImage/Flatpak. An Arch Linux
  `PKGBUILD` lives in `packaging/aur/`.

## Releases

Releases are tag-driven and automated. Cutting a new release requires `git-cliff`
(`cargo install git-cliff`):

```bash
make release                # bumps the version, regenerates CHANGELOG.md, commits and tags
```

`make release` reads the conventional commits since the last tag to pick the next
semver version (or pass one explicitly: `./scripts/release.sh 0.2.0`). It then bumps
the version in `pyproject.toml` and `src/lostdock/__init__.py`, runs the test suite,
regenerates `CHANGELOG.md`, and creates an annotated `vX.Y.Z` tag.

Pushing the tag triggers CI, which builds the Windows and Linux binaries and the
self-signed Windows installer, then publishes a GitHub Release with auto-generated
notes (grouped features/fixes, issue references, and contributors) via
[git-cliff](https://git-cliff.org).

## Development

```bash
uv run pytest                     # run the test suite
uv run python -m compileall -q src  # sanity-check imports
uv run ruff check src tests       # lint
```

Project layout:

```
src/lostdock/
├── core/         Dork model, operators, query compiler, rate limiter, proxy pool
├── adapters/     Google / DuckDuckGo / Bing / Chrome engine adapters, browser renderer
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           PySide6 widgets: dork builder, results grid, worker, settings, theme, main window
└── main.py       entry point
src/installer/    Windows installer/updater/uninstaller
tests/            pytest suite (compiler, engines, services, proxy, scheduler, plugins)
```

## Documentation

Detailed docs live in the [docs/](docs/) directory:

- [Usage guide](docs/usage.md) — building dorks, running searches, re-checking URLs,
  filters, and export
- [Search engines](docs/engines.md) — adapters, rate limiting, proxies, Chrome pipe mode
- [Scheduled dorks](docs/scheduler.md) — background scheduling
- [Plugins](docs/plugins.md) — the plugin system reference
- [Packaging](docs/packaging.md) — builds, the Windows installer, and the AUR package
- [Development](docs/development.md) — setup, tests, code layout, releasing

## Disclaimer

LostDock is a **security research and OSINT** tool. Use it only against systems you own
or are explicitly authorized to test. Respect search-engine Terms of Service: keep rate
limits low, use proxies responsibly, and never use this tool for unauthorized access,
scraping of personal data, or any unlawful activity. The authors are not responsible
for misuse.

## License

MIT — see [LICENSE](LICENSE).
