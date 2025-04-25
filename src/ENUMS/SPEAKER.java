package ENUMS;

/**
 * SPEAKER - defines roles for the chat interface
 * USER inputs or questions will appear on the left side of the chat interface
 * AI inputs and responses will appear on the right side of the chat interface
 */
public enum SPEAKER {
  /**
   * represents the user's input query
   */
  USER,
  /**
   * represents the response from Pulsy (the LLM endpoint)
   */
  AI
}
