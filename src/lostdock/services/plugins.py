"""Minimal plugin system: discover, load, and invoke plugins."""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)

# Plugin modules may export:
#   NAME: str          - display name
#   setup(app)         - called once at startup with the app-level context
#   on_result(result)  - called for each search result (can transform/filter)
#   on_export(results, fmt, path) - hook before exporting
# Any subset is optional.


class Plugin:
    def __init__(self, name: str, module) -> None:
        self.name = name
        self._module = module

    def call(self, hook: str, *args, **kwargs):
        fn = getattr(self._module, hook, None)
        if fn is not None:
            try:
                return fn(*args, **kwargs)
            except Exception:
                log.exception("Plugin %s hook %s failed", self.name, hook)
                raise
        return None

    def has(self, hook: str) -> bool:
        return callable(getattr(self._module, hook, None))


def discover_plugins(paths: list[Path]) -> list[Plugin]:
    """Load all *.py modules from the given directories (non-recursive)."""
    plugins: list[Plugin] = []
    for directory in paths:
        if not directory.is_dir():
            continue
        for file in sorted(directory.glob("*.py")):
            if file.name.startswith("_"):
                continue
            try:
                module_name = f"lostdock_plugin_{file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, file)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                name = getattr(module, "NAME", file.stem)
                plugins.append(Plugin(name, module))
                log.info("Loaded plugin: %s", name)
            except Exception:
                log.exception("Failed to load plugin %s", file)
    return plugins
