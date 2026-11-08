"""
ROLE:
PostgreSQL operations for sessions.
"""

from datetime import datetime

from persistence.database.connection import get_connection
from persistence.session_service.models import Session


class SessionRepository:
    """
    PostgreSQL persistence layer for sessions.

    PostgreSQL is the authoritative source of truth.

    Redis must never be used to determine permanent session validity.

    Responsibilities:
        - Persist sessions.
        - Retrieve sessions.
        - Update session activity.
        - Explicitly revoke sessions.
    """

    def create(
        self,
        session_id: str,
        conversation_id: str,
        created_at: datetime,
    ) -> Session:
        """
        Persist a new session in PostgreSQL.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    INSERT INTO sessions (
                        id,
                        conversation_id,
                        created_at,
                        last_active_at,
                        revoked_at
                    )
                    VALUES (%s, %s, %s, %s, NULL)
                    """,
                    (
                        session_id,
                        conversation_id,
                        created_at,
                        created_at,
                    ),
                )

        return Session(
            session_id=session_id,
            conversation_id=conversation_id,
            created_at=created_at,
            last_active_at=created_at,
            revoked_at=None,
        )

    def get(
        self,
        session_id: str,
    ) -> Session | None:
        """
        Retrieve a session from PostgreSQL.

        Returns:
            Session if it exists.
            None if no such session exists.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    SELECT
                        id,
                        conversation_id,
                        created_at,
                        last_active_at,
                        revoked_at
                    FROM sessions
                    WHERE id = %s
                    """,
                    (session_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return Session(
            session_id=row[0],
            conversation_id=row[1],
            created_at=row[2],
            last_active_at=row[3],
            revoked_at=row[4],
        )

    def update_last_active(
        self,
        session_id: str,
        last_active_at: datetime,
    ) -> bool:
        """
        Update the last activity timestamp.

        Returns:
            True if the session exists and was updated.
            False otherwise.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    UPDATE sessions
                    SET last_active_at = %s
                    WHERE id = %s
                      AND revoked_at IS NULL
                    """,
                    (
                        last_active_at,
                        session_id,
                    ),
                )

                return cursor.rowcount > 0

    def revoke(
        self,
        session_id: str,
        revoked_at: datetime,
    ) -> bool:
        """
        Explicitly revoke a session.

        Revocation is permanent unless a future feature
        explicitly introduces session restoration.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    UPDATE sessions
                    SET revoked_at = %s
                    WHERE id = %s
                      AND revoked_at IS NULL
                    """,
                    (
                        revoked_at,
                        session_id,
                    ),
                )

                return cursor.rowcount > 0