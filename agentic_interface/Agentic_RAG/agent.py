"""
AgenticRAG - AI Health Advisor with Tool-Calling Capabilities

This module implements a ReAct (Reasoning + Acting) agent using LangGraph.
The agent can:
1. Reason about user health queries
2. Call tools to fetch device data or retrieve knowledge
3. Synthesize personalized health advice

Architecture:
- Uses GPT-4 for natural language understanding
- LangGraph for agentic workflow orchestration
- Tool calling for dynamic data retrieval
- Pinecone for RAG knowledge retrieval
- PostgreSQL for logging and user data

The agent operates as a singleton - one instance handles all users.
User context is passed per-request for personalization.

TODO: Add error handling for file IO operations
"""

# External Libraries
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition  # Conditional edge for tool calling
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from langgraph.checkpoint.memory import MemorySaver
import json
import datetime
from logger import Logger
import time
from config.settings import settings

# Internal Modules
from database.user_db_call import UserDbOperations
from config.settings import settings
from Agentic_RAG.tools import (
    get_heart_rate_data, 
    get_sleep_data, 
    get_stress_data, 
    get_Andrew_Huberman_Insights
)

# Constants
SYSTEM_PROMPT = "Agentic_RAG/system_instructions.md"

class AgenticRAG:
    """
    ReAct Agent for Health Advisory
    
    Implements a reasoning + acting loop where the agent:
    1. Reasons about the best response to user queries
    2. Decides whether to call tools for data/knowledge
    3. Uses tool results to formulate final advice
    
    The agent is stateless - each request is independent.
    Conversation history is passed explicitly per request.
    """
    
    def __init__(self):
        """
        Initialize the AgenticRAG system
        
        Sets up:
        - GPT-4 model with streaming
        - Available tools (device data + RAG retrieval)
        - LangGraph workflow
        - Database connection
        - System prompt
        """
        # Initialize GPT-4 model with tool calling
        # self.llm = ChatOllama(
        #     model=settings.OLLAMA_MODEL,
        #     temperature=1.0,
        # )

        self.llm = ChatOpenAI(model = 'gpt-4.1', streaming = True, openai_api_key = settings.OPENAI_API_KEY)
        
        # Define available tools for the agent
        self.tools = [
            get_heart_rate_data,          # Fetch HR from user's wearable
            get_sleep_data,                # Fetch sleep metrics
            get_stress_data,               # Fetch stress metrics
            get_Andrew_Huberman_Insights   # RAG retrieval from knowledge base
        ]
        
        # Bind tools to LLM for function calling
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Load system instructions from markdown file
        self.sys_msg = SystemMessage(content=self.__get_system_instructions())

        # Build LangGraph ReAct workflow
        self.react_graph = self.build_graph()

        # Initialize conversation history with system message
        self.messageHistory = [self.sys_msg]

        # Initialize database operations
        self.user_db_operations = UserDbOperations()
        
        print("✓ AgenticRAG initialized successfully")

    def __get_system_instructions(self) -> str:
        """
        Load system prompt from markdown file
        
        Returns:
            str: System instructions for the AI
        """
        with open(SYSTEM_PROMPT, 'r') as file:
            return file.read()

    def build_graph(self) -> StateGraph:
        """
        Build LangGraph ReAct workflow
        
        Graph structure:
        START → reasoner → [tools_condition] → tools → reasoner → END
        
        The tools_condition is a conditional edge that checks if the
        reasoner requested tool calls. If yes, execute tools; if no, end.
        
        Returns:
            StateGraph: Compiled LangGraph workflow
        """
        builder = StateGraph(MessagesState)

        # Add nodes to the graph
        builder.add_node("reasoner", self.reasoner)  # LLM reasoning step
        builder.add_node("tools", ToolNode(self.tools))  # Tool execution step

        # Define workflow edges
        builder.add_edge(START, "reasoner")  # Start with reasoning
        
        # Conditional edge: if tools requested, go to tools; else end
        builder.add_conditional_edges(
            "reasoner",
            tools_condition  # Built-in LangGraph condition checker
        )
        
        # After tools execute, return to reasoner for final response
        builder.add_edge("tools", "reasoner")

        # Compile the graph into an executable workflow
        # return builder.compile(checkpointer=MemorySaver())
        return builder.compile()

    def reasoner(self, state: MessagesState) -> MessagesState:
        """
        Reasoning node - invokes LLM with tool calling
        
        This node:
        1. Takes the message history from state
        2. Invokes GPT-4 with available tools
        3. Returns updated state with LLM response
        
        The LLM may return:
        - A direct text response (if no tools needed)
        - Tool call requests (if data is needed)
        
        Args:
            state: Current conversation state with message history
        
        Returns:
            MessagesState: Updated state with LLM response appended
        """
        prior_messages = state["messages"]
        
        # Invoke LLM with tool calling capability
        response = self.llm_with_tools.invoke(prior_messages)

        # Append response to message history
        return {"messages": prior_messages + [response]}

    async def run(self,
        query: str,
        user_id: str,
        query_history: list[str],
        response_history: list[str],
        eval_mode: bool = False,
        config: dict = None
        ) -> dict[str, str|int]:
        """
        Execute the agent workflow for a user query
        
        This is the main entry point for the agent. It:
        1. Builds context (date, user ID, preferences, conversation history)
        2. Retrieves user's device API key
        3. Invokes the LangGraph ReAct workflow
        4. Logs the interaction to database
        5. Returns the AI response and log ID
        
        Args:
            query: User's current question/request
            user_id: Username for personalization and data access
            query_history: List of previous user messages in this session
            response_history: List of previous AI responses in this session
        
        Returns:
            dict: Contains 'response' (AI message text) and 'log_id' (for feedback)
        
        """
        # Add current date to context for time-aware responses
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        date_message = f"Today's date is: {current_date}"
        user_specific_message = "My name and user_key is: "

        # Build message history starting with system prompt
        message_history = [self.sys_msg, date_message]
        message_history.extend([SystemMessage(content=user_specific_message + user_id)])
        
        # Convert conversation history to LangChain message format
        message_conversation, chatml_conversation = self.create_message_history(
            query_history, 
            response_history
        )
        message_history.extend(message_conversation)

        # Retrieve and add user preferences (e.g., preferred metrics, goals)
        user_preferences = await self.user_db_operations.get_agentic_preferences(user_id)
        if user_preferences is not None:
            user_preferences = user_preferences[0]
            user_preferences_message = SystemMessage(
                content=f"User preferences: {user_preferences}"
            )
            message_history.extend([user_preferences_message])
        else:
            user_preferences = []
        
        # Retrieve user's device API key (needed for tool calls)
        # TODO: Implement secure key management instead of passing in context
        user_key = await self.__get_device_api_key(user_id, "Oura Ring")
        message_history.extend([
            SystemMessage(content=f"{user_specific_message}{user_id} USER_KEY: {user_key}")
        ])
        
        # Add current query
        message_history.extend([HumanMessage(content=query)])
        query_idx = len(message_history) - 1

        messages = None

        start_time = time.time()

        if not eval_mode:
            messages = self.react_graph.invoke({"messages": message_history})
            inference_time = time.time() - start_time

            log_id = await self.log_message(
                query, 
                response=messages['messages'][-1], 
                message_hist=chatml_conversation, 
                query_idx=query_idx, 
                inference_time=inference_time, 
                messages=messages,
                user_spec=f"{date_message} {user_specific_message}USER_KEY", 
                preferences=user_preferences,
                eval_mode=eval_mode
            )

        else:
            try:
                messages = self.react_graph.invoke({"messages": message_history}, config=config)
                inference_time = time.time() - start_time
            except Exception as e:
                inference_time = time.time() - start_time
                state = self.react_graph.get_state(config=config)
                # Convert state to messages format
                messages = {"messages": state.values.get('messages')}
                error_dump = (
                    f"Error: {e}\n"
                    f"Query: {query}\n"
                    f"Last Message: {messages['messages'][-1].content}"
                )

                raise Exception(error_dump)

        # If Eval Mode, return the response from the query index onwards
        if eval_mode:
            return {
                "response": messages['messages'][-1].content,
                "tool_calls": messages['messages'][query_idx:-1]
            }
        # Return final AI response and log ID
        return {
            "response": messages['messages'][-1].content, 
            "log_id": log_id
        }

    def create_message_history(
        self, 
        query_history: list[str], 
        response_history: list[str]
        ) -> tuple[list, list]:
        """
        Convert conversation history to LangChain message format
        
        Creates two representations:
        1. LangChain messages (HumanMessage/AIMessage) for graph execution
        2. ChatML format (dict) for database logging
        
        Args:
            query_history: List of user messages
            response_history: List of AI responses
        
        Returns:
            tuple: (langchain_messages, chatml_messages)
        
        Note: Not ideal for long conversations - consider implementing
              conversation summarization for production use
        """
        message_history = []
        chatml_history = []
        
        for i in range(len(query_history)):
            # Add user message
            message_history.append(HumanMessage(content=query_history[i]))
            chatml_history.append({
                "role": "user",
                "content": query_history[i]
            })
            
            # Add AI response (if available)
            if len(response_history) > i:
                message_history.append(AIMessage(content=response_history[i]))
                chatml_history.append({
                    "role": "assistant",
                    "content": response_history[i]
                })
        
        return message_history, chatml_history
    
    async def log_message(self, query: str, response: str, message_hist: list[str], query_idx: int, messages: MessagesState, inference_time: float, user_spec: str, preferences: list[str], eval_mode: bool = False):
        # Query_id: allows us to identify the query in the message history
        # Additionally extract function calls from the response and log them
        # Load the messages type from args
        logger = Logger(
            message_id=str(query_idx),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            inference_time=inference_time,
            prompt=[{
                "role": "user",
                "content": query
            }],
            response=[],
            system_prompt=SYSTEM_PROMPT,
            response_metadata= response.response_metadata,
            feedback=None,
            preferred_response=None,
            message_history=message_hist,
        )

        logger.message_history.append({
            "role": "system",
            "content": user_spec
        })

        logger.message_history.append({
            "role": "system",
            "content": "\n".join(preferences)
        })

        # latest_idx_tools = 0
        for message in messages['messages'][query_idx:]:
            if isinstance(message, AIMessage) and message.content == '':
                # This is a tool call - so extract arguments - multiple tool calls are possible within this message - so we likely need to take a look at the logic here
                tool_chatml_format = {
                    "role": "assistant",
                    "tool_calls": []
                }
                for tool_call in message.tool_calls:
                    tool_chatml_format['tool_calls'].append({
                        "id": tool_call['id'],
                        "name": tool_call['name'],
                        "function": {
                            "arguments": tool_call['args'],
                            "name": tool_call['name']
                        }
                    })
                    # Replace the user_id with [USER_ID] in the arguments
                    if 'user_key' in tool_chatml_format['tool_calls'][-1]['function']['arguments']:
                        tool_chatml_format['tool_calls'][-1]['function']['arguments']['user_key'] = "USER_KEY"
                logger.response.append(tool_chatml_format)
                
            if isinstance(message, ToolMessage):
                tool_response_chatml_format = {
                    "role": "tool",
                    "tool_call_id": message.tool_call_id,
                    "name": message.name,
                    "content": message.content
                }
                logger.response.append(tool_response_chatml_format)

        # add the response to the response list
        logger.response.append({
            "role": "assistant",
            "content": response.content
        })
        # Tool Call - returns _id in the form of a tuple: ex. (6,)
        log_id = await self.user_db_operations.log_message(logger, eval_mode=eval_mode)
        return log_id[0]
    
    async def __get_device_api_key(self, user_id: str, device_type: str) -> str:
        """
        Get the API key for the user - query via the user_db_call class
        """
        key = await self.user_db_operations.get_api_key(user_id, device_type)
        return key

if __name__ == "__main__":
    agent = AgenticRAG()
    agent.log_message_test()
    
