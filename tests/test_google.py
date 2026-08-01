from lostdock.adapters.google import GoogleEngine


SAMPLE_HTML = """
<html><body>
<div class="g">
  <h3><a href="/url?q=https%3A%2F%2Fexposed.example%2Fconfig.php&amp;sa=U">Config File</a></h3>
  <div>Some snippet text about the config.</div>
</div>
<div class="g">
  <h3><a href="https://other.example/page.html">Other page</a></h3>
  <div>Another snippet.</div>
</div>
<a href="https://www.google.com/advanced_search?hl=en">nav</a>
</body></html>
"""


def test_parser_extracts_results():
    engine = GoogleEngine()
    results = engine._parse(SAMPLE_HTML, "config filetype:php")
    assert len(results) == 2
    assert results[0].url == "https://exposed.example/config.php"
    assert results[0].title == "Config File"
    assert "exposed.example" in results[0].url
    # Google's own nav links are excluded
    assert not any("www.google.com" in r.url for r in results)
