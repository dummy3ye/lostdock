from lostdock.adapters.google import GoogleEngine, _google_429_message
from lostdock.adapters.base import RateLimitedError


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
    monkeypatch.setattr(
        "lostdock.adapters.google.random.uniform", lambda a, b: b
    )
    monkeypatch.setattr(
        "lostdock.adapters.google.time.sleep", lambda s: None
    )
    engine = GoogleEngine(
        session=FakeSession([FakeResponse(429), FakeResponse(429), FakeResponse(200, "<html>ok</html>")]),
        max_retries=3,
    )
    html = engine._fetch_page("test", 0, 10)
    assert html == "<html>ok</html>"
    # 3 attempts: 429, 429, 200
    assert len(engine.session.calls) == 3


def test_429_gives_up_after_retries(monkeypatch):
    monkeypatch.setattr(
        "lostdock.adapters.google.random.uniform", lambda a, b: b
    )
    monkeypatch.setattr(
        "lostdock.adapters.google.time.sleep", lambda s: None
    )
    engine = GoogleEngine(
        session=FakeSession([FakeResponse(429), FakeResponse(429), FakeResponse(429), FakeResponse(429)]),
        max_retries=2,
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
    monkeypatch.setattr(
        "lostdock.adapters.google.random.uniform", lambda a, b: b
    )
    engine = GoogleEngine(
        session=FakeSession([FakeResponse(429, headers={"Retry-After": "2"}), FakeResponse(200, "<html>ok</html>")]),
        max_retries=1,
    )
    engine._fetch_page("test", 0, 10)
    assert sleeps[0] == 2.0


def test_429_message_mentions_mitigations():
    msg = _google_429_message("q")
    assert "429" in msg
    assert "proxies" in msg
    assert "DuckDuckGo" in msg
