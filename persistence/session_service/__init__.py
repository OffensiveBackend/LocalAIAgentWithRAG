"""
1. persistence/session_service/

Responsibility: Manage the lifecycle and identity of sessions.

session_service/
├── models.py
├── repository.py
├── service.py
└── cache.py
models.py — Defines the session data structure: session_id, user_id, conversation_id, timestamps, revocation state, etc.
repository.py — PostgreSQL persistence operations for sessions: create, retrieve, delete/revoke, etc.
service.py — Business logic: create a session, validate it, recover it after restart, associate it with a conversation.
cache.py — Redis interaction for fast active-session lookups.

The important hierarchy is:

SessionService
    │
    ├── SessionRepository → PostgreSQL
    │
    └── SessionCache      → Redis
"""