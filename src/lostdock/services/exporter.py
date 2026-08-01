"""Export search results to JSON, CSV, Markdown, and HTML."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Iterable, List

from ..core.models import SearchResult


def export_json(results: List[SearchResult], path: str | Path) -> None:
    Path(path).write_text(
        json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def export_csv(results: List[SearchResult], path: str | Path) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["position", "title", "url", "snippet", "engine", "query"])
        for r in results:
            writer.writerow([r.position, r.title, r.url, r.snippet, r.engine, r.query])


def export_markdown(results: List[SearchResult], path: str | Path) -> None:
    lines: List[str] = ["# Dork Results", ""]
    for r in results:
        lines.append(f"## {r.title}")
        lines.append(f"- **URL**: {r.url}")
        lines.append(f"- **Engine**: {r.engine} (pos {r.position})")
        if r.snippet:
            lines.append(f"- **Snippet**: {r.snippet[:300]}")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def export_html(results: List[SearchResult], path: str | Path) -> None:
    """Self-contained HTML report with clickable links."""
    rows = []
    for r in results:
        rows.append(
            "<tr>"
            f"<td>{r.position}</td>"
            f'<td>{html.escape(r.title)}</td>'
            f'<td><a href="{html.escape(r.url)}" target="_blank" rel="noopener">{html.escape(r.url)}</a></td>'
            f"<td>{html.escape(r.snippet[:300])}</td>"
            f"<td>{html.escape(r.engine)}</td>"
            "</tr>"
        )
    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>LostDock Report</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; margin: 2rem; color: #1f2328; }}
  h1 {{ font-size: 1.4rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; vertical-align: top; font-size: 0.9rem; }}
  th {{ background: #f6f8fa; }}
  tr:nth-child(even) td {{ background: #fbfbfc; }}
  a {{ color: #0969da; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>LostDock — {len(results)} result(s)</h1>
<table>
<thead><tr><th>#</th><th>Title</th><th>URL</th><th>Snippet</th><th>Engine</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>"""
    Path(path).write_text(document, encoding="utf-8")


EXPORTERS = {
    "json": export_json,
    "csv": export_csv,
    "md": export_markdown,
    "html": export_html,
}


def export_results(results: Iterable[SearchResult], path: str | Path, fmt: str) -> None:
    """Export results by format name ('json', 'csv', 'md', 'html')."""
    results = list(results)
    exporter = EXPORTERS.get(fmt.lower())
    if exporter is None:
        raise ValueError(f"Unsupported format: {fmt}. Use {list(EXPORTERS)}")
    exporter(results, path)
