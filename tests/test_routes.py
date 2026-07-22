import pytest

from app.extensions import db
from app.models import User


@pytest.mark.parametrize(
    ("path", "expected_text"),
    [
        ("/", b"CityGuide AI"),
        ("/login", b"Sign in to CityGuide AI"),
        ("/signup", b"Create your account"),
        ("/terms", b"Terms of Service"),
        ("/privacy", b"Privacy Policy"),
        ("/dashboard", b"Dashboard"),
    ],
)
def test_page_routes_return_success(client, path, expected_text):
    response = client.get(path)

    assert response.status_code == 200
    assert expected_text in response.data


def test_unknown_route_returns_not_found(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404


def test_signup_creates_user_and_redirects_to_login(client, app):
    response = client.post(
        "/signup",
        data={
            "displayName": "Simon Lartey",
            "email": "simon@example.com",
            "password": "secure-password-123",
            "confirmPassword": "secure-password-123",
            "terms": "on",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login?signup=success")

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.email == "simon@example.com")
        ).scalar_one()

        assert user.display_name == "Simon Lartey"
        assert user.check_password("secure-password-123")


def test_signup_rejects_duplicate_email(client, app):
    with app.app_context():
        user = User(
            email="simon@example.com",
            display_name="Simon Lartey",
            password_hash="",
        )
        user.set_password("secure-password-123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/signup",
        data={
            "displayName": "Another User",
            "email": "simon@example.com",
            "password": "secure-password-123",
            "confirmPassword": "secure-password-123",
            "terms": "on",
        },
    )

    assert response.status_code == 200
    assert b"An account with that email already exists." in response.data

    with app.app_context():
        users = db.session.execute(
            db.select(User).where(User.email == "simon@example.com")
        ).scalars().all()

        assert len(users) == 1


@pytest.mark.parametrize(
    "path",
    [
        "/static/css/styles.css",
        "/static/css/auth.css",
        "/static/css/dashboard.css",
        "/static/css/legal.css",
        "/static/js/app.js",
        "/static/js/auth.js",
        "/static/js/dashboard.js",
        "/static/images/hero_img.jpg",
    ],
)
def test_static_assets_are_served(client, path):
    response = client.get(path)

    assert response.status_code == 200


def test_dashboard_javascript_uses_assistant_response(client):
    response = client.get(
        "/static/js/dashboard.js"
    )

    assert response.status_code == 200

    javascript = response.get_data(
        as_text=True
    )

    assert (
        "searchResponse.assistant_response"
        in javascript
    )

    assert (
        "assistantResponse ||"
        in javascript
    )


def test_dashboard_centralizes_selected_location(client):
    javascript_response = client.get(
        "/static/js/dashboard.js"
    )

    template_response = client.get(
        "/dashboard"
    )

    assert javascript_response.status_code == 200
    assert template_response.status_code == 200

    javascript = javascript_response.get_data(
        as_text=True
    )

    html = template_response.get_data(
        as_text=True
    )

    assert "const DEFAULT_LOCATION" in javascript

    assert (
        "selectedLocation.latitude"
        in javascript
    )

    assert (
        "selectedLocation.longitude"
        in javascript
    )

    assert (
        "selectedLocation.label"
        in javascript
    )

    assert (
        "data-current-location-label"
        in html
    )


def test_dashboard_supports_manual_location_selection(client):
    javascript_response = client.get(
        "/static/js/dashboard.js"
    )

    dashboard_response = client.get(
        "/dashboard"
    )

    stylesheet_response = client.get(
        "/static/css/dashboard.css"
    )

    assert javascript_response.status_code == 200
    assert dashboard_response.status_code == 200
    assert stylesheet_response.status_code == 200

    javascript = javascript_response.get_data(
        as_text=True
    )

    html = dashboard_response.get_data(
        as_text=True
    )

    stylesheet = stylesheet_response.get_data(
        as_text=True
    )

    assert "PlaceAutocompleteElement" in javascript
    assert '"gmp-select"' in javascript
    assert "setSelectedLocation" in javascript
    assert "data-location-selector" in html
    assert "data-location-panel" in html
    assert "data-location-autocomplete" in html
    assert ".location-panel" in stylesheet
    assert 'aria-expanded="false"' in html

    assert (
        'aria-controls="dashboard-location-panel"'
        in html
    )

    assert 'id="dashboard-location-panel"' in html

    assert (
        'aria-label="Choose a search location"'
        in html
    )

    assert 'role="status"' in html

    assert 'aria-live="polite"' in html


def test_dashboard_supports_current_location_detection(client):
    javascript_response = client.get(
        "/static/js/dashboard.js"
    )

    dashboard_response = client.get(
        "/dashboard"
    )

    stylesheet_response = client.get(
        "/static/css/dashboard.css"
    )

    assert javascript_response.status_code == 200
    assert dashboard_response.status_code == 200
    assert stylesheet_response.status_code == 200

    javascript = javascript_response.get_data(
        as_text=True
    )

    html = dashboard_response.get_data(
        as_text=True
    )

    stylesheet = stylesheet_response.get_data(
        as_text=True
    )

    assert "navigator.geolocation" in javascript

    assert (
        "navigator.geolocation.getCurrentPosition"
        in javascript
    )

    assert '"geocoding"' in javascript

    assert "getLocationLabel" in javascript
    assert "getGeolocationErrorMessage" in javascript
    assert "fallbackLabel" in javascript

    assert (
        "latitude.toFixed(4)"
        in javascript
    )

    assert (
        "longitude.toFixed(4)"
        in javascript
    )

    assert (
        "data-current-location-button"
        in html
    )

    assert (
        "Use my current location"
        in html
    )

    assert (
        ".current-location-button"
        in stylesheet
    )
