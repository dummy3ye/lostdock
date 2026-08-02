"""Light/dark theme stylesheets applied at the application level."""

from __future__ import annotations

from typing import ClassVar

_THEMES: ClassVar[dict[str, dict[str, str]]] = {
    "dark": {
        "window": "#1e1e2e",
        "base": "#313244",
        "alt": "#45475a",
        "text": "#cdd6f4",
        "muted": "#a6adc8",
        "accent": "#89b4fa",
        "border": "#45475a",
        "disabled": "#6c7086",
    },
    "light": {
        "window": "#f5f5f7",
        "base": "#ffffff",
        "alt": "#ececf0",
        "text": "#1e1e2e",
        "muted": "#585860",
        "accent": "#1f5bb0",
        "border": "#d4d4da",
        "disabled": "#9a9aa2",
    },
}


def themes() -> tuple[str, ...]:
    return tuple(_THEMES)


def _stylesheet(c) -> str:
    return f"""
QMainWindow, QDialog, QWidget {{
    background-color: {c["window"]};
    color: {c["text"]};
}}
QMenuBar {{
    background-color: {c["window"]};
    color: {c["text"]};
}}
QMenuBar::item:selected, QMenu::item:selected {{
    background-color: {c["accent"]};
    color: #ffffff;
}}
QMenu {{
    background-color: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
}}
QToolBar {{
    background-color: {c["window"]};
    border: none;
    padding: 4px;
    spacing: 6px;
}}
QToolBar QLabel {{
    color: {c["muted"]};
}}
QStatusBar {{
    background-color: {c["base"]};
    color: {c["text"]};
}}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background-color: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 3px 6px;
    selection-background-color: {c["accent"]};
    selection-color: #ffffff;
}}
QComboBox::drop-down, QSpinBox::up-button, QSpinBox::down-button {{
    border: none;
    background-color: {c["alt"]};
}}
QPushButton {{
    background-color: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 4px 12px;
}}
QPushButton:hover {{
    background-color: {c["alt"]};
}}
QPushButton:pressed {{
    background-color: {c["accent"]};
    color: #ffffff;
}}
QPushButton:disabled {{
    color: {c["disabled"]};
}}
QCheckBox, QGroupBox, QLabel {{
    color: {c["text"]};
}}
QGroupBox {{
    border: 1px solid {c["border"]};
    border-radius: 6px;
    margin-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
QFrame {{
    border: none;
}}
QTableWidget {{
    background-color: {c["window"]};
    alternate-background-color: {c["base"]};
    color: {c["text"]};
    gridline-color: {c["border"]};
    selection-background-color: {c["accent"]};
    selection-color: #ffffff;
}}
QHeaderView::section {{
    background-color: {c["alt"]};
    color: {c["text"]};
    border: none;
    border-right: 1px solid {c["border"]};
    padding: 4px 8px;
}}
QScrollBar:vertical {{
    background: {c["window"]};
    width: 12px;
}}
QScrollBar::handle:vertical {{
    background: {c["alt"]};
    border-radius: 6px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QToolTip {{
    background-color: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
}}
QLabel[class="preview"] {{
    background-color: {c["base"]};
    color: {c["muted"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 8px;
    font-family: monospace;
}}
QSplitter::handle {{
    background-color: {c["border"]};
}}
"""


def stylesheet(name: str) -> str:
    try:
        palette = _THEMES[name]
    except KeyError:
        raise ValueError(f"unknown theme: {name!r} (available: {', '.join(_THEMES)})") from None
    return _stylesheet(palette)
