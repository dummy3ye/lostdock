"""Settings dialog: proxies, scheduling, and plugins."""

from __future__ import annotations

import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from ..services.repository import Repository


class _ProxyTester(QThread):
    """Tests proxies against a real Google search off the UI thread."""

    finished_with = Signal(list)  # list[tuple[str, bool, str]]

    def __init__(self, proxy_strings: list[str], parent=None) -> None:
        super().__init__(parent)
        self.proxy_strings = proxy_strings

    def run(self) -> None:
        from lostdock.adapters.google import _looks_blocked

        results = []
        for url in self.proxy_strings:
            entry = {"http": url, "https": url}
            try:
                resp = requests.get(
                    "https://www.google.com/search",
                    params={"q": "test", "hl": "en", "num": "10"},
                    proxies=entry,
                    timeout=10,
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                    },
                )
                if resp.status_code != 200:
                    results.append((url, False, f"HTTP {resp.status_code}"))
                elif _looks_blocked(resp.text):
                    results.append((url, False, "blocked by Google"))
                else:
                    results.append((url, True, "OK"))
            except requests.RequestException:
                results.append((url, False, "unreachable"))
        self.finished_with.emit(results)


class SettingsDialog(QDialog):
    def __init__(self, repo: Repository, parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        proxy_group = QGroupBox("Proxies (one per line: http://host:port)")
        proxy_layout = QVBoxLayout(proxy_group)
        self.proxy_edit = QPlainTextEdit()
        self.proxy_edit.setPlaceholderText("http://127.0.0.1:8080\nsocks5://127.0.0.1:1080")
        self.proxy_edit.setMinimumHeight(70)
        proxy_layout.addWidget(self.proxy_edit)
        test_row = QHBoxLayout()
        self.test_btn = QPushButton("Test Proxies")
        self.test_btn.clicked.connect(self._test_proxies)
        self.test_status = QLabel()
        test_row.addWidget(self.test_btn)
        test_row.addWidget(self.test_status, 1)
        proxy_layout.addLayout(test_row)
        layout.addWidget(proxy_group)

        schedule_group = QGroupBox("Schedule dork")
        schedule_layout = QHBoxLayout(schedule_group)
        self.schedule_dork_combo = QListWidget()
        self.schedule_dork_combo.setMaximumHeight(100)
        schedule_layout.addWidget(self.schedule_dork_combo)
        form = QFormLayout()
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10080)
        self.interval_spin.setValue(60)
        form.addRow("Every (minutes)", self.interval_spin)
        schedule_layout.addLayout(form)
        layout.addWidget(schedule_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load(self) -> None:
        for row in self.repo.list_dorks():
            self.schedule_dork_combo.addItem(row["name"])

    def set_proxies(self, proxy_strings: list[str]) -> None:
        self.proxy_edit.setPlainText("\n".join(proxy_strings))

    def _test_proxies(self) -> None:
        proxies = self.proxy_list()
        if not proxies:
            QMessageBox.information(self, "Test Proxies", "Enter at least one proxy first.")
            return
        self.test_btn.setEnabled(False)
        self.test_status.setText("Testing...")
        self._tester = _ProxyTester(proxies, self)
        self._tester.finished_with.connect(self._on_proxy_test_done)
        self._tester.start()

    def _on_proxy_test_done(self, results: list[tuple[str, bool, str]]) -> None:
        self.test_btn.setEnabled(True)
        ok_count = sum(1 for _, ok, _ in results if ok)
        self.test_status.setText(f"{ok_count}/{len(results)} proxies OK")
        lines = [f"{'OK ' if ok else 'FAIL'} {url}" for url, ok, _ in results]
        QMessageBox.information(
            self,
            "Proxy test results",
            "\n".join(lines) if lines else "No proxies tested.",
        )

    def proxy_list(self) -> list[str]:
        return [p.strip() for p in self.proxy_edit.toPlainText().splitlines() if p.strip()]

    def schedule_choice(self) -> tuple[str, int] | None:
        selected = self.schedule_dork_combo.currentItem()
        if selected is None:
            return None
        return selected.text(), self.interval_spin.value()

    def _on_save(self) -> None:
        choice = self.schedule_choice()
        if choice:
            name, interval = choice
            self.repo.save_schedule(name, interval, "duckduckgo")
        self.accept()
