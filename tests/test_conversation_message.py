import pytest

from app.models.conversation_message import (
    ConversationMessage,
    MessageRole,
)


def test_conversation_message_stores_role_and_content():
    message = ConversationMessage(
        role=MessageRole.USER,
        content="Find a quiet coffee shop.",
    )

    assert message.role is MessageRole.USER
    assert message.content == "Find a quiet coffee shop."


def test_message_roles_have_expected_string_values():
    assert MessageRole.USER.value == "user"
    assert MessageRole.ASSISTANT.value == "assistant"
    assert MessageRole.SYSTEM.value == "system"


def test_conversation_message_is_immutable():
    message = ConversationMessage(
        role=MessageRole.ASSISTANT,
        content="Here are three options.",
    )

    with pytest.raises(AttributeError):
        message.content = "Changed"
