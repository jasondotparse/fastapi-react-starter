import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConversationInitializer from './ConversationInitializer';
import { Participant } from '../../types/models';
import { agentPlaygroundBackendClient } from '../../services/AgentPlaygroundBackendClient';

// Mock the backend client
jest.mock('../services/AgentPlaygroundBackendClient', () => ({
  agentPlaygroundBackendClient: {
    initializeConversation: jest.fn()
  }
}));

// Mock data for testing
const mockParticipants: Participant[] = [
  {
    type: 'HUMAN',
    name: 'Stranger',
    backstory: 'A curious human exploring in a fantasy realm.'
  },
  {
    type: 'AI',
    name: 'Seraphina Vale',
    backstory: 'A half-angel, half-human warrior born in the celestial realm of Valoria.'
  },
  {
    type: 'AI',
    name: 'Thorne Blackwood',
    backstory: 'A mysterious druid with the ability to communicate with ancient forest spirits.'
  }
];

describe('ConversationInitializer', () => {
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
    (agentPlaygroundBackendClient.initializeConversation as jest.Mock).mockResolvedValue(mockParticipants);
  });

  // Rendering tests
  describe('Rendering', () => {
    test('renders with default values', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Check that the component title is rendered
      expect(screen.getByText('Initialize Conversation')).toBeInTheDocument();
      
      // Check that the character count is set to 2 by default
      expect(screen.getByText('2')).toBeInTheDocument();
      
      // Check that the user participation checkbox is checked by default
      expect(screen.getByLabelText(/Enable User Participation/i)).toBeChecked();
      
      // Check that the start button is rendered
      expect(screen.getByText('Start Conversation')).toBeInTheDocument();
    });

    test('renders loading state', async () => {
      // Mock implementation to delay resolution
      (agentPlaygroundBackendClient.initializeConversation as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockParticipants), 100))
      );
      
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Click the start button to trigger loading state
      fireEvent.click(screen.getByText('Start Conversation'));
      
      // Check that the loading spinner and message are displayed
      expect(screen.getByText('generating character names and backstories...')).toBeInTheDocument();
      expect(screen.getByText('Initializing...')).toBeInTheDocument();
    });

    test('displays max characters warning when limit is reached', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Increment character count to maximum (4 for AI + 1 for user = 5 total)
      fireEvent.click(screen.getByText('+'));
      fireEvent.click(screen.getByText('+'));
      
      // Check that the warning is displayed
      expect(screen.getByText(/Maximum of 5 participants reached/i)).toBeInTheDocument();
      
      // Check that the + button is disabled
      const incrementButton = screen.getByText('+');
      expect(incrementButton).toBeDisabled();
    });

    test('displays user engagement note when only 1 AI character', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Decrement character count to 1
      fireEvent.click(screen.getByText('-'));
      
      // Check that the note is displayed
      expect(screen.getByText(/User participation is required with only 1 AI character/i)).toBeInTheDocument();
      
      // Check that the checkbox is disabled
      expect(screen.getByLabelText(/Enable User Participation/i)).toBeDisabled();
    });
  });

  // Interaction tests
  describe('User Interaction', () => {
    test('increments character count when + is clicked', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Check initial count
      expect(screen.getByText('2')).toBeInTheDocument();
      
      // Click the + button
      fireEvent.click(screen.getByText('+'));
      
      // Check that the count increased
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    test('decrements character count when - is clicked', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Check initial count
      expect(screen.getByText('2')).toBeInTheDocument();
      
      // Click the - button
      fireEvent.click(screen.getByText('-'));
      
      // Check that the count decreased
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    test('does not decrement below 1', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Decrement to 1
      fireEvent.click(screen.getByText('-'));
      
      // Try to decrement again
      fireEvent.click(screen.getByText('-'));
      
      // Check that the count remains at 1
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    test('toggles user engagement when checkbox is clicked', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      const checkbox = screen.getByLabelText(/Enable User Participation/i);
      
      // Check initial state
      expect(checkbox).toBeChecked();
      
      // Click the checkbox
      fireEvent.click(checkbox);
      
      // Check that the checkbox is unchecked
      expect(checkbox).not.toBeChecked();
      
      // Click the checkbox again
      fireEvent.click(checkbox);
      
      // Check that the checkbox is checked again
      expect(checkbox).toBeChecked();
    });

    test('adjusts max AI characters when user participation is toggled', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Increment to max with user participation (4 AI characters)
      fireEvent.click(screen.getByText('+'));
      fireEvent.click(screen.getByText('+'));
      
      // Check that we're at the max (4)
      expect(screen.getByText('4')).toBeInTheDocument();
      const incrementButton = screen.getByText('+');
      expect(incrementButton).toBeDisabled(); // + button
      
      // Disable user participation
      fireEvent.click(screen.getByLabelText(/Enable User Participation/i));
      
      // Check that the + button is now enabled (max is now 5)
      const incrementButtonAfterToggle = screen.getByText('+');
      expect(incrementButtonAfterToggle).not.toBeDisabled();
      
      // Increment to the new max
      fireEvent.click(screen.getByText('+'));
      
      // Check that we're at the new max (5)
      expect(screen.getByText('5')).toBeInTheDocument();
      const incrementButtonAtMax = screen.getByText('+');
      expect(incrementButtonAtMax).toBeDisabled(); // + button
    });

    test('enforces user participation with 1 AI character', () => {
      render(<ConversationInitializer onInitialized={jest.fn()} />);
      
      // Disable user participation
      fireEvent.click(screen.getByLabelText(/Enable User Participation/i));
      
      // Decrement to 1
      fireEvent.click(screen.getByText('-'));
      
      // Check that user participation is automatically enabled
      expect(screen.getByLabelText(/Enable User Participation/i)).toBeChecked();
    });
  });

  // API interaction tests
  describe('API Interaction', () => {
    test('calls backend service when start button is clicked', async () => {
      const onInitializedMock = jest.fn();
      
      render(<ConversationInitializer onInitialized={onInitializedMock} />);
      
      // Click the start button
      fireEvent.click(screen.getByText('Start Conversation'));
      
      // Wait for the API call to complete
      await waitFor(() => {
        expect(agentPlaygroundBackendClient.initializeConversation).toHaveBeenCalled();
      });
      
      // Check that the API was called with the correct parameters
      expect(agentPlaygroundBackendClient.initializeConversation).toHaveBeenCalledWith(2, true);
      
      // Wait for the onInitialized callback to be called
      await waitFor(() => {
        expect(onInitializedMock).toHaveBeenCalled();
      });
      
      // Check that the onInitialized callback was called with the participants
      expect(onInitializedMock).toHaveBeenCalledWith(mockParticipants);
    });

    test('handles API errors gracefully', async () => {
      // Mock implementation to reject
      (agentPlaygroundBackendClient.initializeConversation as jest.Mock).mockRejectedValue(
        new Error('API error')
      );
      
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      const onInitializedMock = jest.fn();
      
      render(<ConversationInitializer onInitialized={onInitializedMock} />);
      
      // Click the start button
      fireEvent.click(screen.getByText('Start Conversation'));
      
      // Wait for the error to be logged
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalled();
      });
      
      // Check that the onInitialized callback was not called
      expect(onInitializedMock).not.toHaveBeenCalled();
      
      // Check that the loading state is cleared
      expect(screen.getByText('Start Conversation')).toBeInTheDocument();
      
      // Restore console.error
      consoleErrorSpy.mockRestore();
    });

    test('passes correct parameters to API based on UI state', async () => {
      const onInitializedMock = jest.fn();
      
      render(<ConversationInitializer onInitialized={onInitializedMock} />);
      
      // Change character count to 3
      fireEvent.click(screen.getByText('+'));
      
      // Disable user participation
      fireEvent.click(screen.getByLabelText(/Enable User Participation/i));
      
      // Click the start button
      fireEvent.click(screen.getByText('Start Conversation'));
      
      // Wait for the API call to complete
      await waitFor(() => {
        expect(agentPlaygroundBackendClient.initializeConversation).toHaveBeenCalled();
      });
      
      // Check that the API was called with the correct parameters
      expect(agentPlaygroundBackendClient.initializeConversation).toHaveBeenCalledWith(3, false);
    });
  });
});
