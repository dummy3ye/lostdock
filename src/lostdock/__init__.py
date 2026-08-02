"""LostDock — cross-platform Google dorking tool."""

__version__ = "0.2.1"

from .core.compiler import compile_dork
from .core.models import Dork, SearchResult
from .services.exporter import export_results
from .services.repository import Repository

__all__ = [
    "Dork",
    "Repository",
    "SearchResult",
    "__version__",
    "compile_dork",
    "export_results",
]
