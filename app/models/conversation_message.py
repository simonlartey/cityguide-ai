from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ConversationMessage:
    role: MessageRole
    content: str
