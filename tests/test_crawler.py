from lostdock.services.crawler import crawl_url


def test_crawl_url_success():
    report = crawl_url("https://example.com", timeout=15)
    assert report.ok is True
    assert report.status_code == 200
    assert report.content_type == "text/html"


def test_crawl_url_failure_never_raises():
    report = crawl_url("http://127.0.0.1:1/nonexistent", timeout=1)
    assert report.ok is False
    assert report.status_code is None
    assert report.error
