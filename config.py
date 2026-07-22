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

    ASSISTANT_PROVIDER = os.environ.get(
        "ASSISTANT_PROVIDER",
        "fake",
    ).strip().lower()

    OPENAI_API_KEY = os.environ.get(
        "OPENAI_API_KEY",
    )

    ASSISTANT_MODEL = os.environ.get(
        "ASSISTANT_MODEL",
    )

    PLACES_API_KEY = os.environ.get(
        "PLACES_API_KEY",
    )

    MAPS_JAVASCRIPT_API_KEY = os.environ.get(
        "MAPS_JAVASCRIPT_API_KEY",
    )

    GOOGLE_MAP_ID = os.environ.get(
        "GOOGLE_MAP_ID",
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