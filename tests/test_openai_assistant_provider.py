from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.providers.assistant.openai_provider import (
    OpenAIAssistantProvider,
)


def build_provider(output_text: str):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(
        output_text=output_text,
    )

    provider = OpenAIAssistantProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    return provider, client


def test_provider_requires_api_key():
    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is required",
    ):
        OpenAIAssistantProvider(
            api_key="",
            model="test-model",
        )


def test_provider_requires_model():
    with pytest.raises(
        ValueError,
        match="ASSISTANT_MODEL is required",
    ):
        OpenAIAssistantProvider(
            api_key="test-key",
            model="",
        )


def test_parse_search_intent_returns_structured_intent():
    provider, client = build_provider(
        """
        {
          "search_query": "African restaurant",
          "category": "restaurant",
          "cuisine": "African",
          "price_levels": ["PRICE_LEVEL_INEXPENSIVE"],
          "preferences": ["affordable"],
          "max_distance_meters": 1600,
          "open_now": true
        }
        """
    )

    intent = provider.parse_search_intent(
        "Find affordable African food nearby"
    )

    assert intent.original_query == (
        "Find affordable African food nearby"
    )
    assert intent.search_query == "African restaurant"
    assert intent.category == "restaurant"
    assert intent.cuisine == "African"
    assert intent.price_levels == (
        "PRICE_LEVEL_INEXPENSIVE",
    )
    assert intent.preferences == ("affordable",)
    assert intent.max_distance_meters == 1600
    assert intent.open_now is True

    client.responses.create.assert_called_once()


def test_parse_search_intent_uses_safe_defaults():
    provider, _ = build_provider("{}")

    intent = provider.parse_search_intent(" coffee ")

    assert intent.original_query == " coffee "
    assert intent.search_query == "coffee"
    assert intent.category is None
    assert intent.cuisine is None
    assert intent.price_levels == ()
    assert intent.preferences == ()
    assert intent.max_distance_meters is None
    assert intent.open_now is None


def test_parse_search_intent_rejects_non_object_json():
    provider, _ = build_provider("[]")

    with pytest.raises(
        ValueError,
        match="must be a JSON object",
    ):
        provider.parse_search_intent("coffee")


def test_parse_search_intent_normalizes_invalid_field_types():
    provider, _ = build_provider(
        """
        {
          "search_query": 123,
          "category": [],
          "cuisine": false,
          "price_levels": "cheap",
          "preferences": null,
          "max_distance_meters": "nearby",
          "open_now": "yes"
        }
        """
    )

    intent = provider.parse_search_intent(" coffee ")

    assert intent.search_query == "coffee"
    assert intent.category is None
    assert intent.cuisine is None
    assert intent.price_levels == ()
    assert intent.preferences == ()
    assert intent.max_distance_meters is None
    assert intent.open_now is None


def test_generate_search_response_uses_grounded_places():
    provider, client = build_provider(
        "Campus Cafe is the strongest match."
    )

    response = provider.generate_search_response(
        query="Find a quiet cafe",
        places=[
            {
                "name": "Campus Cafe",
                "rating": 4.7,
            }
        ],
    )

    assert response == "Campus Cafe is the strongest match."

    call = client.responses.create.call_args.kwargs

    assert call["model"] == "test-model"
    assert "Campus Cafe" in call["input"]
    assert "Do not invent" in call["instructions"]


def test_generate_search_response_handles_no_places_without_api_call():
    provider, client = build_provider(
        "This response should not be used."
    )

    response = provider.generate_search_response(
        query="Find a cafe",
        places=[],
    )

    assert response == (
        "I could not find any places matching your request."
    )

    client.responses.create.assert_not_called()


def test_continue_conversation_uses_history_and_places():
    provider, client = build_provider(
        "Campus Cafe has the higher rating."
    )

    response = provider.continue_conversation(
        history=[
            {
                "role": "user",
                "content": "Find quiet cafes",
            },
            {
                "role": "assistant",
                "content": "I found two options.",
            },
        ],
        message="Which one has the higher rating?",
        places=[
            {
                "name": "Campus Cafe",
                "rating": 4.7,
            }
        ],
    )

    assert response == "Campus Cafe has the higher rating."

    call = client.responses.create.call_args.kwargs

    assert "Find quiet cafes" in call["input"]
    assert "Which one has the higher rating?" in call["input"]
    assert "Campus Cafe" in call["input"]


def test_provider_rejects_empty_output_text():
    provider, _ = build_provider("   ")

    with pytest.raises(
        ValueError,
        match="OpenAI returned an empty response",
    ):
        provider.generate_search_response(
            query="Find a cafe",
            places=[
                {
                    "name": "Campus Cafe",
                }
            ],
        )


def test_provider_rejects_missing_output_text():
    client = Mock()
    client.responses.create.return_value = SimpleNamespace()

    provider = OpenAIAssistantProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    with pytest.raises(
        ValueError,
        match="OpenAI returned an invalid text response",
    ):
        provider.generate_search_response(
            query="Find a cafe",
            places=[
                {
                    "name": "Campus Cafe",
                }
            ],
        )
