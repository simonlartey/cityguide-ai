from app.models.conversation_message import (
    ConversationMessage,
    MessageRole,
)
from app.models.search_intent import SearchIntent
from app.repositories.in_memory_search_session import (
    InMemorySearchSessionRepository,
)
from app.services.conversation_manager import ConversationManager


def create_intent() -> SearchIntent:
    return SearchIntent(
        original_query="Find a quiet cafe",
        search_query="quiet cafe",
        category="cafe",
        preferences=("quiet",),
    )


def test_start_session_stores_search_state():
    repository = InMemorySearchSessionRepository()
    manager = ConversationManager(repository)

    places = [
        {
            "id": "place-1",
            "name": "Campus Cafe",
        }
    ]

    ranked_places = [
        {
            "id": "place-1",
            "name": "Campus Cafe",
        }
    ]

    session = manager.start_session(
        original_query="Find a quiet cafe",
        intent=create_intent(),
        places=places,
        ranked_places=ranked_places,
    )

    assert session.original_query == "Find a quiet cafe"
    assert session.intent == create_intent()
    assert session.places == places
    assert session.ranked_places == ranked_places
    assert repository.get(session.session_id) is session


def test_start_session_records_opening_user_message():
    manager = ConversationManager(
        InMemorySearchSessionRepository()
    )

    session = manager.start_session(
        original_query="Find a quiet cafe",
        intent=create_intent(),
        places=[],
        ranked_places=[],
    )

    assert session.conversation_history == [
        ConversationMessage(
            role=MessageRole.USER,
            content="Find a quiet cafe",
        )
    ]


def test_get_session_returns_stored_session():
    repository = InMemorySearchSessionRepository()
    manager = ConversationManager(repository)

    session = manager.start_session(
        original_query="Find a quiet cafe",
        intent=create_intent(),
        places=[],
        ranked_places=[],
    )

    assert manager.get_session(session.session_id) is session


def test_get_session_returns_none_for_unknown_id():
    manager = ConversationManager(
        InMemorySearchSessionRepository()
    )

    assert manager.get_session("missing-session") is None


def test_start_session_records_assistant_response():
    manager = ConversationManager(
        InMemorySearchSessionRepository()
    )

    session = manager.start_session(
        original_query="Find a quiet cafe",
        intent=create_intent(),
        places=[],
        ranked_places=[],
        assistant_response="Campus Cafe is the best option.",
    )

    assert session.conversation_history == [
        ConversationMessage(
            role=MessageRole.USER,
            content="Find a quiet cafe",
        ),
        ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="Campus Cafe is the best option.",
        ),
    ]


def test_get_session_details_returns_serialized_session():
    repository = InMemorySearchSessionRepository()

    manager = ConversationManager(repository)

    session = manager.start_session(
        original_query="Find a quiet cafe",
        intent=create_intent(),
        places=[
            {
                "id": "cafe-1",
                "name": "Campus Cafe",
            }
        ],
        ranked_places=[
            {
                "id": "cafe-1",
                "name": "Campus Cafe",
            }
        ],
        assistant_response="Campus Cafe is the best option.",
    )

    details = manager.get_session_details(
        session.session_id
    )

    assert details["session_id"] == session.session_id

    assert details["query"] == (
        "Find a quiet cafe"
    )

    assert details["conversation_history"] == [
        {
            "role": "user",
            "content": "Find a quiet cafe",
        },
        {
            "role": "assistant",
            "content": (
                "Campus Cafe is the best option."
            ),
        },
    ]

    assert details["results"] == [
        {
            "id": "cafe-1",
            "name": "Campus Cafe",
        }
    ]
