import json
import logging
import asyncio
from typing import List, Dict, Tuple
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
        self.REQUEST_STAGGER_TIME_SECONDS = 4
        logger.info("CharacterSandboxService initialized with valid API key and CHAI API client")
    
    async def _generate_character(self, index: int) -> Tuple[Participant, int]:
        """
        Generate a complete character (name and backstory) using the CHAI API.
        
        Args:
            index: The index of the character being generated
            
        Returns:
            A tuple containing the generated Participant and the original index
        """
        try:
            if index > 0:
              # Introduce a staggered delay to avoid rate limiting
              await asyncio.sleep(self.REQUEST_STAGGER_TIME_SECONDS * index)
              
            # Generate character name
            response_from_charAI_link1 = await self.chai_client.invoke_llm(
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

            await asyncio.sleep(self.REQUEST_STAGGER_TIME_SECONDS * 2)

            # Generate character backstory
            response_from_charAI_link2 = await self.chai_client.invoke_llm(
                prompt="An engaging texting conversation between Jason and Brian, an author and his cowriter. Jason is working on a new fantasy novel, and he comes to Brian when he has writer's block.",
                character_1_name="Brian",
                character_2_name="Jason",
                chat_history=[
                  {"sender": "Jason", "message": "Hey Brian, I need your help coming up with a backstory for a new character in my fantasy novel. Name: Seraphina Vale. Make up this character's backstory, and key attributes!"},
                  {"sender": "Brian", "message": "Seraphina is a half-angel, half-human warrior born in the celestial realm of Valoria. She was exiled from Valoria at a young age due to her rebellious nature and powerful magic which threatened the angelic rulers there."},
                  {"sender": "Jason", "message": f"Amazing!, Ok, now one more. Name: {character_name}."}
                ]
            )
            
            logger.info(f"Generated character backstory for {character_name}")
            
            return (
                Participant(
                    type="AI",
                    name=character_name,
                    backstory=response_from_charAI_link2
                ),
                index
            )
        except Exception as e:
            logger.error(f"Error generating character {index+1}: {str(e)}")
            # Return a default character in case of error
            return (
                Participant(
                    type="AI",
                    name=f"Character{index+1}",
                    backstory=f"A mysterious character from a fantasy world."
                ),
                index
            )
    
    async def initialize_characters(self, request: InitalizeCharactersRequest) -> List[Participant]:
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
        
        # Create tasks for generating characters with a 1-second delay between each
        character_tasks = []
        for i in range(request.count):
            task = asyncio.create_task(self._generate_character(i))
            character_tasks.append(task)
        
        # Wait for all character generation tasks to complete
        character_results = await asyncio.gather(*character_tasks)
        
        # Sort results by index to maintain order
        character_results.sort(key=lambda x: x[1])
        
        # Add the generated characters to the participants list
        for participant, _ in character_results:
            participants.append(participant)
        
        logger.info(f"service initialize_characters returning {len(participants)} participants")
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
