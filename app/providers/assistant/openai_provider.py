import json
from typing import Any

from openai import OpenAI

from app.models.search_intent import SearchIntent
from app.providers.assistant.base import AssistantProvider


class OpenAIAssistantProvider(AssistantProvider):
    """OpenAI-backed assistant provider for grounded place search."""

    def __init__(
        self,
        api_key: str,
        model: str,
        client: Any | None = None,
    ):
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for the OpenAI provider"
            )

        if not model:
            raise ValueError(
                "ASSISTANT_MODEL is required for the OpenAI provider"
            )

        self.client = client or OpenAI(
            api_key=api_key,
        )
        self.model = model

    def parse_search_intent(
        self,
        query: str,
    ) -> SearchIntent:
        """Convert a natural-language query into structured search intent."""

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Extract structured local-search intent from the user's "
                "request. Return only valid JSON with these keys: "
                "search_query, category, cuisine, price_levels, "
                "preferences, max_distance_meters, open_now. "
                "Use null for unknown scalar values and empty arrays for "
                "unknown list values. Preserve Google Places price-level "
                "values when applicable."
            ),
            input=query,
        )

        output_text = self._extract_output_text(response)
        payload = json.loads(output_text)

        if not isinstance(payload, dict):
            raise ValueError(
                "OpenAI intent response must be a JSON object"
            )

        price_levels = payload.get("price_levels")
        preferences = payload.get("preferences")

        if not isinstance(price_levels, list):
            price_levels = []

        if not isinstance(preferences, list):
            preferences = []

        search_query = payload.get("search_query")

        if not isinstance(search_query, str):
            search_query = ""

        return SearchIntent(
            original_query=query,
            search_query=search_query.strip() or query.strip(),
            category=self._optional_string(
                payload.get("category")
            ),
            cuisine=self._optional_string(
                payload.get("cuisine")
            ),
            price_levels=tuple(
                value
                for value in price_levels
                if isinstance(value, str)
            ),
            preferences=tuple(
                value
                for value in preferences
                if isinstance(value, str)
            ),
            max_distance_meters=self._optional_integer(
                payload.get("max_distance_meters")
            ),
            open_now=self._optional_boolean(
                payload.get("open_now")
            ),
        )

    def generate_search_response(
        self,
        query: str,
        places: list[dict[str, Any]],
    ) -> str:
        """Generate a response using only retrieved place results."""

        if not places:
            return (
                "I could not find any places matching your request."
            )

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Answer the user's local-search request using only the "
                "supplied place results. Do not invent places, ratings, "
                "prices, addresses, opening hours, distances, or other "
                "facts. If the supplied data does not answer part of the "
                "request, say that clearly."
            ),
            input=(
                f"User request:\n{query}\n\n"
                "Retrieved place results:\n"
                f"{json.dumps(places, ensure_ascii=False)}"
            ),
        )

        return self._extract_output_text(response)

    def continue_conversation(
        self,
        history: list[dict],
        message: str,
        places: list[dict],
    ) -> str:
        """Continue a conversation using existing grounded results."""

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Continue the local-search conversation using only the "
                "supplied conversation history and place results. "
                "Do not invent place facts. If the requested information "
                "is unavailable in the supplied data, say so clearly."
            ),
            input=(
                "Conversation history:\n"
                f"{json.dumps(history, ensure_ascii=False)}\n\n"
                "Retrieved place results:\n"
                f"{json.dumps(places, ensure_ascii=False)}\n\n"
                f"Latest user message:\n{message}"
            ),
        )

        return self._extract_output_text(response)

    @staticmethod
    def _extract_output_text(response: Any) -> str:
        output_text = getattr(
            response,
            "output_text",
            None,
        )

        if not isinstance(output_text, str):
            raise ValueError(
                "OpenAI returned an invalid text response"
            )

        normalized_output = output_text.strip()

        if not normalized_output:
            raise ValueError(
                "OpenAI returned an empty response"
            )

        return normalized_output

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if not isinstance(value, str):
            return None

        normalized_value = value.strip()

        return normalized_value or None

    @staticmethod
    def _optional_integer(value: Any) -> int | None:
        if isinstance(value, bool):
            return None

        if isinstance(value, int):
            return value

        return None

    @staticmethod
    def _optional_boolean(value: Any) -> bool | None:
        if isinstance(value, bool):
            return value

        return None
