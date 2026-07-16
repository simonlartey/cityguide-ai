from datetime import datetime, timezone
from unittest.mock import Mock, patch

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
                "utcOffsetMinutes": -240,
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

    with patch(
        "app.providers.places.google_provider.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = datetime(
            2026,
            7,
            13,
            14,
            0,
            tzinfo=timezone.utc,
        )

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
            "distance_miles": 0.2,
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


def test_current_day_hours_returns_first_day_without_offset():
    hours = GooglePlacesProvider._get_current_day_hours(
        weekday_descriptions=[
            "Monday: 9:00 AM – 5:00 PM",
            "Tuesday: 9:00 AM – 5:00 PM",
        ],
        utc_offset_minutes=None,
    )

    assert hours == "Hours unavailable"


@pytest.mark.parametrize(
    "response_data",
    [None, [], "invalid", 42],
)
def test_google_provider_rejects_non_object_response(
    provider,
    session,
    response_data,
):
    response = Mock()
    response.json.return_value = response_data
    session.post.return_value = response

    with pytest.raises(
        PlacesProviderError,
        match="invalid response",
    ):
        provider.search("coffee")


def test_current_day_hours_uses_place_local_weekday():
    current_utc_time = datetime(
        2026,
        7,
        16,
        14,
        0,
        tzinfo=timezone.utc,
    )

    hours = GooglePlacesProvider._get_current_day_hours(
        weekday_descriptions=[
            "Sunday: Closed",
            "Monday: 9:00 AM – 5:00 PM",
            "Tuesday: 9:00 AM – 5:00 PM",
            "Wednesday: 9:00 AM – 5:00 PM",
            "Thursday: 10:00 AM – 7:00 PM",
            "Friday: 9:00 AM – 5:00 PM",
            "Saturday: Closed",
        ],
        utc_offset_minutes=-240,
        current_utc_time=current_utc_time,
    )

    assert hours == "Thursday: 10:00 AM – 7:00 PM"


def test_current_day_hours_handles_nonstandard_day_order():
    current_utc_time = datetime(
        2026,
        7,
        16,
        14,
        0,
        tzinfo=timezone.utc,
    )

    hours = GooglePlacesProvider._get_current_day_hours(
        weekday_descriptions=[
            "Saturday: Closed",
            "Thursday: 10:00 AM – 7:00 PM",
            "Monday: 9:00 AM – 5:00 PM",
        ],
        utc_offset_minutes=-240,
        current_utc_time=current_utc_time,
    )

    assert hours == "Thursday: 10:00 AM – 7:00 PM"


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


def test_google_provider_returns_no_distance_without_origin(
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

    assert place["distance_miles"] is None


def test_google_provider_returns_no_distance_without_place_coordinates(
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
            }
        ]
    }
    session.post.return_value = response

    place = provider.search(
        "test place",
        latitude=43.6591,
        longitude=-70.2568,
    )[0]

    assert place["distance_miles"] is None


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