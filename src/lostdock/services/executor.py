"""High-level query execution service."""

from __future__ import annotations

import logging
from typing import Callable, List, Optional

from ..adapters import SearchEngine
from ..core.compiler import compile_dork
from ..core.models import Dork, SearchResult
from ..services.repository import Repository

log = logging.getLogger(__name__)

OnResult = Callable[[SearchResult], None]
OnError = Callable[[Exception], None]


class Executor:
    """Runs a Dork against an engine, persisting results to a repository."""

    def __init__(self, engine: SearchEngine, repo: Repository) -> None:
        self.engine = engine
        self.repo = repo

    def run(
        self,
        dork: Dork,
        pages: int = 1,
        stop_at: Optional[int] = None,
        on_result: Optional[OnResult] = None,
        on_error: Optional[OnError] = None,
    ) -> List[SearchResult]:
        query = compile_dork(dork)
        job_id = self.repo.create_job(query, self.engine.name)
        collected: List[SearchResult] = []
        try:
            for result in self.engine.search(query, pages=pages, stop_at=stop_at):
                collected.append(result)
                self.repo.add_result(job_id, result)
                if on_result:
                    on_result(result)
            self.repo.dedup(job_id)
            self.repo.finish_job(job_id)
        except Exception as exc:
            log.exception("Query failed: %s", query)
            self.repo.fail_job(job_id)
            if on_error:
                on_error(exc)
            else:
                raise
        return collected
