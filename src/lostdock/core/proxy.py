"""Rotating proxy pool with optional validation."""

from __future__ import annotations

import logging
import random
import threading
import time
from typing import Dict, List, Optional

import requests

log = logging.getLogger(__name__)


class ProxyPool:
    """Manages a pool of proxies and rotates through them.

    A proxy entry is a dict: {"http": ..., "https": ...} or a plain
    "http://host:port" string (used for both schemes). Failed proxies
    are disabled for a cooldown period.
    """

    def __init__(
        self,
        proxies: Optional[List[Dict[str, str]]] = None,
        cooldown: float = 60.0,
    ) -> None:
        self.cooldown = cooldown
        self._lock = threading.Lock()
        self._proxies: List[Dict[str, str]] = []
        self._disabled_until: Dict[int, float] = {}
        for proxy in proxies or []:
            self.add(proxy)

    @classmethod
    def from_strings(cls, proxy_strings: List[str]) -> "ProxyPool":
        pool = cls()
        for p in proxy_strings:
            pool.add(p)
        return pool

    def add(self, proxy: Dict[str, str] | str) -> None:
        if isinstance(proxy, str):
            entry = {"http": proxy, "https": proxy}
        else:
            entry = dict(proxy)
        with self._lock:
            self._proxies.append(entry)

    def __len__(self) -> int:
        with self._lock:
            return len(self._proxies)

    def next(self) -> Optional[Dict[str, str]]:
        """Return the next available proxy (or None if none enabled)."""
        now = time.monotonic()
        with self._lock:
            candidates = [
                (i, p)
                for i, p in enumerate(self._proxies)
                if self._disabled_until.get(i, 0) <= now
            ]
            if not candidates:
                return None
            # Rotate: pop the front, push to back for round-robin feel.
            idx, proxy = candidates[0]
            if len(candidates) > 1:
                self._proxies.append(self._proxies.pop(idx))
            return proxy

    def mark_failed(self, proxy: Dict[str, str] | None) -> None:
        if proxy is None:
            return
        with self._lock:
            for i, p in enumerate(self._proxies):
                if p == proxy:
                    self._disabled_until[i] = time.monotonic() + self.cooldown
                    log.debug("Proxy %s disabled for %.0fs", p.get("https"), self.cooldown)
                    break

    def validate(
        self,
        timeout: float = 8.0,
        test_url: str = "https://example.com",
    ) -> None:
        """Remove proxies that fail a quick request."""
        with self._lock:
            proxies = list(self._proxies)
        healthy: List[Dict[str, str]] = []
        for p in proxies:
            try:
                requests.get(
                    test_url,
                    proxies=p,
                    timeout=timeout,
                    headers={"User-Agent": "lostdock-proxy-check"},
                )
                healthy.append(p)
            except requests.RequestException as exc:
                log.debug("Proxy check failed for %s: %s", p.get("https"), exc)
        with self._lock:
            self._proxies = healthy
