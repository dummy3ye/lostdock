"""Search operator definitions used to build dorks."""

from __future__ import annotations

from dataclasses import dataclass

# Boolean / modifier operators (prefix or standalone).
BOOLEAN_OPERATORS = ["AND", "OR", "NOT"]

# Prefix operators that take a value, e.g. site:example.com
PREFIX_OPERATORS = {
    "site:": "Restrict results to a domain",
    "inurl:": "Search within URL",
    "intitle:": "Search within page title",
    "intext:": "Search within body text",
    "inanchor:": "Search within link anchor text",
    "allintitle:": "All words in title",
    "allinurl:": "All words in URL",
    "allintext:": "All words in body text",
    "filetype:": "Restrict to a file type",
    "ext:": "Restrict to a file extension",
    "cache:": "Show Google cached version",
    "link:": "Pages linking to a URL",
    "related:": "Similar pages",
    "info:": "Page overview",
    "define:": "Definition of a term",
    "author:": "Author of a result",
    "daterange:": "Date range (Julian)",
    "numrange:": "Numeric range",
    "loc:": "Location",
    "after:": "Results after a date (YYYY-MM-DD)",
    "before:": "Results before a date (YYYY-MM-DD)",
}

# Supported file types for the filetype: operator, grouped by category.
# The dork builder renders these as a 2x2 grid with a "Select All" per group.
FILE_TYPE_CATEGORIES = {
    "Documents": ["pdf", "doc", "docx", "txt", "ppt", "pptx"],
    "Media": ["png", "jpg", "mp4", "mp3", "svg", "gif"],
    "Spreadsheets & Data": ["xls", "xlsx", "csv", "json"],
    "Code & Web": ["html", "css", "js", "py"],
}

# Flattened list kept for the core package export and any external consumers.
FILE_TYPES = [ft for group in FILE_TYPE_CATEGORIES.values() for ft in group]

# Modifier operators that are combined with a keyword (prefix chars).
MODIFIERS = {
    "exact_phrase": '"',
    "exclude": "-",
    "synonym": "~",
    "wildcard": "*",
}


@dataclass(frozen=True)
class Operator:
    """A single operator application in a dork."""

    op: str
    value: str

    def render(self) -> str:
        return f"{self.op}{self.value}"
