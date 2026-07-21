from app.providers.assistant.base import AssistantProvider
from app.providers.assistant.fake_provider import FakeAssistantProvider


def create_assistant_provider(config: dict) -> AssistantProvider:
    """Create the assistant provider selected by application configuration."""

    provider_name = config.get(
        "ASSISTANT_PROVIDER",
        "fake",
    )

    if provider_name == "fake":
        return FakeAssistantProvider()

    raise ValueError(
        f"Unsupported assistant provider: {provider_name}"
    )
