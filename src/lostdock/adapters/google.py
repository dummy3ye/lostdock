"""Google search adapter (HTML scraping with rate limiting + anti-block)."""

from __future__ import annotations

import logging
import random
import time

import requests
from bs4 import BeautifulSoup

from ..core.models import SearchResult
from ..core.proxy import ProxyPool
from ..core.ratelimit import RateLimiter, default_limiter
from .base import BlockedError, RateLimitedError, SearchEngine
from .browser import BrowserRenderer, BrowserUnavailable

log = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


def _parse_google_serp(html: str, query: str, position_offset: int = 0) -> list[SearchResult]:
    """Extract organic results from a Google SERP page."""
    from urllib.parse import parse_qs, urlparse

    soup = BeautifulSoup(html, "html.parser")
    results: list[SearchResult] = []
    seen_urls: set[str] = set()

    def organic_blocks():
        # Classic layout, udm=14 layout, then generic result containers.
        # Merge all matched containers so mixed page structures don't lose results.
        seen: set[int] = set()
        merged = []
        for selector in ("div.g", "div.MjjYud", "div[data-sncf]", "div[data-hveid]"):
            for block in soup.select(selector):
                if id(block) not in seen:
                    seen.add(id(block))
                    merged.append(block)
        return merged

    for block in organic_blocks():
        a = block.find("a", href=True)
        if a is None:
            continue
        href = a.get("href", "")
        if not href.startswith("http") and "/url?q=" not in href:
            continue
        url = href
        if href.startswith("/url?q="):
            parsed = parse_qs(urlparse(href).query)
            url = parsed.get("q", [""])[0]

        # Skip google's own links and navigation.
        if any(x in url for x in ("google.com", "google.", "/search", "gstatic")):
            continue

        # Reject known non-result / javascript links.
        if url.startswith(("javascript:", "data:")):
            continue

        # Skip duplicate containers (e.g. wrapper + inner g both matching).
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Prefer the heading text as the title, falling back to the anchor.
        heading = block.find("h3")
        title = (heading.get_text(" ", strip=True) if heading else a.get_text(" ", strip=True))[
            :300
        ]
        if not title:
            continue

        snippet = block.get_text(" ", strip=True)[:400]

        results.append(
            SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                engine="google",
                position=position_offset + len(results) + 1,
                query=query,
            )
        )
    return results


def _google_429_message(query: str) -> str:
    return (
        f"Google is rate-limiting requests after several retries (429): {query!r}. "
        "Google blocks datacenter IPs aggressively. Try: (1) adding proxies in "
        "Tools -> Settings, or (2) switching to the DuckDuckGo or Bing engine, "
        "or (3) slowing down via Settings limits."
    )


def _looks_blocked(html: str) -> bool:
    """Detect Google's various anti-bot pages regardless of which variant is served.

    Google returns several block shapes depending on client and network:
    a ``/sorry`` CAPTCHA, an "unusual traffic" interstitial, and a JS-required
    shell (``enablejs``) that returns HTTP 200 with zero results.
    """
    low = html.lower()
    markers = (
        "/sorry",
        "unusual traffic",
        "enable javascript",
        "enablejs",
        "detected unusual traffic",
        "are not a robot",
    )
    return any(m in low for m in markers)


class GoogleEngine(SearchEngine):
    """Scrapes Google SERP HTML.

    Uses plain HTTP scraping first (fast, works from clean residential IPs).
    If Google responds with a CAPTCHA / rate-limit block, falls back to
    rendering the SERP in a real headless Chromium via Playwright, which defeats
    behavioral bot-detection on most networks.

    NOTE: Google's ToS restrict automated access. This adapter exists for
    security research and is rate-limited by default. Prefer the Custom
    Search JSON API for production compliance.
    """

    name = "google"

    def __init__(
        self,
        limiter: RateLimiter | None = None,
        session: requests.Session | None = None,
        timeout: float = 15.0,
        proxies: ProxyPool | None = None,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        backoff_max: float = 30.0,
        use_browser_fallback: bool = True,
    ) -> None:
        self.limiter = limiter or default_limiter()
        self.session = session or requests.Session()
        self.session.headers.update({"Accept-Language": "en-US,en;q=0.9"})
        self.timeout = timeout
        self.proxies = proxies
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.use_browser_fallback = use_browser_fallback
        self._renderer: BrowserRenderer | None = None

    def _headers(self) -> dict:
        return {"User-Agent": random.choice(USER_AGENTS)}

    def _request_proxies(self) -> dict | None:
        if not self.proxies or len(self.proxies) == 0:
            return None
        return self.proxies.next()

    def _browser(self) -> BrowserRenderer:
        if self._renderer is None:
            proxy = self._request_proxies()
            self._renderer = BrowserRenderer(
                user_agent=self._headers()["User-Agent"],
                proxy=proxy.get("https") if proxy else None,
            )
        return self._renderer

    def _fetch_page(self, query: str, start: int, per_page: int) -> str:
        try:
            return self._fetch_http(query, start, per_page)
        except (BlockedError, RateLimitedError) as exc:
            if not self.use_browser_fallback:
                raise
            return self._fetch_browser(query, start, per_page, exc)

    def _fetch_http(self, query: str, start: int, per_page: int) -> str:
        self.limiter.acquire()
        params = {
            "q": query,
            "start": start,
            "num": per_page,
            "hl": "en",
            "udm": "14",  # classic web view: avoids AI Overview / heavy JS
        }
        attempts = self.max_retries + 1
        if self.proxies:
            attempts = max(attempts, len(self.proxies) + 1)
        last_error: Exception | None = None
        for attempt in range(attempts):
            proxy = self._request_proxies()
            if proxy is None and self.proxies:
                # every proxy is in cooldown; nothing left to try
                break
            try:
                resp = self.session.get(
                    "https://www.google.com/search",
                    params=params,
                    headers=self._headers(),
                    timeout=self.timeout,
                    proxies=proxy,
                )
            except requests.RequestException:
                if self.proxies:
                    self.proxies.mark_failed(proxy)
                if attempt < attempts - 1:
                    self._sleep_backoff(attempt, retry_after=None)
                    continue
                raise
            if resp.status_code == 429:
                if self.proxies:
                    self.proxies.mark_failed(proxy)
                if attempt < attempts - 1:
                    retry_after = resp.headers.get("Retry-After")
                    self._sleep_backoff(attempt, retry_after)
                    continue
                raise RateLimitedError(_google_429_message(query))
            if resp.status_code in (403, 503) or _looks_blocked(resp.text):
                if self.proxies:
                    self.proxies.mark_failed(proxy)
                last_error = BlockedError("Google served a CAPTCHA / bot-check page")
                if attempt < attempts - 1:
                    self._sleep_backoff(attempt, retry_after=None)
                    continue
                raise last_error
            if resp.status_code != 200:
                resp.raise_for_status()
            return resp.text
        if last_error is not None:
            raise last_error
        raise RateLimitedError(_google_429_message(query))

    def _fetch_browser(self, query: str, start: int, per_page: int, cause: Exception) -> str:
        """Render the SERP in headless Chromium after an HTTP block."""
        log.info("HTTP scraping blocked (%s); falling back to headless browser", cause)
        from urllib.parse import urlencode

        params = {"q": query, "start": start, "num": per_page, "hl": "en", "udm": "14"}
        url = "https://www.google.com/search?" + urlencode(params)
        try:
            html = self._browser().render(url, wait_selector="div.g")
        except BrowserUnavailable as exc:
            raise RateLimitedError(
                f"{cause}\n\nHeadless-browser fallback unavailable: {exc}"
            ) from exc
        if _looks_blocked(html):
            raise BlockedError(
                "Google blocked this network at the IP level (CAPTCHA). Add proxies "
                "in Tools -> Settings to search Google, or use another engine."
            )
        return html

    def _sleep_backoff(self, attempt: int, retry_after: str | None) -> None:
        """Sleep before the next retry, honoring Retry-After when provided."""
        if retry_after:
            try:
                delay = min(max(float(retry_after), 0.5), self.backoff_max)
                time.sleep(delay)
                return
            except ValueError:
                pass
        delay = min(self.backoff_base * (2**attempt), self.backoff_max)
        delay *= random.uniform(0.8, 1.2)  # jitter
        time.sleep(delay)

    def _parse(self, html: str, query: str, position_offset: int = 0) -> list[SearchResult]:
        return _parse_google_serp(html, query, position_offset=position_offset)

    def search(
        self,
        query: str,
        pages: int = 1,
        per_page: int = 10,
        stop_at: int | None = None,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        for page in range(pages):
            start = page * per_page
            html = self._fetch_page(query, start, per_page)
            results.extend(self._parse(html, query, position_offset=len(results)))
            if stop_at and len(results) >= stop_at:
                return results[:stop_at]
            time.sleep(random.uniform(0.5, 1.5))
        return results
