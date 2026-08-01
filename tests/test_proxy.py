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
