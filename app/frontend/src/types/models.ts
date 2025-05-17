/**
 * Represents a participant in the conversation.
 * Can be either an AI character or a human user.
 */
export interface Participant {
  /**
   * The type of participant: "HUMAN" or "AI"
   */
  type: string;
  
  /**
   * The backstory of the participant.
   * For AI characters, this provides context for their responses.
   */
  backstory: string;
  
  /**
   * The name of the participant.
   */
  name: string;
}

/**
 * Represents a single turn in the conversation.
 */
export interface DialogTurn {
  /**
   * The name of the participant who is speaking.
   * Must match one of the participant names in the conversation.
   */
  participant: string;
  
  /**
   * The content of the dialog turn.
   * What the participant said.
   */
  content: string;
}

/**
 * Represents the entire state of a conversation at a given point in time.
 */
export interface Conversation {
  /**
   * The list of participants in the conversation.
   */
  participants: Participant[];
  
  /**
   * The list of dialog turns that make up the conversation.
   * Ordered chronologically.
   */
  dialogTurns: DialogTurn[];
}

/**
 * Request parameters for initializing characters.
 */
export interface InitializeCharactersRequest {
  /**
   * The number of AI characters to generate.
   */
  count: number;
  
  /**
   * Whether the user will participate in the conversation.
   */
  userEngagementEnabled: boolean;
}
