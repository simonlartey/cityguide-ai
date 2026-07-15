import pytest

from app.schemas.search import (
    SearchLocation,
    SearchRequest,
    SearchValidationError,
)


def test_search_request_accepts_query_without_location():
    search_request = SearchRequest.from_dict(
        {"query": "Affordable barber"}
    )

    assert search_request.query == "Affordable barber"
    assert search_request.location is None


def test_search_request_strips_query_whitespace():
    search_request = SearchRequest.from_dict(
        {"query": "  Quiet study space  "}
    )

    assert search_request.query == "Quiet study space"


def test_search_request_accepts_valid_location():
    search_request = SearchRequest.from_dict(
        {
            "query": "Coffee shop",
            "location": {
                "latitude": 43.6591,
                "longitude": -70.2568,
            },
        }
    )

    assert search_request.location == SearchLocation(
        latitude=43.6591,
        longitude=-70.2568,
    )


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (None, "Request body must be a JSON object."),
        ([], "Request body must be a JSON object."),
        ({}, "The query field must be a string."),
        ({"query": None}, "The query field must be a string."),
        ({"query": 123}, "The query field must be a string."),
        ({"query": ""}, "Please enter a search query."),
        ({"query": "   "}, "Please enter a search query."),
        (
            {"query": "a" * 501},
            "The search query must be 500 characters or fewer.",
        ),
    ],
)
def test_search_request_rejects_invalid_query(
    payload,
    expected_message,
):
    with pytest.raises(
        SearchValidationError,
        match=expected_message,
    ):
        SearchRequest.from_dict(payload)


def test_search_request_rejects_non_object_location():
    with pytest.raises(
        SearchValidationError,
        match="The location field must be an object.",
    ):
        SearchRequest.from_dict(
            {
                "query": "Barber",
                "location": "Portland",
            }
        )


@pytest.mark.parametrize(
    ("latitude", "longitude", "expected_message"),
    [
        ("43.6591", -70.2568, "Location latitude must be a number."),
        (True, -70.2568, "Location latitude must be a number."),
        (43.6591, "-70.2568", "Location longitude must be a number."),
        (43.6591, False, "Location longitude must be a number."),
        (91, -70.2568, "Latitude must be between -90 and 90."),
        (-91, -70.2568, "Latitude must be between -90 and 90."),
        (43.6591, 181, "Longitude must be between -180 and 180."),
        (43.6591, -181, "Longitude must be between -180 and 180."),
    ],
)
def test_search_request_rejects_invalid_coordinates(
    latitude,
    longitude,
    expected_message,
):
    with pytest.raises(
        SearchValidationError,
        match=expected_message,
    ):
        SearchRequest.from_dict(
            {
                "query": "Barber",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
            }
        )