from app.extensions import db
from app.models import User


def create_user(
    *,
    email="simon@example.com",
    password="secure-password-123",
):
    user = User(
        email=email,
        display_name="Simon Lartey",
        password_hash="",
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return user.id


def test_login_with_valid_credentials_creates_session(client, app):
    with app.app_context():
        user_id = create_user()

    response = client.post(
        "/login",
        data={
            "email": "simon@example.com",
            "password": "secure-password-123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert session["user_id"] == user_id


def test_login_rejects_incorrect_password(client, app):
    with app.app_context():
        create_user()

    response = client.post(
        "/login",
        data={
            "email": "simon@example.com",
            "password": "incorrect-password",
        },
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/login",
        data={
            "email": "unknown@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_normalizes_email(client, app):
    with app.app_context():
        user_id = create_user()

    response = client.post(
        "/login",
        data={
            "email": "  SIMON@EXAMPLE.COM  ",
            "password": "secure-password-123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert session["user_id"] == user_id


def test_logout_clears_session(client, app):
    with app.app_context():
        user_id = create_user()

    with client.session_transaction() as session:
        session["user_id"] = user_id

    response = client.post(
        "/logout",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    with client.session_transaction() as session:
        assert "user_id" not in session