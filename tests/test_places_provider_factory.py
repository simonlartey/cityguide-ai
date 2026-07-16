import pytest

from app.providers.places.factory import create_places_provider
from app.providers.places.google_provider import GooglePlacesProvider
from app.providers.places.mock_provider import MockPlacesProvider


def test_factory_creates_mock_provider():
    provider = create_places_provider(
        {
            "PLACES_PROVIDER": "mock",
        }
    )

    assert isinstance(provider, MockPlacesProvider)


def test_factory_creates_google_provider():
    provider = create_places_provider(
        {
            "PLACES_PROVIDER": "google",
            "PLACES_API_KEY": "test-api-key",
            "PLACES_REQUEST_TIMEOUT_SECONDS": 5,
        }
    )

    assert isinstance(provider, GooglePlacesProvider)
    assert provider.api_key == "test-api-key"
    assert provider.timeout_seconds == 5


def test_factory_rejects_unsupported_provider():
    with pytest.raises(
        ValueError,
        match="Unsupported places provider: unknown",
    ):
        create_places_provider(
            {
                "PLACES_PROVIDER": "unknown",
            }
        )