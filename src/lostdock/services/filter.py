"""Result filtering by domain whitelist/blacklist and URL patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from ..core.models import SearchResult


def _normalize_domain(domain: str) -> str:
    return domain.strip().lower().removeprefix("www.")


@dataclass
class ResultFilter:
    """Filters results by allowed/blocked domains and regex patterns."""

    whitelist: list[str] = field(default_factory=list)
    blacklist: list[str] = field(default_factory=list)
    url_patterns: list[str] = field(default_factory=list)  # regexes; keep if match
    keep_duplicates: bool = False

    def _passes_domain(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        for domain in self.whitelist:
            if host == _normalize_domain(domain) or host.endswith("." + _normalize_domain(domain)):
                return True
        if self.whitelist:
            return False
        for domain in self.blacklist:
            if host == _normalize_domain(domain) or host.endswith("." + _normalize_domain(domain)):
                return False
        return True

    def _passes_patterns(self, url: str) -> bool:
        if not self.url_patterns:
            return True
        return any(re.search(p, url) for p in self.url_patterns)

    def apply(self, results: list[SearchResult]) -> list[SearchResult]:
        out: list[SearchResult] = []
        seen_urls: set[str] = set()
        for r in results:
            if not self._passes_domain(r.url):
                continue
            if not self._passes_patterns(r.url):
                continue
            if not self.keep_duplicates:
                if r.url in seen_urls:
                    continue
                seen_urls.add(r.url)
            out.append(r)
        return out
