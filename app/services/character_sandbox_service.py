import logging
import asyncio
import re
from typing import List, Tuple
from app.schemas import ContinueConversationRequest, Participant, Conversation, InitalizeCharactersRequest, DialogTurn
from app.utils.env_validator import validate_chai_api_key
from app.clients.chai_api_client import CHAIAPIClient

logger = logging.getLogger(__name__)

class CharacterSandboxService:
    """
    Service for handling character sandbox operations.
    """
    
    def __init__(self):
        self.api_key = validate_chai_api_key()
        self.chai_client = CHAIAPIClient()
        self.REQUEST_STAGGER_TIME_SECONDS = 5
        self.generated_character_names: List[str] = []
    
    def post_process_character_name_generation_response(self, response: str) -> str:
        """
        Process the raw response from the CHAI API for character name generation.
        
        Args:
            response: The raw response from the CHAI API
            
        Returns:
            The extracted character name
        """
        character_name = re.split(r'\.|\*|Jason|<| ', response)[0]  # Extract the name before any additional text
        self.generated_character_names.append(character_name)
        return character_name
    
    def post_process_continue_conversation_response(self, response: str) -> str:
        """
        Process the raw response from the CHAI API for conversation continuation.
        
        Args:
            response: The raw response from the CHAI API
            
        Returns:
            The processed response with any content after 'USER' removed
        """
        if "USER" in response:
            response = re.split('USER', response)[0]
        if ":" in response:
            response = re.split(':', response)[0]
        return response
    
    async def _generate_character(self, index: int) -> Tuple[Participant, int]:
        """
        Generate a complete character (name and backstory) using the CHAI API.
        The API uses a staggered approach to avoid 429 errors due to rate limits.
        The stagger time was set to 5 seconds, but this can be adjusted if we can remove the throttling
        which has apparently been applied to this API key.
        
        Args:
            index: The index of the character being generated
            
        Returns:
            A tuple containing the generated Participant and the original index
        """
        try:
            if index > 0:
              await asyncio.sleep(self.REQUEST_STAGGER_TIME_SECONDS * index)
              
            # Generate character name
            response_from_charAI_link1 = await self.chai_client.invoke_llm(
                prompt="An engaging texting conversation between Jason and Brian, an author and his cowriter. Jason is working on a new fantasy novel, and he comes to Brian when he needs help coming up with character names.",
                character_1_name="Brian",
                character_2_name="Jason",
                chat_history=[
                  {"sender": "Jason", "message": "Hey Brian, I need your help coming up with some characters for my new novel. Can you make up new character's name? Just the name, please."},
                  {"sender": "Brian", "message": self.generated_character_names[-1] if self.generated_character_names else "Seraphina Vale."}, # hack to prevent the same name from being generated twice (LLM temperature/top_p is not a parameter which can be set via API). This amounts to a RANDOM_SEED in the LLM input.
                  {"sender": "Jason", "message": "Perfect! One more... just the first name and last name, please."},
                ]
            )

            character_name = self.post_process_character_name_generation_response(response_from_charAI_link1)

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
                    name="Unknown",
                    backstory="A curious human exploring in a fantasy realm."
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
    
    def _determine_next_speaker(self, conversation: Conversation) -> Participant:
        """
        Determine which character should speak next in the conversation.
        
        Logic:
        1. If there are dialog turns, find a character who isn't the most recent speaker
        2. If there are no dialog turns, choose a random AI character
        3. If there are characters which haven't been mentioned in the last 5 dialog turns, choose one of them at random
        
        Args:
            conversation: The current conversation state
            
        Returns:
            The participant who should speak next
        """
        import random
        
        ai_participants = [p for p in conversation.participants if p.type == "AI"]
        
        if not ai_participants:
            logger.error("No AI participants found in the conversation")
            raise ValueError("Unable to choose next speaker; no AI participants found in the conversation")
        
        # If there are no dialog turns, choose a random AI character
        if not conversation.dialogTurns:
            return random.choice(ai_participants)
        
        most_recent_turn = conversation.dialogTurns[-1]
        most_recent_speaker_name = most_recent_turn.participant
        
        # Check if the most recent message mentions or addresses another character
        # This is a simple implementation - just check if any character's name is in the message
        mentioned_participants = []
        for participant in ai_participants:
            # Skip the most recent speaker
            if participant.name == most_recent_speaker_name:
                continue
                
            # Check if this participant's name is mentioned in the most recent message
            if participant.name in most_recent_turn.content:
                mentioned_participants.append(participant)
        
        # If any characters were mentioned, choose one of them
        if mentioned_participants:
            return random.choice(mentioned_participants)
        
        # Check for characters not mentioned in the last 5 dialog turns
        # Get the last 5 dialog turns (or fewer if there aren't 5)
        recent_turns = conversation.dialogTurns[-5:] if len(conversation.dialogTurns) >= 5 else conversation.dialogTurns
        
        # Find all characters mentioned in these turns
        recently_mentioned_names = set()
        for turn in recent_turns:
            # Add the speaker
            recently_mentioned_names.add(turn.participant)
            
            # Check for mentions of other characters in the content
            for participant in ai_participants:
                if participant.name in turn.content:
                    recently_mentioned_names.add(participant.name)
        
        # Find characters who haven't been mentioned recently
        not_recently_mentioned = [p for p in ai_participants if p.name not in recently_mentioned_names]
        
        # If there are characters who haven't been mentioned recently, choose one
        if not_recently_mentioned:
            return random.choice(not_recently_mentioned)
        
        # otherwise, choose a random AI character who isn't the most recent speaker
        available_speakers = [p for p in ai_participants if p.name != most_recent_speaker_name]
        
        # If all AI characters have spoken and there's only one, we have to reuse them
        if not available_speakers and ai_participants:
            return ai_participants[0]
            
        return random.choice(available_speakers) if available_speakers else random.choice(ai_participants)
    
    def _format_chat_history(self, conversation: Conversation) -> list:
        """
        Format the conversation's dialog turns into the format expected by the CHAI API.
        
        Args:
            conversation: The current conversation state
            
        Returns:
            A list of dictionaries with 'sender' and 'message' keys
        """
        chat_history = []
        
        for turn in conversation.dialogTurns:
            chat_history.append({
                "sender": turn.participant,
                "message": turn.content
            })
            
        return chat_history
    
    def _generate_prompt(self, conversation: Conversation) -> str:
        """
        Generate a prompt for the CHAI API based on the participants in the conversation.
        
        Args:
            conversation: The current conversation state
            
        Returns:
            A string prompt describing the conversation context
        """
        ai_participants = [p for p in conversation.participants if p.type == "AI"]
        
        # Create a basic prompt describing the conversation
        if len(ai_participants) == 1:
            # One-on-one conversation
            return f"An engaging conversation between {ai_participants[0].name} and a user."
        else:
            # Multi-character conversation
            character_names = [p.name for p in ai_participants]
            characters_str = ", ".join(character_names[:-1]) + " and " + character_names[-1] if len(character_names) > 1 else character_names[0]
            
            # Add backstories to provide context
            backstories = []
            for p in ai_participants:
                # Take just the first sentence of each backstory to keep the prompt short
                backstory = p.backstory if p.backstory else ''
                backstories.append(f"{p.name}: {backstory}")
            
            backstories_str = " ".join(backstories)
            
            return f"A dialogue amongst fantasy characters in a magical realm. {characters_str}. {backstories_str}"
    
    def _get_most_recent_speaker(self, conversation: Conversation) -> str:        
        return conversation.dialogTurns[-1].participant
    
    async def continue_conversation(self, request: ContinueConversationRequest) -> Conversation:
        conversation = request.conversation
        
        # 1. Determine who should speak next. This will end up as the character_1_name in the CHAI API client request.
        next_speaker = self._determine_next_speaker(conversation)
        
        # 2. Format the chat history for the CHAI API
        chat_history = self._format_chat_history(conversation)
        
        # If there are no dialog turns, we need to bootstrap the conversation
        if not chat_history:
            # Create a generic greeting from the first speaker
            greeting = f"Hello. I am {next_speaker.name}."
            
            # Add it to the chat history
            chat_history.append({
                "sender": next_speaker.name,
                "message": greeting
            })
            
            # Also add it to the conversation as the first dialog turn
            conversation.dialogTurns.append(
                DialogTurn(
                    participant=next_speaker.name,
                    content=greeting
                )
            )
            
            # Return the conversation with the initial greeting
            return conversation
        
        # 3. Generate an appropriate prompt
        prompt = self._generate_prompt(conversation)
        
        # 4. Determine the most recent speaker (for CHAI API parameters)
        most_recent_speaker = self._get_most_recent_speaker(conversation)
        
        logger.info(f"Continuing conversation with next speaker: {next_speaker.name}")
        logger.info(f"Chat history: {chat_history}")
        
        # 5. Call the CHAI API to generate a response
        response_from_charAI = await self.chai_client.invoke_llm(
            prompt=prompt,
            character_1_name=next_speaker.name, # this should be the participant we want to speak next
            character_2_name=most_recent_speaker, # this should be the last participant in the chat history
            chat_history=chat_history
        )

        response_from_charAI = self.post_process_continue_conversation_response(response_from_charAI)
        
        # 6. Add the response to the conversation
        conversation.dialogTurns.append(
            DialogTurn(
                participant=next_speaker.name,
                content=response_from_charAI
            )
        )
        
        return conversation
