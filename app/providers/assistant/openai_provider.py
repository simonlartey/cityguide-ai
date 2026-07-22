import json
from typing import Any

from openai import OpenAI

from app.models.search_intent import SearchIntent
from app.providers.assistant.base import AssistantProvider


ASSISTANT_PLACE_FIELDS = (
    "id",
    "name",
    "category",
    "address",
    "rating",
    "review_count",
    "price_level",
    "open_now",
    "distance_miles",
    "hours_text",
    "description",
    "tags",
    "match_reasons",
)


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

    @staticmethod
    def _grounding_instructions() -> str:
        return (
            "Use only facts explicitly present in the supplied place "
            "results. Never infer an attribute from a place category, "
            "business name, rating, popularity, or price. In particular, "
            "do not infer quietness, noise level, study suitability, "
            "Wi-Fi, electrical outlets, atmosphere, safety, "
            "accessibility, official hotel star classification, or any "
            "other missing amenity or quality. A Google review rating is "
            "not an official hotel star classification. If a requested "
            "constraint cannot be verified from the supplied fields, say "
            "so clearly. Recommend no more than four places unless the "
            "user explicitly requests more. Be concise and do not repeat "
            "phone numbers, websites, map links, or raw metadata."
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

        place_context = self._build_place_context(
            places
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Answer the user's local-search request. "
                f"{self._grounding_instructions()}"
            ),
            input=(
                f"User request:\n{query}\n\n"
                "Retrieved place results:\n"
                f"{json.dumps(place_context, ensure_ascii=False)}"
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

        place_context = self._build_place_context(
            places
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Continue the current local-search conversation using "
                "the existing result set. Do not perform or imply a new "
                "place search. "
                f"{self._grounding_instructions()}"
            ),
            input=(
                "Conversation history:\n"
                f"{json.dumps(history, ensure_ascii=False)}\n\n"
                "Retrieved place results:\n"
                f"{json.dumps(place_context, ensure_ascii=False)}\n\n"
                f"Latest user message:\n{message}"
            ),
        )

        return self._extract_output_text(response)

    @classmethod
    def _build_place_context(
        cls,
        places: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Return only factual fields needed by the assistant."""

        return [
            cls._compact_place(place)
            for place in places
            if isinstance(place, dict)
        ]

    @staticmethod
    def _compact_place(
        place: dict[str, Any],
    ) -> dict[str, Any]:
        """Remove fields that are unnecessary for assistant reasoning."""

        compact_place = {}

        for field in ASSISTANT_PLACE_FIELDS:
            value = place.get(field)

            if value is None:
                continue

            if isinstance(value, str):
                normalized_value = value.strip()

                if not normalized_value:
                    continue

                compact_place[field] = normalized_value
                continue

            if isinstance(value, (list, tuple)):
                normalized_items = [
                    item.strip()
                    for item in value
                    if isinstance(item, str) and item.strip()
                ]

                if normalized_items:
                    compact_place[field] = normalized_items

                continue

            compact_place[field] = value

        return compact_place

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
