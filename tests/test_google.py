from typing import ClassVar

from lostdock.adapters.google import GoogleEngine, _looks_blocked

SAMPLE_HTML = """
<html><body>
<div class="g">
  <h3><a href="/url?q=https%3A%2F%2Fexposed.example%2Fconfig.php&amp;sa=U">Config File</a></h3>
  <div>Some snippet text about the config.</div>
</div>
<div class="g">
  <h3><a href="https://other.example/page.html">Other page</a></h3>
  <div>Another snippet.</div>
</div>
<a href="https://www.google.com/advanced_search?hl=en">nav</a>
</body></html>
"""


def test_parser_extracts_results():
    engine = GoogleEngine()
    results = engine._parse(SAMPLE_HTML, "config filetype:php")
    assert len(results) == 2
    assert results[0].url == "https://exposed.example/config.php"
    assert results[0].title == "Config File"
    assert "exposed.example" in results[0].url
    # Google's own nav links are excluded
    assert not any("www.google.com" in r.url for r in results)


def test_looks_blocked_detects_all_block_shapes():
    assert _looks_blocked("<title>Sorry</title>unusual traffic from your computer network")
    assert _looks_blocked("enable javascript on your web browser")
    assert _looks_blocked("enablejs")
    assert _looks_blocked("/sorry")
    assert not _looks_blocked('<div class="g"><h3>OpenCode</h3></div>')
    assert not _looks_blocked(SAMPLE_HTML)


def test_http_block_rotates_through_proxies(monkeypatch):
    from lostdock.adapters.google import BlockedError
    from lostdock.core.proxy import ProxyPool

    responses = []

    class FakeResp:
        status_code = 200
        text = "enable javascript on your web browser"
        headers: ClassVar[dict] = {}

        def raise_for_status(self):
            pass

    class FakeSession:
        headers: ClassVar[dict] = {}

        def get(self, url, params, headers, timeout, proxies):
            responses.append(proxies)
            return FakeResp()

    pool = ProxyPool.from_strings(["http://a:1", "http://b:2"])
    engine = GoogleEngine(session=FakeSession(), proxies=pool, use_browser_fallback=False)
    try:
        engine._fetch_http("test", 0, 10)
        raise AssertionError("expected BlockedError")
    except BlockedError:
        pass
    # both proxies were tried and marked failed
    assert len(responses) == 2
    assert responses[0] == {"http": "http://a:1", "https": "http://a:1"}
    assert responses[1] == {"http": "http://b:2", "https": "http://b:2"}


def test_http_success_returns_html(monkeypatch):
    class FakeResp:
        status_code = 200
        text = "<html>real results</html>"
        headers: ClassVar[dict] = {}

        def raise_for_status(self):
            pass

    class FakeSession:
        headers: ClassVar[dict] = {}

        def get(self, url, params, headers, timeout, proxies):
            return FakeResp()

    engine = GoogleEngine(session=FakeSession(), use_browser_fallback=False)
    html = engine._fetch_http("test", 0, 10)
    assert html == "<html>real results</html>"
