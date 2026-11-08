"""
3. persistence/database/

This is the infrastructure underneath both services.
The shared database infrastructure.

database/
├── connection.py
└── schema.sql

connection.py

Responsible for establishing PostgreSQL connections / connection pooling.

Session Service ─────┐
                     ├── PostgreSQL
Conversation Service ┘

schema.sql

Defines the durable relational structure:

users
  │
  ├── conversations
  │       │
  │       └── messages
  │
  └── sessions
          │
          └── conversation_id
"""