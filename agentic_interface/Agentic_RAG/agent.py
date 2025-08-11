# Agentic RAG Class
# This class will self contain the RAG pipeline - there will be a SINGLE instance to control the entire application
# inputs for getting a response will be query and context {username, query, historical_conversations}

#Libraries
from email import message
from operator import index
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition # this is the checker for the if you got a tool back
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
import json
import os
import yaml
import datetime

#Internal Classes
from Agentic_RAG.tools import get_heart_rate_data, get_sleep_data, get_stress_data, get_Andrew_Huberman_Insights, get_user_preferences, set_user_preferences, create_user_goal, add_goal_evidence

# Work ToDo
# TODO: Error handling for file IO errors

# CONSTANTS
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../config/config.yaml"))
SYSTEM_PROMPT = "Agentic_RAG/system_instructions.txt"

class AgenticRAG:
    def __init__(self):
        # LLM and Tools Initialization
        self.llm = ChatOpenAI(model = 'gpt-4.1', api_key = self.__get_api_key())
        self.tools = [get_heart_rate_data, get_sleep_data, get_stress_data, get_Andrew_Huberman_Insights, get_user_preferences, set_user_preferences, create_user_goal, add_goal_evidence]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # System Instruction Loading
        self.sys_msg = SystemMessage(content = self.__get_system_instructions())

        # Build the Graph
        self.react_graph = self.build_graph()

        # Message History
        self.messageHistory = [self.sys_msg]

        # Print Confirmation
        print("AgenticRAG Initialized")

    # Private Methods
    def __get_system_instructions(self) -> str:
        with open(SYSTEM_PROMPT, 'r') as file:
            return file.read()

    def __get_api_key(self) -> str:
        with open(CONFIG_PATH, 'r') as file:
            return yaml.safe_load(file)['OPENAI_API_KEY']

    # Build the Graph
    def build_graph(self) -> StateGraph:
        builder = StateGraph(MessagesState)

        # Build Graph
        # Add Reasoner and Tool Nodes
        builder.add_node("reasoner", self.reasoner)
        builder.add_node("tools", ToolNode(self.tools))

        # Add Edges
        builder.add_edge(START, "reasoner")
        # This conditional edge allows for the reasoner to make the call on whether 
        # a tool call is necessary or not
        builder.add_conditional_edges(
            "reasoner",
            tools_condition
        )
        builder.add_edge("tools", "reasoner")

        # Compile the DAG
        return builder.compile()

    # Reasoner Node
    def reasoner(self, state: MessagesState) -> MessagesState:
        # state["messages"] is the list of messages that have been passed to the reasoner
        prior_messages = state["messages"]
        response = self.llm_with_tools.invoke(prior_messages)

        return {"messages": prior_messages + [response]}

    # Run the Agent
    def run(self,
        query: str, # The query to be passed to the LLM
        user_id: str, # The user_id to be passed to the LLM - needs to match up with user_id from the db
        query_history: list[str], # The history of queries
        response_history: list[str] # The history of responses
        ) -> list[str]:

        # Get the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Create the message history
        message_history = [self.sys_msg, "Today's date is: " + current_date]
        message_history.extend([SystemMessage(content = "My name and user_id is: " + user_id)])
        message_history.extend(self.create_message_history(query_history, response_history))
        # Add the query to the message history
        message_history.extend([HumanMessage(content = query)])

        # Run the graph
        messages = self.react_graph.invoke({"messages": message_history})
        # Return only the latest message -> Node will handle the aggregation of messages
        return messages['messages'][-1].content

    # Not Ideal Implementation - but for the purpose of supposed short chat histories - this should be ok
    def create_message_history(self, query_history: list[str], response_history: list[str]) -> list[str]:
        """ Create the message history as LangGraph HumanMessage and AIMessage Objects"""
        message_history = []
        for i in range(len(query_history)):
            message_history.append(HumanMessage(content = query_history[i]))

            if len(response_history) > i: # meant to handle initial case
                message_history.append(AIMessage(content = response_history[i]))
        return message_history
