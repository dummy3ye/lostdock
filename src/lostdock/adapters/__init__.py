"""Engine adapters."""

from .base import SearchEngine, EngineError, BlockedError, RateLimitedError
from .google import GoogleEngine
from .duckduckgo import DuckDuckGoEngine
from .bing import BingEngine
from .chrome import ChromeEngine

ENGINES = {
    "google": GoogleEngine,
    "duckduckgo": DuckDuckGoEngine,
    "bing": BingEngine,
    "google-chrome": ChromeEngine,
}

__all__ = [
    "SearchEngine",
    "EngineError",
    "BlockedError",
    "RateLimitedError",
    "GoogleEngine",
    "DuckDuckGoEngine",
    "BingEngine",
    "ChromeEngine",
    "ENGINES",
]
