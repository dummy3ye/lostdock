"""Token-bucket rate limiter with randomized jitter."""

from __future__ import annotations

import random
import threading
import time
from typing import Optional


class RateLimiter:
    """Simple token-bucket limiter.

    capacity: max burst size
    rate: tokens added per second (queries per second)
    jitter: random fraction of interval to add, to avoid patterns
    """

    def __init__(
        self,
        capacity: float = 5.0,
        rate: float = 1.0,
        jitter: float = 0.3,
    ) -> None:
        self.capacity = capacity
        self.rate = rate
        self.jitter = jitter
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
        self._last = now

    def acquire(self) -> None:
        """Block until a token is available."""
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    break
                wait = (1.0 - self._tokens) / self.rate
            time.sleep(wait)
            # Optional jitter delay after acquiring.
            if self.jitter > 0:
                time.sleep(random.uniform(0, self.jitter))


def default_limiter() -> RateLimiter:
    # ~20 queries/min bursty with jitter: polite default.
    return RateLimiter(capacity=5, rate=1.0 / 3.0, jitter=0.4)
