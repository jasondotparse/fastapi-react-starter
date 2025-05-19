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
        Choose a character count and start a conversation to bootstrap a cast of fantasy characters with backstories.
      </p>
      
      {!initialized ? (
        <ConversationInitializer onInitialized={handleInitialized} />
      ) : (
        <div className="conversation-container">
          <p>Participants:</p>
          <ul>
            {conversation!.participants.map((participant, index) => (
              <li key={index}>
                <strong>{participant.name}</strong> ({participant.type}): {participant.backstory}
              </li>
            ))}
          </ul>
          <p>Interact amongst the characters conversation or let them talk amongst themselves. 
          Optionally, reference a character by name to direct a comment towards them.</p>
          {conversation!.dialogTurns.length > 0 && (
            <div className="dialog-turns">
              <h3>Conversation:</h3>
              {conversation!.dialogTurns
                // Filter out dialog turns that begin with "This is what I know about myself"; these essentially are system messages
                .filter(turn => !turn.content.startsWith("This is what I know about myself"))
                .map((turn, index) => {
                  const isUser = turn.participant === "Stranger";
                  
                  return (
                    <div 
                      key={index} 
                      className={`dialog-turn ${isUser ? 'user-turn' : 'ai-turn'}`}
                    >
                      <strong>{turn.participant}:</strong> {turn.content}
                    </div>
                  );
                })}
            </div>
          )}
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
