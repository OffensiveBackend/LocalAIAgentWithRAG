"""
ROLE:
    Responsible for establishing PostgreSQL connections.

Architecture:

    Session Service ─────┐
                         │
                         ▼
                    PostgreSQL
                         ▲
                         │
    Conversation Service ┘

This module centralizes PostgreSQL connection creation so that
repositories do not need to manage DATABASE_URL themselves.

PostgreSQL is the durable source of truth for:

    - sessions
    - conversations
    - messages
"""

import os

import psycopg
from dotenv import load_dotenv
from psycopg import Connection


def get_connection() -> Connection:
    """
    Create and return a PostgreSQL database connection.

    Returns
    -------
    Connection
        An active psycopg PostgreSQL connection.

    Raises
    ------
    RuntimeError
        If DATABASE_URL has not been configured.
    """
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    return psycopg.connect(database_url)