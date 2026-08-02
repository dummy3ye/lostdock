"""Multi-engine aggregator that never lets one blocked engine kill a search."""

from __future__ import annotations

import logging
from collections.abc import Callable

from ..core.models import SearchResult
from .base import SearchEngine

log = logging.getLogger(__name__)

StatusFn = Callable[[str], None]


class MultiEngine(SearchEngine):
    """Runs several engines for one query and merges their results.

    Each engine is tried independently: a CAPTCHA or rate limit on one engine
    is logged and the next engine still runs, so the search returns every
    result that any engine could produce. Results are deduplicated by URL
    (first occurrence wins).

    ``on_status`` is invoked with short progress messages as engines run.
    """

    name = "all"

    def __init__(
        self,
        engines: list[SearchEngine],
        on_status: StatusFn | None = None,
    ) -> None:
        self.engines = engines
        self.on_status = on_status

    def _emit(self, message: str) -> None:
        log.debug("MultiEngine: %s", message)
        if self.on_status:
            self.on_status(message)

    def search(
        self,
        query: str,
        pages: int = 1,
        per_page: int = 10,
        stop_at: int | None = None,
    ) -> list[SearchResult]:
        seen: set[str] = set()
        merged: list[SearchResult] = []
        errors: list[str] = []
        for engine in self.engines:
            try:
                self._emit(f"{engine.name}: searching...")
                results = engine.search(query, pages=pages, per_page=per_page, stop_at=stop_at)
            except Exception as exc:  # one blocked engine must not abort the rest
                log.warning("Engine %s failed: %s", engine.name, exc)
                errors.append(f"{engine.name}: {exc}")
                self._emit(f"{engine.name}: blocked ({type(exc).__name__})")
                continue
            fresh = 0
            for result in results:
                key = result.url.rstrip("/").lower()
                if key in seen:
                    continue
                seen.add(key)
                merged.append(result)
                fresh += 1
            self._emit(f"{engine.name}: {fresh} new results")
            if stop_at is not None and len(merged) >= stop_at:
                break
        if not merged and errors:
            raise RuntimeError("All engines failed: " + "; ".join(errors))
        return merged

    def close(self) -> None:
        for engine in self.engines:
            close = getattr(engine, "close", None)
            if callable(close):
                close()
