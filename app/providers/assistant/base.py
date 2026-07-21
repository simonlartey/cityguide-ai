from abc import ABC, abstractmethod
from typing import Any

from app.models.search_intent import SearchIntent


class AssistantProvider(ABC):
    """Interface for AI-assisted search interpretation and responses."""

    @abstractmethod
    def parse_search_intent(
        self,
        query: str,
    ) -> SearchIntent:
        """Convert a natural-language query into structured search intent."""
        raise NotImplementedError

    @abstractmethod
    def generate_search_response(
        self,
        query: str,
        places: list[dict[str, Any]],
    ) -> str:
        """Generate a grounded response using retrieved place results."""
        raise NotImplementedError
