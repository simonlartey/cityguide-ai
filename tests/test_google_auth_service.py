import pytest

from app.extensions import db
from app.models import User
from app.services.auth_service import create_or_link_google_user


def test_create_google_only_user(app):
    with app.app_context():
        user = create_or_link_google_user(
            google_sub="google-user-123",
            email="SIMON@EXAMPLE.COM",
            email_verified=True,
            display_name="Simon Lartey",
            avatar_url="https://example.com/avatar.jpg",
        )

        saved_user = db.session.get(User, user.id)

        assert saved_user is not None
        assert saved_user.email == "simon@example.com"
        assert saved_user.google_sub == "google-user-123"
        assert saved_user.password_hash is None
        assert saved_user.avatar_url == "https://example.com/avatar.jpg"


def test_link_google_to_existing_password_account(app):
    with app.app_context():
        user = User(
            email="simon@example.com",
            display_name="Simon",
            password_hash="",
        )
        user.set_password("secure-password-123")

        db.session.add(user)
        db.session.commit()

        original_user_id = user.id

        linked_user = create_or_link_google_user(
            google_sub="google-user-123",
            email="simon@example.com",
            email_verified=True,
            display_name="Simon Lartey",
            avatar_url="https://example.com/avatar.jpg",
        )

        assert linked_user.id == original_user_id
        assert linked_user.google_sub == "google-user-123"
        assert linked_user.display_name == "Simon Lartey"
        assert linked_user.check_password("secure-password-123")


def test_returning_google_user_is_updated(app):
    with app.app_context():
        user = User(
            email="simon@example.com",
            display_name="Old Name",
            password_hash=None,
            google_sub="google-user-123",
            avatar_url=None,
        )

        db.session.add(user)
        db.session.commit()

        original_user_id = user.id

        returned_user = create_or_link_google_user(
            google_sub="google-user-123",
            email="simon@example.com",
            email_verified=True,
            display_name="Updated Name",
            avatar_url="https://example.com/new-avatar.jpg",
        )

        assert returned_user.id == original_user_id
        assert returned_user.display_name == "Updated Name"
        assert returned_user.avatar_url == "https://example.com/new-avatar.jpg"


@pytest.mark.parametrize(
    "overrides",
    [
        {"google_sub": ""},
        {"email": ""},
        {"email_verified": False},
    ],
)
def test_google_user_requires_valid_verified_profile(app, overrides):
    profile = {
        "google_sub": "google-user-123",
        "email": "simon@example.com",
        "email_verified": True,
        "display_name": "Simon Lartey",
        "avatar_url": None,
    }
    profile.update(overrides)

    with app.app_context(), pytest.raises(ValueError):
        create_or_link_google_user(**profile)


def test_rejects_email_linked_to_different_google_account(app):
    with app.app_context():
        user = User(
            email="simon@example.com",
            display_name="Simon",
            password_hash=None,
            google_sub="different-google-sub",
        )

        db.session.add(user)
        db.session.commit()

        with pytest.raises(
            ValueError,
            match="linked to another Google account",
        ):
            create_or_link_google_user(
                google_sub="google-user-123",
                email="simon@example.com",
                email_verified=True,
                display_name="Simon Lartey",
                avatar_url=None,
            )