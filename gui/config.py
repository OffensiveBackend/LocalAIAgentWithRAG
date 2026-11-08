# gui/config.py

"""
ROLE:
Central configuration for the desktop GUI.

This file contains presentation and API configuration only.
Backend configuration remains inside the backend.
"""

API_BASE_URL = "http://127.0.0.1:8000"

WINDOW_TITLE = "Local AI Agent"

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750

APP_STYLE = """
QMainWindow {
    background-color: #212121;
}

QWidget {
    font-family: "Segoe UI";
    font-size: 14px;
}

QLabel {
    color: #ececec;
}

QScrollArea {
    border: none;
    background-color: #212121;
}

QLineEdit {
    background-color: #2f2f2f;
    color: #ececec;
    border: 1px solid #4a4a4a;
    border-radius: 18px;
    padding: 10px 14px;
    selection-background-color: #5b5bd6;
}

QLineEdit:focus {
    border: 1px solid #7777ff;
}

QPushButton {
    background-color: #3a3a3a;
    color: #ececec;
    border: none;
    border-radius: 16px;
    padding: 9px 16px;
}

QPushButton:hover {
    background-color: #4a4a4a;
}

QPushButton:pressed {
    background-color: #303030;
}

QPushButton:disabled {
    color: #777777;
    background-color: #2a2a2a;
}
"""