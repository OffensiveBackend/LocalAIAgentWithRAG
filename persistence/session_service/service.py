from datetime import datetime, timezone
from uuid import uuid4

from persistence.session_service.cache import SessionCache
from persistence.session_service.models import Session
from persistence.session_service.repository import SessionRepository


class SessionService:
    """
    Application/service layer responsible for session lifecycle.

    Responsibilities:
        - Create sessions.
        - Retrieve sessions.
        - Validate sessions.
        - Recover sessions after process/server restarts.
        - Update session activity.
        - Explicitly revoke sessions.

    PostgreSQL:
        Durable source of truth.

    Redis:
        Fast cache/accelerator.
    """

    def __init__(
        self,
        repository: SessionRepository | None = None,
        cache: SessionCache | None = None,
    ):
        self.repository = repository or SessionRepository()
        self.cache = cache or SessionCache()

    def create_session(
        self,
        conversation_id: str,
    ) -> Session:
        """
        Create and durably persist a new session.
        """

        session_id = str(uuid4())
        now = self._now()

        session = self.repository.create(
            session_id=session_id,
            conversation_id=conversation_id,
            created_at=now,
        )

        # Cache only after PostgreSQL has successfully persisted
        # the session.
        self.cache.set(
            session_id=session.session_id,
            conversation_id=session.conversation_id,
        )

        return session

    def get_session(
        self,
        session_id: str,
    ) -> Session | None:
        """
        Retrieve a session.

        Lookup strategy:

            1. PostgreSQL is authoritative.
            2. Redis is used only as an accelerator for
               session -> conversation mapping.

        This implementation deliberately retrieves the durable
        session record to ensure validity is never determined
        solely by Redis.
        """

        session = self.repository.get(session_id)

        if session is None:
            return None

        if not session.is_valid:
            return None

        # Refresh the Redis cache if it was lost because of
        # a Redis restart, cache flush, etc.
        self.cache.set(
            session_id=session.session_id,
            conversation_id=session.conversation_id,
        )

        return session

    def validate_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Determine whether a session is currently valid.

        Validity depends on the durable PostgreSQL record,
        not Redis.
        """

        session = self.repository.get(session_id)

        if session is None:
            return False

        return session.is_valid

    def get_conversation_id(
        self,
        session_id: str,
    ) -> str | None:
        """
        Resolve a valid session to its conversation.

        Redis is checked first for speed, but PostgreSQL remains
        authoritative when the cache misses.
        """

        session = self.repository.get(session_id)

        if session is None or not session.is_valid:
            return None

        cached_conversation_id = self.cache.get(session_id)

        if cached_conversation_id is not None:
            return cached_conversation_id

        # Redis cache miss / Redis restart / cache flush.
        # Reconstruct the cache from PostgreSQL.
        self.cache.set(
            session_id=session.session_id,
            conversation_id=session.conversation_id,
        )

        return session.conversation_id

    def touch_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Update the session's activity timestamp.

        This does NOT expire the session.
        """

        session = self.repository.get(session_id)

        if session is None or not session.is_valid:
            return False

        return self.repository.update_last_active(
            session_id=session_id,
            last_active_at=self._now(),
        )

    def revoke_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Explicitly invalidate a session.

        PostgreSQL records the permanent revocation.
        Redis cache is removed afterward.
        """

        revoked = self.repository.revoke(
            session_id=session_id,
            revoked_at=self._now(),
        )

        if revoked:
            self.cache.delete(session_id)

        return revoked

    @staticmethod
    def _now() -> datetime:
        """
        Generate timezone-aware UTC timestamps.
        """

        return datetime.now(timezone.utc)