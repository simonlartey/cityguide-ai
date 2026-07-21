from typing import Any

from app.models.conversation_message import MessageRole
from app.models.search_intent import SearchIntent
from app.models.search_session import SearchSession
from app.repositories.search_session import SearchSessionRepository


class ConversationManager:
    """Create and retrieve search conversation sessions."""

    def __init__(
        self,
        session_repository: SearchSessionRepository,
    ) -> None:
        self.session_repository = session_repository

    def start_session(
        self,
        original_query: str,
        intent: SearchIntent,
        places: list[dict[str, Any]],
        ranked_places: list[dict[str, Any]],
    ) -> SearchSession:
        session = SearchSession(
            original_query=original_query,
            intent=intent,
            places=places,
            ranked_places=ranked_places,
        )

        session.add_message(
            role=MessageRole.USER,
            content=original_query,
        )

        self.session_repository.save(session)

        return session

    def get_session(
        self,
        session_id: str,
    ) -> SearchSession | None:
        return self.session_repository.get(session_id)
