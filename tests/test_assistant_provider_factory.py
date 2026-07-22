import pytest

from app.providers.assistant.factory import (
    create_assistant_provider,
)
from app.providers.assistant.fake_provider import (
    FakeAssistantProvider,
)
from app.providers.assistant.openai_provider import (
    OpenAIAssistantProvider,
)


def test_factory_defaults_to_fake_provider():
    provider = create_assistant_provider({})

    assert isinstance(provider, FakeAssistantProvider)


def test_factory_creates_fake_provider():
    provider = create_assistant_provider(
        {
            "ASSISTANT_PROVIDER": "fake",
        }
    )

    assert isinstance(provider, FakeAssistantProvider)


def test_factory_creates_openai_provider():
    provider = create_assistant_provider(
        {
            "ASSISTANT_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-openai-key",
            "ASSISTANT_MODEL": "test-model",
        }
    )

    assert isinstance(provider, OpenAIAssistantProvider)
    assert provider.model == "test-model"


def test_factory_requires_openai_api_key():
    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is required",
    ):
        create_assistant_provider(
            {
                "ASSISTANT_PROVIDER": "openai",
                "OPENAI_API_KEY": None,
                "ASSISTANT_MODEL": "test-model",
            }
        )


def test_factory_requires_openai_model():
    with pytest.raises(
        ValueError,
        match="ASSISTANT_MODEL is required",
    ):
        create_assistant_provider(
            {
                "ASSISTANT_PROVIDER": "openai",
                "OPENAI_API_KEY": "test-openai-key",
                "ASSISTANT_MODEL": None,
            }
        )


def test_factory_rejects_unsupported_provider():
    with pytest.raises(
        ValueError,
        match="Unsupported assistant provider: unknown",
    ):
        create_assistant_provider(
            {
                "ASSISTANT_PROVIDER": "unknown",
            }
        )
