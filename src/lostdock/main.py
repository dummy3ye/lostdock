"""Application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

if getattr(sys, "frozen", False) or __package__ in (None, ""):
    from lostdock.services.repository import Repository
    from lostdock.services.plugins import discover_plugins
    from lostdock.ui.main_window import MainWindow
else:
    from .services.repository import Repository
    from .services.plugins import discover_plugins


def load_plugins(app) -> None:
    """Discover plugins from ~/.lostdock/plugins and the bundled ./plugins dir."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        bundled = base / "lostdock" / "plugins"
    else:
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

    if getattr(sys, "frozen", False) or __package__ in (None, ""):
        from lostdock.ui.main_window import MainWindow
    else:
        from .ui.main_window import MainWindow

    window = MainWindow(repo, db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
