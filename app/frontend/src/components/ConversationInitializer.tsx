import React, { useState } from 'react';
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

  const incrementCount = () => setCharacterCount(prev => prev + 1);
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
          <button onClick={incrementCount} disabled={loading}>+</button>
        </div>
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
