"""
2. persistence/conversation_service/

Responsibility: Manage durable conversations and their messages.

conversation_service/
├── models.py
├── repository.py
└── service.py
models.py — Conversation and message data structures.
repository.py — PostgreSQL operations for conversations/messages.
service.py — Higher-level operations such as creating conversations, adding messages, retrieving history.

Its relationship with sessions is:

Session Service
      │
      │ identifies active context
      ▼
Conversation Service
      │
      ├── Conversation
      └── Messages

They must not become one service.
"""