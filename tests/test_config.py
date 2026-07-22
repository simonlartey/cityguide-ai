import importlib

import config


def reload_config(monkeypatch, **environment):
    """Reload configuration after applying environment variables."""

    monkeypatch.setattr(
        "dotenv.load_dotenv",
        lambda *args, **kwargs: False,
    )

    variable_names = (
        "PLACES_PROVIDER",
        "ASSISTANT_PROVIDER",
        "OPENAI_API_KEY",
        "ASSISTANT_MODEL",
        "PLACES_API_KEY",
        "PLACES_REQUEST_TIMEOUT_SECONDS",
    )

    for variable_name in variable_names:
        monkeypatch.delenv(variable_name, raising=False)

    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    return importlib.reload(config).Config


def test_places_provider_defaults_to_mock(monkeypatch):
    config_class = reload_config(monkeypatch)

    assert config_class.PLACES_PROVIDER == "mock"


def test_places_configuration_reads_environment(monkeypatch):
    config_class = reload_config(
        monkeypatch,
        PLACES_PROVIDER="LIVE",
        PLACES_API_KEY="test-api-key",
        PLACES_REQUEST_TIMEOUT_SECONDS="5.5",
    )

    assert config_class.PLACES_PROVIDER == "live"
    assert config_class.PLACES_API_KEY == "test-api-key"
    assert config_class.PLACES_REQUEST_TIMEOUT_SECONDS == 5.5


def test_assistant_provider_defaults_to_fake(monkeypatch):
    config_class = reload_config(monkeypatch)

    assert config_class.ASSISTANT_PROVIDER == "fake"


def test_assistant_provider_reads_environment(monkeypatch):
    config_class = reload_config(
        monkeypatch,
        ASSISTANT_PROVIDER="FAKE",
    )

    assert config_class.ASSISTANT_PROVIDER == "fake"


def test_openai_configuration_defaults_to_none(monkeypatch):
    config_class = reload_config(monkeypatch)

    assert config_class.OPENAI_API_KEY is None
    assert config_class.ASSISTANT_MODEL is None


def test_openai_configuration_reads_environment(monkeypatch):
    config_class = reload_config(
        monkeypatch,
        OPENAI_API_KEY="test-openai-key",
        ASSISTANT_MODEL="test-model",
    )

    assert config_class.OPENAI_API_KEY == "test-openai-key"
    assert config_class.ASSISTANT_MODEL == "test-model"
