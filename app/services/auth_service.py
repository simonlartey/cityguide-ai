import re
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class SignupData:
    display_name: str
    email: str
    password: str
    confirm_password: str
    accepted_terms: bool


class SignupValidationError(ValueError):
    """Raised when signup input fails validation."""

    def __init__(self, errors: dict[str, str]):
        super().__init__("Signup validation failed.")
        self.errors = errors


class DuplicateEmailError(ValueError):
    """Raised when an account already uses an email address."""


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_signup_data(data: SignupData) -> None:
    errors: dict[str, str] = {}

    if len(data.display_name.strip()) < 2:
        errors["displayName"] = "Enter a name with at least 2 characters."

    if not EMAIL_PATTERN.fullmatch(data.email):
        errors["email"] = "Enter a valid email address."

    if len(data.password) < 8:
        errors["password"] = "Password must contain at least 8 characters."
    elif not any(character.isalpha() for character in data.password):
        errors["password"] = "Password must contain at least one letter."
    elif not any(character.isdigit() for character in data.password):
        errors["password"] = "Password must contain at least one number."

    if data.password != data.confirm_password:
        errors["confirmPassword"] = "Passwords do not match."

    if not data.accepted_terms:
        errors["terms"] = (
            "You must agree to the Terms of Service and Privacy Policy."
        )

    if errors:
        raise SignupValidationError(errors)


def create_user(data: SignupData) -> User:
    normalized_data = SignupData(
        display_name=data.display_name.strip(),
        email=normalize_email(data.email),
        password=data.password,
        confirm_password=data.confirm_password,
        accepted_terms=data.accepted_terms,
    )

    validate_signup_data(normalized_data)

    existing_user = db.session.execute(
        db.select(User).where(User.email == normalized_data.email)
    ).scalar_one_or_none()

    if existing_user is not None:
        raise DuplicateEmailError(
            "An account with that email already exists."
        )

    user = User(
        display_name=normalized_data.display_name,
        email=normalized_data.email,
        password_hash="",
    )
    user.set_password(normalized_data.password)

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        raise DuplicateEmailError(
            "An account with that email already exists."
        ) from error

    return user


def authenticate_user(email: str, password: str) -> User | None:
    """Return the matching user when the credentials are valid."""

    normalized_email = normalize_email(email)

    if not normalized_email or not password:
        return None

    user = db.session.execute(
        db.select(User).where(User.email == normalized_email)
    ).scalar_one_or_none()

    if user is None or not user.check_password(password):
        return None

    return user


def create_or_link_google_user(
    *,
    google_sub: str,
    email: str,
    email_verified: bool,
    display_name: str,
    avatar_url: str | None,
) -> User:
    """Create or update a user authenticated through Google."""

    if not google_sub:
        raise ValueError("Google profile is missing a subject identifier.")

    normalized_email = normalize_email(email)

    if not normalized_email or not email_verified:
        raise ValueError("Google did not provide a verified email address.")

    user = db.session.execute(
        db.select(User).where(User.google_sub == google_sub)
    ).scalar_one_or_none()

    if user is None:
        user = db.session.execute(
            db.select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()

    if user is None:
        user = User(
            email=normalized_email,
            display_name=display_name.strip() or normalized_email,
            password_hash=None,
            google_sub=google_sub,
            avatar_url=avatar_url,
        )
        db.session.add(user)
    else:
        if user.google_sub not in (None, google_sub):
            raise ValueError(
                "That email address is linked to another Google account."
            )

        user.google_sub = google_sub

        if display_name.strip():
            user.display_name = display_name.strip()

        if avatar_url:
            user.avatar_url = avatar_url

    db.session.commit()

    return user