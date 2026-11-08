"""
ROLE:
Defines the data contracts for the FastAPI API.

Responsibilities:
    - Validate incoming HTTP request data.
    - Define the structure of API responses.
    - Keep HTTP data contracts separate from business logic.

Pydantic models are used by FastAPI for:
    - validation
    - serialization
    - automatic OpenAPI documentation
"""

from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# SESSION
# ------------------------------------------------------------------

class SessionResponse(BaseModel):
    """
    Response returned when a persistent session is created.
    """

    session_id: str = Field(
        ...,
        description="Unique identifier of the persistent session.",
    )


# ------------------------------------------------------------------
# CHAT REQUEST
# ------------------------------------------------------------------

class ChatRequest(BaseModel):
    """
    Incoming chat request.

    The session_id identifies the persistent conversation context
    that should be used when processing the question.
    """

    session_id: str = Field(
        ...,
        description="Identifier of the persistent chat session.",
    )

    question: str = Field(
        ...,
        min_length=1,
        description="Question submitted by the user.",
    )


# ------------------------------------------------------------------
# CHAT RESPONSE
# ------------------------------------------------------------------

class ChatResponse(BaseModel):
    """
    Response returned after the AI processes a question.
    """

    session_id: str = Field(
        ...,
        description="Identifier of the session used for this request.",
    )

    answer: str = Field(
        ...,
        description="AI-generated response.",
    )