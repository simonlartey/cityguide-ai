from unittest.mock import Mock

import pytest
import requests

from app.providers.places.errors import PlacesProviderError
from app.providers.places.google_provider import GooglePlacesProvider


@pytest.fixture
def session():
    return Mock()


@pytest.fixture
def provider(session):
    return GooglePlacesProvider(
        api_key="test-api-key",
        timeout_seconds=5,
        session=session,
    )


def test_google_provider_requires_api_key():
    with pytest.raises(
        ValueError,
        match="Google Places API key is required",
    ):
        GooglePlacesProvider(api_key="")


def test_google_provider_searches_and_normalizes_results(
    provider,
    session,
):
    response = Mock()
    response.json.return_value = {
        "places": [
            {
                "id": "place-123",
                "displayName": {
                    "text": "Portland Fade Studio",
                },
                "formattedAddress": "123 Congress St",
                "location": {
                    "latitude": 43.657,
                    "longitude": -70.258,
                },
                "rating": 4.8,
                "userRatingCount": 240,
                "priceLevel": "PRICE_LEVEL_MODERATE",
                "currentOpeningHours": {
                    "openNow": True,
                },
                "regularOpeningHours": {
                    "weekdayDescriptions": [
                        "Monday: 9:00 AM – 6:00 PM",
                    ],
                },
                "nationalPhoneNumber": "(207) 555-0100",
                "websiteUri": "https://example.com",
                "googleMapsUri": "https://maps.google.com/example",
            }
        ]
    }
    session.post.return_value = response

    results = provider.search(
        "barbers for textured hair",
        latitude=43.6591,
        longitude=-70.2568,
    )

    assert results == [
        {
            "id": "place-123",
            "name": "Portland Fade Studio",
            "category": "Local business",
            "address": "123 Congress St",
            "latitude": 43.657,
            "longitude": -70.258,
            "rating": 4.8,
            "review_count": 240,
            "distance_miles": None,
            "price_level": 2,
            "open_now": True,
            "hours_text": "Monday: 9:00 AM – 6:00 PM",
            "description": (
                "Portland Fade Studio is rated 4.8 based on "
                "240 Google reviews."
            ),
            "tags": [
                "Highly rated",
                "Moderate price",
                "Open now",
            ],
            "match_reasons": [
                "Rated 4.8 from 240 reviews",
                "Price level: $$",
            ],
            "phone": "(207) 555-0100",
            "website": "https://example.com",
            "maps_url": "https://maps.google.com/example",
        }
    ]

    session.post.assert_called_once()

    request = session.post.call_args

    assert request.kwargs["timeout"] == 5
    assert request.kwargs["json"]["textQuery"] == (
        "barbers for textured hair"
    )
    assert request.kwargs["json"]["locationBias"] == {
        "circle": {
            "center": {
                "latitude": 43.6591,
                "longitude": -70.2568,
            },
            "radius": 10000.0,
        }
    }


def test_google_provider_matches_dashboard_place_schema(
    provider,
    session,
):
    response = Mock()
    response.json.return_value = {
        "places": [
            {
                "id": "place-123",
                "displayName": {
                    "text": "Test Place",
                },
                "location": {
                    "latitude": 43.65,
                    "longitude": -70.25,
                },
            }
        ]
    }
    session.post.return_value = response

    place = provider.search("test place")[0]

    expected_fields = {
        "id",
        "name",
        "category",
        "address",
        "latitude",
        "longitude",
        "rating",
        "review_count",
        "distance_miles",
        "price_level",
        "open_now",
        "hours_text",
        "description",
        "tags",
        "match_reasons",
        "phone",
        "website",
        "maps_url",
    }

    assert set(place) == expected_fields


def test_google_provider_returns_empty_list(
    provider,
    session,
):
    response = Mock()
    response.json.return_value = {}
    session.post.return_value = response

    assert provider.search("unknown place") == []


def test_google_provider_handles_request_failure(
    provider,
    session,
):
    session.post.side_effect = requests.Timeout()

    with pytest.raises(
        PlacesProviderError,
        match="Google Places search failed",
    ):
        provider.search("coffee")


def test_google_provider_handles_invalid_json(
    provider,
    session,
):
    response = Mock()
    response.json.side_effect = ValueError()
    session.post.return_value = response

    with pytest.raises(
        PlacesProviderError,
        match="invalid response",
    ):
        provider.search("coffee")


def test_google_provider_rejects_malformed_places(
    provider,
    session,
):
    response = Mock()
    response.json.return_value = {
        "places": "not-a-list",
    }
    session.post.return_value = response

    with pytest.raises(
        PlacesProviderError,
        match="malformed place data",
    ):
        provider.search("coffee")