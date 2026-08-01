"""Application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .services.repository import Repository
from .services.plugins import discover_plugins


def load_plugins(app) -> None:
    """Discover plugins from ~/.lostdock/plugins and the bundled ./plugins dir."""
    bundled = Path(__file__).resolve().parent.parent.parent / "plugins"
    user_dir = Path.home() / ".lostdock" / "plugins"
    user_dir.mkdir(parents=True, exist_ok=True)
    plugins = discover_plugins([bundled, user_dir])
    for plugin in plugins:
        plugin.call("setup", app)
    return plugins


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("LostDock")

    plugins = load_plugins(app)
    app.plugins = plugins

    db_path = Path.home() / ".lostdock" / "lostdock.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    repo = Repository(db_path)

    from .ui.main_window import MainWindow

    window = MainWindow(repo, db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
