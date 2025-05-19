import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ContinueConversation from './ContinueConversation';
import { Conversation, Participant, DialogTurn } from '../types/models';
import { agentPlaygroundBackendClient } from '../services/AgentPlaygroundBackendClient';

// Mock the backend client
jest.mock('../services/AgentPlaygroundBackendClient', () => ({
  agentPlaygroundBackendClient: {
    continueConversation: jest.fn()
  }
}));

// Mock data for testing
const mockHumanParticipant: Participant = {
  type: 'HUMAN',
  name: 'Stranger',
  backstory: 'A curious human exploring in a fantasy realm.'
};

const mockAIParticipant: Participant = {
  type: 'AI',
  name: 'Seraphina Vale',
  backstory: 'A half-angel, half-human warrior born in the celestial realm of Valoria.'
};

const mockDialogTurns: DialogTurn[] = [
  {
    participant: 'Stranger',
    content: 'Hello, I\'m new to this realm. Who are you?'
  },
  {
    participant: 'Seraphina Vale',
    content: 'Greetings, traveler. I am Seraphina Vale, a warrior from the celestial realm of Valoria.'
  }
];

// Create conversation with both human and AI participants
const mockConversationWithHuman: Conversation = {
  participants: [mockHumanParticipant, mockAIParticipant],
  dialogTurns: [...mockDialogTurns]
};

// Create conversation with only AI participants
const mockConversationAIOnly: Conversation = {
  participants: [mockAIParticipant],
  dialogTurns: [...mockDialogTurns]
};

// Mock updated conversation after API call
const mockUpdatedConversation: Conversation = {
  participants: [mockHumanParticipant, mockAIParticipant],
  dialogTurns: [
    ...mockDialogTurns,
    {
      participant: 'Stranger',
      content: 'Tell me more about Valoria.'
    },
    {
      participant: 'Seraphina Vale',
      content: 'Valoria is a celestial realm of eternal light, where angelic beings dwell in harmony with the cosmic energies.'
    }
  ]
};

describe('ContinueConversation', () => {
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
    (agentPlaygroundBackendClient.continueConversation as jest.Mock).mockResolvedValue(mockUpdatedConversation);
  });

  // Rendering tests
  describe('Rendering', () => {
    test('renders with user participants', () => {
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={jest.fn()} 
        />
      );
      
      // Check that the textarea is rendered
      expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
      
      // Check that the continue button is rendered
      expect(screen.getByText('Continue Conversation')).toBeInTheDocument();
    });

    test('does not render input field without user participants', () => {
      render(
        <ContinueConversation 
          conversation={mockConversationAIOnly} 
          setConversation={jest.fn()} 
        />
      );
      
      // Check that the textarea is not rendered
      expect(screen.queryByPlaceholderText('Type your message...')).not.toBeInTheDocument();
      
      // Check that the continue button is still rendered
      expect(screen.getByText('Continue Conversation')).toBeInTheDocument();
    });

    test('renders loading state', () => {
      // Mock implementation to delay resolution
      (agentPlaygroundBackendClient.continueConversation as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockUpdatedConversation), 100))
      );
      
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={jest.fn()} 
        />
      );
      
      // Click the continue button to trigger loading state
      fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
        target: { value: 'Test message' }
      });
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Check that the button text changes to "Processing..."
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    test('renders error message when API call fails', async () => {
      // Mock implementation to reject
      (agentPlaygroundBackendClient.continueConversation as jest.Mock).mockRejectedValue(
        new Error('API error')
      );
      
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={jest.fn()} 
        />
      );
      
      // Click the continue button to trigger API call
      fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
        target: { value: 'Test message' }
      });
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Wait for the error message to appear
      await waitFor(() => {
        expect(screen.getByText('Failed to continue conversation. Please try again.')).toBeInTheDocument();
      });
    });
  });

  // User input tests
  describe('User Input', () => {
    test('allows typing in textarea', () => {
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={jest.fn()} 
        />
      );
      
      const textarea = screen.getByPlaceholderText('Type your message...');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      
      expect(textarea).toHaveValue('Test message');
    });

    test('clears input after successful submission', async () => {
      const setConversationMock = jest.fn();
      
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={setConversationMock} 
        />
      );
      
      const textarea = screen.getByPlaceholderText('Type your message...');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Wait for the API call to complete
      await waitFor(() => {
        expect(setConversationMock).toHaveBeenCalledWith(mockUpdatedConversation);
      });
      
      // Check that the textarea is cleared
      expect(textarea).toHaveValue('');
    });
  });

  // Button state tests
  describe('Continue Button', () => {
    test('is disabled in one-on-one conversation with no input', () => {
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={jest.fn()} 
        />
      );
      
      // Check that the button is disabled
      expect(screen.getByText('Continue Conversation')).toBeDisabled();
      
      // Add some input
      fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
        target: { value: 'Test message' }
      });
      
      // Check that the button is now enabled
      expect(screen.getByText('Continue Conversation')).not.toBeDisabled();
    });

    test('is enabled in AI-only conversation without input', () => {
      render(
        <ContinueConversation 
          conversation={mockConversationAIOnly} 
          setConversation={jest.fn()} 
        />
      );
      
      // Check that the button is enabled
      expect(screen.getByText('Continue Conversation')).not.toBeDisabled();
    });

    test('is disabled during loading', async () => {
      // Mock implementation to delay resolution
      (agentPlaygroundBackendClient.continueConversation as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockUpdatedConversation), 100))
      );
      
      render(
        <ContinueConversation 
          conversation={mockConversationAIOnly} 
          setConversation={jest.fn()} 
        />
      );
      
      // Click the continue button to trigger loading state
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Check that the button is disabled during loading
      expect(screen.getByText('Processing...')).toBeDisabled();
    });
  });

  // Functionality tests
  describe('API Interaction', () => {
    test('calls backend service when continue button is clicked', async () => {
      const setConversationMock = jest.fn();
      
      render(
        <ContinueConversation 
          conversation={mockConversationAIOnly} 
          setConversation={setConversationMock} 
        />
      );
      
      // Click the continue button
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Wait for the backend service to be called
      await waitFor(() => {
        expect(agentPlaygroundBackendClient.continueConversation).toHaveBeenCalledWith(mockConversationAIOnly);
      });
      
      // Wait for the setConversation to be called
      await waitFor(() => {
        expect(setConversationMock).toHaveBeenCalled();
      });
      
      // Check that the conversation state was updated with the mock response
      expect(setConversationMock).toHaveBeenCalledWith(mockUpdatedConversation);
    });

    test('adds user input to conversation before API call', async () => {
      const setConversationMock = jest.fn();
      const userInput = 'Tell me more about Valoria.';
      
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={setConversationMock} 
        />
      );
      
      // Add user input
      fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
        target: { value: userInput }
      });
      
      // Click the continue button
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Wait for the API call to complete
      await waitFor(() => {
        expect(agentPlaygroundBackendClient.continueConversation).toHaveBeenCalled();
      });
      
      // Check that the backend service was called with the updated conversation
      expect(agentPlaygroundBackendClient.continueConversation).toHaveBeenCalledWith(
        expect.objectContaining({
          dialogTurns: [
            ...mockDialogTurns,
            {
              participant: 'Stranger',
              content: userInput
            }
          ]
        })
      );
    });

    test('handles API errors gracefully', async () => {
      // Mock implementation to reject
      (agentPlaygroundBackendClient.continueConversation as jest.Mock).mockRejectedValue(
        new Error('API error')
      );
      
      const setConversationMock = jest.fn();
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      render(
        <ContinueConversation 
          conversation={mockConversationWithHuman} 
          setConversation={setConversationMock} 
        />
      );
      
      // Add user input
      fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
        target: { value: 'Test message' }
      });
      
      // Click the continue button
      fireEvent.click(screen.getByText('Continue Conversation'));
      
      // Wait for the error message to appear
      await waitFor(() => {
        expect(screen.getByText('Failed to continue conversation. Please try again.')).toBeInTheDocument();
      });
      
      // Check that the error was logged
      expect(consoleErrorSpy).toHaveBeenCalled();
      
      // Check that the conversation state was not updated
      expect(setConversationMock).not.toHaveBeenCalled();
      
      // Restore console.error
      consoleErrorSpy.mockRestore();
    });
  });
});
