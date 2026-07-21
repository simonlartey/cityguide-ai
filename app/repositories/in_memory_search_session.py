from app.models.search_session import SearchSession
from app.repositories.search_session import SearchSessionRepository


class InMemorySearchSessionRepository(SearchSessionRepository):
    """Store search sessions in process memory."""

    def __init__(self) -> None:
        self._sessions: dict[str, SearchSession] = {}

    def save(self, session: SearchSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> SearchSession | None:
        return self._sessions.get(session_id)
