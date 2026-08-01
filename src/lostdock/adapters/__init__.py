"""Engine adapters."""

from .base import SearchEngine, EngineError, BlockedError, RateLimitedError
from .google import GoogleEngine
from .duckduckgo import DuckDuckGoEngine

ENGINES = {
    "google": GoogleEngine,
    "duckduckgo": DuckDuckGoEngine,
}

__all__ = [
    "SearchEngine",
    "EngineError",
    "BlockedError",
    "RateLimitedError",
    "GoogleEngine",
    "DuckDuckGoEngine",
    "ENGINES",
]
