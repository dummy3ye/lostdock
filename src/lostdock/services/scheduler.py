"""Background scheduler for recurring dorks."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from ..adapters import ENGINES
from ..core.proxy import ProxyPool
from ..services.repository import Repository
from .query import run_query

log = logging.getLogger(__name__)


class Scheduler:
    """Polls the repository for due schedules and runs them in a worker thread.

    Each run creates a new job and stores results via the shared query path.
    The `on_run` callback fires once per completed run.
    """

    def __init__(
        self,
        repo: Repository,
        poll_seconds: float = 30.0,
        proxies: ProxyPool | None = None,
        on_run: Callable[[str, int], None] | None = None,
        on_error: Callable[[str, str], None] | None = None,
    ) -> None:
        self.repo = repo
        self.poll_seconds = poll_seconds
        self.proxies = proxies
        self.on_run = on_run
        self.on_error = on_error
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="lostdock-scheduler", daemon=True)
        self._thread.start()
        log.info("Scheduler started (poll %ss)", self.poll_seconds)

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                for schedule in self.repo.due_schedules():
                    if self._stop.is_set():
                        break
                    self._run_schedule(schedule)
            except Exception as exc:
                log.exception("Scheduler loop error")
                if self.on_error:
                    self.on_error("scheduler", str(exc))
            self._stop.wait(self.poll_seconds)

    def _run_schedule(self, schedule: dict) -> None:
        name = schedule["dork_name"]
        dork = self.repo.load_dork(name)
        if dork is None:
            log.warning("Schedule references missing dork: %s", name)
            self.repo.delete_schedule(name)
            return
        engine_name = schedule["engine"]
        try:
            engine = ENGINES[engine_name](proxies=self.proxies)
        except KeyError:
            engine = ENGINES["duckduckgo"](proxies=self.proxies)
        failed = {"value": False}
        try:
            collected = run_query(
                engine,
                self.repo,
                dork,
                pages=1,
                on_error=lambda exc: self._note_error(name, str(exc), failed),
            )
        finally:
            self.repo.bump_schedule(name, schedule["interval_minutes"])
        if not failed["value"] and self.on_run:
            self.on_run(name, len(collected))

    def _note_error(self, name: str, message: str, failed: dict) -> None:
        failed["value"] = True
        log.warning("Scheduled dork %s failed: %s", name, message)
        if self.on_error:
            self.on_error(name, message)
