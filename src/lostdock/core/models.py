"""The Dork model: a structured representation of a search query."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Dork:
    """Structured dork query. Each piece is rendered by the compiler."""

    keywords: str = ""
    exact_phrase: str = ""
    exclude_terms: List[str] = field(default_factory=list)
    required_terms: List[str] = field(default_factory=list)  # AND terms
    any_terms: List[str] = field(default_factory=list)       # OR terms
    sites: List[str] = field(default_factory=list)
    file_types: List[str] = field(default_factory=list)
    in_url: str = ""
    in_title: str = ""
    in_text: str = ""
    in_anchor: str = ""
    after: str = ""
    before: str = ""
    language: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Dork":
        known = {f: data[f] for f in cls.__dataclass_fields__ if f in data}
        return cls(**known)


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    engine: str = "google"
    position: int = 0
    query: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
