# ui_styler.py
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette
# Import specific colors from app_config
from app_config import (
    CRIMSON_RED, DARK_BACKGROUND, MID_BACKGROUND, LIGHT_GRAY_TEXT,
    DARK_GRAY_BORDER, DISABLED_COLOR, TEXT_ON_RED
)

def apply_app_styles(application_instance, main_window):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, DARK_BACKGROUND)
    palette.setColor(QPalette.ColorRole.WindowText, LIGHT_GRAY_TEXT)
    palette.setColor(QPalette.ColorRole.Base, MID_BACKGROUND)
    palette.setColor(QPalette.ColorRole.AlternateBase, DARK_GRAY_BORDER)
    palette.setColor(QPalette.ColorRole.ToolTipBase, DARK_BACKGROUND)
    palette.setColor(QPalette.ColorRole.ToolTipText, LIGHT_GRAY_TEXT)
    palette.setColor(QPalette.ColorRole.Text, LIGHT_GRAY_TEXT)
    palette.setColor(QPalette.ColorRole.Button, MID_BACKGROUND)
    palette.setColor(QPalette.ColorRole.ButtonText, LIGHT_GRAY_TEXT)
    palette.setColor(QPalette.ColorRole.BrightText, CRIMSON_RED)
    palette.setColor(QPalette.ColorRole.Link, CRIMSON_RED.lighter(120))
    palette.setColor(QPalette.ColorRole.Highlight, CRIMSON_RED)
    palette.setColor(QPalette.ColorRole.HighlightedText, TEXT_ON_RED)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, DISABLED_COLOR)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, DISABLED_COLOR)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, DISABLED_COLOR)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, DISABLED_COLOR.darker(110))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, DARK_BACKGROUND.lighter(105))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, DARK_BACKGROUND.lighter(105))
    application_instance.setPalette(palette)

    qss = f"""
        QMainWindow {{
            background-color: {DARK_BACKGROUND.name()};
        }}

        /* === QTabWidget and QTabBar === */
        QTabWidget::pane {{ /* The Container for the tab contents */
            border: 1px solid {DARK_GRAY_BORDER.name()};
            border-top: none; /* Tab bar will blend or have its own top border */
            background-color: {DARK_BACKGROUND.name()}; /* Match main window background */
            padding: 10px;
        }}

        QTabBar::tab {{
            background: {MID_BACKGROUND.name()};
            color: {LIGHT_GRAY_TEXT.name()};
            border: 1px solid {DARK_GRAY_BORDER.name()};
            border-bottom: none; /* Blends into the pane */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 15px;
            margin-right: 2px; /* Space between tabs */
            min-width: 120px; /* Ensure tabs have some width */
        }}

        QTabBar::tab:selected {{
            background: {DARK_BACKGROUND.name()}; /* Match pane background to "lift" tab */
            color: {CRIMSON_RED.name()};
            font-weight: bold;
            border-color: {DARK_GRAY_BORDER.name()};
            /* border-bottom-color: {DARK_BACKGROUND.name()}; */ /* To make selected tab blend into pane */
        }}

        QTabBar::tab:!selected {{
            background: {MID_BACKGROUND.darker(110).name()};
            margin-top: 2px; /* Make non-selected tabs appear slightly receded */
        }}

        QTabBar::tab:!selected:hover {{
            background: {MID_BACKGROUND.lighter(110).name()};
            color: {LIGHT_GRAY_TEXT.lighter(120).name()};
        }}
        QTabBar::tab:selected:hover {{
            background: {DARK_BACKGROUND.lighter(105).name()};
            color: {CRIMSON_RED.lighter(110).name()};
        }}

        /* === QGroupBox === */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {DARK_GRAY_BORDER.name()};
            border-radius: 5px;
            margin-top: 1em; 
            padding: 8px;
            /* background-color: {DARK_BACKGROUND.lighter(102).name()}; */ /* Optional: slightly different bg for groupbox */
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
            background-color: {DARK_BACKGROUND.name()}; /* Crucial: Needs to match parent of QGroupBox (pane or window) */
            color: {CRIMSON_RED.name()};
        }}
        /* If QGroupBox is inside a QTabWidget::pane, its title background should match pane's background */
        QTabWidget::pane > QGroupBox::title {{
             background-color: {DARK_BACKGROUND.name()}; /* Match pane bg */
        }}


        QLabel {{
            color: {LIGHT_GRAY_TEXT.name()}; background-color: transparent;
        }}
        QLabel#FooterLabel {{
            font-size: 8pt; color: {DISABLED_COLOR.name()};
        }}

        QLineEdit, QPlainTextEdit, QSpinBox, QComboBox {{
            padding: 5px; border: 1px solid {DARK_GRAY_BORDER.name()}; border-radius: 3px;
            background-color: {MID_BACKGROUND.name()}; color: {LIGHT_GRAY_TEXT.name()};
            selection-background-color: {CRIMSON_RED.name()}; selection-color: {TEXT_ON_RED.name()};
            min-height: 1.6em;
        }}
        QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 1px solid {CRIMSON_RED.name()};
        }}
        QLineEdit[readOnly="true"] {{ background-color: {DARK_BACKGROUND.name()}; }}
        QLineEdit::placeholder {{ color: {DISABLED_COLOR.darker(110).name()}; }}
        
        QPlainTextEdit {{
            background-color: {DARK_BACKGROUND.lighter(110).name()};
            font-family: Consolas, Courier New, monospace;
        }}

        /* QComboBox specific styling */
        QComboBox {{
            padding-right: 20px; /* Space for the arrow */
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 18px;
            border-left-width: 1px;
            border-left-color: {DARK_GRAY_BORDER.name()};
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: {MID_BACKGROUND.name()};
        }}
        QComboBox::down-arrow {{
            image: url(); /* Remove default arrow, or use custom: url(path/to/your/arrow.png); */
            /* Basic CSS arrow: */
            border-style: solid;
            border-width: 4px 4px 0 4px; /* top, right, bottom, left */
            border-color: {LIGHT_GRAY_TEXT.name()} transparent transparent transparent;
            width: 0px; height: 0px;
            position: relative; top: 40%; /* Adjust for vertical centering */
            left: -2px; /* Fine-tune position */
        }}
        QComboBox::down-arrow:on {{ /* Arrow when combobox is open */
            border-width: 0 4px 4px 4px;
            border-color: transparent transparent {LIGHT_GRAY_TEXT.name()} transparent;
        }}
        QComboBox QAbstractItemView {{ /* The dropdown list */
            border: 1px solid {DARK_GRAY_BORDER.name()};
            background-color: {MID_BACKGROUND.name()};
            color: {LIGHT_GRAY_TEXT.name()};
            selection-background-color: {CRIMSON_RED.name()};
            selection-color: {TEXT_ON_RED.name()};
            padding: 2px;
        }}
        QComboBox:disabled {{
             background-color: {DARK_BACKGROUND.name()}; color: {DISABLED_COLOR.name()};
             border-color: {DISABLED_COLOR.name()};
        }}
         QComboBox::down-arrow:disabled {{
            border-top-color: {DISABLED_COLOR.name()};
        }}


        QSpinBox::up-button, QSpinBox::down-button {{
            subcontrol-origin: border; background-color: {MID_BACKGROUND.name()};
            border: 1px solid {DARK_GRAY_BORDER.name()}; border-radius: 2px;
            width: 18px; height: 0.8em; margin-right: 1px;
        }}
        QSpinBox::up-button {{ subcontrol-position: top right; margin-top: 1px; }}
        QSpinBox::down-button {{ subcontrol-position: bottom right; margin-bottom: 1px; }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: {DARK_GRAY_BORDER.name()}; }}
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{ background-color: {DARK_BACKGROUND.name()}; }}
        QSpinBox::up-arrow {{
            border-left: 4px solid transparent; border-right: 4px solid transparent;
            border-bottom: 4px solid {LIGHT_GRAY_TEXT.name()}; width: 0px; height: 0px;
            position: relative; top: -1px;
        }}
        QSpinBox::down-arrow {{
            border-left: 4px solid transparent; border-right: 4px solid transparent;
            border-top: 4px solid {LIGHT_GRAY_TEXT.name()}; width: 0px; height: 0px;
            position: relative; top: 1px;
        }}
        QSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off,
        QSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off {{
            border-top-color: {DISABLED_COLOR.name()}; border-bottom-color: {DISABLED_COLOR.name()};
        }}
        QSpinBox:disabled {{
             background-color: {DARK_BACKGROUND.name()}; color: {DISABLED_COLOR.name()};
             border-color: {DISABLED_COLOR.name()};
        }}

        QPushButton {{
            padding: 7px 12px; border: 1px solid {DARK_GRAY_BORDER.name()}; border-radius: 3px;
            background-color: {MID_BACKGROUND.name()}; color: {LIGHT_GRAY_TEXT.name()};
        }}
        QPushButton:hover {{ background-color: {DARK_GRAY_BORDER.name()}; }}
        QPushButton:pressed {{ background-color: {DARK_BACKGROUND.name()}; }}
        QPushButton:disabled {{
            background-color: {DARK_BACKGROUND.name()}; border: 1px solid {DISABLED_COLOR.name()};
            color: {DISABLED_COLOR.name()};
        }}
        QPushButton#BuildButton {{ /* Used for Build and Send Command buttons */
            background-color: {CRIMSON_RED.name()}; color: {TEXT_ON_RED.name()};
            font-weight: bold; border: 1px solid {CRIMSON_RED.darker(120).name()};
        }}
        QPushButton#BuildButton:hover {{ background-color: {CRIMSON_RED.lighter(110).name()}; }}
        QPushButton#BuildButton:disabled {{
             background-color: {DISABLED_COLOR.name()}; color: {DARK_BACKGROUND.name()};
             border-color: {DISABLED_COLOR.darker(110).name()};
        }}
        QPushButton#IconButton {{
            border: 1px solid transparent; background: transparent;
            padding: 2px; color: {LIGHT_GRAY_TEXT.name()}; font-weight: bold;
            font-size: 1.1em; border-radius: 3px;
            text-align: center;
        }}
        QPushButton#IconButton:hover {{
            background-color: {DARK_GRAY_BORDER.name()};
            border: 1px solid {CRIMSON_RED.lighter(130).name()};
        }}
        QPushButton#IconButton:pressed {{
            background-color: {DARK_BACKGROUND.name()};
            border: 1px solid {CRIMSON_RED.name()};
        }}
        QPushButton#IconButton:focus {{
             border: 1px solid {CRIMSON_RED.name()};
        }}
        QPushButton#IconButton:disabled {{
            background: transparent; border: 1px solid transparent; color: {DISABLED_COLOR.name()};
        }}

        QCheckBox {{
            color: {LIGHT_GRAY_TEXT.name()};
            background-color: transparent;
            spacing: 5px;
            min-height: 18px;
        }}
        QCheckBox::indicator {{
            width: 13px;
            height: 13px;
            border: 1px solid {DARK_GRAY_BORDER.name()};
            border-radius: 3px;
            background-color: {MID_BACKGROUND.name()};
        }}
        QCheckBox::indicator:checked {{
            background-color: {CRIMSON_RED.name()};
            border-color: {CRIMSON_RED.darker(110).name()};
            image: none;
        }}
        QCheckBox:disabled {{
            color: {DISABLED_COLOR.name()};
        }}
        QCheckBox::indicator:disabled {{
             background-color: {DISABLED_COLOR.darker(120).name()};
             border-color: {DISABLED_COLOR.name()};
        }}

        QProgressBar {{
            border: 1px solid {DARK_GRAY_BORDER.name()}; border-radius: 3px;
            text-align: center; color: {LIGHT_GRAY_TEXT.name()};
            background-color: {MID_BACKGROUND.name()}; min-height: 2.0em;
        }}
        QProgressBar::chunk {{
            background-color: {CRIMSON_RED.name()};
            border-radius: 2px; margin: 1px;
            /* color: {TEXT_ON_RED.name()}; */ /* Chunk text color is tricky with QSS */
        }}
    """
    try:
        # Apply to main window first, then to application for global effect if needed
        # For QTabWidget::pane > QGroupBox::title, the main_window stylesheet is what matters here
        main_window.setStyleSheet(qss)
        # application_instance.setStyleSheet(qss) # Can cause issues if applied globally too broadly
        # application_instance.style().unpolish(application_instance) # Force re-evaluation
        # application_instance.style().polish(application_instance)
        main_window.style().unpolish(main_window)
        main_window.style().polish(main_window)
    except Exception as e:
        print(f"--- QSS Parsing Error ---")
        print(f"Error: {e}")
        print(f"QSS content:\n{qss}")
        print(f"--- End QSS Error ---")