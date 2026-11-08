-- ROLE:
        -- Defines the durable relational structure:
        -- ***
--users
--   │
--   ├── conversations
--   │       │
--   │       └── messages
--   │
--   └── sessions
--           │
--           └── conversation_id 
        --   ***
-- ============================================================
-- LocalAIAgentWithRAG
-- Persistence Layer Database Schema
--
-- PostgreSQL is the durable source of truth.
--
-- Relationships:
--
-- Session
--    │
--    └──────────────► Conversation
--                         │
--                         └──────────────► Messages
--
-- A session represents the user's current interaction context.
-- A conversation represents the persistent historical record.
-- ============================================================


-- ============================================================
-- CONVERSATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


-- ============================================================
-- SESSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,

    conversation_id UUID NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,
    last_active_at TIMESTAMPTZ NOT NULL,

    revoked_at TIMESTAMPTZ NULL,

    CONSTRAINT fk_sessions_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE RESTRICT
);


-- ============================================================
-- MESSAGES
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,

    conversation_id UUID NOT NULL,

    role VARCHAR(20) NOT NULL,

    content TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    CONSTRAINT valid_message_role
        CHECK (
            role IN (
                'user',
                'assistant',
                'system'
            )
        )
);


-- ============================================================
-- INDEXES
-- ============================================================

-- Fast lookup of a session's conversation.
CREATE INDEX IF NOT EXISTS idx_sessions_conversation_id
    ON sessions(conversation_id);


-- Fast retrieval of active/non-revoked sessions.
CREATE INDEX IF NOT EXISTS idx_sessions_revoked_at
    ON sessions(revoked_at);


-- Fast retrieval of messages belonging to a conversation.
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);


-- Supports chronological conversation-history retrieval.
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created_at
    ON messages(conversation_id, created_at);


-- Supports ordering/filtering conversations by recent activity.
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations(updated_at);