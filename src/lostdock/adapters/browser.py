"""Headless-browser page rendering via Playwright.

Plain HTTP scraping trips Google's behavioral anti-bot checks (JS execution,
TLS fingerprint, webdriver detection) from many networks. Rendering the SERP in
a real headless Chromium defeats those checks because the page sees an actual
browser. The browser is launched lazily and reused across requests.

The Chromium binary must be installed once (``python -m playwright install
chromium``). If Playwright or the browser is unavailable, ``render()`` raises
BrowserUnavailable so callers can fall back to plain HTTP scraping.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# Strip the most obvious automation markers. Chromium exposes `navigator.webdriver`
# unless it is patched before any page script runs.
_STEALTH_SCRIPT = """
Object.defineProperty(navigator, "webdriver", { get: () => undefined });
window.chrome = window.chrome || { runtime: {} };
Object.defineProperty(navigator, "languages", { get: () => ["en-US", "en"] });
Object.defineProperty(navigator, "plugins", { get: () => [1, 2, 3, 4, 5] });
"""


class BrowserUnavailable(Exception):
    """Raised when Playwright or the Chromium binary is not installed."""


class BrowserRenderer:
    """Renders URLs in a shared headless Chromium and returns page HTML."""

    def __init__(
        self,
        user_agent: str | None = None,
        headless: bool = True,
        timeout_ms: int = 45_000,
        proxy: str | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.proxy = proxy
        self._browser = None
        self._playwright = None

    def _ensure_browser(self):
        if self._browser is not None:
            return
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - env dependent
            raise BrowserUnavailable(
                "Playwright is not installed. Run `pip install playwright`."
            ) from exc
        try:
            self._playwright = sync_playwright().start()
            launch_args = ["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            launch_kwargs = {"headless": self.headless, "args": launch_args}
            if self.proxy:
                launch_kwargs["proxy"] = {"server": self.proxy}
            self._browser = self._playwright.chromium.launch(**launch_kwargs)
        except Exception as exc:
            self.close()
            raise BrowserUnavailable(
                "Chromium is not installed. Run `python -m playwright install chromium`."
            ) from exc

    def render(self, url: str, wait_selector: str | None = None) -> str:
        """Navigate to `url` and return the rendered page HTML."""
        self._ensure_browser()
        context = self._browser.new_context(
            user_agent=self.user_agent,
            locale="en-US",
            viewport={"width": 1280, "height": 900},
        )
        context.add_init_script(_STEALTH_SCRIPT)
        page = context.new_page()
        try:
            page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=self.timeout_ms)
                except Exception:
                    pass
            else:
                page.wait_for_timeout(2500)
            return page.content()
        finally:
            context.close()

    def close(self) -> None:
        try:
            if self._browser is not None:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright is not None:
                self._playwright.stop()
        except Exception:
            pass
        self._browser = None
        self._playwright = None
