"""LostDock — cross-platform Google dorking tool."""

__version__ = "0.1.1"

from .core.models import Dork, SearchResult
from .core.compiler import compile_dork
from .services.repository import Repository
from .services.exporter import export_results

__all__ = [
    "Dork",
    "SearchResult",
    "compile_dork",
    "Repository",
    "export_results",
    "__version__",
]
