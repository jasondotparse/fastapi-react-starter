import React, { useState, useEffect } from 'react';
import { agentPlaygroundBackendClient } from '../services/AgentPlaygroundBackendClient';
import { Conversation, Participant } from '../types/models';
import './ContinueConversation.css';

interface ContinueConversationProps {
  conversation: Conversation;
  setConversation: React.Dispatch<React.SetStateAction<Conversation | undefined>>;
}

const ContinueConversation: React.FC<ContinueConversationProps> = ({ 
  conversation, 
  setConversation 
}) => {
  // State for user input
  const [userInput, setUserInput] = useState<string>('');
  // Loading state
  const [loading, setLoading] = useState<boolean>(false);
  // Error state
  const [error, setError] = useState<string | null>(null);
  
  // Find USER participants
  const userParticipants = conversation.participants.filter(p => p.type === "HUMAN");
  
  // Determine if this is a 1-on-1 conversation (1 user and 1 AI)
  const isOneOnOneConversation = () => {
    const aiParticipants = conversation.participants.filter(p => p.type === "AI");
    return userParticipants.length === 1 && aiParticipants.length === 1;
  };
  
  // Determine if the continue button should be disabled
  const isContinueButtonDisabled = () => {
    // In 1-on-1 conversations, require user input
    if (isOneOnOneConversation() && !userInput.trim()) {
      return true;
    }
    // Always disable during loading
    return loading;
  };
  
  // Handle key press in textarea
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // If Enter is pressed without Shift key, submit the form
    if (e.key === 'Enter' && !e.shiftKey && !isContinueButtonDisabled()) {
      e.preventDefault(); // Prevent adding a new line
      handleContinue();
    }
  };
  
  // Handle continue button click
  const handleContinue = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let updatedConversation = { ...conversation };
      
      // If user input is provided and a user is selected, add it to the conversation
      if (userInput.trim()) {
        updatedConversation = {
          ...conversation,
          dialogTurns: [
            ...conversation.dialogTurns,
            {
              participant: "Stranger",
              content: userInput.trim()
            }
          ]
        };
      } else {
        updatedConversation = conversation
      }
      
      // Call the API to continue the conversation
      const result = await agentPlaygroundBackendClient.continueConversation(updatedConversation);
      
      // Update the conversation with the result
      setConversation(result);
      
      // Clear user input
      setUserInput('');
    } catch (err) {
      console.error('Error continuing conversation:', err);
      setError('Failed to continue conversation. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="continue-conversation">
      {userParticipants.length > 0 && (
        <div className="user-input-section">
          <div className="input-container">
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              disabled={loading}
            />
          </div>
        </div>
      )}
      
      {error && <div className="error-message">{error}</div>}
      
      {isOneOnOneConversation() && !userInput.trim() && (
        <div className="input-required-message">
          Please type a message to continue the conversation.
        </div>
      )}
      
      <button 
        className="continue-button"
        onClick={handleContinue}
        disabled={isContinueButtonDisabled()}
      >
        {loading ? 'Processing...' : 'Continue Conversation'}
      </button>
    </div>
  );
};

export default ContinueConversation;
