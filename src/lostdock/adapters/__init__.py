"""Engine adapters."""

from .base import SearchEngine, EngineError, BlockedError, RateLimitedError
from .google import GoogleEngine
from .duckduckgo import DuckDuckGoEngine
from .bing import BingEngine

ENGINES = {
    "google": GoogleEngine,
    "duckduckgo": DuckDuckGoEngine,
    "bing": BingEngine,
}

__all__ = [
    "SearchEngine",
    "EngineError",
    "BlockedError",
    "RateLimitedError",
    "GoogleEngine",
    "DuckDuckGoEngine",
    "BingEngine",
    "ENGINES",
]
