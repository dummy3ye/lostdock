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

# Supported file types for the filetype: operator.
FILE_TYPES = [
    "pdf", "html", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "rtf", "csv", "json", "xml", "sql", "log", "conf", "ini",
    "php", "asp", "aspx", "jsp", "js", "css", "git", "bak", "db",
    "sqlite", "zip", "gz", "tar", "7z", "rar", "png", "jpg", "gif",
]

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
