import React, { useState } from 'react';
import ConversationInitializer from '../components/ConversationInitializer';
import { Participant } from '../types/models';

const MainPage: React.FC = () => {
  const [initialized, setInitialized] = useState<boolean>(false);
  const [participants, setParticipants] = useState<Participant[]>([]);

  const handleInitialized = (newParticipants: Participant[]) => {
    setParticipants(newParticipants);
    setInitialized(true);
  };

  return (
    <div className="main-page">
      <h1>CHAI Character Sandbox</h1>
      <p>
        This is a sandbox for testing and playing with CHAI characters.
      </p>
      
      {!initialized ? (
        <ConversationInitializer onInitialized={handleInitialized} />
      ) : (
        <div className="conversation-container">
          <h2>Conversation Initialized!</h2>
          <p>Participants:</p>
          <ul>
            {participants.map((participant, index) => (
              <li key={index}>
                <strong>{participant.name}</strong> ({participant.type}): {participant.backstory}
              </li>
            ))}
          </ul>
          {/* Future: Add conversation display and interaction components here */}
        </div>
      )}
    </div>
  );
};

export default MainPage;
