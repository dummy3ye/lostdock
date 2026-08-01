"""Google search routed through the user's real Chrome/Chromium browser.

Instead of scraping HTTP (which Google 429s / reCAPTCHAs from many IPs),
this engine simply opens the Google search URL in the user's own browser.

Chrome's native single-instance behavior does the right thing:
  * if a Chrome instance is already running -> opens the search in a new tab
  * otherwise                          -> opens a new Chrome window

No results are captured back into LostDock; the user reviews the search in
the browser. This is intentionally the simplest possible integration.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from typing import List, Optional
from urllib.parse import urlencode

from ..core.models import SearchResult
from ..core.ratelimit import RateLimiter, default_limiter
from .base import EngineError, SearchEngine

log = logging.getLogger(__name__)


def _find_chrome() -> Optional[str]:
    """Locate a Chrome/Chromium binary (or 'open' on macOS)."""
    if sys.platform == "darwin":
        return "open"
    env = os.environ.get("LOSTDOCK_CHROME")
    candidates = [
        env,
        "google-chrome-stable",
        "google-chrome",
        "chromium",
        "chromium-browser",
        "chrome",
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if os.path.exists(candidate):
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


class ChromeEngine(SearchEngine):
    """Opens the Google search in the user's Chrome/Chromium browser."""

    name = "google-chrome"

    def __init__(
        self,
        limiter: Optional[RateLimiter] = None,
        proxies=None,
        browser: Optional[str] = None,
    ) -> None:
        self.limiter = limiter or default_limiter()
        self.proxies = proxies
        self.browser = browser if browser is not None else _find_chrome()

    def _launch(self, url: str) -> None:
        if self.browser is None:
            raise EngineError(
                "No Chrome/Chromium found. Install Google Chrome or Chromium, or "
                "set the LOSTDOCK_CHROME env var to the binary path."
            )
        try:
            if sys.platform == "darwin":
                cmd = [self.browser, "-a", "Google Chrome", url]
            else:
                cmd = [self.browser, url]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            raise EngineError(f"Failed to launch Chrome: {exc}") from exc

    def search(
        self,
        query: str,
        pages: int = 1,
        per_page: int = 10,
        stop_at: Optional[int] = None,
    ) -> List[SearchResult]:
        self.limiter.acquire()
        params = {"q": query, "num": per_page, "hl": "en"}
        url = "https://www.google.com/search?" + urlencode(params)
        log.info("Opening in browser: %s", url)
        self._launch(url)
        return []  # no capture; user reviews in the browser
