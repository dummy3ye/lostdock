from lostdock.core.models import Dork, SearchResult
from lostdock.services.repository import Repository
from lostdock.services.exporter import export_results

import json
import csv


def test_repository_roundtrip(tmp_path):
    repo = Repository(tmp_path / "test.db")
    job = repo.create_job("test query", "google")
    repo.add_results(
        job,
        [SearchResult(title="A", url="https://a.example", snippet="s", position=1)],
    )
    results = repo.results_for_job(job)
    assert len(results) == 1
    assert results[0].url == "https://a.example"
    repo.close()


def test_repository_dedup(tmp_path):
    repo = Repository(tmp_path / "test.db")
    job = repo.create_job("dup", "google")
    r = SearchResult(title="A", url="https://x.example", snippet="", position=1)
    repo.add_results(job, [r, r])
    removed = repo.dedup(job)
    assert removed == 1
    assert len(repo.results_for_job(job)) == 1
    repo.close()


def test_export_json(tmp_path):
    results = [SearchResult(title="A", url="https://a.example", snippet="s", position=1)]
    path = tmp_path / "out.json"
    export_results(results, path, "json")
    data = json.loads(path.read_text())
    assert data[0]["url"] == "https://a.example"


def test_export_csv(tmp_path):
    results = [SearchResult(title="A", url="https://a.example", snippet="s", position=1)]
    path = tmp_path / "out.csv"
    export_results(results, path, "csv")
    rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    assert rows[0] == ["position", "title", "url", "snippet", "engine", "query"]
    assert rows[1][2] == "https://a.example"


def test_export_unknown_format(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        export_results([], tmp_path / "x.xml", "xml")


def test_dork_dict_roundtrip():
    d = Dork(keywords="k", sites=["a.com"])
    assert Dork.from_dict(d.to_dict()) == d
