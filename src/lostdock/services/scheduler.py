"""Background scheduler for recurring dorks."""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

from ..adapters import ENGINES
from ..core.compiler import compile_dork
from ..core.proxy import ProxyPool
from ..services.repository import Repository

log = logging.getLogger(__name__)


class Scheduler:
    """Polls the repository for due schedules and runs them in a worker thread.

    Each run creates a new job (via the engine's executor path in the worker)
    and stores results. The `on_run` callback fires once per completed run.
    """

    def __init__(
        self,
        repo: Repository,
        poll_seconds: float = 30.0,
        proxies: Optional[ProxyPool] = None,
        on_run: Optional[Callable[[str, int], None]] = None,
        on_error: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.repo = repo
        self.poll_seconds = poll_seconds
        self.proxies = proxies
        self.on_run = on_run
        self.on_error = on_error
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

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
            except Exception as exc:  # noqa: BLE001
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
        query = compile_dork(dork)
        job_id = self.repo.create_job(query, engine.name)
        count = 0
        try:
            for result in engine.search(query, pages=1):
                self.repo.add_result(job_id, result)
                count += 1
            self.repo.dedup(job_id)
            self.repo.finish_job(job_id)
        except Exception as exc:  # noqa: BLE001
            self.repo.fail_job(job_id)
            log.warning("Scheduled dork %s failed: %s", name, exc)
            if self.on_error:
                self.on_error(name, str(exc))
            return
        finally:
            self.repo.bump_schedule(name, schedule["interval_minutes"])
        if self.on_run:
            self.on_run(name, count)
