from app.models.search_intent import SearchIntent
from app.models.search_session import SearchSession
from app.repositories.in_memory_search_session import (
    InMemorySearchSessionRepository,
)


def create_session() -> SearchSession:
    return SearchSession(
        original_query="Find a quiet cafe",
        intent=SearchIntent(
            original_query="Find a quiet cafe",
            search_query="quiet cafe",
            category="cafe",
            preferences=("quiet",),
        ),
    )


def test_repository_saves_and_retrieves_session():
    repository = InMemorySearchSessionRepository()
    session = create_session()

    repository.save(session)

    assert repository.get(session.session_id) is session


def test_repository_returns_none_for_unknown_session():
    repository = InMemorySearchSessionRepository()

    assert repository.get("missing-session") is None


def test_repository_replaces_existing_session():
    repository = InMemorySearchSessionRepository()
    original_session = create_session()

    repository.save(original_session)

    replacement_session = SearchSession(
        session_id=original_session.session_id,
        original_query="Find an affordable restaurant",
        intent=SearchIntent(
            original_query="Find an affordable restaurant",
            search_query="affordable restaurant",
            category="restaurant",
            preferences=("affordable",),
        ),
    )

    repository.save(replacement_session)

    assert repository.get(original_session.session_id) is replacement_session


def test_repository_instances_do_not_share_sessions():
    first_repository = InMemorySearchSessionRepository()
    second_repository = InMemorySearchSessionRepository()
    session = create_session()

    first_repository.save(session)

    assert first_repository.get(session.session_id) is session
    assert second_repository.get(session.session_id) is None
