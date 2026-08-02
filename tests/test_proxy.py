from lostdock.core.proxy import ProxyPool


def test_proxy_pool_rotates():
    pool = ProxyPool.from_strings(["http://a:1", "http://b:2"])
    first = pool.next()
    second = pool.next()
    assert first != second
    assert first in pool._proxies


def test_proxy_pool_empty():
    pool = ProxyPool()
    assert pool.next() is None


def test_proxy_pool_mark_failed_cooldown():
    pool = ProxyPool.from_strings(["http://a:1"])
    proxy = pool.next()
    assert proxy is not None
    pool.mark_failed(proxy)
    assert pool.next() is None  # in cooldown


def test_proxy_pool_strings_roundtrip():
    pool = ProxyPool.from_strings(["http://a:1", "http://b:2"])
    assert pool.strings() == ["http://a:1", "http://b:2"]


def test_proxy_pool_check_all_mutates_nothing(monkeypatch):
    import requests

    pool = ProxyPool.from_strings(["http://a:1", "http://b:2"])

    def fake_get(url, proxies, timeout, headers):
        if proxies.get("https") == "http://a:1":
            raise requests.RequestException("boom")
        return object()

    monkeypatch.setattr(requests, "get", fake_get)
    results = pool.check_all()
    assert results == [
        ({"http": "http://a:1", "https": "http://a:1"}, False),
        ({"http": "http://b:2", "https": "http://b:2"}, True),
    ]
    assert len(pool) == 2  # unchanged
