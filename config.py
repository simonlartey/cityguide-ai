import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-before-production",
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'cityguide.db'}",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False