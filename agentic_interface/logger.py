"""
Logging Data Models for AI Conversation Tracking

Defines Pydantic models for structured logging of:
- User queries and AI responses
- Tool calls and their results
- Conversation context and metadata
- User feedback for response quality

These logs enable:
- Performance monitoring (inference time tracking)
- Feedback collection for model improvement
- Debugging tool call issues
- Conversation history analysis
"""

from pydantic import BaseModel
from typing import Optional, Any

class ToolCall(BaseModel):
    """
    Represents a single tool invocation during AI reasoning
    
    Attributes:
        tool_name: Name of the tool called (e.g., "get_sleep_data")
        tool_args: Arguments passed to the tool
        result: Return value from tool execution
        error: Error message if tool call failed
    """
    tool_name: str
    tool_args: dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None

class Feedback(BaseModel):
    """
    User feedback on AI response quality
    
    Attributes:
        good_bad: True for positive, False for negative feedback
        reason: Optional text explaining the feedback
    """
    good_bad: bool
    reason: str

class MessageContext(BaseModel):
    """
    Context and metadata for a conversation turn
    
    Attributes:
        system_prompt: Path to system instructions file
        tool_calls: List of tools invoked during this turn
        message_history: Prior conversation messages
    """
    system_prompt: str
    tool_calls: list[ToolCall]
    message_history: Optional[list[dict]] = None

class Logger(BaseModel):
    """
    Complete log entry for an AI conversation turn
    
    Captures all information needed for monitoring, debugging,
    and improving the AI system over time.
    
    Attributes:
        message_id: Unique identifier for this conversation turn
        timestamp: When the query was processed
        inference_time: How long the AI took to respond (seconds)
        prompt: User's input message
        response: AI's generated response
        response_metadata: Token usage, model info, etc.
        feedback: Optional user rating ("Up" or "Down")
        message_context: Tools used, system prompt, conversation history
    """
    message_id: str
    timestamp: str
    inference_time: float
    prompt: list[dict]
    response: list[dict]
    system_prompt: str
    response_metadata: dict[str, Any]
    feedback: Optional[str] = None # "Up" or "Down"
    preferred_response: Optional[str] = None
    message_history: Optional[list[dict]] = None