"""Search engine adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.models import SearchResult


class EngineError(Exception):
    """Base engine error."""


class BlockedError(EngineError):
    """The engine detected automated access (CAPTCHA / 403)."""


class RateLimitedError(EngineError):
    """The engine returned a rate limit signal."""


class SearchEngine(ABC):
    """Interface every engine adapter must implement."""

    name = "base"

    @abstractmethod
    def search(
        self,
        query: str,
        pages: int = 1,
        per_page: int = 10,
        stop_at: int | None = None,
    ) -> list[SearchResult]:
        """Execute a search and return structured results.

        pages: number of result pages to fetch
        per_page: results per page (engine-specific)
        stop_at: stop early once this many results are collected
        """
