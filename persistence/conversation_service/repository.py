"""
ROLE:
PostgreSQL operations for conversations/messages.
"""

from datetime import datetime

from persistence.conversation_service.models import (
    Conversation,
    Message,
)
from persistence.database.connection import get_connection


class ConversationRepository:
    """
    PostgreSQL persistence layer for conversations and messages.

    PostgreSQL is the durable source of truth.

    Responsibilities:
        - Persist conversations.
        - Retrieve conversations.
        - Persist messages.
        - Retrieve conversation history.
    """

    def create_conversation(
        self,
        conversation_id: str,
        created_at: datetime,
    ) -> Conversation:
        """
        Persist a new conversation.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    INSERT INTO conversations (
                        id,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        conversation_id,
                        created_at,
                        created_at,
                    ),
                )

        return Conversation(
            conversation_id=conversation_id,
            created_at=created_at,
            updated_at=created_at,
        )

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        """
        Retrieve a conversation by ID.

        Returns:
            Conversation if it exists.
            None otherwise.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    SELECT
                        id,
                        created_at,
                        updated_at
                    FROM conversations
                    WHERE id = %s
                    """,
                    (conversation_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return Conversation(
            conversation_id=row[0],
            created_at=row[1],
            updated_at=row[2],
        )

    def add_message(
        self,
        message_id: str,
        conversation_id: str,
        role: str,
        content: str,
        created_at: datetime,
    ) -> Message:
        """
        Persist one message and update the conversation's
        last-modified timestamp.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    INSERT INTO messages (
                        id,
                        conversation_id,
                        role,
                        content,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        message_id,
                        conversation_id,
                        role,
                        content,
                        created_at,
                    ),
                )

                cursor.execute(
                    """
                    UPDATE conversations
                    SET updated_at = %s
                    WHERE id = %s
                    """,
                    (
                        created_at,
                        conversation_id,
                    ),
                )

        return Message(
            message_id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=created_at,
        )

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[Message]:
        """
        Retrieve all messages belonging to a conversation
        in chronological order.
        """

        with (get_connection() as connection,
            connection.cursor() as cursor):
                cursor.execute(
                    """
                    SELECT
                        id,
                        conversation_id,
                        role,
                        content,
                        created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC, id ASC
                    """,
                    (conversation_id,),
                )

                rows = cursor.fetchall()

        return [
            Message(
                message_id=row[0],
                conversation_id=row[1],
                role=row[2],
                content=row[3],
                created_at=row[4],
            )
            for row in rows
        ]