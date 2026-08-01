# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)

**LostDock** is an industry-grade, cross-platform Google-dorking desktop tool built in Python.
It gives you a visual query builder for every search-engine operator, multi-engine execution
with rate limiting and proxy rotation, persistent result storage, live URL re-checking,
recurring scheduled dorks, regex highlighting, and a plugin system — all in a native PySide6 (Qt) UI
that runs on **Windows, macOS, and Linux**.

> **Read this README in:** [中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [हिन्दी](README.hi.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [العربية](README.ar.md)

---

## Table of Contents

- [Features](#features)
- [Screenshot](#screenshot)
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
- [Development](#development)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Features

- **Visual dork builder** — compose queries from keywords, exact phrases, boolean logic
  (`AND`/`OR`/`NOT`), exclusions, required terms, sites, file types, and every Google operator,
  with a live query-preview.
- **Multi-engine** — Google, DuckDuckGo, and Bing adapters behind one interface; pick any in the UI.
- **Rate limiting & anti-block** — token-bucket limiter with jitter, rotating User-Agents,
  exponential retries, and CAPTCHA/bot-check detection.
- **Proxy rotation** — pool of proxies with round-robin rotation, failure cooldown, and validation.
- **Persistent storage** — every job and result stored in SQLite, deduplicated across engines.
- **Live URL re-checking** — re-fetch stored URLs and annotate status code / content type / title.
- **Scheduled dorks** — run saved dorks on a recurring interval in the background.
- **Regex highlighting** — instantly highlight rows matching a pattern.
- **Filters** — domain whitelist/blacklist and URL-regex keep-filters applied on export.
- **Export** — JSON, CSV, Markdown, and a styled self-contained HTML report.
- **Saved dork library** — name, save, load, and delete dorks.
- **Plugin system** — drop Python modules into `~/.lostdock/plugins/` with `setup`, `on_result`,
  and `on_export` hooks.
- **Cross-platform** — single codebase packaged for Windows (`.exe`), macOS (`.app`), and Linux.

## Architecture

```
┌─ UI Layer (PySide6/Qt) ───────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings   │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  Service Layer                                          │
│  Repository │ Executor │ Filter │ Crawler │ Scheduler   │
│  Exporter │ Plugins                                     │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  Core Engine                                            │
│  Adapters (Google / DuckDuckGo / Bing)                  │
│  Rate Limiter │ Proxy Pool │ Compiler │ Operators        │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  SQLite (jobs, results, saved dorks, schedules)         │
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
git clone https://github.com/your-user/lostdock.git
cd lostdock

# 2. Create a virtual environment and install
uv venv
uv pip install -e ".[dev]"

# 3. Run
uv run lostdock
```

If you do not have `uv`, you can use plain `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
lostdock
```

### Alternative: run from the repository root without installing

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen for headless testing
```

## Usage

1. **Build a query** — type keywords, add an exact phrase, exclusions, `AND`/`OR` terms,
   sites (`site:`), file types, and inline operators. The compiled query updates live.
2. **Pick an engine** (Google / DuckDuckGo / Bing) and the number of pages.
3. Click **Run Search**. Results stream into the table; every result is persisted to SQLite.
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
rate-limited by default. Add a new engine by subclassing `SearchEngine` and registering it
in `adapters/__init__.py`.

> **Note on Google:** Google restricts automated access and may serve CAPTCHAs to scrapers.
> The adapter detects this and surfaces a clear error. For fully compliant production use,
> integrate the Google Custom Search JSON API (100 free queries/day).

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
3. A background scheduler runs due dorks, stores results as new jobs, and bumps the next run.

## URL Re-checking

The **Re-check URLs** button fetches every URL in the current results with politeness delays
and annotates each row with `status code`, `content type`, and a live `<title>`. Failures are
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
- Tables: `jobs`, `results`, `saved_dorks`, `schedules`. Old databases migrate automatically.

## Packaging

The project includes a `lostdock.spec` for PyInstaller. Build per-platform:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # creates dist/lostdock
```

- **Windows:** `dist/lostdock.exe` (or `--onefile`)
- **macOS:** bundle into `dist/lostdock.app` (sign with `codesign` for distribution)
- **Linux:** `dist/lostdock` binary, or wrap in an AppImage/Flatpak

## Development

```bash
uv run pytest                     # run the test suite
uv run python -m compileall -q src  # sanity-check imports
```

Project layout:

```
src/lostdock/
├── core/         Dork model, operators, query compiler, rate limiter, proxy pool
├── adapters/     Google / DuckDuckGo / Bing engine adapters
├── services/     repository, executor, filter, crawler, scheduler, exporter, plugins
├── ui/           PySide6 widgets: dork builder, results grid, worker, settings, main window
└── main.py       entry point
tests/            pytest suite (compiler, engines, services, proxy, scheduler, plugins)
```

## Disclaimer

LostDock is a **security research and OSINT** tool. Use it only against systems you own or
are explicitly authorized to test. Respect search-engine Terms of Service: keep rate limits
low, use proxies responsibly, and never use this tool for unauthorized access, scraping of
personal data, or any unlawful activity. The authors are not responsible for misuse.

## License

MIT — see [LICENSE](LICENSE).
