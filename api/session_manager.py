"""
ROLE:
Manages persistent sessions.

A session is the user's current interaction context.

A conversation is the durable historical record associated with that
session.

PostgreSQL is the authoritative source of session validity.

This manager deliberately does NOT keep the session registry in a
process-local dictionary.

Therefore:

    Worker A ─┐
    Worker B ─┼──► PostgreSQL
    Worker C ─┘

Any worker can retrieve the same session.
"""

from datetime import datetime, timezone
from uuid import uuid4

from chat.conversation_history import ConversationHistory
from persistence.conversation_service.repository import (
    ConversationRepository,
)
from persistence.session_service.repository import SessionRepository


class SessionManager:

    def __init__(
        self,
        session_repository: SessionRepository | None = None,
        conversation_repository: ConversationRepository | None = None,
    ):
        self._session_repository = (
            session_repository
            or SessionRepository()
        )

        self._conversation_repository = (
            conversation_repository
            or ConversationRepository()
        )

    # ------------------------------------------------------------------
    # CREATE SESSION
    # ------------------------------------------------------------------

    def create_session(self) -> str:
        """
        Create a new persistent session and its conversation.

        Returns
        -------
        str
            UUID identifying the newly created session.
        """

        now = datetime.now(timezone.utc)

        session_id = str(uuid4())
        conversation_id = str(uuid4())

        # --------------------------------------------------------------
        # Create durable conversation first.
        # --------------------------------------------------------------

        self._conversation_repository.create_conversation(
            conversation_id=conversation_id,
            created_at=now,
        )

        # --------------------------------------------------------------
        # Create session pointing to that conversation.
        # --------------------------------------------------------------

        self._session_repository.create(
            session_id=session_id,
            conversation_id=conversation_id,
            created_at=now,
        )

        return session_id

    # ------------------------------------------------------------------
    # GET SESSION
    # ------------------------------------------------------------------

    def get_session(
        self,
        session_id: str,
    ) -> ConversationHistory:
        """
        Retrieve a persistent session.

        The session is looked up in PostgreSQL, meaning this works
        regardless of which FastAPI worker receives the request.

        Raises
        ------
        KeyError
            If the session does not exist or has been revoked.
        """

        session = self._session_repository.get(
            session_id
        )

        if session is None:
            raise KeyError(
                f"Session '{session_id}' does not exist."
            )

        # --------------------------------------------------------------
        # Session validity is determined exclusively by PostgreSQL.
        # --------------------------------------------------------------

        if session.revoked_at is not None:
            raise KeyError(
                f"Session '{session_id}' has been revoked."
            )

        # --------------------------------------------------------------
        # Update activity timestamp.
        # --------------------------------------------------------------

        self._session_repository.update_last_active(
            session_id=session_id,
            last_active_at=datetime.now(timezone.utc),
        )

        # --------------------------------------------------------------
        # Reconstruct conversation history from durable storage.
        # --------------------------------------------------------------

        return ConversationHistory(
            conversation_id=session.conversation_id
        )

    # ------------------------------------------------------------------
    # DELETE / REVOKE SESSION
    # ------------------------------------------------------------------

    def delete_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Explicitly revoke a session.

        This does NOT delete the historical conversation.

        Session validity therefore follows:

            valid
              │
              ▼
          explicitly revoked
              │
              ▼
            invalid
        """

        return self._session_repository.revoke(
            session_id=session_id,
            revoked_at=datetime.now(timezone.utc),
        )