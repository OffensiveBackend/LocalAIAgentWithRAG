from chat.conversation_history import ConversationHistory
from chat.llm import chain
from knowledge.formatter import format_documents
from knowledge.knowledge_services import search


class ChatEngine:
    """
    Core AI service.

    The ChatEngine is deliberately independent of session management.

    Responsibilities:
        - retrieve knowledge
        - format retrieved documents
        - invoke the LLM
        - use supplied conversation history
        - return the AI response

    It does NOT decide:
        - which user is making the request
        - how sessions are identified
        - where sessions are stored
        - how HTTP requests are handled
    """
    
    # Approach one.
    def ask(
        self,
        query_from_user: str,
        history: ConversationHistory,
    ) -> str:

        # --------------------------------------------------------------
        # Store user message.
        #
        # ConversationHistory now persists this message in PostgreSQL.
        # --------------------------------------------------------------

        history.add_user_message(
            query_from_user
        )

        # --------------------------------------------------------------
        # Retrieve THIS conversation's history.
        # --------------------------------------------------------------

        formatted_conversation_history = (
            history.context()
        )

        # --------------------------------------------------------------
        # RAG retrieval.
        # --------------------------------------------------------------

        retrieved_documents = search(
            query_from_user
        )

        # --------------------------------------------------------------
        # Format retrieved documents for the LLM.
        # --------------------------------------------------------------

        formatted_retrieved_context = format_documents(
            retrieved_documents
        )

        # --------------------------------------------------------------
        # Invoke LLM.
        # --------------------------------------------------------------

        response_from_ai = chain.invoke(
            {
                "reviews": formatted_retrieved_context,
                "conversation_history":
                    formatted_conversation_history,
                "query_from_user":
                    query_from_user,
            }
        )

        # --------------------------------------------------------------
        # Persist assistant response.
        # --------------------------------------------------------------

        history.add_ai_message(
            response_from_ai
        )

        return response_from_ai

    # Approach two.
    def askLLMdirectly(
        self, 
        query_from_user: str,
        history: ConversationHistory,
        ) -> str:
        
        from chat.ask_LLM_directly import chain
        
        history.add_user_message(query_from_user)
        
        formatted_conversation_history = (history.context())
        
        # talk to an LLM    
        response_from_ai = chain.invoke(
                    {
                        "conversation_history":
                            formatted_conversation_history,
                        "query_from_user":
                            query_from_user,
                    }
                )
        
        history.add_ai_message(response_from_ai)
        
        return response_from_ai
        
        # ARCHITECTURE:
        # user -> prompt -> langChain -> Ollama -> llama(model) -> response.

    # ------------------------------------------------------------------
    # CLI INTERFACE
    # ------------------------------------------------------------------

    def start(self):
        """
        Runs a standalone CLI session.

        The CLI remains intentionally independent from FastAPI.

        A temporary in-process ConversationHistory is used because the
        CLI is currently a standalone interface.
        """

        # ---------------------------------------------------------------
        # CLI-only local history.
        #
        # This preserves existing CLI behaviour without forcing the CLI
        # through the HTTP session architecture yet.
        # ---------------------------------------------------------------

        history = ConversationHistory(
            conversation_id=self._create_cli_conversation()
        )

        quitting = [
            "q",
            "shutdown",
            "power off",
            "quit",
            "exit",
            "out",
            "deactivate",
        ]

        while True:

            print("\n\n" + "-" * 159)

            query_from_user = input(
                "Ask your question (q to quit): "
            )

            print("\n\n")

            if query_from_user.lower() in quitting:
                break

            response_from_ai = self.ask(
                query_from_user,
                history,
            )

            print(response_from_ai)
            
    
    # ====================================
    # CLI Exclusive ConversationHistory
    # ====================================
    
    def _create_cli_conversation(self) -> str:
        """
        Create a conversation specifically for the standalone CLI.

        This keeps the CLI compatible with the new persistent
        ConversationHistory model.
        """

        from datetime import datetime, timezone
        from uuid import uuid4

        from persistence.conversation_service.repository import (
            ConversationRepository,
        )

        conversation_id = str(uuid4())

        ConversationRepository().create_conversation(
            conversation_id=conversation_id,
            created_at=datetime.now(timezone.utc),
        )

        return conversation_id