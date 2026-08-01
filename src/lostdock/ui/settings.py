"""Settings dialog: proxies, scheduling, and plugins."""

from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
)

from ..services.repository import Repository


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

    def proxy_list(self) -> List[str]:
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
