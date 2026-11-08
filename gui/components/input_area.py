# gui/components/input_area.py

"""
ROLE:
Chat composer.

Responsibilities:
    - Collect user questions.
    - Provide a send button.
    - Provide an upload-files button placeholder.
    - Emit user actions to ChatWindow.

The component does not perform HTTP requests.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class InputArea(QWidget):
    """
    Chat input component.
    """

    message_submitted = Signal(str)

    files_selected = Signal(list)

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #212121;
            }
            """
        )

        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "Ask anything..."
        )

        self.input.setMinimumHeight(
            42
        )

        self.send_button = QPushButton(
            "Send"
        )

        self.send_button.setMinimumHeight(
            42
        )

        self.upload_button = QPushButton(
            "📎"
        )

        self.upload_button.setToolTip(
            "Upload files"
        )

        self.upload_button.setFixedSize(
            42,
            42,
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            30,
            8,
            30,
            20,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            self.upload_button
        )

        layout.addWidget(
            self.input,
            stretch=1,
        )

        layout.addWidget(
            self.send_button
        )

        self.send_button.clicked.connect(
            self._submit
        )

        self.input.returnPressed.connect(
            self._submit
        )

        self.upload_button.clicked.connect(
            self._select_files
        )

    def _submit(self) -> None:
        """
        Submit the current question.
        """

        message = self.input.text().strip()

        if not message:
            return

        self.input.clear()

        self.message_submitted.emit(
            message
        )

    def _select_files(self) -> None:
        """
        Open the file picker.

        The backend upload endpoint is not implemented yet, so this
        currently only selects files and emits their paths.
        """

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select files",
            "",
            (
                "Documents (*.txt *.pdf *.docx *.md);;"
                "All Files (*)"
            ),
        )

        if not files:
            return

        self.files_selected.emit(
            files
        )

    def set_enabled(
        self,
        enabled: bool,
    ) -> None:
        """
        Enable or disable the composer.
        """

        self.input.setEnabled(
            enabled
        )

        self.send_button.setEnabled(
            enabled
        )

        self.upload_button.setEnabled(
            enabled
        )

    def focus_input(self) -> None:
        """
        Return keyboard focus to the message input.
        """

        self.input.setFocus()