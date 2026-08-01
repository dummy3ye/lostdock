from lostdock.adapters.base import SearchEngine
from lostdock.core.models import Dork, SearchResult
from lostdock.services.executor import Executor
from lostdock.services.plugins import Plugin
from lostdock.services.repository import Repository
from types import SimpleNamespace


class FakeEngine(SearchEngine):
    name = "fake"

    def __init__(self, results):
        self.results = results

    def search(self, query, pages=1, per_page=10, stop_at=None):
        for r in self.results:
            yield r


def _plugin(hooks):
    return Plugin("test", SimpleNamespace(**hooks))


def test_executor_persists_and_finishes_job(tmp_path):
    repo = Repository(tmp_path / "e.db")
    engine = FakeEngine(
        [SearchResult(title="A", url="https://a.example", snippet="s", position=1)]
    )
    executor = Executor(engine, repo)
    collected = executor.run(Dork(keywords="test"))
    assert len(collected) == 1
    jobs = repo.recent_jobs()
    assert jobs[0]["status"] == "done"
    assert len(repo.results_for_job(jobs[0]["id"])) == 1
    repo.close()


def test_executor_surfaces_errors(tmp_path):
    import pytest

    repo = Repository(tmp_path / "e2.db")

    class BoomEngine(SearchEngine):
        name = "boom"

        def search(self, query, pages=1, per_page=10, stop_at=None):
            raise RuntimeError("network down")

    with pytest.raises(RuntimeError):
        Executor(BoomEngine(), repo).run(Dork(keywords="x"))
    assert repo.recent_jobs()[0]["status"] == "failed"
    repo.close()


def test_executor_calls_on_result_hook(tmp_path):
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

    executor = Executor(engine, repo)
    executor.run(Dork(keywords="test"), on_result=on_result)
    assert seen == ["https://a.example", "https://b.example"]
    repo.close()


def test_executor_plugins_can_drop_results(tmp_path):
    repo = Repository(tmp_path / "e4.db")

    def on_result(result):
        if "drop.example" in result.url:
            return None
        return result

    plugin = _plugin({"on_result": on_result})
    engine = FakeEngine(
        [
            SearchResult(title="A", url="https://a.example", snippet="s", position=1),
            SearchResult(
                title="B", url="https://drop.example", snippet="s", position=2
            ),
        ]
    )
    executor = Executor(engine, repo)
    collected = executor.run(Dork(keywords="test"), plugins=[plugin])
    assert [r.url for r in collected] == ["https://a.example"]
    assert repo.recent_jobs()[0]["status"] == "done"
    repo.close()
