import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-before-production",
    )

    GOOGLE_OAUTH_CLIENT_ID = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_ID",
    )

    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_SECRET",
    )

    PLACES_PROVIDER = os.environ.get(
        "PLACES_PROVIDER",
        "mock",
    ).strip().lower()

    PLACES_API_KEY = os.environ.get(
        "PLACES_API_KEY",
    )

    PLACES_REQUEST_TIMEOUT_SECONDS = float(
        os.environ.get(
            "PLACES_REQUEST_TIMEOUT_SECONDS",
            "10",
        )
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'cityguide.db'}",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False