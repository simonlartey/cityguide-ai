from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.models.conversation_message import (
    ConversationMessage,
    MessageRole,
)
from app.models.search_intent import SearchIntent


@dataclass
class SearchSession:
    original_query: str
    intent: SearchIntent
    places: list[dict[str, Any]] = field(default_factory=list)
    ranked_places: list[dict[str, Any]] = field(default_factory=list)
    conversation_history: list[ConversationMessage] = field(
        default_factory=list
    )
    session_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    def add_message(
        self,
        role: MessageRole,
        content: str,
    ) -> None:
        self.conversation_history.append(
            ConversationMessage(
                role=role,
                content=content,
            )
        )
