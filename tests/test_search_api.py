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