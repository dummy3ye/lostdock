"""Compile a structured Dork into a search engine query string."""

from __future__ import annotations

from typing import List

from .models import Dork


def _quote_phrase(terms: List[str]) -> List[str]:
    return [f'"{t}"' if " " in t else t for t in terms if t]


def compile_dork(dork: Dork) -> str:
    """Render a Dork object into a Google-compatible query string."""
    parts: List[str] = []

    if dork.exact_phrase:
        parts.append(f'"{dork.exact_phrase}"')

    if dork.keywords:
        parts.append(dork.keywords)

    # Exclusions: -term
    parts.extend(f"-{t}" for t in _quote_phrase(dork.exclude_terms))

    # Required terms joined with AND (implicit in Google, but explicit reads clearer)
    required = _quote_phrase(dork.required_terms)
    if required:
        parts.extend(required)

    # OR terms: (term1 OR term2 OR ...)
    any_terms = _quote_phrase(dork.any_terms)
    if any_terms:
        parts.append("(" + " OR ".join(any_terms) + ")")

    # site: operator (multiple sites OR'd inside parens)
    if dork.sites:
        sites = [f"site:{s}" for s in dork.sites if s]
        if len(sites) == 1:
            parts.append(sites[0])
        else:
            parts.append("(" + " OR ".join(sites) + ")")

    # filetype: operator
    if dork.file_types:
        fts = [f"filetype:{ft}" for ft in dork.file_types if ft]
        if len(fts) == 1:
            parts.append(fts[0])
        else:
            parts.append("(" + " OR ".join(fts) + ")")

    for value, op in (
        (dork.in_url, "inurl:"),
        (dork.in_title, "intitle:"),
        (dork.in_text, "intext:"),
        (dork.in_anchor, "inanchor:"),
        (dork.after, "after:"),
        (dork.before, "before:"),
        (dork.language, "lang:"),
    ):
        if value:
            parts.append(f"{op}{value}")

    return " ".join(p for p in parts if p)
