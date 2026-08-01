import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from lostdock.core.models import SearchResult
from lostdock.services.crawler import CrawlReport
from lostdock.ui.results_view import ResultsView


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication([])
    yield app


def _view(app):
    view = ResultsView()
    view.add_result(
        SearchResult(title="A", url="https://a.example", snippet="s", position=1)
    )
    return view


def test_annotate_url_writes_status_column(app):
    view = _view(app)
    report = CrawlReport(
        url="https://a.example",
        status_code=200,
        http_title="Live",
        content_type="text/html",
        size=10,
        ok=True,
    )
    view.annotate_url("https://a.example", report)
    assert view.item(0, 5).text() == "200 text/html"
    assert view.item(0, 1).text() == "Live"


def test_annotate_url_matches_across_redirect(app):
    view = _view(app)
    report = CrawlReport(
        url="https://redirected.example/landed",
        status_code=301,
        http_title="Moved",
        content_type="text/html",
        size=10,
        ok=False,
        original_url="https://a.example",
    )
    view.annotate_url(report.original_url, report)
    assert view.item(0, 5).text() == "301 text/html"
    assert view.item(0, 2).data(0x0100) == "https://a.example"


def test_annotate_url_error_status(app):
    view = _view(app)
    report = CrawlReport(
        url="https://a.example",
        status_code=None,
        http_title="",
        content_type="",
        size=0,
        ok=False,
        error="connection refused",
    )
    view.annotate_url("https://a.example", report)
    assert view.item(0, 5).text().startswith("ERR")
