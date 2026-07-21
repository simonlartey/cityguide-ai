import pytest

from app.providers.assistant.factory import (
    create_assistant_provider,
)
from app.providers.assistant.fake_provider import (
    FakeAssistantProvider,
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
