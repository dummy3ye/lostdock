"""Example plugin: logs results matching a regex and skips them.

Drop this file (or your own *.py) into ~/.lostdock/plugins/ and it is
loaded automatically at startup.
"""

from __future__ import annotations

import re

NAME = "skip_tracking"

# URLs containing these fragments are filtered out before display.
TRACKING_FRAGMENTS = ("utm_", "fbclid=", "mc_cid=", "gclid=")


def on_result(result) -> object | None:
    """Return None to drop the result, or the result to keep it."""
    if any(frag in result.url for frag in TRACKING_FRAGMENTS):
        return None
    return result


def on_export(results, fmt, path) -> None:
    """Called right before export; can mutate the results list."""
    return None
