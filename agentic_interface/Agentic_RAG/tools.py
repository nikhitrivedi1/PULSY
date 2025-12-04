"""
AI Agent Tools - Data Retrieval and Knowledge Base Access

Provides tool functions that the LangGraph agent can call to:
1. Fetch wearable device data (Oura Ring API)
   - Sleep metrics (score, contributors, timing)
   - Stress levels (high stress periods)
   - Heart rate data (BPM over time)

2. Retrieve health insights from knowledge base
   - RAG retrieval from Pinecone vector database
   - Embeddings via HuggingFace models
   - Content from health podcasts (Huberman, Goggins)

All tools are designed for OpenAI function calling format.
They return string representations that the LLM can interpret.

Dependencies:
- Oura Ring API for device data
- Pinecone for vector search
- HuggingFace for embeddings
- PostgreSQL for user API keys
"""

import requests
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd

from database.user_db_call import UserDbOperations
from config.settings import settings

# Singleton database connection for tool functions
user_db_operations = UserDbOperations()


# ========== Oura Ring Data Tools ==========

def get_sleep_data(start_date: str, end_date: str, user_key: str) -> str:
    """
    Fetch sleep metrics from Oura Ring API
    
    Retrieves comprehensive sleep data including:
    - Overall sleep score (0-100)
    - Contributors (deep sleep, REM, latency, etc.)
    - Sleep timing and quality
    
    This tool is called by the AI agent when users ask about
    their sleep patterns, quality, or specific contributors.
    
    Args:
        start_date: Start date for data range (format: YYYY-MM-DD)
        end_date: End date for data range (format: YYYY-MM-DD)
        user_key: User's Oura Ring API access token
    
    Returns:
        str: Formatted string with sleep scores and contributors for each day
             Format: "Score: 85, Contributors: {...}, Day: 2025-01-15"
    
    Example:
        >>> get_sleep_data("2025-01-01", "2025-01-07", "ABC123...")
        "Score: 85, Contributors: {'deep_sleep': 90, ...}, Day: 2025-01-01\\n..."
    """
    # Configure Oura API request
    URL = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    headers = {'Authorization': f'Bearer {user_key}'}
    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    # Fetch data from Oura API
    response = requests.request("GET", URL, headers=headers, params=params).json()

    if response["data"] == []:
        return "No sleep data found for the given date range"

    # Format response for LLM consumption
    print("Sleep Data Response:", response)
    response_messages = []
    for result in response["data"]:
        score = result["score"]
        contributors = result["contributors"]  # Dict of metric scores
        day = result["day"]
        response_messages.append(
            f"Score: {score}, Contributors: {contributors}, Day: {day}"
        )

    return "\n".join(response_messages)

def get_stress_data(start_date: str, end_date: str, user_key: str) -> str:
    """
    Fetch stress metrics from Oura Ring API
    
    Retrieves daily stress data including:
    - Overall stress day summary
    - High stress periods (daytime stress)
    - Recovery stress (nighttime)
    
    Args:
        start_date: Start date for data range (format: YYYY-MM-DD)
        end_date: End date for data range (format: YYYY-MM-DD)
        user_key: User's Oura Ring API access token
    
    Returns:
        str: Formatted string with stress metrics for each day
             Format: "Day: 2025-01-15, Stress Summary: {...}"
    """
    # Configure Oura API request
    URL = "https://api.ouraring.com/v2/usercollection/daily_stress"
    headers = {'Authorization': f'Bearer {user_key}'}
    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    # Fetch data from Oura API
    response = requests.request("GET", URL, headers=headers, params=params).json()

    if response["data"] == []:
        return "No stress data found for the given date range"

    response_messages = []
    for result in response["data"]:
        # Extract Score, Contributors, and Day
        stress_high = result["stress_high"]
        recovery_high = result["recovery_high"]
        day = result["day"]
        day_summary = result["day_summary"]
        response_messages.append(f"Stress High: {stress_high}, Recovery High: {recovery_high}, Day: {day}, Day Summary: {day_summary}")

    return "\n".join(response_messages)

# Get the user heart rate data from the Oura API between the start and end date
# Returns: dict - the heart rate data between the start and end date - formatted as a dictionary
def get_heart_rate_data(start_date: str, end_date: str, user_key: str) -> dict:
    """
    Get the user heart rate data from the Oura API between the start and end date
    
    Args:
    start_date: the start date of the heart rate data - format %Y-%m-%d
    end_date: the end date of the heart rate data - format %Y-%m-%d
    user_key: the API key for the user

    Returns:
    heart_rate_data(dict): the heart rate data between the start and end date
    """

    # Build the GET Request Components
    URL = "https://api.ouraring.com/v2/usercollection/heartrate" # specific endpoint for heart rate data
    headers = {'Authorization': f'Bearer {user_key}'}
    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    # Make the GET Request
    response = requests.request("GET", URL, headers=headers, params=params).json()

    # Extract the maximum "bpm" seen
    # Extract the minimum "bpm" seen
    # Extract the average "bpm" for workout sourse
    # Extract the average "bpm" for non-workout sources
    # In case the response is empty
    if response["data"] == []:
        return {
            "max_bpm": None,
            "min_bpm": None,
            "average_bpm_workout": None,
            "average_bpm_non_workout": None
        }
    df = pd.DataFrame(response["data"])
    max_bpm = df["bpm"].max()
    min_bpm = df["bpm"].min()
    average_bpm_workout = df[df["source"] == "workout"]["bpm"].mean()
    average_bpm_non_workout = df[df["source"] != "workout"]["bpm"].mean()

    response_dict = {
        "max_bpm": max_bpm,
        "min_bpm": min_bpm,
        "average_bpm_workout": average_bpm_workout,
        "average_bpm_non_workout": average_bpm_non_workout
    }
    return response_dict

# Vector DB Tools

# MedlinePlus Database
# Returns: str - semantic search results - returning top 5 results from the vector db
def get_MedlinePlus_Insights(query:str) -> str:
    """
    Given the user query, search the Pinecone VectorDB for the most relevant insights from MedlinePlus
    When using information from this tool - ensure that you note to the user that this information is from MedlinePlus

    Args:
    query: the query to search for in the Pinecone Vector DB

    Returns:
    results(dict): the most relevant insights from MedlinePlus along with the corresponding metadata
    """
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key = settings.PINECONE_API_KEY)
        index = pc.Index(host = settings.PINECONE_HOST)
        embeddings = HuggingFaceEmbeddings(model_name = settings.PINECONE_EMBEDDING_MODEL)

        # Convert query to vector space using embeddings model
        queryVec = embeddings.embed_query(query)

        results = index.query(
            namespace = settings.PINECONE_NAMESPACE_2,
            vector = queryVec,
            top_k = 3,
            include_metadata = True
        )

        # Return the documents and the query - note that this will not be returning any metadata
        response_messages = [f"Source: {result['metadata']['source']}, Text: {result['metadata']['text']}, Similarity: {result['score']}" for result in results["matches"]]
        return "\n".join(response_messages)
    except RuntimeError as r:
        # This is an internal endpoint - users do not need to provide any information
        # Build out further exceptions to handle connection errors, etc.
        raise RuntimeError("Pinecone Server Error")


# Andrew Huberman Podcast Transcripts
# Returns: str - semantic search results - returning top 5 results from the vector db
def get_Andrew_Huberman_Insights(query:str) -> str:
    """
    Given the user query, search the Pinecone VectorDB for the most relevant insights from Andrew Huberman's podcast transripts
    When using information from this tool - ensure that you note to the user that this information is from Andrew Huberman's podcast 
    
    Args:
    query: the query to search for in the Pinecone Vector DB

    Returns:
    results(dict): the most relevant insights from Andrew Huberman's podcast transripts along with the corresponding metadata
    """

    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key = settings.PINECONE_API_KEY)
        index = pc.Index(host = settings.PINECONE_HOST)
        embeddings = HuggingFaceEmbeddings(model_name = settings.PINECONE_EMBEDDING_MODEL)

       # Convert query to vector space using embeddings model
        queryVec = embeddings.embed_query(query)

        results = index.query(
            namespace = settings.PINECONE_NAMESPACE_1,
            vector = queryVec,
            top_k = 3,
            include_metadata = True
        )

        # distill the results into a list of messages
        response_messages = [f"Source: {result['metadata']['source']}, Text: {result['metadata']['text']}, Similarity: {result['score']}" for result in results["matches"]]

        # Return the documents and the query - note that this will not be returning any metadata
        return "\n".join(response_messages)
    except RuntimeError as r:
        # This is an internal endpoint - users do not need to provide any information
        # Build out further exceptions to handle connection errors, etc.
        raise RuntimeError("Pinecone Server Error")