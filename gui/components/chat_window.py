# gui/components/chat_window.py

"""
ROLE:
Main desktop chat window.

This component orchestrates the GUI but does not contain AI logic.

Architecture:

    ChatWindow
        │
        ├── MessageView
        │
        ├── InputArea
        │
        └── APIClient
                │
                ▼
             FastAPI
                │
                ▼
            ChatEngine
"""

from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from gui.api.client import APIClient
from gui.components.input_area import InputArea
from gui.components.message_view import MessageView
from gui.config import (
    API_BASE_URL,
    APP_STYLE,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)


class MessageWorker(QObject):
    """
    Performs one blocking API request outside the GUI thread.
    """

    finished = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        client: APIClient,
        session_id: str,
        question: str,
    ):
        super().__init__()

        self.client = client
        self.session_id = session_id
        self.question = question

    @Slot()
    def run(self) -> None:
        """
        Execute the API request.
        """

        try:

            response = self.client.send_message(
                session_id=self.session_id,
                question=self.question,
            )

            self.finished.emit(
                response
            )

        except RuntimeError as exc:

            self.failed.emit(
                str(exc)
            )


class ChatWindow(QMainWindow):
    """
    One desktop chat window.

    Each window owns one persistent backend session ID.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            WINDOW_TITLE
        )

        self.resize(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )

        self.setStyleSheet(
            APP_STYLE
        )

        self.client = APIClient(
            base_url=API_BASE_URL
        )

        self.session_id = None

        self._worker_thread = None
        self._worker = None

        self._build_ui()

        self._create_session()

    def _build_ui(self) -> None:
        """
        Construct the window layout.
        """

        central_widget = QWidget()

        layout = QVBoxLayout(
            central_widget
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            0
        )

        self.status_label = QLabel(
            "Connecting..."
        )

        self.status_label.setStyleSheet(
            """
            QLabel {
                background-color: #212121;
                color: #8e8e8e;
                padding: 12px 24px;
                font-size: 12px;
            }
            """
        )

        self.message_view = MessageView()

        self.input_area = InputArea()

        self.input_area.set_enabled(
            False
        )

        self.input_area.message_submitted.connect(
            self._handle_message
        )

        self.input_area.files_selected.connect(
            self._handle_files_selected
        )

        layout.addWidget(
            self.status_label
        )

        layout.addWidget(
            self.message_view,
            stretch=1,
        )

        layout.addWidget(
            self.input_area
        )

        self.setCentralWidget(
            central_widget
        )

    def _create_session(self) -> None:
        """
        Create a persistent backend session.

        Session creation is currently performed synchronously because
        it is a lightweight operation. Message generation is moved to
        a worker thread because it can take considerably longer.
        """

        try:

            self.session_id = (
                self.client.create_session()
            )

            self.status_label.setText(
                "Connected"
            )

            self.input_area.set_enabled(
                True
            )

            self.input_area.focus_input()

        except RuntimeError as exc:

            self.status_label.setText(
                "Backend unavailable"
            )

            self.message_view.add_error_message(
                f"Could not connect to the AI backend.\n\n{exc}"
            )

    def _handle_message(
        self,
        question: str,
    ) -> None:
        """
        Handle a submitted question.
        """

        if not self.session_id:
            return

        self.message_view.add_user_message(
            question
        )

        self.input_area.set_enabled(
            False
        )

        self.status_label.setText(
            "Thinking..."
        )

        self._start_worker(
            question
        )

    def _handle_files_selected(
        self,
        files: list[str],
    ) -> None:
        """
        Handle files selected through the upload button.

        Upload transport will be connected after the FastAPI upload
        endpoint is implemented.
        """

        self.status_label.setText(
            f"{len(files)} file(s) selected"
        )

    def _start_worker(
        self,
        question: str,
    ) -> None:
        """
        Start a worker thread for the blocking API request.
        """

        self._worker_thread = QThread(
            self
        )

        self._worker = MessageWorker(
            client=self.client,
            session_id=self.session_id,
            question=question,
        )

        self._worker.moveToThread(
            self._worker_thread
        )

        self._worker_thread.started.connect(
            self._worker.run
        )

        self._worker.finished.connect(
            self._handle_response
        )

        self._worker.failed.connect(
            self._handle_error
        )

        self._worker.finished.connect(
            self._worker_thread.quit
        )

        self._worker.failed.connect(
            self._worker_thread.quit
        )

        self._worker_thread.finished.connect(
            self._worker.deleteLater
        )

        self._worker_thread.finished.connect(
            self._worker_thread.deleteLater
        )

        self._worker_thread.start()

    @Slot(str)
    def _handle_response(
        self,
        response: str,
    ) -> None:
        """
        Display an assistant response.
        """

        self.message_view.add_assistant_message(
            response
        )

        self.status_label.setText(
            "Connected"
        )

        self.input_area.set_enabled(
            True
        )

        self.input_area.focus_input()

    @Slot(str)
    def _handle_error(
        self,
        error: str,
    ) -> None:
        """
        Display an API/network failure.
        """

        self.message_view.add_error_message(
            f"Request failed:\n\n{error}"
        )

        self.status_label.setText(
            "Request failed"
        )

        self.input_area.set_enabled(
            True
        )

        self.input_area.focus_input()

    def closeEvent(self, event) -> None:
        """
        Cleanly close the HTTP client when the window exits.
        """

        self.client.close()

        super().closeEvent(
            event
        )