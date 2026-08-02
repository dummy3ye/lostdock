from lostdock.adapters.browser import BrowserRenderer, BrowserUnavailable


def test_browser_unavailable_raised_when_playwright_missing(monkeypatch):

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "playwright.sync_api":
            raise ImportError("No module named 'playwright'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    renderer = BrowserRenderer()
    try:
        renderer.render("https://example.com")
        raise AssertionError("expected BrowserUnavailable")
    except BrowserUnavailable as exc:
        assert "Playwright is not installed" in str(exc)


def test_browser_renderer_close_is_safe_when_never_started():
    renderer = BrowserRenderer()
    renderer.close()
    assert renderer._browser is None
    assert renderer._playwright is None
