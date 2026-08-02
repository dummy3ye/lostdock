from lostdock.core.models import Dork
from lostdock.services.repository import Repository


def test_migration_adds_columns(tmp_path):
    """Create a DB with the old schema, then confirm migration works."""
    import sqlite3

    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            title TEXT, url TEXT NOT NULL, snippet TEXT,
            engine TEXT NOT NULL, position INTEGER, query TEXT,
            collected_at TEXT NOT NULL DEFAULT (datetime('now')))"""
    )
    conn.commit()
    conn.close()

    repo = Repository(path)
    cols = {row["name"] for row in repo._conn.execute("PRAGMA table_info(results)")}
    assert "status_code" in cols
    assert "http_title" in cols
    assert "checked_at" in cols
    repo.close()


def test_schedule_flow(tmp_path):
    repo = Repository(tmp_path / "s.db")
    repo.save_dork("weekly", Dork(keywords="security pdf", file_types=["pdf"]))
    repo.save_schedule("weekly", 60, "duckduckgo")
    scheds = repo.list_schedules()
    assert len(scheds) == 1
    assert scheds[0]["dork_name"] == "weekly"
    assert scheds[0]["enabled"] == 1
    # not due yet (next run is 60 min out)
    assert repo.due_schedules() == []
    repo.close()


def test_schedule_due_after_bump(tmp_path):
    repo = Repository(tmp_path / "s2.db")
    repo.save_dork("hourly", Dork(keywords="x"))
    repo.save_schedule("hourly", 60, "duckduckgo")
    # force it due
    import datetime

    past = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
    ).isoformat()
    with repo._lock:
        repo._conn.execute("UPDATE schedules SET next_run_at = ?", (past,))
        repo._conn.commit()
    due = repo.due_schedules()
    assert len(due) == 1
    assert due[0]["dork_name"] == "hourly"
    repo.close()


def test_update_crawl(tmp_path):
    repo = Repository(tmp_path / "c.db")
    job = repo.create_job("q", "google")
    repo.add_results(
        job,
        [
            __import__("lostdock.core.models", fromlist=["SearchResult"]).SearchResult(
                title="t", url="https://x.example", snippet="s", position=1
            )
        ],
    )
    row = repo.urls_in_job(job)[0]
    repo.update_crawl(row["id"], 200, "Live Page", "text/html")
    # verify via row content
    with repo._lock:
        r = repo._conn.execute(
            "SELECT status_code, http_title, content_type FROM results WHERE id=?",
            (row["id"],),
        ).fetchone()
    assert r["status_code"] == 200
    assert r["http_title"] == "Live Page"
    assert r["content_type"] == "text/html"
    repo.close()


def test_update_crawl_by_url(tmp_path):
    from lostdock.core.models import SearchResult

    repo = Repository(tmp_path / "c2.db")
    job = repo.create_job("q", "google")
    repo.add_results(
        job,
        [
            SearchResult(title="t", url="https://y.example", snippet="s", position=1),
            SearchResult(title="t2", url="https://y.example", snippet="s", position=2),
        ],
    )
    repo.update_crawl_by_url("https://y.example", 404, "Gone", "text/html")
    with repo._lock:
        rows = repo._conn.execute(
            "SELECT status_code, http_title FROM results WHERE url=?", ("https://y.example",)
        ).fetchall()
    assert len(rows) == 2
    assert all(r["status_code"] == 404 for r in rows)
    assert rows[0]["http_title"] == "Gone"
    repo.close()
