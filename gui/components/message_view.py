# gui/components/message_view.py

"""
ROLE:
Conversation presentation layer.

Responsibilities:
    - Display user messages as bubbles.
    - Display assistant responses as normal prose.
    - Maintain conversation scrolling.
    - Provide a clean visual separation between messages.

This component does not know anything about FastAPI, sessions,
ChatEngine, PostgreSQL, or the LLM.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class MessageView(QScrollArea):
    """
    Scrollable conversation display.
    """

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.setWidgetResizable(True)

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: #212121;
            }

            QScrollBar:vertical {
                background: #212121;
                width: 10px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #454545;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )

        self.container = QWidget()

        self.container.setStyleSheet(
            """
            QWidget {
                background-color: #212121;
            }
            """
        )

        self.layout = QVBoxLayout(
            self.container
        )

        self.layout.setContentsMargins(
            40,
            30,
            40,
            30,
        )

        self.layout.setSpacing(20)

        self.layout.addStretch()

        self.setWidget(
            self.container
        )

    def add_user_message(
        self,
        message: str,
    ) -> None:
        """
        Display a user message in a right-aligned bubble.
        """

        bubble = QFrame()

        bubble.setMaximumWidth(650)

        bubble.setStyleSheet(
            """
            QFrame {
                background-color: #303030;
                border-radius: 16px;
            }
            """
        )

        bubble_layout = QVBoxLayout(
            bubble
        )

        bubble_layout.setContentsMargins(
            14,
            10,
            14,
            10,
        )

        label = QLabel(
            message
        )

        label.setWordWrap(True)

        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        label.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: #f1f1f1;
                padding: 0;
            }
            """
        )

        bubble_layout.addWidget(
            label
        )

        row = QWidget()

        row_layout = QHBoxLayout(
            row
        )

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row_layout.addStretch()

        row_layout.addWidget(
            bubble
        )

        self._insert_message(
            row
        )

    def add_assistant_message(
        self,
        message: str,
    ) -> None:
        """
        Display an assistant response as normal prose.
        """

        wrapper = QWidget()

        wrapper_layout = QVBoxLayout(
            wrapper
        )

        wrapper_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        wrapper_layout.setSpacing(5)

        role_label = QLabel(
            "Local AI Agent"
        )

        role_label.setStyleSheet(
            """
            QLabel {
                color: #9b9b9b;
                font-size: 12px;
                font-weight: 600;
                padding-left: 2px;
            }
            """
        )

        response_label = QLabel(
            message
        )

        response_label.setWordWrap(True)

        response_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        response_label.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: #ececec;
                font-size: 14px;
                line-height: 1.5;
                padding: 0 2px;
            }
            """
        )

        wrapper_layout.addWidget(
            role_label
        )

        wrapper_layout.addWidget(
            response_label
        )

        self._insert_message(
            wrapper
        )

    def add_error_message(
        self,
        message: str,
    ) -> None:
        """
        Display a backend/network error.
        """

        label = QLabel(
            message
        )

        label.setWordWrap(True)

        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        label.setStyleSheet(
            """
            QLabel {
                color: #ff8a8a;
                background: #351f1f;
                border-radius: 10px;
                padding: 12px;
            }
            """
        )

        self._insert_message(
            label
        )

    def clear_messages(self) -> None:
        """
        Remove all displayed messages.
        """

        while self.layout.count() > 1:

            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _insert_message(
        self,
        widget: QWidget,
    ) -> None:
        """
        Insert a message immediately before the permanent stretch.
        """

        self.layout.insertWidget(
            self.layout.count() - 1,
            widget,
        )

        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        """
        Scroll to the newest message.
        """

        scrollbar = self.verticalScrollBar()

        scrollbar.setValue(
            scrollbar.maximum()
        )