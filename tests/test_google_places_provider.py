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
                "photos": [
                    {
                        "name": (
                            "places/place-123/photos/"
                            "photo-reference-1"
                        ),
                        "widthPx": 1600,
                        "heightPx": 900,
                        "authorAttributions": [
                            {
                                "displayName": "Example Photographer",
                                "uri": "https://example.com/profile",
                                "photoUri": "https://example.com/avatar.jpg",
                            }
                        ],
                    },
                    {
                        "name": (
                            "places/place-123/photos/"
                            "photo-reference-2"
                        ),
                        "widthPx": 1200,
                        "heightPx": 800,
                        "authorAttributions": [],
                    },
                ],
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
            "photos": [
                {
                    "name": (
                        "places/place-123/photos/"
                        "photo-reference-1"
                    ),
                    "width": 1600,
                    "height": 900,
                    "author_attributions": [
                        {
                            "displayName": "Example Photographer",
                            "uri": "https://example.com/profile",
                            "photoUri": "https://example.com/avatar.jpg",
                        }
                    ],
                },
                {
                    "name": (
                        "places/place-123/photos/"
                        "photo-reference-2"
                    ),
                    "width": 1200,
                    "height": 800,
                    "author_attributions": [],
                },
            ],
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
    assert "places.photos" in request.kwargs["headers"]["X-Goog-FieldMask"]


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
        "photos",
    }

    assert set(place) == expected_fields


def test_google_provider_returns_empty_photos_when_missing(
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

    place = provider.search("test place")[0]

    assert place["photos"] == []


def test_google_provider_ignores_malformed_photos(
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
                "photos": [
                    None,
                    "invalid",
                    {},
                    {
                        "name": "",
                    },
                    {
                        "name": (
                            "places/place-123/photos/"
                            "valid-photo"
                        ),
                        "widthPx": "not-an-integer",
                        "heightPx": 800,
                        "authorAttributions": "invalid",
                    },
                ],
            }
        ]
    }
    session.post.return_value = response

    place = provider.search("test place")[0]

    assert place["photos"] == [
        {
            "name": (
                "places/place-123/photos/"
                "valid-photo"
            ),
            "width": None,
            "height": 800,
            "author_attributions": [],
        }
    ]


def test_google_provider_limits_and_normalizes_photos():
    photos = GooglePlacesProvider._normalize_photos(
        [
            {
                "name": "places/1/photos/1",
                "widthPx": 100,
                "heightPx": 200,
                "authorAttributions": [
                    {
                        "displayName": "One",
                    }
                ],
            },
            {"name": ""},
            "invalid",
            {
                "name": "places/1/photos/2",
                "widthPx": 300,
                "heightPx": 400,
                "authorAttributions": [],
            },
            {
                "name": "places/1/photos/3",
                "widthPx": 500,
                "heightPx": 600,
            },
            {
                "name": "places/1/photos/4",
                "widthPx": 700,
                "heightPx": 800,
            },
            {
                "name": "places/1/photos/5",
                "widthPx": 900,
                "heightPx": 1000,
            },
            {
                "name": "places/1/photos/6",
                "widthPx": 1100,
                "heightPx": 1200,
            },
        ]
    )

    assert photos == [
        {
            "name": "places/1/photos/1",
            "width": 100,
            "height": 200,
            "author_attributions": [
                {
                    "displayName": "One",
                }
            ],
        },
        {
            "name": "places/1/photos/2",
            "width": 300,
            "height": 400,
            "author_attributions": [],
        },
        {
            "name": "places/1/photos/3",
            "width": 500,
            "height": 600,
            "author_attributions": [],
        },
        {
            "name": "places/1/photos/4",
            "width": 700,
            "height": 800,
            "author_attributions": [],
        },
        {
            "name": "places/1/photos/5",
            "width": 900,
            "height": 1000,
            "author_attributions": [],
        },
    ]


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