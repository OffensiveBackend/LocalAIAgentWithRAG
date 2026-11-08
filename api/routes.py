"""
ROLE:
HTTP API routes for the Local AI Agent.

Responsibilities:
    - Expose REST endpoints.
    - Create and revoke persistent sessions.
    - Resolve session IDs through SessionManager.
    - Pass requests to ChatEngine.
    - Keep HTTP concerns separate from AI and persistence logic.

Architecture:

    Client
       │
       ▼
    FastAPI
       │
       ▼
    routes.py
       │
       ├── SessionManager ──► PostgreSQL
       │
       └── ChatEngine
              │
              ├── RAG
              └── LLM
"""

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from api.schemas import (
    ChatRequest,
    ChatResponse,
    SessionResponse,
)
from api.session_manager import SessionManager
from chat.chat_engine import ChatEngine

# ------------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------------

router = APIRouter()


# ------------------------------------------------------------------
# SHARED APPLICATION SERVICES
# ------------------------------------------------------------------
#
# These are application-level services.
#
# IMPORTANT:
# Creating one ChatEngine here does NOT create one conversation.
# ChatEngine is stateless with respect to user sessions.
#
# SessionManager resolves each session_id to its persistent
# ConversationHistory.
# ------------------------------------------------------------------

session_manager = SessionManager()
chat_engine = ChatEngine()


# ------------------------------------------------------------------
# HEALTH / ROOT
# ------------------------------------------------------------------

@router.get("/")
def root():
    """
    Basic API availability endpoint.
    """

    return {
        "message": "Local AI Agent API is running."
    }


@router.get("/health")
def health():
    """
    Health-check endpoint.

    Currently verifies application availability.
    """

    return {
        "status": "healthy"
    }


# ------------------------------------------------------------------
# SESSION MANAGEMENT
# ------------------------------------------------------------------

@router.post(
    "/sessions",
    response_model=SessionResponse,
)
def create_session():
    """
    Create a new persistent session.

    SessionManager creates:
        1. A conversation in PostgreSQL.
        2. A session linked to that conversation.

    Returns:
        A persistent session ID.
    """

    session_id = session_manager.create_session()

    return SessionResponse(
        session_id=session_id
    )


@router.delete(
    "/sessions/{session_id}"
)
def delete_session(session_id: str):
    """
    Explicitly revoke a persistent session.

    Revoking the session does not delete its conversation history.
    """

    deleted = session_manager.delete_session(
        session_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "message": "Session revoked.",
        "session_id": session_id,
    }


# ------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):
    """
    Process one user question.

    Flow:

        HTTP request
            ↓
        session_id
            ↓
        SessionManager
            ↓
        PostgreSQL
            ↓
        ConversationHistory
            ↓
        ChatEngine
            ↓
        RAG + LLM
            ↓
        response
            ↓
        HTTP response

    ChatEngine.ask() is synchronous, potentially blocking work.
    Therefore it is executed outside FastAPI's event loop.
    """

    # --------------------------------------------------------------
    # Resolve the persistent session.
    # --------------------------------------------------------------

    try:

        history = session_manager.get_session(
            request.session_id
        )

    except KeyError:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    # --------------------------------------------------------------
    # Execute the synchronous AI pipeline outside the event loop.
    # --------------------------------------------------------------

    response = await run_in_threadpool(
        chat_engine.ask,
        # ChatEngine.askLLMdirectly,
        request.question,
        history,
    )

    # --------------------------------------------------------------
    # Return structured API response.
    # --------------------------------------------------------------

    return ChatResponse(
        session_id=request.session_id,
        answer=response,
    )