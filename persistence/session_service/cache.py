"""
ROLE:
    Redis interaction for fast active-session lookups.
"""
import os

import redis


class SessionCache:
    """
    Redis-backed cache for active session state.
    
    Redis is an accelaerator only.
    
    Important:
            - No expiration is configured.
            - Redis  does not determine whether a session permanently exists.
            - PostgreeSQL remains the source of truth.
    """
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            raise RuntimeError(
                "REDIS_URL environment variable is not configured."
            )
            
        self.client = redis.Redis.from_url(
            redis_url,
            decode_responses = True,
        )
        
    def set(self, session_id: str, conversation_id: str,) -> None:
        """
        Cache the relation between a session and conversation.
        
        No TTL is supplied bcoz the application does not use
        expiration to determine session validity.
        """
        
        self.client.set(
            self._key(session_id),
            conversation_id,
        )
        
    def get(self, session_id: str,) -> str | None:
        """
        Retrieve the conversation ID association with a cahed session.
        
        Returns:
        conversation_id if cached.
        None if not cached.
        """
        
        return self.client.get(
            self._key(session_id)
        )
        
    def delete(self, session_id: str,) -> None:
        """
        Remove the session from Redis.
        
        This does not delete the durable PostgreeSQL session.
        """
        
        self.client.delete(
            self._key(session_id)
        )
        
    @staticmethod
    def _key(session_id: str) -> str:
        """
        Namespace Redis keys belonging to the session service.
        """
        
        return f"session: {session_id}"
        
        
        