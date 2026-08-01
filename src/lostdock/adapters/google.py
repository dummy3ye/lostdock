"""Google search adapter (HTML scraping with rate limiting + anti-block)."""

from __future__ import annotations

import logging
import random
import time
from typing import List, Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from ..core.models import SearchResult
from ..core.proxy import ProxyPool
from ..core.ratelimit import RateLimiter, default_limiter
from .base import BlockedError, RateLimitedError, SearchEngine

log = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


class GoogleEngine(SearchEngine):
    """Scrapes Google SERP HTML.

    NOTE: Google's ToS restrict automated access. This adapter exists for
    security research and is rate-limited by default. Prefer the Custom
    Search JSON API for production compliance.
    """

    name = "google"

    def __init__(
        self,
        limiter: Optional[RateLimiter] = None,
        session: Optional[requests.Session] = None,
        timeout: float = 15.0,
        proxies: Optional["ProxyPool"] = None,
    ) -> None:
        self.limiter = limiter or default_limiter()
        self.session = session or requests.Session()
        self.session.headers.update({"Accept-Language": "en-US,en;q=0.9"})
        self.timeout = timeout
        self.proxies = proxies

    def _headers(self) -> dict:
        return {"User-Agent": random.choice(USER_AGENTS)}

    def _request_proxies(self) -> Optional[dict]:
        if not self.proxies or len(self.proxies) == 0:
            return None
        return self.proxies.next()

    def _fetch_page(self, query: str, start: int, per_page: int) -> str:
        self.limiter.acquire()
        params = {
            "q": query,
            "start": start,
            "num": per_page,
            "hl": "en",
        }
        proxy = self._request_proxies()
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
            raise
        if resp.status_code == 429:
            raise RateLimitedError(f"HTTP 429 from Google: {query!r}")
        if resp.status_code in (403, 503) or "unusual traffic" in resp.text.lower():
            raise BlockedError("Google served a CAPTCHA / bot-check page")
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp.text

    def _parse(self, html: str, query: str, position_offset: int = 0) -> List[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[SearchResult] = []
        for i, a in enumerate(soup.select("a[href]")):
            href = a.get("href", "")
            if not href.startswith("http") and "/url?q=" not in href:
                continue
            url = href
            if href.startswith("/url?q="):
                from urllib.parse import parse_qs, urlparse

                parsed = parse_qs(urlparse(href).query)
                url = parsed.get("q", [""])[0]

            # Skip google's own links and navigation.
            if any(x in url for x in ("google.com", "google.", "/search", "gstatic")):
                continue

            # Reject known non-result / javascript links.
            if url.startswith(("javascript:", "data:")):
                continue

            # Grab title from parent heading or link text.
            container = a.find_parent("h3") or a.parent
            title = (a.get_text(" ", strip=True) or container.get_text(" ", strip=True) if container else "")[:300]

            snippet = ""
            parent = a.find_parent("div")
            if parent:
                snippet = parent.get_text(" ", strip=True)[:400]

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
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
        for page in range(pages):
            start = page * per_page
            html = self._fetch_page(query, start, per_page)
            results.extend(self._parse(html, query, position_offset=len(results)))
            if stop_at and len(results) >= stop_at:
                return results[:stop_at]
            time.sleep(random.uniform(0.5, 1.5))
        return results
