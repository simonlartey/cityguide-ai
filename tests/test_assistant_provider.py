import pytest

from app.providers.assistant.base import AssistantProvider


def test_assistant_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AssistantProvider()
