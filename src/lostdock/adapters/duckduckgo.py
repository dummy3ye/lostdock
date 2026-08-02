"""DuckDuckGo HTML search adapter."""

from __future__ import annotations

import random
import time

import requests
from bs4 import BeautifulSoup

from ..core.models import SearchResult
from ..core.proxy import ProxyPool
from ..core.ratelimit import RateLimiter, default_limiter
from .base import BlockedError, RateLimitedError, SearchEngine

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class DuckDuckGoEngine(SearchEngine):
    """Scrapes DuckDuckGo's HTML endpoint (html.duckduckgo.com).

    Lightweight and generally tolerant of automated access at modest rates.
    """

    name = "duckduckgo"

    def __init__(
        self,
        limiter: RateLimiter | None = None,
        session: requests.Session | None = None,
        timeout: float = 15.0,
        proxies: ProxyPool | None = None,
    ) -> None:
        self.limiter = limiter or default_limiter()
        self.session = session or requests.Session()
        self.timeout = timeout
        self.proxies = proxies

    def _fetch_page(self, query: str, page: int, per_page: int) -> str:
        self.limiter.acquire()
        params = {
            "q": query,
            "s": max(page - 1, 0) * 30,
            "kl": "us-en",
        }
        proxy = None
        if self.proxies and len(self.proxies) > 0:
            proxy = self.proxies.next()
        try:
            resp = self.session.get(
                "https://html.duckduckgo.com/html/",
                params=params,
                headers={"User-Agent": random.choice(USER_AGENTS)},
                timeout=self.timeout,
                proxies=proxy,
            )
        except requests.RequestException:
            if self.proxies:
                self.proxies.mark_failed(proxy)
            raise
        if resp.status_code == 429:
            raise RateLimitedError("HTTP 429 from DuckDuckGo")
        if resp.status_code in (403, 503):
            raise BlockedError(f"DuckDuckGo block page (HTTP {resp.status_code})")
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp.text

    def _parse(self, html: str, query: str, position_offset: int = 0) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []
        blocks = soup.select("div.result")
        for i, block in enumerate(blocks):
            a = block.select_one("a.result__a")
            if not a:
                continue
            url = a.get("href", "")
            # DDG wraps urls via uddg=... param
            from urllib.parse import parse_qs, urlparse

            if "uddg=" in url:
                url = parse_qs(urlparse(url).query).get("uddg", [""])[0]
            if not url.startswith(("http://", "https://")):
                continue
            snippet_el = block.select_one("a.result__snippet")
            snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
            results.append(
                SearchResult(
                    title=a.get_text(" ", strip=True),
                    url=url,
                    snippet=snippet[:400],
                    engine=self.name,
                    position=position_offset + i + 1,
                    query=query,
                )
            )
        return results

    def search(
        self,
        query: str,
        pages: int = 1,
        per_page: int = 30,
        stop_at: int | None = None,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        for page in range(1, pages + 1):
            html = self._fetch_page(query, page, per_page)
            results.extend(self._parse(html, query, position_offset=len(results)))
            if stop_at and len(results) >= stop_at:
                return results[:stop_at]
            time.sleep(random.uniform(0.6, 1.5))
        return results
