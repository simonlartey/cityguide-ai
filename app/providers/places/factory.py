from app.providers.places.base import PlacesProvider
from app.providers.places.google_provider import GooglePlacesProvider
from app.providers.places.mock_provider import MockPlacesProvider


def create_places_provider(config: dict) -> PlacesProvider:
    """Create the places provider selected by application configuration."""

    provider_name = config.get(
        "PLACES_PROVIDER",
        "mock",
    )

    if provider_name == "mock":
        return MockPlacesProvider()

    if provider_name == "google":
        return GooglePlacesProvider(
            api_key=config.get("PLACES_API_KEY"),
            timeout_seconds=config.get(
                "PLACES_REQUEST_TIMEOUT_SECONDS",
                10,
            ),
        )

    raise ValueError(
        f"Unsupported places provider: {provider_name}"
    )