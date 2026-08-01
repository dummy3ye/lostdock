from lostdock.services.filter import ResultFilter
from lostdock.core.models import SearchResult


def _r(url):
    return SearchResult(title="t", url=url, snippet="s")


def test_whitelist_only():
    f = ResultFilter(whitelist=["example.com"])
    out = f.apply([_r("https://example.com/a"), _r("https://other.com/b")])
    assert [r.url for r in out] == ["https://example.com/a"]


def test_whitelist_matches_subdomains():
    f = ResultFilter(whitelist=["example.com"])
    out = f.apply([_r("https://sub.example.com/a"), _r("https://other.com/b")])
    assert [r.url for r in out] == ["https://sub.example.com/a"]


def test_blacklist_excludes():
    f = ResultFilter(blacklist=["badexample.com"])
    out = f.apply([_r("https://badexample.com/a"), _r("https://good.com/b")])
    assert [r.url for r in out] == ["https://good.com/b"]


def test_url_patterns_keep_matching():
    f = ResultFilter(url_patterns=[r"/uploads/", r"/docs/"])
    out = f.apply([_r("https://x.com/uploads/f.pdf"), _r("https://x.com/other")])
    assert [r.url for r in out] == ["https://x.com/uploads/f.pdf"]


def test_dedup():
    f = ResultFilter()
    out = f.apply([_r("https://x.com/a"), _r("https://x.com/a")])
    assert len(out) == 1


def test_keep_duplicates():
    f = ResultFilter(keep_duplicates=True)
    out = f.apply([_r("https://x.com/a"), _r("https://x.com/a")])
    assert len(out) == 2
