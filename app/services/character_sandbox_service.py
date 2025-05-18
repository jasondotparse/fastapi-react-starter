import json
import logging
from typing import List, Dict
from app.schemas import Participant, Conversation, InitalizeCharactersRequest, DialogTurn
from app.utils.env_validator import validate_chai_api_key
from app.clients.chai_api_client import CHAIAPIClient

logger = logging.getLogger(__name__)

class CharacterSandboxService:
    """
    Service for handling character sandbox operations.
    """
    
    def __init__(self):
        """
        Initialize the service and validate the CHAI API key.
        """
        # Validate that the CHAI API key is present
        self.api_key = validate_chai_api_key()
        # Initialize the CHAI API client
        self.chai_client = CHAIAPIClient()
        logger.info("CharacterSandboxService initialized with valid API key and CHAI API client")
    
    def initialize_characters(self, request: InitalizeCharactersRequest) -> List[Participant]:
        logger.info(f"Initializing {request.count} characters with userEngagement={request.userEngagementEnabled}")
        
        participants = []
        
        if request.userEngagementEnabled:
            participants.append(
                Participant(
                    type="HUMAN",
                    name="User",
                    backstory="A curious human exploring conversations with AI characters."
                )
            )
        
        for i in range(request.count):

            # Call the CHAI API to generate a character name
            try:
                response_from_charAI_link1 = self.chai_client.invoke_llm(
                    prompt="An engaging texting conversation between Jason and Brian, an author and his cowriter. Jason is working on a new fantasy novel, and he comes to Brian when he has writer's block.",
                    character_1_name="Brian",
                    character_2_name="Jason",
                    chat_history=[
                      {"sender": "Jason", "message": "Hey Brian, I need your help coming up with some characters for my new novel. Can you make up new character's name? Just the name, please."},
                      {"sender": "Brian", "message": "Eamon Blackwood."},
                      {"sender": "Jason", "message": "Perfect! One more... just the first name and last name, please."},
                    ]
                )

                character_name = response_from_charAI_link1.split(".")[0]

                logger.info(f"Generated character name: {character_name}")

                response_from_charAI_link2 = self.chai_client.invoke_llm(
                    prompt="An engaging texting conversation between Jason and Brian, an author and his cowriter. Jason is working on a new fantasy novel, and he comes to Brian when he has writer's block.",
                    character_1_name="Brian",
                    character_2_name="Jason",
                    chat_history=[
                      {"sender": "Jason", "message": "Hey Brian, I need your help coming up with a backstory for a new character in my fantasy novel. Name: Seraphina Vale. Make up this character's backstory, and key attributes!"},
                      {"sender": "Brian", "message": "Seraphina is a half-angel, half-human warrior born in the celestial realm of Valoria. She was exiled from Valoria at a young age due to her rebellious nature and powerful magic which threatened the angelic rulers there."},
                      {"sender": "Jason", "message": f"Amazing!, Ok, now one more. Name: {character_name}."}
                    ]
                )

                logger.info(f"Generated character backstory: {response_from_charAI_link2}")
                
                participants.append(
                    Participant(
                        type="AI",
                        name=character_name,
                        backstory="todo"
                    )
                )
                
            except Exception as e:
                logger.error(f"Error generating character {i+1}: {str(e)}")
                # Add a default character in case of error
                participants.append(
                    Participant(
                        type="AI",
                        name=f"Character{i+1}",
                        backstory=f"A mysterious character from a fantasy world."
                    )
                )
        
        return participants
    
    def continue_conversation(self, conversation: Conversation) -> Conversation:
        """
        Continue a conversation by generating the next AI response.
        
        Args:
            conversation: The current state of the conversation
            
        Returns:
            The updated conversation
        """
        # For now, return the conversation as is
        # TODO: Implement conversation continuation using CHAI API
        logger.info(f"Continuing conversation with {len(conversation.participants)} participants and {len(conversation.dialogTurns)} turns")
        return conversation
