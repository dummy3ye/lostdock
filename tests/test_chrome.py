import json

import pytest

from lostdock.adapters.chrome import _CdpSession, _WebSocket, _is_bot_page, _find_chrome
from lostdock.adapters.base import BlockedError
from lostdock.core.models import SearchResult


# ---------- WebSocket framing ----------

def _unmask(frame: bytes) -> bytes:
    """Turn a client (masked) frame back into plaintext for assertions."""
    assert frame[0] == 0x81
    b2 = frame[1]
    assert b2 & 0x80, "expected masked client frame"
    length = b2 & 0x7F
    offset = 2
    if length == 126:
        length = int.from_bytes(frame[2:4], "big")
        offset = 4
    elif length == 127:
        length = int.from_bytes(frame[2:10], "big")
        offset = 10
    mask = frame[offset : offset + 4]
    payload = frame[offset + 4 :]
    return bytes(b ^ mask[i % 4] for i, b in enumerate(payload))


def test_websocket_send_text_masks_and_encodes():
    ws = _WebSocket("h", 1, "/")
    sent = []

    class FakeSock:
        def sendall(self, data):
            sent.append(bytes(data))

    ws._sock = FakeSock()
    ws.send_text("hello")
    assert len(sent) == 1
    assert _unmask(sent[0]) == b"hello"


def test_cdp_session_sends_id_and_returns_matching_result():
    ws = _WebSocket("h", 1, "/")
    ws._sock = __import__("socket").socket()

    outbound = []
    responses = iter(
        [
            json.dumps({"method": "Page.loadEventFired", "params": {}}),
            json.dumps(
                {
                    "id": 1,
                    "result": {"result": {"type": "string", "value": "complete"}},
                }
            ),
        ]
    )

    ws.send_text = lambda text, opcode=0x1: outbound.append((opcode, text))
    ws.recv_text = lambda timeout=None: next(responses)

    session = _CdpSession(ws)
    result = session.call(
        "Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True}
    )
    assert result["result"]["value"] == "complete"
    msg = json.loads(outbound[0][1])
    assert msg["id"] == 1
    assert msg["method"] == "Runtime.evaluate"


# ---------- bot-page detection ----------

def test_is_bot_page_detects_recaptcha():
    assert _is_bot_page('<form id="captcha-form">g-recaptcha</form>')
    assert _is_bot_page("unusual traffic on your computer network")
    assert _is_bot_page('/sorry/index')
    assert not _is_bot_page("<html><div>real results here</div></html>")


# ---------- ChromeEngine search with a fake session ----------

class FakeEngineSession:
    def __init__(self, pages):
        self._pages = iter(pages)
        self.calls = []

    def call(self, method, params=None):
        self.calls.append((method, params))
        if method == "Runtime.evaluate":
            expr = (params or {}).get("expression", "")
            if "readyState" in expr:
                return {"result": {"value": "complete"}}
            if "outerHTML" in expr:
                return {"result": {"value": next(self._pages)}}
        return {}


GOOGLE_HTML = """
<html><body>
<div id="search">
  <a href="https://result.example/page"><h3>Result One</h3></a>
</div>
</body></html>
"""

BOT_HTML = '<html><body><form id="captcha-form">g-recaptcha</form></body></html>'


def _make_engine(tmp_path, pages):
    from lostdock.adapters.chrome import ChromeEngine

    engine = ChromeEngine(user_data_dir=tmp_path, port=0)
    session = FakeEngineSession(pages)
    engine._session = session

    class FakeWS:
        def close(self):
            pass

    engine._ws = FakeWS()
    engine._ensure_browser = lambda: None  # do not launch a real Chrome
    return engine, session


def test_chrome_search_returns_results(tmp_path):
    engine, session = _make_engine(tmp_path, [GOOGLE_HTML])
    results = engine.search("test query", pages=1)
    assert len(results) == 1
    assert results[0].url == "https://result.example/page"
    assert results[0].title == "Result One"
    assert results[0].engine == "google"
    assert any(m[0] == "Page.navigate" for m in session.calls)


def test_chrome_search_raises_blocked_on_captcha(tmp_path):
    engine, _session = _make_engine(tmp_path, [BOT_HTML])
    with pytest.raises(BlockedError):
        engine.search("test query", pages=1)


def test_chrome_search_stop_at(tmp_path):
    htmls = [GOOGLE_HTML, GOOGLE_HTML.replace("Result One", "Result Two")]
    engine, _session = _make_engine(tmp_path, htmls)
    results = engine.search("q", pages=2, stop_at=1)
    assert len(results) == 1


def test_chrome_no_browser_raises(tmp_path):
    from lostdock.adapters.chrome import ChromeEngine

    engine = ChromeEngine(
        browser="/nonexistent/chrome/binary", user_data_dir=tmp_path, port=0
    )
    with pytest.raises(Exception, match="No Chrome/Chromium found"):
        engine.search("q", pages=1)


def test_find_chrome_returns_none_when_absent(monkeypatch):
    monkeypatch.setattr("lostdock.adapters.chrome.shutil.which", lambda _: None)
    monkeypatch.setattr("lostdock.adapters.chrome.os.path.exists", lambda _: False)
    monkeypatch.setattr("lostdock.adapters.chrome.os.environ", {})
    assert _find_chrome() is None
