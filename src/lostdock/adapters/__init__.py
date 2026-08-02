"""Engine adapters."""

from .base import BlockedError, EngineError, RateLimitedError, SearchEngine
from .bing import BingEngine
from .chrome import ChromeEngine
from .duckduckgo import DuckDuckGoEngine
from .google import GoogleEngine

ENGINES = {
    "google": GoogleEngine,
    "duckduckgo": DuckDuckGoEngine,
    "bing": BingEngine,
    "google-chrome": ChromeEngine,
}

__all__ = [
    "ENGINES",
    "BingEngine",
    "BlockedError",
    "ChromeEngine",
    "DuckDuckGoEngine",
    "EngineError",
    "GoogleEngine",
    "RateLimitedError",
    "SearchEngine",
]
