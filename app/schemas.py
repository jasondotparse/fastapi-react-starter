# schemas.py
from pydantic import BaseModel
from typing import List
from pydantic import Field

class InitalizeCharactersRequest(BaseModel):
    """
    This API is invoked at the start of a conversation, to generate a cast of AI agents which will 
    List<Participant> (see section "data model" below) in the conversation.
    """
    count: int
    userEngagementEnabled: bool

class Participant(BaseModel):
    """
    Represents a participant in the conversation.
    """
    type: str
    backstory: str
    name: str

class DialogTurn(BaseModel):
    """
     The primitive for a single turn in the conversation.
    """
    participant: str
    content: str

class Conversation(BaseModel):
    """
      The core data model for the conversation. Defines the entire conversation state at a given point in time. 
    """
    participants: List[Participant]
    dialogTurns: List[DialogTurn]