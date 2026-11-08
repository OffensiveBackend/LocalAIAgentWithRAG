"""
ROLE:
Durable conversation-history adapter.

ConversationHistory represents the messages belonging to ONE persistent
conversation.

PostgreSQL is the source of truth.

The class may maintain an in-memory copy of the messages for the lifetime
of this Python object, but that memory is NOT the authoritative storage.
"""

from datetime import datetime, timezone
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage

from persistence.conversation_service.repository import (
    ConversationRepository,
)


class ConversationHistory:

    def __init__(
        self,
        conversation_id: str,
        repository: ConversationRepository | None = None,
    ):
        """
        Parameters
        ----------
        conversation_id:
            UUID identifying the persistent conversation.

        repository:
            PostgreSQL repository used to load and persist messages.
        """

        self.conversation_id = conversation_id

        self._repository = repository or ConversationRepository()

        # Local working copy.
        #
        # PostgreSQL remains the durable source of truth.
        self._history = []

        self._load_history()

    # ------------------------------------------------------------------
    # LOAD PERSISTED HISTORY
    # ------------------------------------------------------------------

    def _load_history(self) -> None:
        """
        Load the persistent conversation from PostgreSQL.
        """

        messages = self._repository.get_messages(
            self.conversation_id
        )

        for message in messages:

            if message.role == "user":

                self._history.append(
                    HumanMessage(
                        content=message.content
                    )
                )

            elif message.role == "assistant":

                self._history.append(
                    AIMessage(
                        content=message.content
                    )
                )

            # System messages are intentionally ignored by the current
            # ChatEngine history representation.
            #
            # They remain persisted in PostgreSQL and can be supported
            # here when system-message handling is introduced.

    # ------------------------------------------------------------------
    # ADD USER MESSAGE
    # ------------------------------------------------------------------

    def add_user_message(
        self,
        message: str,
    ) -> None:
        """
        Persist and locally record a user message.
        """

        now = datetime.now(timezone.utc)

        self._repository.add_message(
            message_id=str(uuid4()),
            conversation_id=self.conversation_id,
            role="user",
            content=message,
            created_at=now,
        )

        self._history.append(
            HumanMessage(
                content=message
            )
        )

    # ------------------------------------------------------------------
    # ADD AI MESSAGE
    # ------------------------------------------------------------------

    def add_ai_message(
        self,
        message: str,
    ) -> None:
        """
        Persist and locally record an assistant response.
        """

        now = datetime.now(timezone.utc)

        self._repository.add_message(
            message_id=str(uuid4()),
            conversation_id=self.conversation_id,
            role="assistant",
            content=message,
            created_at=now,
        )

        self._history.append(
            AIMessage(
                content=message
            )
        )

    # ------------------------------------------------------------------
    # READ HISTORY
    # ------------------------------------------------------------------

    def messages(self):
        """
        Return LangChain message objects belonging to this conversation.
        """

        return self._history

    def formatted_history(self) -> str:
        """
        Format the conversation for prompt injection.

        Example:

        User:
        What time do you close?

        Assistant:
        We close at 11 PM.
        """

        conversation = []

        for message in self._history:

            if isinstance(message, HumanMessage):

                conversation.append(
                    f"User:\n{message.content}"
                )

            elif isinstance(message, AIMessage):

                conversation.append(
                    f"Assistant:\n{message.content}"
                )

        return "\n\n".join(conversation)

    def context(self) -> str:
        """
        Abstraction layer around formatted_history().
        """

        return self.formatted_history()

    # ------------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Clear only the local working representation.

        Persistent database history is intentionally NOT deleted here.

        Permanent conversation deletion requires an explicit persistence
        operation and is therefore outside this method's responsibility.
        """

        self._history.clear()

    def __len__(self):
        return len(self._history)

    def is_empty(self) -> bool:
        return len(self._history) == 0