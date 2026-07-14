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