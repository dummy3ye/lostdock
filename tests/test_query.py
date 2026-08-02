from types import SimpleNamespace

from lostdock.adapters.base import SearchEngine
from lostdock.core.models import Dork, SearchResult
from lostdock.services.plugins import Plugin
from lostdock.services.query import run_query
from lostdock.services.repository import Repository


class FakeEngine(SearchEngine):
    name = "fake"

    def __init__(self, results):
        self.results = results

    def search(self, query, pages=1, per_page=10, stop_at=None):
        yield from self.results


def _plugin(hooks):
    return Plugin("test", SimpleNamespace(**hooks))


def test_run_query_persists_and_finishes_job(tmp_path):
    repo = Repository(tmp_path / "e.db")
    engine = FakeEngine([SearchResult(title="A", url="https://a.example", snippet="s", position=1)])
    collected = run_query(engine, repo, Dork(keywords="test"))
    assert len(collected) == 1
    jobs = repo.recent_jobs()
    assert jobs[0]["status"] == "done"
    assert len(repo.results_for_job(jobs[0]["id"])) == 1
    repo.close()


def test_run_query_surfaces_errors(tmp_path):
    import pytest

    repo = Repository(tmp_path / "e2.db")

    class BoomEngine(SearchEngine):
        name = "boom"

        def search(self, query, pages=1, per_page=10, stop_at=None):
            raise RuntimeError("network down")

    with pytest.raises(RuntimeError):
        run_query(BoomEngine(), repo, Dork(keywords="x"))
    assert repo.recent_jobs()[0]["status"] == "failed"
    repo.close()


def test_run_query_calls_on_result_hook(tmp_path):
    repo = Repository(tmp_path / "e3.db")
    engine = FakeEngine(
        [
            SearchResult(title="A", url="https://a.example", snippet="s", position=1),
            SearchResult(title="B", url="https://b.example", snippet="s", position=2),
        ]
    )
    seen = []

    def on_result(result):
        seen.append(result.url)

    run_query(engine, repo, Dork(keywords="test"), on_result=on_result)
    assert seen == ["https://a.example", "https://b.example"]
    repo.close()


def test_run_query_plugins_can_drop_results(tmp_path):
    repo = Repository(tmp_path / "e4.db")

    def on_result(result):
        if "drop.example" in result.url:
            return None
        return result

    plugin = _plugin({"on_result": on_result})
    engine = FakeEngine(
        [
            SearchResult(title="A", url="https://a.example", snippet="s", position=1),
            SearchResult(title="B", url="https://drop.example", snippet="s", position=2),
        ]
    )
    collected = run_query(engine, repo, Dork(keywords="test"), plugins=[plugin])
    assert [r.url for r in collected] == ["https://a.example"]
    assert repo.recent_jobs()[0]["status"] == "done"
    repo.close()


def test_run_query_cancellation_stops_loop(tmp_path):
    repo = Repository(tmp_path / "e5.db")
    engine = FakeEngine(
        [
            SearchResult(title="A", url="https://a.example", snippet="s", position=1),
            SearchResult(title="B", url="https://b.example", snippet="s", position=2),
        ]
    )
    calls = {"n": 0}

    def cancel_after_first():
        calls["n"] += 1
        return calls["n"] > 1

    collected = run_query(engine, repo, Dork(keywords="test"), is_cancelled=cancel_after_first)
    assert [r.url for r in collected] == ["https://a.example"]
    assert repo.recent_jobs()[0]["status"] == "done"
    repo.close()
