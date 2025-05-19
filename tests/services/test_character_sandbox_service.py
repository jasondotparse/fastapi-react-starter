"""
Unit tests for the CharacterSandboxService class.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.character_sandbox_service import CharacterSandboxService
from app.schemas import Participant, DialogTurn, Conversation, ContinueConversationRequest

class TestCharacterSandboxService:
    """Test cases for the CharacterSandboxService class."""

    def test_post_process_character_name_generation_response(self, mock_chai_api_key):
        """Test that character names are correctly extracted from API responses."""
        service = CharacterSandboxService()
        
        # Test simple name extraction
        response = "Elara Moonwhisper"
        result = service.post_process_character_name_generation_response(response)
        assert result == "Elara"
        
        # Test name extraction with additional text
        response = "Thorne Blackwood. He's a mysterious druid."
        result = service.post_process_character_name_generation_response(response)
        assert result == "Thorne"
        
        # Test name extraction with special characters
        response = "Zephyr*the wind mage"
        result = service.post_process_character_name_generation_response(response)
        assert result == "Zephyr"

        # Test name extraction when the LLM squishes generations together
        response = "AllerienJason: thanks a lot! Ok, now can you make a new name for me?"
        result = service.post_process_character_name_generation_response(response)
        assert result == "Allerien"
        
        # Test that the name is added to generated_character_names
        assert "Elara" in service.generated_character_names
        assert "Thorne" in service.generated_character_names
        assert "Zephyr" in service.generated_character_names
        assert "Allerien" in service.generated_character_names

    def test_post_process_continue_conversation_response(self, mock_chai_api_key):
        """Test that conversation responses are correctly processed."""
        service = CharacterSandboxService()
        
        # Test simple response
        response = "I sense a disturbance in the magical energies."
        result = service.post_process_continue_conversation_response(response)
        assert result == response
        
        # Test response with USER
        response = "I sense a disturbance in the magical energies. USER: What kind of disturbance?"
        result = service.post_process_continue_conversation_response(response)
        assert result == "I sense a disturbance in the magical energies. "
        
        # Test response with colon
        response = "Elara: I sense a disturbance in the magical energies."
        result = service.post_process_continue_conversation_response(response)
        assert result == "Elara"

    def test_format_chat_history(self, mock_chai_api_key, sample_conversation):
        """Test that chat history is correctly formatted for the CHAI API."""
        service = CharacterSandboxService()
        
        chat_history = service._format_chat_history(sample_conversation)
        
        assert len(chat_history) == 3
        assert chat_history[0]["sender"] == "Stranger"
        assert chat_history[0]["message"] == "Hello, I'm new to this realm. Who are you?"
        assert chat_history[1]["sender"] == "Seraphina Vale"
        assert chat_history[1]["message"] == "Greetings, traveler. I am Seraphina Vale, a warrior from the celestial realm of Valoria."
        assert chat_history[2]["sender"] == "Thorne Blackwood"
        assert chat_history[2]["message"] == "*steps from the shadows* I am Thorne Blackwood, keeper of the ancient forest secrets."

    def test_generate_prompt(self, mock_chai_api_key, sample_conversation, sample_empty_conversation):
        """Test that prompts are correctly generated for different conversation scenarios."""
        service = CharacterSandboxService()
        
        # Test prompt for conversation with multiple AI participants
        prompt = service._generate_prompt(sample_conversation)
        assert "dialogue amongst fantasy characters" in prompt.lower()
        assert "Seraphina Vale" in prompt
        assert "Thorne Blackwood" in prompt
        
        # Create a conversation with only one AI participant
        one_ai_conversation = Conversation(
            participants=[
                Participant(
                    type="HUMAN",
                    name="Stranger",
                    backstory="A curious human exploring in a fantasy realm."
                ),
                Participant(
                    type="AI",
                    name="Seraphina Vale",
                    backstory="A half-angel, half-human warrior born in the celestial realm of Valoria."
                )
            ],
            dialogTurns=[]
        )
        
        # Test prompt for conversation with one AI participant
        prompt = service._generate_prompt(one_ai_conversation)
        assert "engaging conversation between seraphina vale and a user" in prompt.lower()
        assert "mystical in a fantasy novel" in prompt

    def test_determine_next_speaker_empty_conversation(self, mock_chai_api_key, sample_empty_conversation):
        """Test that a random AI character is chosen when there are no dialog turns."""
        service = CharacterSandboxService()
        
        next_speaker = service._determine_next_speaker(sample_empty_conversation)
        
        assert next_speaker.type == "AI"
        assert next_speaker.name in ["Seraphina Vale", "Thorne Blackwood"]

    def test_determine_next_speaker_with_turns(self, mock_chai_api_key, sample_conversation):
        """Test that an appropriate next speaker is chosen based on conversation state."""
        service = CharacterSandboxService()
        
        # The last speaker in sample_conversation is Thorne Blackwood
        next_speaker = service._determine_next_speaker(sample_conversation)
        
        # The next speaker should not be Thorne Blackwood
        assert next_speaker.name != "Thorne Blackwood"
        assert next_speaker.type == "AI"
        assert next_speaker.name in ["Seraphina Vale"]
        
        # Test with a character mentioned in the last message
        conversation = Conversation(
            participants=sample_conversation.participants,
            dialogTurns=[
                DialogTurn(
                    participant="Stranger",
                    content="Hello, I'm new to this realm. Who are you?"
                ),
                DialogTurn(
                    participant="Seraphina Vale",
                    content="Greetings, traveler. I am Seraphina Vale, a warrior from the celestial realm of Valoria. Thorne Blackwood, would you like to introduce yourself?"
                )
            ]
        )
        
        next_speaker = service._determine_next_speaker(conversation)
        assert next_speaker.name == "Thorne Blackwood"

    @pytest.mark.asyncio
    async def test_initialize_characters(self, mock_chai_api_key, mock_chai_client, sample_initialize_request, mock_character_name_response, mock_character_backstory_response):
        """Test that characters are correctly initialized with mocked API responses."""
        # Set up the mock to return specific responses
        mock_chai_client.invoke_llm.side_effect = [
            mock_character_name_response,
            mock_character_backstory_response,
            "Another Character",
            "Another character backstory"
        ]
        
        service = CharacterSandboxService()
        service.chai_client = mock_chai_client
        
        participants = await service.initialize_characters(sample_initialize_request)
        
        # Check that the correct number of participants were created
        assert len(participants) == 3  # 1 human + 2 AI
        
        # Check that the human participant was created correctly
        assert participants[0].type == "HUMAN"
        assert participants[0].name == "Stranger"
        
        # Check that the AI participants were created correctly
        assert participants[1].type == "AI"
        assert participants[2].type == "AI"
        
        # Check that the API was called the correct number of times
        assert mock_chai_client.invoke_llm.call_count == 4  # 2 characters * 2 calls each (name + backstory)

    @pytest.mark.asyncio
    async def test_continue_conversation(self, mock_chai_api_key, mock_chai_client, sample_conversation, mock_continue_conversation_response):
        """Test that the conversation is correctly continued with a mocked API response."""
        # Set up the mock to return a specific response
        mock_chai_client.invoke_llm.return_value = mock_continue_conversation_response
        
        service = CharacterSandboxService()
        service.chai_client = mock_chai_client
        
        request = ContinueConversationRequest(conversation=sample_conversation)
        updated_conversation = await service.continue_conversation(request)
        
        # Check that a new dialog turn was added
        assert len(updated_conversation.dialogTurns) == 4
        
        # Check that the new dialog turn has the correct content
        assert updated_conversation.dialogTurns[-1].content == mock_continue_conversation_response
        
        # Check that the API was called
        mock_chai_client.invoke_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_continue_conversation_empty_history(self, mock_chai_api_key, mock_chai_client, sample_empty_conversation, mock_continue_conversation_response):
        """Test that the conversation is correctly continued when there are no existing dialog turns."""
        # Set up the mock to return a specific response
        mock_chai_client.invoke_llm.return_value = mock_continue_conversation_response
        
        service = CharacterSandboxService()
        service.chai_client = mock_chai_client
        
        request = ContinueConversationRequest(conversation=sample_empty_conversation)
        
        # Add a dialog turn to the empty conversation to simulate a user starting the conversation
        request.conversation.dialogTurns.append(
            DialogTurn(
                participant="Stranger",
                content="Hello, I'm new to this realm. Who are you?"
            )
        )
        
        updated_conversation = await service.continue_conversation(request)
        
        # Check that backstory dialog turns were added for each AI character
        # Plus the user's initial message and the AI response
        assert len(updated_conversation.dialogTurns) >= 4
        
        # Check that the new dialog turn has the correct content
        assert updated_conversation.dialogTurns[-1].content == mock_continue_conversation_response
        
        # Check that the API was called
        mock_chai_client.invoke_llm.assert_called_once()
