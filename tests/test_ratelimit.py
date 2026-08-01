import threading
import time

from lostdock.core.ratelimit import RateLimiter


def test_rate_limiter_enforces_minimum_interval():
    limiter = RateLimiter(capacity=1, rate=10.0, jitter=0.0)
    t0 = time.monotonic()
    limiter.acquire()
    limiter.acquire()
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.09


def test_rate_limiter_parallel_safety():
    limiter = RateLimiter(capacity=4, rate=100.0, jitter=0.0)
    errors = []

    def worker():
        try:
            limiter.acquire()
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
