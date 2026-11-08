# gui/api/client.py

"""
ROLE:
HTTP boundary between the desktop GUI and FastAPI.

The GUI communicates with the backend exclusively through this class.

The client owns one reusable HTTP connection pool instead of creating
a new HTTP client for every request.
"""

import httpx


class APIClient:
    """
    Client for the Local AI Agent REST API.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/")

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(
                timeout,
                connect=10.0,
            ),
        )

    def create_session(self) -> str:
        """
        Create a persistent chat session.

        Returns
        -------
        str
            Session UUID.

        Raises
        ------
        RuntimeError
            If the backend cannot create the session.
        """

        try:
            response = self._client.post(
                "/sessions"
            )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Unable to create chat session: {exc}"
            ) from exc

        data = response.json()

        session_id = data.get("session_id")

        if not session_id:
            raise RuntimeError(
                "API returned an invalid session response."
            )

        return session_id

    def send_message(
        self,
        session_id: str,
        question: str,
    ) -> str:
        """
        Send a question to the AI backend.

        Parameters
        ----------
        session_id:
            Persistent conversation session.

        question:
            User's question.

        Returns
        -------
        str
            Assistant response.
        """

        if not session_id:
            raise ValueError(
                "session_id cannot be empty."
            )

        if not question.strip():
            raise ValueError(
                "question cannot be empty."
            )

        try:
            response = self._client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "question": question,
                },
            )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Unable to send message: {exc}"
            ) from exc

        data = response.json()

        answer = data.get("answer")

        if answer is None:
            raise RuntimeError(
                "API returned an invalid chat response."
            )

        return answer

    def close(self) -> None:
        """
        Close the underlying HTTP connection pool.
        """

        self._client.close()