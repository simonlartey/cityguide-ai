import pytest

from app.extensions import db
from app.models import User
from app.services.auth_service import (
    DuplicateEmailError,
    SignupData,
    SignupValidationError,
    create_user,
    normalize_email,
    validate_signup_data,
)


def make_signup_data(**overrides):
    data = {
        "display_name": "Simon Lartey",
        "email": "simon@example.com",
        "password": "secure-password-123",
        "confirm_password": "secure-password-123",
        "accepted_terms": True,
    }

    data.update(overrides)

    return SignupData(**data)


def test_normalize_email_trims_and_lowercases():
    assert normalize_email("  SIMON@EXAMPLE.COM  ") == "simon@example.com"


@pytest.mark.parametrize(
    ("overrides", "field_name"),
    [
        ({"display_name": "S"}, "displayName"),
        ({"email": "invalid-email"}, "email"),
        (
            {
                "password": "short1",
                "confirm_password": "short1",
            },
            "password",
        ),
        (
            {
                "password": "12345678",
                "confirm_password": "12345678",
            },
            "password",
        ),
        (
            {
                "password": "abcdefgh",
                "confirm_password": "abcdefgh",
            },
            "password",
        ),
        (
            {"confirm_password": "different-password-123"},
            "confirmPassword",
        ),
        ({"accepted_terms": False}, "terms"),
    ],
)
def test_validate_signup_data_rejects_invalid_input(
    overrides,
    field_name,
):
    signup_data = make_signup_data(**overrides)

    with pytest.raises(SignupValidationError) as error:
        validate_signup_data(signup_data)

    assert field_name in error.value.errors


def test_create_user_normalizes_and_persists_data(app):
    with app.app_context():
        user = create_user(
            make_signup_data(
                display_name="  Simon Lartey  ",
                email="  SIMON@EXAMPLE.COM  ",
            )
        )

        saved_user = db.session.get(User, user.id)

        assert saved_user is not None
        assert saved_user.display_name == "Simon Lartey"
        assert saved_user.email == "simon@example.com"
        assert saved_user.check_password("secure-password-123")


def test_create_user_rejects_duplicate_email(app):
    with app.app_context():
        create_user(make_signup_data())

        with pytest.raises(DuplicateEmailError):
            create_user(
                make_signup_data(
                    email="SIMON@EXAMPLE.COM",
                )
            )

        user_count = db.session.scalar(
            db.select(db.func.count()).select_from(User)
        )

        assert user_count == 1