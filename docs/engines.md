# Search Engines

LostDock runs searches through pluggable **engine adapters**. Every adapter implements
the same interface, so adding a new engine means writing one class.

## The engine interface

All adapters subclass `SearchEngine` in `src/lostdock/adapters/base.py`:

```python
class SearchEngine(ABC):
    name = "base"

    @abstractmethod
    def search(self, query, pages=1, per_page=10, stop_at=None) -> list[SearchResult]:
        ...
```

- `query` — the compiled dork string.
- `pages` — how many result pages to fetch.
- `per_page` — results per page (engine-specific; Google/DDG/Bing typically return ~10).
- `stop_at` — stop early once this many results are collected.

Engines may raise `BlockedError` (CAPTCHA/403) or `RateLimitedError` (429/rate signal);
both subclass `EngineError`. The UI and the multi-engine aggregator handle these
gracefully.

Adapters are registered in `src/lostdock/adapters/__init__.py`:

```python
ENGINES = {
    "google": GoogleEngine,
    "duckduckgo": DuckDuckGoEngine,
    "bing": BingEngine,
    "google-chrome": ChromeEngine,
}
```

The toolbar dropdown builds from `ENGINES`, plus an `all` entry that wraps the HTTP
engines in a `MultiEngine`.

## Engine behavior

### Google (`google`)

- Scrapes the SERP over plain HTTP first.
- If Google serves a block page — `/sorry` CAPTCHA, "unusual traffic", or a JS-required
  shell (`enablejs`) — it detects the block and falls back to rendering the page in a
  real headless Chromium via Playwright, which defeats behavioral bot-detection on most
  residential networks. See `_looks_blocked()` in `adapters/google.py`.
- From datacenter IPs Google often blocks at the network level regardless. The engine
  raises a descriptive error suggesting proxies, another engine, or lower limits.
- **ToS note:** Google's terms restrict automated scraping. This adapter is for security
  research and ships rate-limited by default. For fully compliant production use,
  integrate the Custom Search JSON API instead.
- Requires the Chromium binary once: `python -m playwright install chromium`.

### DuckDuckGo (`duckduckgo`)

- Scrapes the lightweight HTML endpoint (`html.duckduckgo.com`).
- Generally tolerant of automated access at modest rates. It is the scheduler's default
  engine for that reason.

### Bing (`bing`)

- Scrapes `www.bing.com/search` SERP HTML.
- Rate-limited like the others and may hit bot-checks when scaled up.

### Chrome — pipe mode (`google-chrome`)

- Does **not** scrape. It opens the Google search URL in the user's own Chrome/Chromium
  browser (a new tab if one is running, otherwise a new window) and returns no results.
- The intended use: when Google blocks all automated access, you still search manually in
  a real, authenticated browser session.
- Locates the browser automatically (Chrome, Chromium, Edge on Windows; `open` on macOS).
  Set `LOSTDOCK_CHROME` to pin a specific binary.
- This is the default engine in the UI.

### All — multi-engine (`all`)

- Runs Google, DuckDuckGo, and Bing for the same query and **merges** the results.
- One blocked engine never aborts the search: each engine is tried independently, errors
  are logged, and every result any engine could produce is kept.
- Results are deduplicated by URL (normalized: stripped trailing `/`, lowercased); first
  occurrence wins. `stop_at` applies to the merged stream.
- Progress messages are emitted as each engine runs and shown in the status bar.

## Rate limiting

Every HTTP engine shares a token-bucket limiter (`core/ratelimit.py`):

- Default: capacity 5, rate 1 token per 3 seconds, plus jitter up to 40% of the interval.
  This keeps requests ~1 per 3–4 seconds.
- `acquire()` blocks until a token is available; jitter is added to avoid detectable
  request patterns.

Lower the rate if you get rate-limited, or raise it for a single trusted query. Keep it
conservative — that is also what keeps the search engines from blocking you.

## Proxies

Set proxies in **Tools → Settings**, one per line:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

They are loaded into a `ProxyPool` (`core/proxy.py`):

- **Round-robin rotation** — each request uses the next proxy.
- **Failure cooldown** — when a request through a proxy fails, that proxy is disabled for
  a cooldown period (60s default) before being tried again.
- **Validation** — `ProxyPool.validate()` issues a quick request through each proxy and
  drops the ones that fail. The Settings dialog offers a "validate" action that tests
  proxies against a real Google search and reports which are blocked vs. usable.

Proxies are persisted in the settings table and reloaded at startup.

## Adding a new engine

1. Create `src/lostdock/adapters/<name>.py`.
2. Subclass `SearchEngine`, set a unique `name`, and implement `search()`.
3. Use the shared `RateLimiter` (and `ProxyPool` if you want proxy support).
4. Register it in `adapters/__init__.py` `ENGINES` dict.
5. Add a test under `tests/` (e.g. a parse test with fixture HTML).
6. If it appears in the toolbar automatically via `ENGINES` — no UI changes needed.

See `CONTRIBUTING.md` for the project's engine rules (one adapter one interface,
conservative defaults, tests).
