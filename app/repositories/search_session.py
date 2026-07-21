from abc import ABC, abstractmethod

from app.models.search_session import SearchSession


class SearchSessionRepository(ABC):
    """Interface for storing and retrieving search sessions."""

    @abstractmethod
    def save(self, session: SearchSession) -> None:
        """Store a new session or replace an existing session."""
        raise NotImplementedError

    @abstractmethod
    def get(self, session_id: str) -> SearchSession | None:
        """Return a session by ID, or None when it does not exist."""
        raise NotImplementedError
