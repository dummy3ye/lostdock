"""SQLite persistence for jobs and results."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Iterator, List, Optional

from ..core.models import SearchResult

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    engine TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'running'
);
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    title TEXT,
    url TEXT NOT NULL,
    snippet TEXT,
    engine TEXT NOT NULL,
    position INTEGER,
    query TEXT,
    collected_at TEXT NOT NULL DEFAULT (datetime('now')),
    status_code INTEGER,
    http_title TEXT,
    content_type TEXT,
    checked_at TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_results_job ON results(job_id);
CREATE INDEX IF NOT EXISTS idx_results_url ON results(url);
CREATE TABLE IF NOT EXISTS saved_dorks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    dork_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dork_name TEXT NOT NULL UNIQUE,
    interval_minutes INTEGER NOT NULL,
    engine TEXT NOT NULL DEFAULT 'duckduckgo',
    next_run_at TEXT NOT NULL,
    last_run_at TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (dork_name) REFERENCES saved_dorks(name) ON DELETE CASCADE
);
"""

MIGRATIONS = [
    "ALTER TABLE results ADD COLUMN status_code INTEGER",
    "ALTER TABLE results ADD COLUMN http_title TEXT",
    "ALTER TABLE results ADD COLUMN content_type TEXT",
    "ALTER TABLE results ADD COLUMN checked_at TEXT",
]


class Repository:
    """Thread-safe SQLite repository."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._migrate()
        self._conn.commit()

    def _migrate(self) -> None:
        """Add columns that older databases may be missing."""
        existing = {row["name"] for row in self._conn.execute("PRAGMA table_info(results)")}
        for statement in MIGRATIONS:
            column = statement.split()[-2]
            if column not in existing:
                self._conn.execute(statement)
                existing.add(column)

    def create_job(self, query: str, engine: str) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO jobs (query, engine) VALUES (?, ?)", (query, engine)
            )
            self._conn.commit()
            return cur.lastrowid

    def finish_job(self, job_id: int) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE jobs SET status = 'done' WHERE id = ?", (job_id,)
            )
            self._conn.commit()

    def fail_job(self, job_id: int, status: str = "failed") -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE jobs SET status = ? WHERE id = ?", (status, job_id)
            )
            self._conn.commit()

    def add_result(self, job_id: int, result: SearchResult) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO results
                   (job_id, title, url, snippet, engine, position, query)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    job_id,
                    result.title,
                    result.url,
                    result.snippet,
                    result.engine,
                    result.position,
                    result.query,
                ),
            )
            self._conn.commit()

    def add_results(self, job_id: int, results: List[SearchResult]) -> None:
        with self._lock:
            self._conn.executemany(
                """INSERT INTO results
                   (job_id, title, url, snippet, engine, position, query)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        job_id,
                        r.title,
                        r.url,
                        r.snippet,
                        r.engine,
                        r.position,
                        r.query,
                    )
                    for r in results
                ],
            )
            self._conn.commit()

    def results_for_job(self, job_id: int) -> List[SearchResult]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM results WHERE job_id = ? ORDER BY position",
                (job_id,),
            ).fetchall()
        return [
            SearchResult(
                title=r["title"] or "",
                url=r["url"],
                snippet=r["snippet"] or "",
                engine=r["engine"],
                position=r["position"] or 0,
                query=r["query"] or "",
            )
            for r in rows
        ]

    def dedup(self, job_id: int) -> int:
        """Remove duplicate URLs for a job; returns number removed."""
        with self._lock:
            rows = self._conn.execute(
                """SELECT id, url FROM results
                   WHERE job_id = ? ORDER BY id""",
                (job_id,),
            ).fetchall()
            seen: set[str] = set()
            to_delete: list[int] = []
            for r in rows:
                if r["url"] in seen:
                    to_delete.append(r["id"])
                else:
                    seen.add(r["url"])
            for rid in to_delete:
                self._conn.execute("DELETE FROM results WHERE id = ?", (rid,))
            self._conn.commit()
            return len(to_delete)

    def recent_jobs(self, limit: int = 20) -> List[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def save_dork(self, name: str, dork: "Dork") -> None:
        import json

        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO saved_dorks (name, dork_json) VALUES (?, ?)",
                (name, json.dumps(dork.to_dict())),
            )
            self._conn.commit()

    def list_dorks(self) -> List[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, name, created_at FROM saved_dorks ORDER BY name"
            ).fetchall()
        return [dict(r) for r in rows]

    def load_dork(self, name: str) -> Optional["Dork"]:
        import json

        from ..core.models import Dork

        with self._lock:
            row = self._conn.execute(
                "SELECT dork_json FROM saved_dorks WHERE name = ?", (name,)
            ).fetchone()
        if row is None:
            return None
        return Dork.from_dict(json.loads(row["dork_json"]))

    def delete_dork(self, name: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM saved_dorks WHERE name = ?", (name,))
            self._conn.commit()

    def urls_in_job(self, job_id: int) -> List[dict]:
        """Return [{id, url}] for a job, for re-crawling."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, url FROM results WHERE job_id = ? ORDER BY position",
                (job_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def update_crawl(self, result_id: int, status_code, http_title: str, content_type: str) -> None:
        with self._lock:
            self._conn.execute(
                """UPDATE results
                   SET status_code = ?, http_title = ?, content_type = ?, checked_at = datetime('now')
                   WHERE id = ?""",
                (status_code, http_title, content_type, result_id),
            )
            self._conn.commit()

    def update_crawl_by_url(self, url: str, status_code, http_title: str, content_type: str) -> None:
        """Update crawl info for every stored result matching a URL."""
        with self._lock:
            self._conn.execute(
                """UPDATE results
                   SET status_code = ?, http_title = ?, content_type = ?, checked_at = datetime('now')
                   WHERE url = ?""",
                (status_code, http_title, content_type, url),
            )
            self._conn.commit()

    # ----- schedules -----
    def save_schedule(self, dork_name: str, interval_minutes: int, engine: str) -> None:
        import datetime

        next_run = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=interval_minutes)
        ).isoformat()
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO schedules
                   (dork_name, interval_minutes, engine, next_run_at)
                   VALUES (?, ?, ?, ?)""",
                (dork_name, interval_minutes, engine, next_run),
            )
            self._conn.commit()

    def list_schedules(self) -> List[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM schedules ORDER BY dork_name"
            ).fetchall()
        return [dict(r) for r in rows]

    def due_schedules(self) -> List[dict]:
        import datetime

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._lock:
            rows = self._conn.execute(
                """SELECT * FROM schedules
                   WHERE enabled = 1 AND next_run_at <= ?""",
                (now,),
            ).fetchall()
        return [dict(r) for r in rows]

    def bump_schedule(self, dork_name: str, interval_minutes: int) -> None:
        import datetime

        next_run = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=interval_minutes)
        ).isoformat()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                """UPDATE schedules
                   SET next_run_at = ?, last_run_at = ?
                   WHERE dork_name = ?""",
                (next_run, now, dork_name),
            )
            self._conn.commit()

    def toggle_schedule(self, dork_name: str, enabled: bool) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE schedules SET enabled = ? WHERE dork_name = ?",
                (1 if enabled else 0, dork_name),
            )
            self._conn.commit()

    def delete_schedule(self, dork_name: str) -> None:
        with self._lock:
            self._conn.execute(
                "DELETE FROM schedules WHERE dork_name = ?", (dork_name,)
            )
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()
