from unittest.mock import Mock

from app.providers.places.errors import PlacesProviderError


def test_search_api_returns_results(client):
    response = client.post(
        "/api/v1/search",
        json={
            "query": "Affordable barber for textured hair",
            "location": {
                "latitude": 43.6591,
                "longitude": -70.2568,
            },
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["query"] == "Affordable barber for textured hair"
    assert data["result_count"] == 3
    assert len(data["results"]) == 3
    assert data["search_id"].startswith("search_")


def test_search_api_returns_normalized_place_fields(client):
    response = client.post(
        "/api/v1/search",
        json={"query": "Barber"},
    )

    place = response.get_json()["results"][0]

    assert place["id"] == "portland-fade-studio"
    assert place["name"] == "Portland Fade Studio"
    assert place["category"] == "Barber shop"
    assert place["rating"] == 4.9
    assert place["open_now"] is True
    assert isinstance(place["match_reasons"], list)


def test_search_api_rejects_blank_query(client):
    response = client.post(
        "/api/v1/search",
        json={"query": "   "},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "code": "invalid_search_request",
            "message": "Please enter a search query.",
        }
    }


def test_search_api_rejects_missing_query(client):
    response = client.post(
        "/api/v1/search",
        json={},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == (
        "invalid_search_request"
    )


def test_search_api_rejects_non_json_request(client):
    response = client.post(
        "/api/v1/search",
        data="query=barber",
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 415
    assert response.get_json() == {
        "error": {
            "code": "invalid_content_type",
            "message": "Request body must use application/json.",
        }
    }


def test_search_api_rejects_malformed_json(client):
    response = client.post(
        "/api/v1/search",
        data='{"query":',
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == (
        "invalid_search_request"
    )


def test_search_api_rejects_invalid_location(client):
    response = client.post(
        "/api/v1/search",
        json={
            "query": "Coffee shop",
            "location": {
                "latitude": 200,
                "longitude": -70.2568,
            },
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["message"] == (
        "Latitude must be between -90 and 90."
    )


def test_search_api_handles_provider_failure(
    app,
    client,
):
    provider = Mock()
    provider.search.side_effect = PlacesProviderError(
        "Google Places search failed."
    )

    app.extensions["places_provider"] = provider

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Coffee shops",
        },
    )

    assert response.status_code == 503
    assert response.get_json() == {
        "error": {
            "code": "places_provider_unavailable",
            "message": (
                "Local recommendations are temporarily unavailable."
            ),
        }
    }

    provider.search.assert_called_once_with(
        query="Coffee shops",
        latitude=None,
        longitude=None,
    )


def test_search_api_does_not_hide_unexpected_errors(
    app,
    client,
):
    provider = Mock()
    provider.search.side_effect = RuntimeError(
        "Unexpected programming error"
    )

    app.extensions["places_provider"] = provider

    try:
        client.post(
            "/api/v1/search",
            json={
                "query": "Coffee shops",
            },
        )
    except RuntimeError as error:
        assert str(error) == "Unexpected programming error"
    else:
        raise AssertionError(
            "Unexpected errors should not be converted "
            "into provider availability responses."
        )


def test_place_photo_redirects_to_resolved_url(
    app,
    client,
):
    provider = Mock()
    provider.get_photo_url.return_value = (
        "https://images.example.com/photo.jpg"
    )

    app.extensions["places_provider"] = provider

    response = client.get(
        "/api/v1/place-photo",
        query_string={
            "name": "places/place-123/photos/photo-456",
            "width": "1200",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == (
        "https://images.example.com/photo.jpg"
    )
    provider.get_photo_url.assert_called_once_with(
        "places/place-123/photos/photo-456",
        max_width=1200,
    )


def test_place_photo_rejects_invalid_width(client):
    response = client.get(
        "/api/v1/place-photo",
        query_string={
            "name": "places/place-123/photos/photo-456",
            "width": "wide",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "code": "invalid_photo_request",
            "message": "Photo width must be an integer.",
        }
    }


def test_place_photo_route_rejects_unavailable_provider(
    app,
    client,
):
    app.extensions["places_provider"] = Mock(spec=[])

    response = client.get(
        "/api/v1/place-photo",
        query_string={
            "name": "places/place-123/photos/photo-456",
        },
    )

    assert response.status_code == 503
    assert response.get_json() == {
        "error": {
            "code": "place_photos_unavailable",
            "message": (
                "Place photos are unavailable for "
                "the configured provider."
            ),
        }
    }


def test_place_photo_route_handles_provider_validation_error(
    app,
    client,
):
    provider = Mock()
    provider.get_photo_url.side_effect = ValueError(
        "Invalid Google Places photo name."
    )

    app.extensions["places_provider"] = provider

    response = client.get(
        "/api/v1/place-photo",
        query_string={
            "name": "bad-name",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "code": "invalid_photo_request",
            "message": "Invalid Google Places photo name.",
        }
    }


def test_place_photo_handles_provider_failure(
    app,
    client,
):
    provider = Mock()
    provider.get_photo_url.side_effect = PlacesProviderError("photo failed")

    app.extensions["places_provider"] = provider

    response = client.get(
        "/api/v1/place-photo",
        query_string={
            "name": "places/place-123/photos/photo-456",
        },
    )

    assert response.status_code == 503
    assert response.get_json() == {
        "error": {
            "code": "place_photo_unavailable",
            "message": (
                "This place photo is temporarily unavailable."
            ),
        }
    }
