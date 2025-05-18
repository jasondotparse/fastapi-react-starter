import React, { useState, useEffect } from 'react';
import { agentPlaygroundBackendClient } from '../services/AgentPlaygroundBackendClient';
import { Participant } from '../types/models';
import './ConversationInitializer.css';

interface ConversationInitializerProps {
  onInitialized: (participants: Participant[]) => void;
}

const ConversationInitializer: React.FC<ConversationInitializerProps> = ({ onInitialized }) => {
  const [characterCount, setCharacterCount] = useState<number>(2);
  const [userEngagementEnabled, setUserEngagementEnabled] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Calculate the maximum AI characters based on whether user participation is enabled
  const maxAICharacters = userEngagementEnabled ? 4 : 5; // 5 total - 1 user = 4 AI (if user enabled)

  // Update character count if it exceeds the new maximum after toggling user participation
  useEffect(() => {
    if (characterCount > maxAICharacters) {
      setCharacterCount(maxAICharacters);
    }
  }, [userEngagementEnabled, maxAICharacters]);

  const incrementCount = () => {
    if (characterCount < maxAICharacters) {
      setCharacterCount(prev => prev + 1);
    }
  };
  
  const decrementCount = () => setCharacterCount(prev => Math.max(1, prev - 1));

  const handleInitialize = async () => {
    setLoading(true);
    try {
      const participants = await agentPlaygroundBackendClient.initializeConversation(
        characterCount,
        userEngagementEnabled
      );
      onInitialized(participants);
    } catch (error) {
      console.error('Failed to initialize conversation:', error);
      // Handle error (could add error state and display message)
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="conversation-initializer">
      <h2>Initialize Conversation</h2>
      
      <div className="form-group">
        <label>Number of AI Characters:</label>
        <div className="character-count-control">
          <button onClick={decrementCount} disabled={characterCount <= 1 || loading}>-</button>
          <span>{characterCount}</span>
          <button onClick={incrementCount} disabled={loading || characterCount >= maxAICharacters}>+</button>
        </div>
        {characterCount >= maxAICharacters && (
          <div className="max-characters-warning">
            Maximum of 5 participants reached (including {userEngagementEnabled ? "you and " : ""}AI characters).
          </div>
        )}
      </div>
      
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={userEngagementEnabled}
            onChange={e => setUserEngagementEnabled(e.target.checked)}
            disabled={loading}
          />
          Enable User Participation
        </label>
      </div>
      
      <button 
        className="start-button"
        onClick={handleInitialize}
        disabled={loading}
      >
        {loading ? 'Initializing...' : 'Start Conversation'}
      </button>
    </div>
  );
};

export default ConversationInitializer;
