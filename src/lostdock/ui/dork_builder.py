"""Visual dork builder panel."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.compiler import compile_dork
from ..core.models import Dork
from ..core.operators import FILE_TYPES


class DorkBuilder(QWidget):
    """Form that builds a Dork object and previews the compiled query."""

    changed = Signal(str)  # emits compiled query on any change

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.keywords = QLineEdit()
        self.keywords.setPlaceholderText("primary search terms (e.g. login password)")
        form.addRow("Keywords", self.keywords)

        self.name = QLineEdit()
        self.name.setPlaceholderText("name this dork to save it")
        form.addRow("Dork name", self.name)

        self.exact_phrase = QLineEdit()
        self.exact_phrase.setPlaceholderText('exact phrase -> "this exact phrase"')
        form.addRow("Exact phrase", self.exact_phrase)

        self.exclude = QLineEdit()
        self.exclude.setPlaceholderText("comma separated: word1, word2")
        form.addRow("Exclude (-)", self.exclude)

        self.required = QLineEdit()
        self.required.setPlaceholderText("comma separated: word1, word2")
        form.addRow("Must have (AND)", self.required)

        self.any_terms = QLineEdit()
        self.any_terms.setPlaceholderText("comma separated: word1, word2")
        form.addRow("Any of (OR)", self.any_terms)

        self.sites = QLineEdit()
        self.sites.setPlaceholderText("comma separated: example.com, *.org")
        form.addRow("Sites (site:)", self.sites)

        self.inurl = QLineEdit()
        self.intitle = QLineEdit()
        self.intext = QLineEdit()
        form.addRow("inurl:", self.inurl)
        form.addRow("intitle:", self.intitle)
        form.addRow("intext:", self.intext)

        date_row = QHBoxLayout()
        self.after = QLineEdit()
        self.after.setPlaceholderText("YYYY-MM-DD")
        self.before = QLineEdit()
        self.before.setPlaceholderText("YYYY-MM-DD")
        date_row.addWidget(QLabel("after:"))
        date_row.addWidget(self.after)
        date_row.addWidget(QLabel("before:"))
        date_row.addWidget(self.before)
        form.addRow("Dates", date_row)

        layout.addLayout(form)

        ft_group = QGroupBox("File types")
        ft_layout = QVBoxLayout(ft_group)
        self.file_types = QListWidget()
        self.file_types.setMaximumHeight(120)
        for ft in FILE_TYPES:
            item = QListWidgetItem(ft)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.file_types.addItem(item)
        ft_layout.addWidget(self.file_types)
        layout.addWidget(ft_group)

        self.preview = QLabel("")
        self.preview.setWordWrap(True)
        self.preview.setStyleSheet(
            "background:#1e1e2e; color:#cdd6f4; padding:8px; border-radius:4px; font-family:monospace;"
        )
        layout.addWidget(QLabel("Query preview"))
        layout.addWidget(self.preview)

        filter_group = QGroupBox("Result filter (applied on export)")
        filter_form = QFormLayout(filter_group)
        self.whitelist_field = QLineEdit()
        self.whitelist_field.setPlaceholderText("only these domains: example.com, foo.org")
        self.blacklist_field = QLineEdit()
        self.blacklist_field.setPlaceholderText("exclude these domains")
        self.patterns_field = QLineEdit()
        self.patterns_field.setPlaceholderText("regex keep: /uploads/, /docs/")
        self.highlight_field = QLineEdit()
        self.highlight_field.setPlaceholderText("regex highlight rows: password|config|backup")
        filter_form.addRow("Allow only", self.whitelist_field)
        filter_form.addRow("Block", self.blacklist_field)
        filter_form.addRow("URL pattern", self.patterns_field)
        filter_form.addRow("Highlight", self.highlight_field)
        layout.addWidget(filter_group)

        for widget in self.findChildren(QLineEdit):
            widget.textChanged.connect(self._on_change)
        self.file_types.itemChanged.connect(self._on_change)

    def _on_change(self, *args) -> None:
        self.changed.emit(self.compiled_query())

    def _checked_file_types(self) -> list[str]:
        return [
            self.file_types.item(i).text()
            for i in range(self.file_types.count())
            if self.file_types.item(i).checkState() == Qt.Checked
        ]

    def dork(self) -> Dork:
        return Dork(
            keywords=self.keywords.text().strip(),
            exact_phrase=self.exact_phrase.text().strip(),
            exclude_terms=_split(self.exclude),
            required_terms=_split(self.required),
            any_terms=_split(self.any_terms),
            sites=_split(self.sites),
            file_types=self._checked_file_types(),
            in_url=self.inurl.text().strip(),
            in_title=self.intitle.text().strip(),
            in_text=self.intext.text().strip(),
            after=self.after.text().strip(),
            before=self.before.text().strip(),
        )

    def compiled_query(self) -> str:
        return compile_dork(self.dork())

    def load_dork(self, dork: Dork) -> None:
        self.keywords.setText(dork.keywords)
        self.exact_phrase.setText(dork.exact_phrase)
        self.exclude.setText(", ".join(dork.exclude_terms))
        self.required.setText(", ".join(dork.required_terms))
        self.any_terms.setText(", ".join(dork.any_terms))
        self.sites.setText(", ".join(dork.sites))
        self.inurl.setText(dork.in_url)
        self.intitle.setText(dork.in_title)
        self.intext.setText(dork.in_text)
        self.after.setText(dork.after)
        self.before.setText(dork.before)
        selected = set(dork.file_types)
        for i in range(self.file_types.count()):
            item = self.file_types.item(i)
            item.setCheckState(Qt.Checked if item.text() in selected else Qt.Unchecked)


def _split(value: QLineEdit) -> list[str]:
    return [t.strip() for t in value.text().split(",") if t.strip()]
