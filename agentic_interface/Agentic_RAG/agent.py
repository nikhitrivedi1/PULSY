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
from langchain_openai import ChatOpenAI
import json
import datetime
from logger import Logger
import time

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
        self.llm = ChatOpenAI(
            model='gpt-4.1', 
            streaming=True, 
            openai_api_key=settings.OPENAI_API_KEY
        )
        
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
        response_history: list[str]
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
        
        TODO: Store API keys more securely (not in message context)
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

        # Execute the ReAct graph workflow
        start_time = time.time()
        messages = self.react_graph.invoke({"messages": message_history})
        inference_time = time.time() - start_time
        
        # Log conversation to database for monitoring and feedback
        log_id = await self.log_message(
            query, 
            response=messages['messages'][-1], 
            message_hist=chatml_conversation, 
            query_idx=query_idx, 
            inference_time=inference_time, 
            messages=messages, 
            user_spec=f"{date_message} {user_specific_message}USER_KEY", 
            preferences=user_preferences
        )

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


    def log_message_test(self):
        messages_with_query =  [HumanMessage(content="Today's date is: 2025-10-25", additional_kwargs={}, response_metadata={}, id='488f9dd2-f869-4074-a83f-c46ebe157dff'), SystemMessage(content='My name and user_id is: Nikhil', additional_kwargs={}, response_metadata={}, id='9ec6c681-ce43-487b-977f-77cb8b5b4dcb'), HumanMessage(content='Can you help me with my sleep scores from last month?', additional_kwargs={}, response_metadata={}, id='e750b85f-b151-45f1-ad43-ea6d5a2b52f1'), AIMessage(content='<p>Here are your sleep scores from the last month:</p>\n<p><strong>Oura Ring</strong> Sleep Scores: <code>&lt;Nikhil, Oura Ring, Sep. 25, 2025 – Oct. 25, 2025&gt;</code></p>\n<ul>\n<li>09.25: 81</li>\n<li>10.02: 85</li>\n<li>10.03: 71</li>\n<li>10.05: 76</li>\n<li>10.06: 81</li>\n<li>10.11: 81</li>\n<li>10.14: 82</li>\n<li>10.16: 89</li>\n<li>10.17: 85</li>\n<li>10.18: 78</li>\n<li>10.19: 74</li>\n<li>10.22: 84</li>\n<li>10.23: 80</li>\n</ul>\n<p>Notable points:</p>\n<ul>\n<li>Several scores are in the optimal range (85+).</li>\n<li>A few lower scores (10.03: 71, 10.05: 76, 10.19: 74) suggest some nights may need attention.</li>\n</ul>\n<p>Scores below 70 are considered &quot;Fair&quot; and those above 85 &quot;Optimal&quot; by Oura standards. Regular variation is normal, but if you&#39;re concerned about consistency, focusing on pre-sleep routines and stress management may help.</p>\n<p>Let me know if you&#39;d like deeper analysis of contributors (deep/REM sleep, latency, etc.) for any specific period!</p>\n', additional_kwargs={}, response_metadata={}, id='f7be94a6-c2ff-4fe8-b76e-838932c96732'), HumanMessage(content='Yeah can you help me figure out what contributors to my sleep score were bad for the 10.03 sleep score?', additional_kwargs={}, response_metadata={}, id='e9f7f3c3-9ed7-47a7-9250-30e90600db7d'), HumanMessage(content='Yeah can you help me figure out what contributors to my sleep score were bad for the 10.03 sleep score?', additional_kwargs={}, response_metadata={}, id='c6b386ce-f918-4939-b6f5-36186560f597')]
        query = "Yeah can you help me figure out what contributors to my sleep score were bad for the 10.03 sleep score?"
        query_idx = len(messages_with_query) - 1
        full_messages = {'messages': [SystemMessage(content='# Pulsy - AI Health Advisor\n\nYou are Pulsy, an AI health advisor specializing in wearable device data analysis. Your purpose is to help users understand their health metrics and develop better habits through informed and factual insights delivered in a clear and concise way.\n\n## Query Types and Response Formats\n\n### 1. Specific Data Query\nWhen user requests a specific health metric for a specific day:\n- Return only the metric name and score\n- Include source as `<user, device_name, date>`\n\nExample:\n**Sleep Score**: 88 `<Nikhil, Oura Ring, Dec. 18, 2025>`\n\n### 2. Daily Summary Query\nWhen user requests general summary of recent scores:\n\n1. Fetch all latest available data\n2. Identify any concerning scores\n3. For concerning scores:\n   - Use get_Andrew_Huberman_Insights() for potential causes\n   - If response is irrelevant, retry with rephrased query\n   - If still irrelevant, proceed without insight\n4. Format response as shown below\n\nExample Response:\n**Oura Ring**\nSleep: `<Nikhil, Oura Ring, Dec. 18, 2025>`\n- **Sleep Score**: 80\n- **Total Sleep**: 7h 30m\n- **Efficiency**: 89%\n- **Latency**: 18m\n- **REM**: 1h 25m \n- **Restfulness**: Good\n- **Deep Sleep**: 1h 8m\n\nYour deep sleep duration was on the lower side of the recommended 1-1.5h. Considering you are 28 years old, you should aim to hit 1.5h of deep sleep every night. \n\nIf you want to get more deep sleep, try to keep your sleep schedule consistent, and avoid heavy meals, stimulants and bright screens 1-2 hours before bed.\n\n`<Andrew Huberman, Night Routines>`\n\nCommon Queries:\n- "How did I do last night?"\n- "Can you provide me a summary of my performance yesterday?"\n- "Daily Summary?"\n\n### 3. Trend Analysis Query\nWhen user requests metric data over time:\n\n1. Fetch only requested metric data for specified timeframe\n2. Identify concerning scores\n3. For concerning scores:\n   - Use get_Andrew_Huberman_Insights() for potential causes\n   - If response is irrelevant, retry with rephrased query\n   - If still irrelevant, proceed without insight\n4. Format response as shown below\n\nTime Period Conventions:\n- "Last week" = Current date minus 7 days\n- "Last month" = Current date minus 1 month\n\nExample Query: "Tell me about my REM sleep from the past week"\n\nExample Response:\n**Oura Ring**\nREM: `<Nikhil, Oura Ring, Dec. 11, 2025, Dec. 16, 2025>`\n12.11: 1h 25m\n\n12.12: 1h \n\n**12.13: 59m**\n\n**12.14: 1h 50m**\n\n**12.15: 30m**\n\n12.16: 1h 25m \n\nI have detected a couple of concerning REM scores from December 11th to December 16th. REM is vital for your creativity and memory consolidation `<Andrew Huberman, Hacking Your Sleep>`. According to Oura, the optimal range for REM sleep is between 1h and 1h 30m `<Oura Ring>`.\n\n## Available Tools\n\n### Oura Ring Tools\n- **get_sleep_data()**: Returns complete sleep metrics (score, total sleep, efficiency, restfulness, REM, deep sleep, latency, timing)\n- **get_stress_data()**: Returns stress metrics\n- **get_heart_rate_data()**: Returns heart rate data\n\n### Knowledge Tools\n- **get_Andrew_Huberman_Insights()**: Searches vector database of podcast transcripts for relevant health insights\n\n## Health Metrics Reference\n\nAll metrics below are sourced from Oura Ring. Always cite as `<Device>`.\n\n### Sleep Score\n**What it measures:** Overall sleep quality based on seven contributors\n- **Optimal**: 85–100\n- **Good**: 70–84\n- **Fair**: 60–69\n- **Needs Attention**: Below 60\n\n### Total Sleep\n**What it measures:** Total time in light, REM and deep sleep\n- **Really good**: 8–9 hours\n- **Good**: 7–8 hours\n- **Needs improvement**: 6–7 hours\n- **Concerning**: <6 hours or >9 hours\n\n### Sleep Efficiency\n**What it measures:** Percentage of time asleep vs time in bed\n- **Really good**: ≥90%\n- **Good**: 85–89%\n- **Needs improvement**: 75–84%\n- **Concerning**: <75%\n\n### Sleep Latency\n**What it measures:** Time to fall asleep\n- **Ideal**: 15–20 minutes\n- **Good**: 5–15 minutes\n- **Needs improvement**: 20–30 minutes\n- **Concerning**: <5 minutes or >30 minutes\n\n### REM Sleep\n**What it measures:** Rapid eye movement sleep phase\n- **Really good**: ≥90 minutes\n- **Good**: 60–89 minutes\n- **Needs improvement**: 30–59 minutes\n- **Concerning**: <30 minutes\n\n### Restfulness\n**What it measures:** Sleep disturbances and movement\n- **Really good**: 85–100\n- **Good**: 70–84\n- **Needs improvement**: 60–69\n- **Concerning**: <60\n\n### Deep Sleep\n**What it measures:** Most restorative sleep phase\n- **Really good**: ≥90 minutes\n- **Good**: 60–89 minutes\n- **Needs improvement**: 30–59 minutes\n- **Concerning**: <30 minutes\n\n## Response Guidelines\n\n### Core Principles\n- Use clear, professional language\n- Structure with bullet points for readability\n- Bold key metrics and takeaways\n- Keep responses concise and scannable\n- Use section headings for longer responses\n\n### Data Integrity\n- Always specify data sources\n- Never make assumptions or invent data\n- Request clarification when needed\n- Verify data relevance before making recommendations\n- Express uncertainty when appropriate\n\n**Remember:** Your role is to be informative and encouraging while maintaining strict accuracy and data integrity.\n', additional_kwargs={}, response_metadata={}, id='93a3c2ff-bcc3-4aa7-91ef-41da112be7ca'), HumanMessage(content="Today's date is: 2025-10-25", additional_kwargs={}, response_metadata={}, id='488f9dd2-f869-4074-a83f-c46ebe157dff'), SystemMessage(content='My name and user_id is: Nikhil', additional_kwargs={}, response_metadata={}, id='9ec6c681-ce43-487b-977f-77cb8b5b4dcb'), HumanMessage(content='Can you help me with my sleep scores from last month?', additional_kwargs={}, response_metadata={}, id='e750b85f-b151-45f1-ad43-ea6d5a2b52f1'), AIMessage(content='<p>Here are your sleep scores from the last month:</p>\n<p><strong>Oura Ring</strong> Sleep Scores: <code>&lt;Nikhil, Oura Ring, Sep. 25, 2025 – Oct. 25, 2025&gt;</code></p>\n<ul>\n<li>09.25: 81</li>\n<li>10.02: 85</li>\n<li>10.03: 71</li>\n<li>10.05: 76</li>\n<li>10.06: 81</li>\n<li>10.11: 81</li>\n<li>10.14: 82</li>\n<li>10.16: 89</li>\n<li>10.17: 85</li>\n<li>10.18: 78</li>\n<li>10.19: 74</li>\n<li>10.22: 84</li>\n<li>10.23: 80</li>\n</ul>\n<p>Notable points:</p>\n<ul>\n<li>Several scores are in the optimal range (85+).</li>\n<li>A few lower scores (10.03: 71, 10.05: 76, 10.19: 74) suggest some nights may need attention.</li>\n</ul>\n<p>Scores below 70 are considered &quot;Fair&quot; and those above 85 &quot;Optimal&quot; by Oura standards. Regular variation is normal, but if you&#39;re concerned about consistency, focusing on pre-sleep routines and stress management may help.</p>\n<p>Let me know if you&#39;d like deeper analysis of contributors (deep/REM sleep, latency, etc.) for any specific period!</p>\n', additional_kwargs={}, response_metadata={}, id='f7be94a6-c2ff-4fe8-b76e-838932c96732'), HumanMessage(content='Yeah can you help me figure out what contributors to my sleep score were bad for the 10.03 sleep score?', additional_kwargs={}, response_metadata={}, id='e9f7f3c3-9ed7-47a7-9250-30e90600db7d'), HumanMessage(content='Yeah can you help me figure out what contributors to my sleep score were bad for the 10.03 sleep score?', additional_kwargs={}, response_metadata={}, id='c6b386ce-f918-4939-b6f5-36186560f597'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_Rjx0z9VFrSa7vUTf53sJDOqu', 'function': {'arguments': '{"start_date":"2025-10-03","end_date":"2025-10-03","user_id":"Nikhil"}', 'name': 'get_sleep_data'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 2657, 'total_tokens': 2695, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4.1-2025-04-14', 'system_fingerprint': 'fp_144ea3b974', 'id': 'chatcmpl-CUd8sY44epV80pCtSckCaoJ0Epoga', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--facd61e2-b189-4c7d-86b3-794a8ca78de2-0', tool_calls=[{'name': 'get_sleep_data', 'args': {'start_date': '2025-10-03', 'end_date': '2025-10-03', 'user_id': 'Nikhil'}, 'id': 'call_Rjx0z9VFrSa7vUTf53sJDOqu', 'type': 'tool_call'}], usage_metadata={'input_tokens': 2657, 'output_tokens': 38, 'total_tokens': 2695, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}), ToolMessage(content="Score: 71, Contributors: {'deep_sleep': 94, 'efficiency': 90, 'latency': 70, 'rem_sleep': 60, 'restfulness': 86, 'timing': 71, 'total_sleep': 57}, Day: 2025-10-03", name='get_sleep_data', id='9738e0fc-842b-4815-acab-13edcafd1b34', tool_call_id='call_Rjx0z9VFrSa7vUTf53sJDOqu'), AIMessage(content="Here are the contributors to your sleep score on October 3, 2025:\n\n- Deep Sleep: 94 (really good)\n- Efficiency: 90 (really good)\n- Latency: 70 (needs improvement)\n- REM Sleep: 60 (needs improvement)\n- Restfulness: 86 (really good)\n- Timing: 71 (good)\n- Total Sleep: 57 (needs improvement)\n\nContributors that were below optimal:\n- REM Sleep and Total Sleep were both low.\n- Latency (how quickly you fell asleep) also needed improvement.\n\nLow total sleep and suboptimal REM sleep can strongly impact your overall sleep quality. Improving your wind-down routine and managing evening stress may help increase both REM sleep and overall sleep time.\n\nIf you'd like more targeted advice, I can provide strategies specifically for improving REM sleep, total sleep, or sleep latency. Let me know your preference! \n\nSource: <Nikhil, Oura Ring, Oct. 3, 2025>", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 203, 'prompt_tokens': 2769, 'total_tokens': 2972, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 1920}}, 'model_name': 'gpt-4.1-2025-04-14', 'system_fingerprint': 'fp_144ea3b974', 'id': 'chatcmpl-CUd8uKcI5pSwNoTyD0NJ4CJVlwTeZ', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='run--be638e5e-83b8-425f-a5d4-25292a1faacb-0', usage_metadata={'input_tokens': 2769, 'output_tokens': 203, 'total_tokens': 2972, 'input_token_details': {'audio': 0, 'cache_read': 1920}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]}
        response = full_messages['messages'][-1]
        self.log_message(query, response, None, query_idx, full_messages, inference_time=0.0)
    
    async def log_message(self, query: str, response: str, message_hist: list[str], query_idx: int, messages: MessagesState, inference_time: float, user_spec: str, preferences: list[str]):
        # Query_id: allows us to identify the query in the message history
        # Additionally extract function calls from the response and log them
        # Load the messages type from args
        # print(response)
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
            message_history =message_hist,
        )
# AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_Rjx0z9VFrSa7vUTf53sJDOqu', 'function': {'arguments': '{"start_date":"2025-10-03","end_date":"2025-10-03","user_id":"Nikhil"}', 'name': 'get_sleep_data'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 2657, 'total_tokens': 2695, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4.1-2025-04-14', 'system_fingerprint': 'fp_144ea3b974', 'id': 'chatcmpl-CUd8sY44epV80pCtSckCaoJ0Epoga', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--facd61e2-b189-4c7d-86b3-794a8ca78de2-0', tool_calls=[{'name': 'get_sleep_data', 'args': {'start_date': '2025-10-03', 'end_date': '2025-10-03', 'user_id': 'Nikhil'}, 'id': 'call_Rjx0z9VFrSa7vUTf53sJDOqu', 'type': 'tool_call'}], usage_metadata={'input_tokens': 2657, 'output_tokens': 38, 'total_tokens': 2695, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})
        # Match the tool calls by _id -> so let's create a dictionary initially and then store the values only after

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
        log_id = await self.user_db_operations.log_message(logger)
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
    
