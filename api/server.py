"""
ROLE:
Creates and activates the FastAPI application.

Responsibilities:
    - Instantiate the FastAPI application.
    - Configure API metadata.
    - Register the application's routes.

This module does NOT contain:
    - AI logic
    - session logic
    - database logic
    - RAG logic
    - LLM logic
"""

from fastapi import FastAPI

from api.routes import router

# ------------------------------------------------------------------
# FASTAPI APPLICATION
# ------------------------------------------------------------------

app = FastAPI(
    title="Local AI Agent API",
    description=(
        "REST API for the Local AI Agent with "
        "RAG and persistent conversation sessions."
    ),
    version="1.0.0",
)


# ------------------------------------------------------------------
# ROUTE REGISTRATION
# ------------------------------------------------------------------

app.include_router(router)