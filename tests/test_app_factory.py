from app import create_app
from app.providers.assistant.fake_provider import (
    FakeAssistantProvider,
)
from app.providers.places.mock_provider import MockPlacesProvider
from app.repositories.in_memory_search_session import (
    InMemorySearchSessionRepository,
)
from tests.conftest import TestConfig


class MockProviderConfig(TestConfig):
    ASSISTANT_PROVIDER = "fake"
    PLACES_PROVIDER = "mock"
    PLACES_API_KEY = None
    PLACES_REQUEST_TIMEOUT_SECONDS = 10


def test_create_app_registers_configured_places_provider():
    app = create_app(MockProviderConfig)

    assert isinstance(
        app.extensions["places_provider"],
        MockPlacesProvider,
    )


def test_create_app_registers_configured_assistant_provider():
    app = create_app(MockProviderConfig)

    assert isinstance(
        app.extensions["assistant_provider"],
        FakeAssistantProvider,
    )


def test_create_app_registers_search_session_repository():
    app = create_app(MockProviderConfig)

    assert isinstance(
        app.extensions["search_session_repository"],
        InMemorySearchSessionRepository,
    )
