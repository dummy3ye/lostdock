from lostdock.adapters.duckduckgo import DuckDuckGoEngine
from lostdock.adapters.bing import BingEngine

DDG_HTML = """
<html><body>
<div class="result">
  <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Ffile.pdf">Example File</a>
  <a class="result__snippet" href="#">Some snippet about the file.</a>
</div>
<div class="result">
  <a class="result__a" href="https://plain.example/page">Plain page</a>
  <a class="result__snippet" href="#">Another snippet.</a>
</div>
</body></html>
"""

BING_HTML = """
<html><body>
<ol id="b_results">
<li class="b_algo">
  <h2><a href="https://found.example/page.php">Found page</a></h2>
  <div class="b_caption"><p>Relevant snippet text.</p></div>
</li>
</ol>
</body></html>
"""


def test_ddg_parser_decodes_uddg():
    engine = DuckDuckGoEngine()
    results = engine._parse(DDG_HTML, "test")
    assert len(results) == 2
    assert results[0].url == "https://example.com/file.pdf"
    assert results[0].title == "Example File"
    assert results[1].url == "https://plain.example/page"


def test_bing_parser():
    engine = BingEngine()
    results = engine._parse(BING_HTML, "test")
    assert len(results) == 1
    assert results[0].url == "https://found.example/page.php"
    assert results[0].title == "Found page"
