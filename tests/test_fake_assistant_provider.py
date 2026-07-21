from app.providers.assistant.fake_provider import (
    FakeAssistantProvider,
)


def test_parse_search_intent_preserves_original_query():
    provider = FakeAssistantProvider()

    intent = provider.parse_search_intent(
        "  Find a quiet cafe  "
    )

    assert intent.original_query == "  Find a quiet cafe  "
    assert intent.search_query == "Find a quiet cafe"


def test_generate_response_for_no_results():
    provider = FakeAssistantProvider()

    response = provider.generate_search_response(
        query="Find a quiet cafe",
        places=[],
    )

    assert response == (
        "I could not find any places matching your request."
    )


def test_generate_response_for_one_named_place():
    provider = FakeAssistantProvider()

    response = provider.generate_search_response(
        query="Find a quiet cafe",
        places=[
            {
                "id": "place-1",
                "name": "Campus Cafe",
            }
        ],
    )

    assert response == "I found one option: Campus Cafe."


def test_generate_response_uses_only_available_place_names():
    provider = FakeAssistantProvider()

    response = provider.generate_search_response(
        query="Find a quiet cafe",
        places=[
            {
                "id": "place-1",
                "name": "Campus Cafe",
            },
            {
                "id": "place-2",
            },
            {
                "id": "place-3",
                "name": "Library Coffee",
            },
        ],
    )

    assert response == (
        "I found 2 options: Campus Cafe, Library Coffee."
    )


def test_generate_response_handles_missing_names():
    provider = FakeAssistantProvider()

    response = provider.generate_search_response(
        query="Find a quiet cafe",
        places=[
            {
                "id": "place-1",
            },
            {
                "id": "place-2",
            },
        ],
    )

    assert response == (
        "I found 2 matching places, but their names are unavailable."
    )


def test_continue_conversation_returns_follow_up_response():
    provider = FakeAssistantProvider()

    response = provider.continue_conversation(
        history=[
            {
                "role": "user",
                "content": "Find a quiet cafe",
            },
            {
                "role": "assistant",
                "content": "Campus Cafe is the best option.",
            },
        ],
        message="Which one is cheaper?",
        places=[
            {
                "id": "place-1",
                "name": "Campus Cafe",
            }
        ],
    )

    assert response == (
        "You asked: Which one is cheaper?. "
        "I can help compare these options: "
        "Campus Cafe."
    )
