"""
ROLE:
     Defines the session data structure: session_id, user_id, conversation_id, timestamps, revocation state, etc.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen = True)
class Session:
        """
        Represents a durable user interactions sessions.
        
        A session remains valid indefinately unless explicitly revoked.
        """
        
        session_id: str
        conversation_id: str
        created_at: datetime
        last_active_at: datetime
        revoked_at: datetime | None = None
        
        @property
        def is_valid(self) -> bool:
                """
                A session is valid when it has not been explicitly revoked.
                """
                return self.revoked_at is None
                