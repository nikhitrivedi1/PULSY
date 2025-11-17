from pydantic import BaseModel
from typing import Optional, Any

# AI Message - responses, tool calls
# User Message - queries, tool calls
# System Message - system prompts, date, user id

class Logger(BaseModel):
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
