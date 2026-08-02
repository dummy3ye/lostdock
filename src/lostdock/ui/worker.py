"""Background search worker for the Qt UI."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal

from ..adapters import MultiEngine, SearchEngine
from ..core.models import Dork
from ..services.crawler import crawl_url
from ..services.plugins import Plugin
from ..services.query import run_query
from ..services.repository import Repository


class SearchWorker(QObject):
    """Runs a dork search off the UI thread, emitting results as they arrive."""

    result_ready = Signal(object)  # SearchResult
    finished = Signal(int)  # total collected
    failed = Signal(str)  # error message
    status = Signal(str)  # progress message

    def __init__(
        self,
        engine: SearchEngine,
        repo: Repository,
        dork: Dork,
        pages: int = 1,
        stop_at: int | None = None,
        plugins: list[Plugin] | None = None,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.repo = repo
        self.dork = dork
        self.pages = pages
        self.stop_at = stop_at
        self.plugins = plugins or []
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        if isinstance(self.engine, MultiEngine):
            self.engine.on_status = lambda msg: self.status.emit(msg)
        collected = run_query(
            self.engine,
            self.repo,
            self.dork,
            pages=self.pages,
            stop_at=self.stop_at,
            plugins=self.plugins,
            on_result=lambda result: self.result_ready.emit(result),
            on_error=lambda exc: self.failed.emit(str(exc)),
            is_cancelled=lambda: self._cancelled,
        )
        self.finished.emit(len(collected))


def run_search(
    engine: SearchEngine,
    repo: Repository,
    dork: Dork,
    pages: int = 1,
    stop_at: int | None = None,
    plugins: list[Plugin] | None = None,
) -> SearchWorker:
    """Start a search in a new QThread; returns the worker.

    Connect to worker.result_ready / finished / failed before starting.
    The returned QThread is owned by the worker object.
    """
    thread = QThread()
    worker = SearchWorker(engine, repo, dork, pages=pages, stop_at=stop_at, plugins=plugins)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    worker.failed.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    worker._thread = thread  # keep reference
    thread.start()
    return worker


class CrawlWorker(QObject):
    """Re-checks URLs off the UI thread, emitting reports as they arrive."""

    report_ready = Signal(object)  # CrawlReport
    finished = Signal(int)  # total crawled
    failed = Signal(str)  # error message

    def __init__(
        self,
        urls: list[str],
        repo: Repository | None = None,
        persist: bool = False,
    ) -> None:
        super().__init__()
        self.urls = list(urls)
        self.repo = repo
        self.persist = persist
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        total = 0
        try:
            for url in self.urls:
                if self._cancelled:
                    break
                report = crawl_url(url)
                if self.persist and self.repo is not None:
                    self.repo.update_crawl_by_url(
                        url, report.status_code, report.http_title, report.content_type
                    )
                self.report_ready.emit(report)
                total += 1
            self.finished.emit(total)
        except Exception as exc:
            self.failed.emit(str(exc))


def run_crawl(
    urls: list[str],
    repo: Repository | None = None,
    persist: bool = False,
) -> CrawlWorker:
    """Start a URL re-check in a new QThread; returns the worker."""
    thread = QThread()
    worker = CrawlWorker(urls, repo=repo, persist=persist)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    worker.failed.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    worker._thread = thread  # keep reference
    thread.start()
    return worker
