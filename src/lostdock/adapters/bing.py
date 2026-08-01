"""Bing HTML search adapter."""

from __future__ import annotations

import random
import time
from typing import List, Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from ..core.models import SearchResult
from ..core.proxy import ProxyPool
from ..core.ratelimit import RateLimiter, default_limiter
from .base import BlockedError, RateLimitedError, SearchEngine

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class BingEngine(SearchEngine):
    """Scrapes Bing SERP HTML. Rate-limited; may hit bot-checks at scale."""

    name = "bing"

    def __init__(
        self,
        limiter: Optional[RateLimiter] = None,
        session: Optional[requests.Session] = None,
        timeout: float = 15.0,
        proxies: Optional[ProxyPool] = None,
    ) -> None:
        self.limiter = limiter or default_limiter()
        self.session = session or requests.Session()
        self.timeout = timeout
        self.proxies = proxies

    def _fetch_page(self, query: str, page: int, per_page: int) -> str:
        self.limiter.acquire()
        params = {"q": query, "count": per_page, "first": max(page - 1, 0) * per_page + 1}
        proxy = None
        if self.proxies and len(self.proxies) > 0:
            proxy = self.proxies.next()
        try:
            resp = self.session.get(
                "https://www.bing.com/search",
                params=params,
                headers={"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "en-US,en;q=0.9"},
                timeout=self.timeout,
                proxies=proxy,
            )
        except requests.RequestException:
            if self.proxies:
                self.proxies.mark_failed(proxy)
            raise
        if resp.status_code == 429:
            raise RateLimitedError("HTTP 429 from Bing")
        if resp.status_code in (403, 503):
            raise BlockedError(f"Bing block page (HTTP {resp.status_code})")
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp.text

    def _parse(self, html: str, query: str, position_offset: int = 0) -> List[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[SearchResult] = []
        for i, li in enumerate(soup.select("li.b_algo")):
            h2 = li.select_one("h2")
            a = li.select_one("h2 a")
            if not a:
                continue
            url = a.get("href", "")
            if not url.startswith(("http://", "https://")):
                continue
            title = a.get_text(" ", strip=True) or h2.get_text(" ", strip=True)
            snippet_el = li.select_one("p, .b_caption p")
            snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
            results.append(
                SearchResult(
                    title=title[:300],
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
        per_page: int = 10,
        stop_at: Optional[int] = None,
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        for page in range(1, pages + 1):
            html = self._fetch_page(query, page, per_page)
            results.extend(self._parse(html, query, position_offset=len(results)))
            if stop_at and len(results) >= stop_at:
                return results[:stop_at]
            time.sleep(random.uniform(0.6, 1.5))
        return results
