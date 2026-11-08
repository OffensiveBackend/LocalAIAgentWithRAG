"""
ROLE:
    Conversation and message data structures.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen = True)
class Conversation:
    """
    Represents a persistent conversation.
    
    A conversation is the durable historical record of an interaction.
    It is independent of the temporary session state used to access it.
    """
    
    conversation_id: str
    created_at: datetime
    updated_at: datetime
    

@dataclass(frozen = True)
class Message:
    """
    Represents one message belonging to a conversation.
    """
    
    message_id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime