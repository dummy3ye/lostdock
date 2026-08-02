"""Shared query execution path used by the UI worker and the scheduler."""

from __future__ import annotations

import logging
from collections.abc import Callable

from ..adapters import SearchEngine
from ..core.compiler import compile_dork
from ..core.models import Dork, SearchResult
from .plugins import Plugin
from .repository import Repository

log = logging.getLogger(__name__)

OnResult = Callable[[SearchResult], None]
OnError = Callable[[Exception], None]


def run_query(
    engine: SearchEngine,
    repo: Repository,
    dork: Dork,
    pages: int = 1,
    stop_at: int | None = None,
    plugins: list[Plugin] | None = None,
    on_result: OnResult | None = None,
    on_error: OnError | None = None,
    is_cancelled: Callable[[], bool] | None = None,
) -> list[SearchResult]:
    """Run a dork against an engine, persisting results to a repository.

    Applies the plugin pipeline per result and emits each kept result via
    `on_result`. On error the job is marked failed and `on_error` is invoked;
    when no `on_error` is provided the exception is re-raised. `is_cancelled`
    short-circuits the loop between results.
    """
    query = compile_dork(dork)
    job_id = repo.create_job(query, engine.name)
    collected: list[SearchResult] = []
    try:
        for result in engine.search(query, pages=pages, stop_at=stop_at):
            if is_cancelled and is_cancelled():
                break
            for plugin in plugins or []:
                result = plugin.call("on_result", result)
                if result is None:
                    break
            if result is None:
                continue
            collected.append(result)
            repo.add_result(job_id, result)
            if on_result:
                on_result(result)
        repo.dedup(job_id)
        repo.finish_job(job_id)
        return collected
    except Exception as exc:
        log.exception("Query failed: %s", query)
        repo.fail_job(job_id)
        if on_error:
            on_error(exc)
            return collected
        raise
