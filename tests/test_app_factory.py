from app import create_app
from app.providers.places.mock_provider import MockPlacesProvider
from tests.conftest import TestConfig


class MockProviderConfig(TestConfig):
    PLACES_PROVIDER = "mock"
    PLACES_API_KEY = None
    PLACES_REQUEST_TIMEOUT_SECONDS = 10


def test_create_app_registers_configured_places_provider():
    app = create_app(MockProviderConfig)

    assert isinstance(
        app.extensions["places_provider"],
        MockPlacesProvider,
    )