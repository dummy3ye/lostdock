"""Results table widget."""

from __future__ import annotations

import re
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
)

from ..core.models import SearchResult


class ResultsView(QTableWidget):
    """Table showing search results with live count."""

    count_changed = Signal(int)

    COLUMNS = ["#", "Title", "URL", "Snippet", "Engine", "Status"]

    def __init__(self, parent=None) -> None:
        super().__init__(0, len(self.COLUMNS), parent)
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        self.setColumnWidth(2, 320)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self._highlight: Optional[re.Pattern] = None

    def set_highlight(self, pattern: Optional[str]) -> None:
        """Highlight rows whose URL/title/snippet match a regex pattern."""
        if pattern:
            try:
                self._highlight = re.compile(pattern, re.IGNORECASE)
            except re.error:
                self._highlight = None
                return
        else:
            self._highlight = None
        self._apply_highlight()

    def _apply_highlight(self) -> None:
        for row in range(self.rowCount()):
            if self._highlight:
                text = " ".join(
                    self.item(row, c).text()
                    for c in (1, 2, 3)
                    if self.item(row, c)
                )
                matched = bool(self._highlight.search(text))
            else:
                matched = False
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setBackground(
                        Qt.green if matched else Qt.white
                    )

    def add_result(self, result: SearchResult) -> None:
        row = self.rowCount()
        self.insertRow(row)
        values = [
            str(result.position),
            result.title,
            result.url,
            result.snippet,
            result.engine,
            "",
        ]
        for col, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            if col == 2:
                item.setData(Qt.UserRole, result.url)
            self.setItem(row, col, item)
        self._apply_highlight()
        self.count_changed.emit(row + 1)

    def results(self) -> List[SearchResult]:
        out: List[SearchResult] = []
        for row in range(self.rowCount()):
            url_item = self.item(row, 2)
            out.append(
                SearchResult(
                    title=self.item(row, 1).text() if self.item(row, 1) else "",
                    url=url_item.data(Qt.UserRole) or url_item.text() if url_item else "",
                    snippet=self.item(row, 3).text() if self.item(row, 3) else "",
                    engine=self.item(row, 4).text() if self.item(row, 4) else "",
                    position=int(self.item(row, 0).text()) if self.item(row, 0) else 0,
                )
            )
        return out

    def selected_url(self) -> Optional[str]:
        items = self.selectedItems()
        for it in items:
            if it.column() == 2:
                return it.data(Qt.UserRole) or it.text()
        return None

    def annotate_url(self, url: str, report) -> None:
        """Update the Status column for the row matching the stored URL.

        Matching uses the original requested URL (report.original_url), so a
        result that redirected is still annotated even though report.url is the
        final, different URL.
        """
        for row in range(self.rowCount()):
            url_item = self.item(row, 2)
            if url_item and (url_item.data(Qt.UserRole) or url_item.text()) == url:
                status = (
                    f"{report.status_code} {report.content_type}"
                    if report.status_code
                    else f"ERR {report.error[:20]}"
                )
                self.item(row, 5).setText(status)
                if report.http_title:
                    title = self.item(row, 1)
                    if title:
                        title.setText(report.http_title)
                break

    def copy_selected_url(self) -> None:
        url = self.selected_url()
        if url:
            QGuiApplication.clipboard().setText(url)
