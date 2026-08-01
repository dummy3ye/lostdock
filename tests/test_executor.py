from lostdock.adapters.base import SearchEngine
from lostdock.core.models import Dork, SearchResult
from lostdock.services.executor import Executor
from lostdock.services.repository import Repository


class FakeEngine(SearchEngine):
    name = "fake"

    def __init__(self, results):
        self.results = results

    def search(self, query, pages=1, per_page=10, stop_at=None):
        for r in self.results:
            yield r


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
