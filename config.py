import os


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-before-production",
    )