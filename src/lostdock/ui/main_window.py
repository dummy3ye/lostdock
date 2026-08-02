"""Main application window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QWidget,
)

from ..adapters import ENGINES, MultiEngine
from ..core.models import SearchResult
from ..core.proxy import ProxyPool
from ..services.exporter import export_results
from ..services.repository import Repository
from ..services.scheduler import Scheduler
from .dork_builder import DorkBuilder
from .results_view import ResultsView
from .settings import SettingsDialog
from .theme import stylesheet, themes
from .worker import CrawlWorker, SearchWorker, run_crawl, run_search

PROXIES_SETTING = "proxies"
HTTP_ENGINES = ("google", "duckduckgo", "bing")


class MainWindow(QMainWindow):
    def __init__(self, repo: Repository, db_path: Path) -> None:
        super().__init__()
        self.repo = repo
        self.db_path = db_path
        self.worker: SearchWorker | None = None
        self.crawl_worker: CrawlWorker | None = None
        self.proxy_pool: ProxyPool | None = None
        self.scheduler = Scheduler(
            repo, on_run=self._on_scheduled_run, on_error=self._on_scheduled_error
        )
        self._build_ui()
        self._apply_theme("dark")
        self._load_persisted_proxies()
        self.scheduler.start()
        self.setWindowTitle("LostDock — Google Dorking")
        self.resize(1180, 760)

    def closeEvent(self, event) -> None:
        self.scheduler.stop()
        super().closeEvent(event)

    def _build_ui(self) -> None:
        self.builder = DorkBuilder()
        self.builder.changed.connect(self._on_preview_changed)
        self.builder.highlight_field.textChanged.connect(self._on_highlight_changed)

        self.results = ResultsView()

        builder_scroll = QScrollArea()
        builder_scroll.setWidget(self.builder)
        builder_scroll.setWidgetResizable(True)
        builder_scroll.setFrameShape(QFrame.NoFrame)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(builder_scroll)
        splitter.addWidget(self.results)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([380, 800])
        self.setCentralWidget(splitter)

        self._build_toolbar()
        self._build_menu()
        self._build_status()
        self._refresh_saved_dorks()

    def _build_toolbar(self) -> None:
        self.toolbar = QToolBar("Search")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addWidget(QLabel("Engine"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("all (auto-fallback)", "all")
        for name in ENGINES:
            label = "chrome (pipe)" if name == "google-chrome" else name
            self.engine_combo.addItem(label, name)
        self.engine_combo.setCurrentIndex(0)
        self.toolbar.addWidget(self.engine_combo)

        self.toolbar.addWidget(QLabel("Pages"))
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 20)
        self.pages_spin.setValue(1)
        self.toolbar.addWidget(self.pages_spin)

        self.run_btn = QPushButton("Run Search")
        self.run_btn.setDefault(True)
        self.run_btn.clicked.connect(self._on_run)
        self.toolbar.addWidget(self.run_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.toolbar.addWidget(self.cancel_btn)

        self.toolbar.addSeparator()

        self.toolbar.addWidget(QLabel("Saved"))
        self.saved_combo = QComboBox()
        self.saved_combo.setMinimumWidth(140)
        self.toolbar.addWidget(self.saved_combo)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save_dork)
        self.toolbar.addWidget(self.save_btn)
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self._on_load_dork)
        self.toolbar.addWidget(self.load_btn)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete_dork)
        self.toolbar.addWidget(self.delete_btn)

        self.recrawl_btn = QPushButton("Re-check URLs")
        self.recrawl_btn.clicked.connect(self._on_recrawl)
        self.toolbar.addWidget(self.recrawl_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        self.export_btn = QPushButton("Export...")
        self.export_btn.clicked.connect(self._on_export)
        self.toolbar.addWidget(self.export_btn)

    def _build_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction("Export Results...", self._on_export)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close)
        view_menu = menu.addMenu("&View")
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        self.theme_menu = view_menu.addMenu("Theme")
        self.theme_actions: dict[str, QAction] = {}
        for name in themes():
            label = name
            if name == "win98":
                label = "Win98"
            elif name.startswith("win98"):
                label = "Win98 " + name.split("-", 1)[1].title()
            else:
                label = name.capitalize()
            action = self.theme_menu.addAction(label)
            action.setCheckable(True)
            self.theme_group.addAction(action)
            self.theme_actions[name] = action
            action.triggered.connect(lambda checked, t=name: self._apply_theme(t))
        tools_menu = menu.addMenu("&Tools")
        tools_menu.addAction("Settings...", self._on_settings)
        tools_menu.addAction("Re-check URLs", self._on_recrawl)

    def _apply_theme(self, name: str) -> None:
        QApplication.instance().setStyleSheet(stylesheet(name))
        self.theme_actions[name].setChecked(True)

    def _build_status(self) -> None:
        status = QStatusBar()
        self.setStatusBar(status)
        self.count_label = QLabel("0 results")
        status.addPermanentWidget(self.count_label)
        self.results.count_changed.connect(lambda n: self.count_label.setText(f"{n} results"))
        status.showMessage("Ready")

    def _filter(self):
        from ..services.filter import ResultFilter

        whitelist = self.builder.whitelist_field.text()
        blacklist = self.builder.blacklist_field.text()
        patterns = self.builder.patterns_field.text()
        return ResultFilter(
            whitelist=[d.strip() for d in whitelist.split(",") if d.strip()],
            blacklist=[d.strip() for d in blacklist.split(",") if d.strip()],
            url_patterns=[p.strip() for p in patterns.split(",") if p.strip()],
        )

    def _refresh_saved_dorks(self) -> None:
        self.saved_combo.clear()
        for row in self.repo.list_dorks():
            self.saved_combo.addItem(row["name"])

    def _on_save_dork(self) -> None:
        name = self.builder.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Save dork", "Enter a name in the 'Dork name' field.")
            return
        self.repo.save_dork(name, self.builder.dork())
        self._refresh_saved_dorks()
        self.saved_combo.setCurrentText(name)
        self.statusBar().showMessage(f"Saved dork '{name}'")

    def _on_load_dork(self) -> None:
        name = self.saved_combo.currentText()
        if not name:
            return
        dork = self.repo.load_dork(name)
        if dork:
            self.builder.load_dork(dork)
            self.statusBar().showMessage(f"Loaded dork '{name}'")

    def _on_delete_dork(self) -> None:
        name = self.saved_combo.currentText()
        if not name:
            return
        self.repo.delete_dork(name)
        self._refresh_saved_dorks()
        self.statusBar().showMessage(f"Deleted dork '{name}'")

    def _load_persisted_proxies(self) -> None:
        raw = self.repo.get_setting(PROXIES_SETTING)
        proxies = [p.strip() for p in raw.splitlines() if p.strip()]
        if proxies:
            self.proxy_pool = ProxyPool.from_strings(proxies)

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self.repo, self)
        dialog.set_proxies(self._proxy_strings())
        if dialog.exec():
            proxies = dialog.proxy_list()
            self.repo.set_setting(PROXIES_SETTING, "\n".join(proxies))
            self.proxy_pool = ProxyPool.from_strings(proxies) if proxies else None
            choice = dialog.schedule_choice()
            if choice:
                name, interval = choice
                self.statusBar().showMessage(f"Scheduled '{name}' every {interval} min")

    def _proxy_strings(self) -> list[str]:
        return self.proxy_pool.strings() if self.proxy_pool else []

    def _on_recrawl(self) -> None:
        """Fetch each shown URL off the UI thread and annotate status."""
        results = self.results.results()
        if not results:
            return
        urls = [r.url for r in results]
        self.recrawl_btn.setEnabled(False)
        self.statusBar().showMessage("Re-checking URLs...")
        self.crawl_worker = run_crawl(urls, repo=self.repo, persist=True)
        self.crawl_worker.report_ready.connect(self._on_crawl_report)
        self.crawl_worker.finished.connect(self._on_crawl_finished)
        self.crawl_worker.failed.connect(self._on_crawl_failed)

    def _on_crawl_report(self, report) -> None:
        match_url = report.original_url or report.url
        self.results.annotate_url(match_url, report)

    def _on_crawl_finished(self, total: int) -> None:
        self.recrawl_btn.setEnabled(True)
        self.statusBar().showMessage(f"URL re-check complete — {total} URLs")

    def _on_crawl_failed(self, message: str) -> None:
        self.recrawl_btn.setEnabled(True)
        self.statusBar().showMessage("URL re-check failed")
        QMessageBox.critical(self, "Re-check failed", message)

    def _on_scheduled_run(self, name: str, count: int) -> None:
        self.statusBar().showMessage(f"Scheduled run '{name}' finished: {count} results")

    def _on_scheduled_error(self, name: str, message: str) -> None:
        self.statusBar().showMessage(f"Scheduled run '{name}' failed: {message}")

    def _on_preview_changed(self, query: str) -> None:
        self.builder.preview.setText(query or "(empty query)")

    def _on_highlight_changed(self, pattern: str) -> None:
        self.results.set_highlight(pattern or None)

    def _build_engine(self, name: str):
        """Build the selected engine, aggregating all HTTP engines for 'all'."""
        if name == "all":
            engines = [ENGINES[n](proxies=self.proxy_pool) for n in HTTP_ENGINES]
            return MultiEngine(engines)
        return ENGINES[name](proxies=self.proxy_pool)

    def _on_run(self) -> None:
        dork = self.builder.dork()
        if not self.builder.compiled_query():
            QMessageBox.warning(self, "Empty query", "Build a query first.")
            return
        engine = self._build_engine(self.engine_combo.currentData())
        self.results.setRowCount(0)
        self.results.count_changed.emit(0)
        plugins = getattr(QApplication.instance(), "plugins", [])
        self.worker = run_search(
            engine,
            self.repo,
            dork,
            pages=self.pages_spin.value(),
            plugins=plugins,
        )
        self.worker.result_ready.connect(self._on_result)
        self.worker.finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.status.connect(lambda msg: self.statusBar().showMessage(msg))
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.statusBar().showMessage("Searching...")

    def _on_cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.statusBar().showMessage("Cancelling...")

    def _on_result(self, result: SearchResult) -> None:
        self.results.add_result(result)

    def _on_finished(self, total: int) -> None:
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage(f"Done — {total} results (dedup applied)")

    def _on_failed(self, message: str) -> None:
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage("Search failed")
        QMessageBox.critical(self, "Search failed", message)

    def _on_export(self) -> None:
        results = self._filter().apply(self.results.results())
        if not results:
            QMessageBox.information(self, "Export", "No results to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export results",
            "lostdock_results.json",
            "JSON (*.json);;CSV (*.csv);;Markdown (*.md);;HTML report (*.html)",
        )
        if not path:
            return
        fmt = Path(path).suffix.lstrip(".")
        plugins = getattr(QApplication.instance(), "plugins", [])
        for plugin in plugins:
            results = plugin.call("on_export", results, fmt, path) or results
        try:
            export_results(results, path, fmt)
            self.statusBar().showMessage(f"Exported {len(results)} results to {path}")
        except ValueError as exc:
            QMessageBox.warning(self, "Export", str(exc))
