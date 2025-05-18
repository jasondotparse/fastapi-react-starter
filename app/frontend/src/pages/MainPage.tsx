import React, { useState } from 'react';
import ConversationInitializer from '../components/ConversationInitializer';
import ContinueConversation from '../components/ContinueConversation';
import { Participant, Conversation } from '../types/models';
import './MainPage.css';

const MainPage: React.FC = () => {
  const [initialized, setInitialized] = useState<boolean>(false);
  const [conversation, setConversation] = useState<Conversation>();

  const handleInitialized = (newParticipants: Participant[]) => {
    setConversation({
      participants: newParticipants,
      dialogTurns: [],
    });
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
            {conversation!.participants.map((participant, index) => (
              <li key={index}>
                <strong>{participant.name}</strong> ({participant.type}): {participant.backstory}
              </li>
            ))}
          </ul>
          
          {/* Display dialog turns if any exist */}
          {conversation!.dialogTurns.length > 0 && (
            <div className="dialog-turns">
              <h3>Conversation:</h3>
              {conversation!.dialogTurns.map((turn, index) => (
                <div key={index} className="dialog-turn">
                  <strong>{turn.participant}:</strong> {turn.content}
                </div>
              ))}
            </div>
          )}
          
          {/* ContinueConversation component */}
          <ContinueConversation 
            conversation={conversation!} 
            setConversation={setConversation} 
          />
        </div>
      )}
    </div>
  );
};

export default MainPage;
