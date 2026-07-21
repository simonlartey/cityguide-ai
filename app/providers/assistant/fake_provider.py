from typing import Any

from app.models.search_intent import SearchIntent
from app.providers.assistant.base import AssistantProvider


class FakeAssistantProvider(AssistantProvider):
    """Deterministic assistant provider for tests and local fallback."""

    def parse_search_intent(
        self,
        query: str,
    ) -> SearchIntent:
        normalized_query = query.strip()

        return SearchIntent(
            original_query=query,
            search_query=normalized_query,
        )

    def generate_search_response(
        self,
        query: str,
        places: list[dict[str, Any]],
    ) -> str:
        if not places:
            return (
                "I could not find any places matching your request."
            )

        place_names = [
            place.get("name")
            for place in places
            if place.get("name")
        ]

        if not place_names:
            return (
                f"I found {len(places)} matching places, "
                "but their names are unavailable."
            )

        if len(place_names) == 1:
            return f"I found one option: {place_names[0]}."

        return (
            f"I found {len(place_names)} options: "
            f"{', '.join(place_names)}."
        )
