# Plugins

LostDock's plugin system lets you hook into searches and exports without touching the
core code. Plugins are plain Python modules dropped into a directory; they are discovered
and loaded at startup.

## Where plugins live

Plugins are discovered (non-recursively) from two directories:

1. The **bundled** `plugins/` directory shipped with the app.
2. `~/.lostdock/plugins/` — your user directory, created automatically on first run.

Any `*.py` file in these directories is loaded, except files starting with `_`.
`plugins/example_skip_tracking.py` is a working example you can copy as a starting point.

## The plugin contract

A plugin module can export any subset of these hooks:

| Hook | Signature | Called |
|------|-----------|--------|
| `NAME` | `NAME: str` | Display name for the plugin (optional) |
| `setup` | `setup(app)` | Once at startup, with the app-level context |
| `on_result` | `on_result(result) -> result \| None` | For every search result; return `None` to drop it, else return the (possibly modified) result |
| `on_export` | `on_export(results, fmt, path)` | Right before results are written to disk; can mutate the `results` list |

There is no required boilerplate — a plugin can implement just one hook.

## Example

```python
"""Drop results that contain tracking parameters."""

NAME = "skip_tracking"

TRACKING_FRAGMENTS = ("utm_", "fbclid=", "mc_cid=", "gclid=")


def on_result(result):
    if any(frag in result.url for frag in TRACKING_FRAGMENTS):
        return None
    return result


def on_export(results, fmt, path):
    # Optionally mutate `results` before export.
    return None
```

Save it as `~/.lostdock/plugins/my_plugin.py` and it is active the next time LostDock
starts.

## Hook behavior in detail

### `setup(app)`

Called once at startup with the application context (`app` carries `app.plugins`, the
list of loaded plugins). Use it for one-time initialization, e.g. opening a log file or
registering state.

### `on_result(result)`

Called for each `SearchResult` in the shared query pipeline (`services/query.py`), before
the result is shown or persisted.

- Return the result unchanged to keep it.
- Return a modified result to transform it (e.g. rewrite the title or snippet).
- Return `None` to **drop** the result entirely — it is neither displayed nor stored.

Hooks run in discovery order; if one hook returns `None`, later hooks are not called for
that result.

### `on_export(results, fmt, path)`

Called right before results are written during export. The `results` list can be mutated
in place (filter, reorder, annotate). `fmt` is the export format (`json`, `csv`,
`markdown`, or `html`) and `path` is the target file.

## Failure handling

Exceptions from any hook are logged by the plugin loader and then **re-raised** — a
broken plugin is visible rather than silently swallowed:

- `setup` runs during startup (`main.py`), so an exception there aborts launch. Keep
  `setup` minimal, or guard it with its own try/except if it does risky work.
- `on_result` propagates through `run_query()` into the worker, which surfaces it as a
  search failure (and an exception without an `on_error` handler is re-raised).
- `on_export` propagates to the export call in the UI, so the export fails loudly.

## Writing tips

- Keep plugins dependency-free or import lazily — they run in the app's process.
- Log with the standard `logging` module; logs go to the app's logger.
- Test plugins against the real pipeline: build a `Dork`, run
  `lostdock.services.query.run_query(...)`, and assert on the results.
