import subprocess

import pytest

from lostdock.adapters.chrome import ChromeEngine, _find_chrome
from lostdock.adapters.base import EngineError


def test_find_chrome_returns_none_when_absent(monkeypatch):
    monkeypatch.setattr("lostdock.adapters.chrome.shutil.which", lambda _: None)
    monkeypatch.setattr("lostdock.adapters.chrome.os.path.exists", lambda _: False)
    monkeypatch.setattr("lostdock.adapters.chrome.os.environ", {})
    assert _find_chrome() is None


def test_search_launches_browser_with_search_url(monkeypatch):
    launched = []

    def fake_popen(cmd, stdout=None, stderr=None):
        launched.append(cmd)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    engine = ChromeEngine(browser="/usr/bin/google-chrome-stable")
    results = engine.search("python requests", pages=1)
    assert results == []
    assert len(launched) == 1
    assert launched[0][0] == "/usr/bin/google-chrome-stable"
    assert "google.com/search" in launched[0][1]
    assert "q=python+requests" in launched[0][1]


def test_search_respects_per_page_and_hl(monkeypatch):
    launched = []

    def fake_popen(cmd, stdout=None, stderr=None):
        launched.append(cmd)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    engine = ChromeEngine(browser="/usr/bin/chromium")
    engine.search("filetype:pdf", pages=1, per_page=25)
    url = launched[0][1]
    assert "num=25" in url
    assert "hl=en" in url


def test_search_raises_when_no_browser(monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: (_ for _ in ()).throw(OSError("no such file")))
    engine = ChromeEngine(browser="/nonexistent/chrome")
    with pytest.raises(EngineError, match="Failed to launch Chrome"):
        engine.search("q", pages=1)


def test_engine_registered_in_engines():
    from lostdock.adapters import ENGINES

    assert "google-chrome" in ENGINES
    assert ENGINES["google-chrome"].name == "google-chrome"
