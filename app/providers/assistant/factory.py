from app.providers.assistant.base import AssistantProvider
from app.providers.assistant.fake_provider import FakeAssistantProvider
from app.providers.assistant.openai_provider import (
    OpenAIAssistantProvider,
)


def create_assistant_provider(config: dict) -> AssistantProvider:
    """Create the assistant provider selected by application configuration."""

    provider_name = config.get(
        "ASSISTANT_PROVIDER",
        "fake",
    )

    if provider_name == "fake":
        return FakeAssistantProvider()

    if provider_name == "openai":
        return OpenAIAssistantProvider(
            api_key=config.get("OPENAI_API_KEY"),
            model=config.get("ASSISTANT_MODEL"),
        )

    raise ValueError(
        f"Unsupported assistant provider: {provider_name}"
    )
