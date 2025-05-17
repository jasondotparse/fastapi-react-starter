import axios from '../axiosConfig';
import config from '../config';
import { Conversation, Participant } from '../types/models';

/**
 * Service class for handling API calls to the backend for the CHAI Agent Playground.
 * This class abstracts the details of communicating with the backend API from the React components.
 */
class AgentPlaygroundBackendClient {
  /**
   * Initializes a new conversation with AI characters.
   * 
   * @param count - The number of AI characters to generate
   * @param userEngagementEnabled - Whether the user will participate in the conversation
   * @returns A Promise that resolves to an array of Participants
   */
  async initializeConversation(count: number, userEngagementEnabled: boolean): Promise<Participant[]> {
    try {
      const response = await axios.post(`${config.apiBaseUrl}/initializeCharacters`, {
        count,
        userEngagementEnabled
      });
      return response.data;
    } catch (error) {
      console.error('Error initializing conversation:', error);
      throw error;
    }
  }

  /**
   * Continues an existing conversation by generating the next AI response.
   * 
   * @param conversation - The current state of the conversation
   * @returns A Promise that resolves to the updated Conversation
   */
  async continueConversation(conversation: Conversation): Promise<Conversation> {
    try {
      const response = await axios.post(`${config.apiBaseUrl}/continueConversation`, {
        conversation
      });
      return response.data;
    } catch (error) {
      console.error('Error continuing conversation:', error);
      throw error;
    }
  }
}

// Export a singleton instance of the service
export const agentPlaygroundBackendClient = new AgentPlaygroundBackendClient();

// Also export the class for testing or if a new instance is needed
export default AgentPlaygroundBackendClient;
