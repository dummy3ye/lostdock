"""Theme stylesheets applied at the application level.

Two families are supported:

* ``dark``/``light`` — modern flat themes driven by the default stylesheet.
* ``win98-*`` — a Windows 9x GDI recreation: hard orthogonal edges, raised /
  sunken 1px bevels, and pixel bitmap typography.
"""

from __future__ import annotations

from typing import ClassVar

_THEMES: ClassVar[dict[str, dict[str, str]]] = {
    "dark": {
        "window": "#1e1e1e",
        "base": "#252526",
        "alt": "#333333",
        "text": "#d4d4d4",
        "muted": "#9a9a9a",
        "accent": "#0e639c",
        "border": "#3c3c3c",
        "disabled": "#6e6e6e",
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

# Win98 GDI palettes. Colour keys mirror the classic/Windows 9x shell roles:
# the UI palette keys (`window`, `base`, ...) are derived from these so the
# shared widget rules keep working, while the classic renderer adds bevels.
_WIN98_THEMES: ClassVar[dict[str, dict[str, str]]] = {
    "win98": {
        "desktop_bg": "#008080",  # Standard Teal
        "surface_main": "#c0c0c0",  # Light Gray / Face
        "surface_light": "#ffffff",  # Highlight
        "surface_shadow": "#808080",  # Dark shadow
        "surface_dark": "#000000",  # Outermost shadow border
        "titlebar_active": "#000080",  # Navy active titlebar
        "titlebar_text": "#ffffff",
        "text_main": "#000000",
    },
    "win98-pink": {
        "desktop_bg": "#ffb6c1",  # Light Pink desktop
        "surface_main": "#fde2e4",  # Soft rose face
        "surface_light": "#ffffff",  # White highlight
        "surface_shadow": "#e8a598",  # Soft terracotta shadow
        "surface_dark": "#4a0e17",  # Deep wine outermost shadow
        "titlebar_active": "#d87093",  # Pale violet red
        "titlebar_text": "#ffffff",
        "text_main": "#330011",  # Deep burgundy text
    },
    "win98-dark": {
        "desktop_bg": "#008080",  # Keep the classic Standard Teal desktop
        "surface_main": "#2b2b31",  # Dark face
        "surface_light": "#44444c",  # Highlight (lighter than face)
        "surface_shadow": "#1a1a1f",  # Dark shadow
        "surface_dark": "#000000",  # Outermost shadow border
        "titlebar_active": "#3b3be0",  # Bright blue active titlebar
        "titlebar_text": "#ffffff",
        "text_main": "#e8e8e8",  # Light text
    },
}


def themes() -> tuple[str, ...]:
    return tuple(_THEMES) + tuple(_WIN98_THEMES)


def _win98_to_palette(c: dict[str, str]) -> dict[str, str]:
    """Derive the shared widget palette keys from a win98 GDI palette."""
    return {
        "window": c["surface_main"],
        "base": c["surface_main"],
        "alt": c["surface_light"],
        "text": c["text_main"],
        "muted": c["surface_shadow"],
        "accent": c["titlebar_active"],
        "border": c["surface_shadow"],
        "disabled": c["surface_shadow"],
        "_win98": c,
    }


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


def _win98_stylesheet(c: dict[str, str]) -> str:
    """Render a Windows 9x GDI stylesheet from a win98 palette."""
    face = c["surface_main"]
    light = c["surface_light"]
    shadow = c["surface_shadow"]
    dark = c["surface_dark"]
    title = c["titlebar_active"]
    title_text = c["titlebar_text"]
    text = c["text_main"]
    desktop = c["desktop_bg"]
    return f"""
* {{
    font-family: "MS Sans Serif", "Tahoma", "Pixelated", "DejaVu Sans", sans-serif;
    font-size: 11px;
    border-radius: 0px !important;
    outline: none;
}}
QMainWindow, QDialog, QWidget {{
    background-color: {desktop};
    color: {text};
}}
QMenuBar {{
    background-color: {face};
    color: {text};
    border-bottom: 2px solid;
    border-color: {face};
}}
QMenuBar::item:selected, QMenu::item:selected {{
    background-color: {title};
    color: {title_text};
}}
QMenu {{
    background-color: {face};
    color: {text};
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
}}
QToolBar {{
    background-color: {face};
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
    padding: 2px;
    spacing: 2px;
}}
QToolBar QLabel {{
    color: {text};
}}
QStatusBar {{
    background-color: {face};
    color: {text};
    border-top: 1px solid {shadow};
}}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background-color: {light};
    color: {text};
    border: 2px solid;
    border-top-color: {shadow};
    border-left-color: {shadow};
    border-right-color: {light};
    border-bottom-color: {light};
    padding: 2px 3px;
    selection-background-color: {title};
    selection-color: {title_text};
}}
QComboBox::drop-down, QSpinBox::up-button, QSpinBox::down-button {{
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
    background-color: {face};
}}
QPushButton {{
    background-color: {face};
    color: {text};
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
    padding: 4px 10px;
}}
QPushButton::pressed {{
    border-top-color: {dark};
    border-left-color: {dark};
    border-right-color: {light};
    border-bottom-color: {light};
    padding: 5px 9px 3px 11px;
}}
QPushButton:disabled {{
    color: {shadow};
    text-shadow: 1px 1px {light};
}}
QCheckBox, QRadioButton, QGroupBox, QLabel {{
    color: {text};
    background: transparent;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 13px;
    height: 13px;
    border: 2px solid;
    border-top-color: {shadow};
    border-left-color: {shadow};
    border-right-color: {light};
    border-bottom-color: {light};
    background-color: {light};
}}
QCheckBox::indicator:checked {{
    background-color: {title};
}}
QRadioButton::indicator:checked {{
    background-color: {title};
}}
QGroupBox {{
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
    margin-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    background-color: {desktop};
}}
QFrame {{
    border: none;
}}
QTableWidget {{
    background-color: {light};
    alternate-background-color: {face};
    color: {text};
    gridline-color: {shadow};
    selection-background-color: {title};
    selection-color: {title_text};
    border: 2px solid;
    border-top-color: {shadow};
    border-left-color: {shadow};
    border-right-color: {light};
    border-bottom-color: {light};
}}
QHeaderView::section {{
    background-color: {face};
    color: {text};
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
    padding: 3px 8px;
}}
QScrollBar:vertical {{
    background: {face};
    width: 16px;
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
}}
QScrollBar::handle:vertical {{
    background: {face};
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 14px;
    background: {face};
    border: 2px solid;
    border-top-color: {light};
    border-left-color: {light};
    border-right-color: {dark};
    border-bottom-color: {dark};
}}
QToolTip {{
    background-color: {light};
    color: {text};
    border: 1px solid {dark};
}}
QLabel[class="preview"] {{
    background-color: {light};
    color: {text};
    border: 2px solid;
    border-top-color: {shadow};
    border-left-color: {shadow};
    border-right-color: {light};
    border-bottom-color: {light};
    padding: 8px;
    font-family: "MS Sans Serif", "Tahoma", monospace;
}}
QSplitter::handle {{
    background-color: {face};
    border: 1px solid {dark};
}}
"""


def stylesheet(name: str) -> str:
    if name in _WIN98_THEMES:
        return _win98_stylesheet(_WIN98_THEMES[name])
    try:
        palette = _THEMES[name]
    except KeyError:
        raise ValueError(f"unknown theme: {name!r} (available: {', '.join(themes())})") from None
    return _stylesheet(palette)
