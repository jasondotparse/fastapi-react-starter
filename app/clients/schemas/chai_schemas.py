from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    """
    Represents a single message in a chat conversation.
    
    Attributes:
        sender: The name of the message sender
        message: The content of the message
    """
    sender: str
    message: str

class CHAIAPIRequest(BaseModel):
    """
    Request payload for the CHAI API.
    
    Attributes:
        memory: Deprecated field, but still required by the API
        prompt: The bot's prompt
        bot_name: The name of the character the model is acting as
        user_name: The name of the agent interacting with the model
        chat_history: List of previous messages in the conversation
    """
    memory: str = ""  # Deprecated but required
    prompt: str
    bot_name: str
    user_name: str
    chat_history: List[ChatMessage]

