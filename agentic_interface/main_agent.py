"""
Backend API Server for Pulsy AI Health Advisor

This FastAPI application serves as the backend for the Pulsy health advisory system.
It provides endpoints for:
- AI-powered chat queries using RAG (Retrieval Augmented Generation)
- User device data loading and aggregation
- User goal management
- Real-time streaming responses via SSE (Server-Sent Events)

Architecture:
- Uses LangGraph for agentic workflow orchestration
- Integrates with Oura Ring and other wearable devices
- Leverages OpenAI GPT-4 for intelligent health insights
- Stores conversation logs for feedback and improvement

Entry Point: Run with `uvicorn main_agent:app --host 0.0.0.0 --port 8000`
"""

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from config.settings import settings
import json

# Local Modules
from Agentic_RAG.agent import AgenticRAG
from user_tools import load_user_devices_service, load_user_goals_service

# Pydantic models for request validation

class QueryBody(BaseModel):
    """Request body for AI chat queries"""
    query: str  # User's question/query
    username: str  # Username for context and personalization
    user_history: list[str]  # Previous user messages in conversation
    ai_chat_history: list[str]  # Previous AI responses in conversation

class LoadUserDevicesBody(BaseModel):
    """Request body for loading device metrics"""
    device_type: str  # Type of wearable device (e.g., "Oura Ring")
    device_name: str  # User-assigned name for device
    api_key: str  # API key for accessing device data

# Initialize FastAPI application
app = FastAPI(
    title="Pulsy Backend API",
    description="AI-powered health advisory backend with RAG capabilities",
    version="1.0.0"
)

# Initialize single shared AgenticRAG instance
# This singleton pattern ensures efficient resource usage
# User-specific context is passed per request
agent = AgenticRAG()

@app.post("/load_user_devices/")
async def load_user_devices(load_user_devices_body: LoadUserDevicesBody) -> dict[str, str|int|float]:
    """
    Load and aggregate user metrics from a wearable device
    
    Currently supports: Oura Ring
    Retrieves yesterday's metrics including sleep, stress, and heart rate data
    
    Args:
        load_user_devices_body: Device information including type, name, and API key
    
    Returns:
        dict: Aggregated metrics (sleep_score, stress_score, heart_rate_data)
    
    Raises:
        HTTPException: If device API call fails or device type not supported
    """
    result_data = await load_user_devices_service(load_user_devices_body.model_dump())
    return result_data

@app.get("/load_user_goals/{user_id}")
async def load_user_goals(user_id: str) -> dict[str, dict[str, str|list[dict]]]:
    """
    Retrieve user's goals from database
    
    Args:
        user_id: Username/ID of the user
    
    Returns:
        dict: User's goals with evidence and tracking information
    """
    result_data = await load_user_goals_service(user_id)
    return result_data

@app.post("/query/")
async def post_query(query: QueryBody) -> dict[str, str|int]:
    """
    Process AI chat query using RAG-powered agent
    
    This endpoint:
    1. Accepts user query and conversation history
    2. Runs agentic RAG workflow with tool calling
    3. May fetch device data or health insights as needed
    4. Logs conversation for feedback and improvement
    
    Args:
        query: QueryBody containing user message and conversation context
    
    Returns:
        dict: Contains 'response' (AI message) and 'log_id' (for feedback tracking)
    """
    res = await agent.run(query.query, query.username, query.user_history, query.ai_chat_history)
    return res

@app.post("/queryTest/")
async def post_query_test(query: QueryBody) -> str:
    """
    Test endpoint for debugging query structure
    Prints query components and returns confirmation
    """
    print(query.query, query.username, query.user_history, query.ai_chat_history)
    return "Test"


@app.get("/query/stream")
async def stream_query(
    query: str = Query(..., description="User's question/query"),
    username: str = Query(..., description="Username for context"),
    user_history: str = Query("[]", description="JSON-encoded list of previous user messages"),
    ai_chat_history: str = Query("[]", description="JSON-encoded list of previous AI responses")
):
    """
    Stream AI chat query responses using Server-Sent Events (SSE)
    
    This endpoint provides real-time streaming of:
    - Tool execution status (tool_start, tool_end events)
    - Token-by-token response generation
    - Completion signal with log_id for feedback tracking
    
    Args:
        query: User's current question/request
        username: Username for personalization and data access
        user_history: JSON-encoded list of previous user messages
        ai_chat_history: JSON-encoded list of previous AI responses
    
    Returns:
        StreamingResponse: SSE stream with events in format "data: {...}\n\n"
    
    Event Types:
        - tool_start: {"type": "tool_start", "tool_name": "..."}
        - tool_end: {"type": "tool_end", "tool_name": "..."}
        - token: {"type": "token", "content": "..."}
        - done: {"type": "done", "log_id": ...}
        - error: {"type": "error", "message": "..."}
    """
    # Parse JSON-encoded history arrays
    try:
        user_history_list = json.loads(user_history)
        ai_chat_history_list = json.loads(ai_chat_history)
    except json.JSONDecodeError:
        user_history_list = []
        ai_chat_history_list = []
    
    async def event_generator():
        """
        Async generator that yields SSE events from the agent stream
        """
        try:
            async for event in agent.run_stream(
                query, 
                username, 
                user_history_list, 
                ai_chat_history_list
            ):
                # Format as SSE: "data: {...}\n\n"
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            # Send error event if something goes wrong
            error_event = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering if behind proxy
        }
    )

