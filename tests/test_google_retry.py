from lostdock.adapters.base import RateLimitedError
from lostdock.adapters.google import GoogleEngine, _google_429_message


class FakeResponse:
    def __init__(self, status_code=200, text="", headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    """Returns a scripted sequence of responses."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, headers=None, timeout=None, proxies=None):
        self.calls.append(params)
        resp = self.responses.pop(0) if self.responses else FakeResponse(429)
        return resp


def test_429_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("lostdock.adapters.google.random.uniform", lambda a, b: b)
    monkeypatch.setattr("lostdock.adapters.google.time.sleep", lambda s: None)
    engine = GoogleEngine(
        session=FakeSession(
            [
                FakeResponse(429),
                FakeResponse(429),
                FakeResponse(200, "<html>ok</html>"),
            ]
        ),
        max_retries=3,
        use_browser_fallback=False,
    )
    html = engine._fetch_page("test", 0, 10)
    assert html == "<html>ok</html>"
    # 3 attempts: 429, 429, 200
    assert len(engine.session.calls) == 3


def test_429_gives_up_after_retries(monkeypatch):
    monkeypatch.setattr("lostdock.adapters.google.random.uniform", lambda a, b: b)
    monkeypatch.setattr("lostdock.adapters.google.time.sleep", lambda s: None)
    engine = GoogleEngine(
        session=FakeSession(
            [
                FakeResponse(429),
                FakeResponse(429),
                FakeResponse(429),
                FakeResponse(429),
            ]
        ),
        max_retries=2,
        use_browser_fallback=False,
    )
    try:
        engine._fetch_page("test", 0, 10)
        raise AssertionError("expected RateLimitedError")
    except RateLimitedError as exc:
        assert "rate-limiting" in str(exc)
        assert "proxies" in str(exc)
    assert len(engine.session.calls) == 3  # 1 + max_retries


def test_honors_retry_after_header(monkeypatch):
    sleeps = []
    monkeypatch.setattr("lostdock.adapters.google.time.sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr("lostdock.adapters.google.random.uniform", lambda a, b: b)
    engine = GoogleEngine(
        session=FakeSession(
            [
                FakeResponse(429, headers={"Retry-After": "2"}),
                FakeResponse(200, "<html>ok</html>"),
            ]
        ),
        max_retries=1,
        use_browser_fallback=False,
    )
    engine._fetch_page("test", 0, 10)
    assert sleeps[0] == 2.0


def test_429_message_mentions_mitigations():
    msg = _google_429_message("q")
    assert "429" in msg
    assert "proxies" in msg
    assert "DuckDuckGo" in msg


class FakeRenderer:
    def __init__(
        self,
        html="<html><div class='g'><h3>"
        "<a href='/url?q=https%3A%2F%2Fok.example'>OK</a></h3></div></html>",
    ):
        self.html = html
        self.calls = []

    def render(self, url, wait_selector=None):
        self.calls.append(url)
        return self.html

    def close(self):
        pass


def test_browser_fallback_used_after_http_block(monkeypatch):
    monkeypatch.setattr("lostdock.adapters.google.random.uniform", lambda a, b: b)
    monkeypatch.setattr("lostdock.adapters.google.time.sleep", lambda s: None)
    engine = GoogleEngine(
        session=FakeSession([FakeResponse(429), FakeResponse(429), FakeResponse(429)]),
        max_retries=1,
    )
    renderer = FakeRenderer()
    monkeypatch.setattr(engine, "_renderer", renderer)
    html = engine._fetch_page("test", 0, 10)
    assert html == renderer.html
    assert len(renderer.calls) == 1
    assert "test" in renderer.calls[0]
    assert "udm=14" in renderer.calls[0]


def test_browser_fallback_blocked_page_raises(monkeypatch):
    monkeypatch.setattr("lostdock.adapters.google.random.uniform", lambda a, b: b)
    monkeypatch.setattr("lostdock.adapters.google.time.sleep", lambda s: None)
    engine = GoogleEngine(
        session=FakeSession([FakeResponse(429), FakeResponse(429), FakeResponse(429)]),
        max_retries=1,
    )
    renderer = FakeRenderer(html="<html>unusual traffic from your network</html>")
    monkeypatch.setattr(engine, "_renderer", renderer)
    try:
        engine._fetch_page("test", 0, 10)
        raise AssertionError("expected BlockedError")
    except Exception as exc:
        from lostdock.adapters.base import BlockedError

        assert isinstance(exc, BlockedError)
        assert "proxies" in str(exc)


def test_browser_fallback_unavailable_wraps_error(monkeypatch):
    from lostdock.adapters.browser import BrowserUnavailable

    monkeypatch.setattr("lostdock.adapters.google.random.uniform", lambda a, b: b)
    monkeypatch.setattr("lostdock.adapters.google.time.sleep", lambda s: None)

    def raise_unavailable():
        raise BrowserUnavailable("Chromium is not installed")

    engine = GoogleEngine(
        session=FakeSession([FakeResponse(429), FakeResponse(429), FakeResponse(429)]),
        max_retries=1,
    )
    monkeypatch.setattr(
        type(engine),
        "_browser",
        lambda self: (_ for _ in ()).throw(BrowserUnavailable("Chromium is not installed")),
    )
    try:
        engine._fetch_page("test", 0, 10)
        raise AssertionError("expected RateLimitedError")
    except RateLimitedError as exc:
        assert "Chromium is not installed" in str(exc)
        assert "rate-limiting" in str(exc)
