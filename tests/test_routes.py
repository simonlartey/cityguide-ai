import pytest


@pytest.mark.parametrize(
    ("path", "expected_text"),
    [
        ("/", b"CityGuide AI"),
        ("/login", b"Sign in to CityGuide AI"),
        ("/signup", b"Create your account"),
        ("/terms", b"Terms of Service"),
        ("/privacy", b"Privacy Policy"),
    ],
)
def test_page_routes_return_success(client, path, expected_text):
    response = client.get(path)

    assert response.status_code == 200
    assert expected_text in response.data


def test_unknown_route_returns_not_found(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/static/css/styles.css",
        "/static/css/auth.css",
        "/static/css/legal.css",
        "/static/js/app.js",
        "/static/js/auth.js",
        "/static/images/hero_img.jpg",
    ],
)
def test_static_assets_are_served(client, path):
    response = client.get(path)

    assert response.status_code == 200