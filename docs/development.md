# Development

How to set up a dev environment, run tests, understand the code layout, and cut a
release. Also read [CONTRIBUTING.md](../CONTRIBUTING.md) before opening a PR.

## Environment

Prerequisites: **Python 3.10+**, **uv** (or plain pip), and optionally `git-cliff` for
releasing.

```bash
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock
uv venv
uv pip install -e ".[dev]"
```

Install the headless Chromium used by the Google engine's anti-block fallback:

```bash
uv run python -m playwright install chromium
```

Run the app:

```bash
uv run lostdock
```

For a headless smoke test:

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main
```

## Tests and lint

```bash
uv run pytest                 # full suite
uv run pytest tests/test_compiler.py -q   # a single module
uv run ruff check src tests   # lint
uv run ruff format --check src tests      # format check
uv run python -m compileall -q src        # import sanity check
```

The CI pipeline runs lint, format check, and tests on every push and PR.

## Project layout

```
src/lostdock/
├── core/         Dork model, operators, query compiler, rate limiter, proxy pool
├── adapters/     Google / DuckDuckGo / Bing / Chrome engine adapters, browser renderer
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           PySide6 widgets: dork builder, results grid, worker, settings, theme, main window
└── main.py       entry point
src/installer/    Windows installer/updater/uninstaller (stdlib-only)
plugins/          bundled example plugins (shipped inside the binary)
packaging/aur/    Arch Linux PKGBUILD
tests/            pytest suite
```

### Data flow

1. The **dork builder** (`ui/dork_builder.py`) emits a `Dork` model and previews the
   compiled query.
2. `core/compiler.py:compile_dork()` renders the `Dork` into a search query string.
3. The UI worker (`ui/worker.py`) runs a `SearchEngine` (from `adapters/`) via the shared
   `services/query.py:run_query()` path — the same path the scheduler uses.
4. `run_query()` compiles the dork, creates a job, iterates results, applies plugin
   `on_result` hooks, persists each kept result, and marks the job status.
5. Results stream into `ui/results_view.py` and land in SQLite via
   `services/repository.py`.
6. The **crawler** (`services/crawler.py`) re-fetches stored URLs and annotates status
   codes; the **exporter** (`services/exporter.py`) writes JSON/CSV/Markdown/HTML.

## Architecture notes

- **Engine adapters** all implement `SearchEngine` (`adapters/base.py`). Google scrapes
  HTTP first and falls back to a headless-Chromium render (`adapters/browser.py`) when it
  detects a block. `adapters/multi.py` merges multiple engines for the "all" mode.
- **Rate limiting** (`core/ratelimit.py`) is a token bucket with jitter; every HTTP engine
  shares one instance by default so requests stay polite.
- **Proxies** (`core/proxy.py`) rotate round-robin with a failure cooldown, persisted in
  the settings table.
- **Plugins** (`services/plugins.py`) are discovered from the bundled and user plugin
  dirs and invoked through `run_query()` and export.
- **Scheduler** (`services/scheduler.py`) polls the repository every 30s for due
  schedules and runs them via the shared query path.

See [engines.md](engines.md) and [plugins.md](plugins.md) for the details.

## Database

SQLite at `~/.lostdock/lostdock.db`, created automatically. Tables:

| Table | Purpose |
|-------|---------|
| `jobs` | one row per search run (query, engine, status) |
| `results` | search results, deduplicated across engines |
| `saved_dorks` | named dorks saved from the builder |
| `schedules` | recurring-run configuration |
| `settings` | key/value config (proxies, theme, filter) |

Old databases migrate automatically via a schema-migration step in `repository.py`.
Results can be re-checked (crawl annotations written back) without losing prior status.

## Releasing

Releases are tag-driven and automated by CI. You need `git-cliff`
(`cargo install git-cliff`):

```bash
make release                # bump version, regenerate CHANGELOG.md, commit, tag
```

or with an explicit version:

```bash
./scripts/release.sh 0.2.0
```

What `release.sh` does:

1. Sanity checks — clean working tree and on `master`.
2. Computes the next version from conventional commits via `git-cliff --bumped-version`
   (or uses the explicit argument).
3. Bumps the version in `pyproject.toml` and `src/lostdock/__init__.py`.
4. Runs the test suite.
5. Regenerates `CHANGELOG.md` with git-cliff.
6. Commits as `chore(release): bump version to X.Y.Z` and creates annotated tag `vX.Y.Z`.
7. Prints the push commands.

Pushing the tag triggers the **build** workflow: it builds the Linux and Windows binaries,
builds and signs the Windows installer, and publishes a GitHub Release with auto-generated
notes (grouped features/fixes, issue references, contributors) via git-cliff. Release
notes are assembled by `cliff.toml`; the release asset URLs point at
`dummy3ye/lostdock/releases/...`.

## Conventional commits

The release tooling depends on [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add bing adapter
fix(ui): handle empty query on run
docs: update README
test: cover proxy pool rotation
```

The `feat`/`fix` types (with optional scope) drive the semver bump and the changelog
groups. Keep commit messages accurate — they become the release notes.
