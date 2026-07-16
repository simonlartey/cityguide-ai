import importlib

import config


def reload_config(monkeypatch, **environment):
    """Reload configuration after applying environment variables."""

    variable_names = (
        "PLACES_PROVIDER",
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