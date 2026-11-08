"""
ROLE:
    Higher-level operations such as creating conversations, adding messages, retrieving history.
"""
from datetime import datetime, timezone
from uuid import uuid4

from persistence.conversation_service.models import (
    Conversation,
    Message,
)
from persistence.conversation_service.repository import (
    ConversationRepository,
)


class ConversationService:
    """
    Application/service layer for durable conversations.

    Responsibilities:
        - Create conversations.
        - Retrieve conversations.
        - Store user messages.
        - Store assistant messages.
        - Retrieve persistent conversation history.

    Session responsibility intentionally remains outside this service.

    Session Service answers:
        "Which conversation is this session currently using?"

    Conversation Service answers:
        "What has happened inside that conversation?"
    """

    def __init__(
        self,
        repository: ConversationRepository | None = None,
    ):
        self.repository = repository or ConversationRepository()

    def create_conversation(self) -> Conversation:
        """
        Create a new persistent conversation.
        """

        conversation_id = str(uuid4())
        now = self._now()

        return self.repository.create_conversation(
            conversation_id=conversation_id,
            created_at=now,
        )

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        """
        Retrieve a persistent conversation.
        """

        return self.repository.get_conversation(
            conversation_id
        )

    def add_user_message(
        self,
        conversation_id: str,
        content: str,
    ) -> Message:
        """
        Persist a message originating from the user.
        """

        return self._add_message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

    def add_assistant_message(
        self,
        conversation_id: str,
        content: str,
    ) -> Message:
        """
        Persist a message originating from the assistant.
        """

        return self._add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
        )

    def get_history(
        self,
        conversation_id: str,
    ) -> list[Message]:
        """
        Retrieve the complete durable message history
        for a conversation.
        """

        return self.repository.get_messages(
            conversation_id
        )

    def _add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> Message:
        """
        Internal message creation operation.
        """

        conversation = self.repository.get_conversation(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                f"Conversation '{conversation_id}' does not exist."
            )

        message_id = str(uuid4())
        now = self._now()

        return self.repository.add_message(
            message_id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=now,
        )

    @staticmethod
    def _now() -> datetime:
        """
        Generate timezone-aware UTC timestamps.
        """

        return datetime.now(timezone.utc)
