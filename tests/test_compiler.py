from lostdock.core.models import Dork
from lostdock.core.compiler import compile_dork


def test_basic_keywords():
    assert compile_dork(Dork(keywords="login password")) == "login password"


def test_exact_phrase():
    d = Dork(exact_phrase="error in log")
    assert compile_dork(d) == '"error in log"'


def test_exclude_terms():
    d = Dork(keywords="password", exclude_terms=["site", "tutorial"])
    q = compile_dork(d)
    assert "password" in q
    assert "-site" in q
    assert '-"tutorial"' in q or "-tutorial" in q


def test_or_terms_grouped():
    d = Dork(any_terms=["php", "asp", "jsp"])
    assert compile_dork(d) == "(php OR asp OR jsp)"


def test_single_site():
    d = Dork(sites=["example.com"])
    assert compile_dork(d) == "site:example.com"


def test_multiple_sites_grouped():
    d = Dork(sites=["example.com", "foo.org"])
    assert compile_dork(d) == "(site:example.com OR site:foo.org)"


def test_file_type():
    d = Dork(file_types=["pdf"])
    assert compile_dork(d) == "filetype:pdf"


def test_multiple_file_types_grouped():
    d = Dork(file_types=["pdf", "xls"])
    assert compile_dork(d) == "(filetype:pdf OR filetype:xls)"


def test_full_dork():
    d = Dork(
        keywords="password",
        exact_phrase="admin panel",
        exclude_terms=["example"],
        required_terms=["login"],
        any_terms=["php", "asp"],
        sites=["example.com"],
        file_types=["pdf"],
        in_url="login",
        in_title="admin",
        after="2024-01-01",
    )
    q = compile_dork(d)
    assert '"admin panel"' in q
    assert "password" in q
    assert "-example" in q
    assert "login" in q
    assert "(php OR asp)" in q
    assert "site:example.com" in q
    assert "filetype:pdf" in q
    assert "inurl:login" in q
    assert "intitle:admin" in q
    assert "after:2024-01-01" in q
