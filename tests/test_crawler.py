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


def test_crawl_report_carries_original_url_on_redirect(monkeypatch):
    from lostdock.services import crawler

    class FakeResponse:
        url = "https://final.example/landed"
        status_code = 200
        headers = {"content-type": "text/html"}
        text = "<html><title>Landed</title></html>"
        content = b"<html><body>hi</body></html>"

    def fake_get(session, url, timeout, headers, allow_redirects):
        assert url == "https://start.example"
        return FakeResponse()

    monkeypatch.setattr("requests.Session.get", fake_get)
    report = crawl_url("https://start.example")
    assert report.url == "https://final.example/landed"
    assert report.original_url == "https://start.example"
    assert report.status_code == 200
