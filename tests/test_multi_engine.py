from lostdock.adapters.base import BlockedError, SearchEngine
from lostdock.adapters.multi import MultiEngine
from lostdock.core.models import SearchResult


def _result(title: str, url: str, engine: str, position: int = 1) -> SearchResult:
    return SearchResult(title=title, url=url, snippet="", engine=engine, position=position)


class _FakeEngine(SearchEngine):
    name = "fake"

    def __init__(self, results, error: Exception | None = None):
        self.results = results
        self.error = error
        self.close_called = False

    def search(self, query, pages=1, per_page=10, stop_at=None):
        if self.error is not None:
            raise self.error
        return list(self.results)

    def close(self):
        self.close_called = True


def test_multi_engine_merges_and_dedups():
    a = _FakeEngine(
        [
            _result("A1", "https://x.com/1", "google", 1),
            _result("A2", "https://x.com/2", "google", 2),
        ]
    )
    b = _FakeEngine(
        [_result("B1", "https://x.com/2", "bing", 1), _result("B2", "https://x.com/3", "bing", 2)]
    )
    multi = MultiEngine([a, b])
    results = multi.search("query")
    assert [r.url for r in results] == ["https://x.com/1", "https://x.com/2", "https://x.com/3"]
    # first occurrence (google's) is kept
    assert results[1].engine == "google"


def test_multi_engine_ignores_blocked_engine():
    blocked = _FakeEngine([], error=BlockedError("captcha"))
    ok = _FakeEngine([_result("OK", "https://ok.com/1", "duckduckgo", 1)])
    multi = MultiEngine([blocked, ok])
    results = multi.search("query")
    assert [r.url for r in results] == ["https://ok.com/1"]


def test_multi_engine_raises_when_all_fail():
    a = _FakeEngine([], error=BlockedError("captcha"))
    b = _FakeEngine([], error=RuntimeError("boom"))
    multi = MultiEngine([a, b])
    try:
        multi.search("query")
        raise AssertionError("expected an exception")
    except RuntimeError as exc:
        assert "All engines failed" in str(exc)


def test_multi_engine_stop_at():
    a = _FakeEngine(
        [_result("A", "https://x.com/1", "google", 1), _result("B", "https://x.com/2", "google", 2)]
    )
    b = _FakeEngine([_result("C", "https://x.com/3", "bing", 1)])
    multi = MultiEngine([a, b])
    results = multi.search("query", stop_at=2)
    assert len(results) == 2
    assert [r.url for r in results] == ["https://x.com/1", "https://x.com/2"]


def test_multi_engine_status_callback():
    seen = []
    a = _FakeEngine([_result("A", "https://x.com/1", "google", 1)])
    b = _FakeEngine([], error=BlockedError("captcha"))
    multi = MultiEngine([a, b], on_status=seen.append)
    multi.search("query")
    assert any("fake" in m and "searching" in m for m in seen)
    assert any("blocked" in m for m in seen)
    assert any("new results" in m for m in seen)


def test_multi_engine_close():
    a = _FakeEngine([])
    b = _FakeEngine([])
    multi = MultiEngine([a, b])
    multi.close()
    assert a.close_called
    assert b.close_called
