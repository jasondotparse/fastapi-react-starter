"""
Shared fixtures for pytest tests.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.schemas import Participant, DialogTurn, Conversation, InitalizeCharactersRequest
from app.clients.chai_api_client import CHAIAPIClient

@pytest.fixture
def mock_chai_api_key():
    """Mock the validate_chai_api_key function to return a dummy API key."""
    with patch('app.utils.env_validator.validate_chai_api_key') as mock:
        mock.return_value = "Bearer dummy_api_key"
        yield mock

@pytest.fixture
def mock_chai_client():
    """Create a mock CHAIAPIClient with a mocked invoke_llm method."""
    with patch('app.clients.chai_api_client.CHAIAPIClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.invoke_llm = AsyncMock()
        mock_client_class.return_value = mock_client
        yield mock_client

@pytest.fixture
def sample_participants():
    """Create a list of sample participants for testing."""
    return [
        Participant(
            type="HUMAN",
            name="Stranger",
            backstory="A curious human exploring in a fantasy realm."
        ),
        Participant(
            type="AI",
            name="Seraphina Vale",
            backstory="A half-angel, half-human warrior born in the celestial realm of Valoria."
        ),
        Participant(
            type="AI",
            name="Thorne Blackwood",
            backstory="A mysterious druid with the ability to communicate with ancient forest spirits."
        )
    ]

@pytest.fixture
def sample_dialog_turns():
    """Create a list of sample dialog turns for testing."""
    return [
        DialogTurn(
            participant="Stranger",
            content="Hello, I'm new to this realm. Who are you?"
        ),
        DialogTurn(
            participant="Seraphina Vale",
            content="Greetings, traveler. I am Seraphina Vale, a warrior from the celestial realm of Valoria."
        ),
        DialogTurn(
            participant="Thorne Blackwood",
            content="*steps from the shadows* I am Thorne Blackwood, keeper of the ancient forest secrets."
        )
    ]

@pytest.fixture
def sample_conversation(sample_participants, sample_dialog_turns):
    """Create a sample conversation for testing."""
    return Conversation(
        participants=sample_participants,
        dialogTurns=sample_dialog_turns
    )

@pytest.fixture
def sample_empty_conversation(sample_participants):
    """Create a sample conversation with no dialog turns for testing."""
    return Conversation(
        participants=sample_participants,
        dialogTurns=[]
    )

@pytest.fixture
def sample_initialize_request():
    """Create a sample initialize characters request for testing."""
    return InitalizeCharactersRequest(
        count=2,
        userEngagementEnabled=True
    )

@pytest.fixture
def mock_character_name_response():
    """Mock response for character name generation."""
    return "Elara Moonwhisper"

@pytest.fixture
def mock_character_backstory_response():
    """Mock response for character backstory generation."""
    return "Elara Moonwhisper is a celestial sorceress who draws her power from the moon. Born during a rare lunar eclipse, she possesses the ability to manipulate moonlight and communicate with celestial beings."

@pytest.fixture
def mock_continue_conversation_response():
    """Mock response for conversation continuation."""
    return "I sense a disturbance in the magical energies of this realm. Something ancient is awakening."
