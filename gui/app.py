# owns the application window
# creates/configures QApplication
# gui/app.py

"""
ROLE:
Creates and configures the Qt application.
"""

import sys

from PySide6.QtWidgets import QApplication

from gui.components.chat_window import ChatWindow


def run() -> None:
    """
    Start the desktop GUI application.
    """

    application = QApplication(
        sys.argv
    )

    window = ChatWindow()

    window.show()

    sys.exit(
        application.exec()
    )