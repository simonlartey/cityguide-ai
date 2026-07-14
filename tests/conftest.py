import pytest

from app import create_app


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()