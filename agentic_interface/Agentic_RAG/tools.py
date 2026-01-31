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
from collections import Counter
from Agentic_RAG.response_checks import ResponseChecks

# Singleton database connection for tool functions
user_db_operations = UserDbOperations()
response_checks = ResponseChecks()


# ========== Oura Ring Data Tools ==========
def sleep_analysis(start_date:str, end_date:str, user_key:str) -> str:
    """
    Analyze the sleep of the user on a particular data
    
    Args:
    start_date: the start date of the sleep data - format %Y-%m-%d
    end_date: the end date of the sleep data - format %Y-%m-%d
    * Note End Data must be greater than start date
    user_key: the API key for the user

    Returns:
    sleep_analysis(dict): the sleep analysis for the user on the particular date
    Included metrics:
    - Bedtime Start
    - Bedtime End
    - Heart Rate Average
    - Lowest Heart Rate
    - Highest Heart Rate
    - Average Breadth
    - Average HRV
    - Movement
    - Normal Sleep Metrics
    - Durations
    """
    # Input Parameter Check to ensure we are not getting multiple days of data
    if start_date == end_date:
        return "Please provide a different start and end date."

    print(f"Start Date: {start_date}, End Date: {end_date}")

    # Configure Oura API request
    URL = "https://api.ouraring.com/v2/usercollection/sleep"
    headers = {'Authorization': f'Bearer {user_key}'}
    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    # Fetch data from Oura API
    try:
        response = requests.request("GET", URL, headers=headers, params=params).json()
        print(f"Response: {response}")
    except Exception as e:
        return f"Unable to retrieve sleep data due to {e}"

    # Perform Response Checks
    checks = response_checks.check_response(response, "oura", "analysis")
    if not checks['basic']:
        return "Data for the specified date appears to be unavailable or empty"
    print(f"Checks: {checks}")

    # if it is fully a boolean -> return immediately with error message 
    # otherwise -> proceed to extract data with error dictionaries

    res = []

    # TODO: Handle multiple days of data
    extracted_data = response['data'][0]

    res.append({
        'bedtime_start': extracted_data['bedtime_start'],
        'bedtime_end': extracted_data['bedtime_end']
    })
    # Heart Rate
    # Need to handle case with null heart rate data value
    heart_rate_items = {}
    if checks['analysis']['heart_rate']:
        heart_rate_items.update({
            'heart_rate_average': extracted_data['average_heart_rate'],
            'lowest_heart_rate': extracted_data['lowest_heart_rate'],
            'highest_heart_rate': max(extracted_data['heart_rate']['items']),
        })
    else:
        heart_rate_items.update({
            'heart_rate_average': None,
            'lowest_heart_rate': None,
            'highest_heart_rate': None
        })

    res.append(heart_rate_items)
    # heart rate variability - how much did your heart rate vary during the night?
    # Need to handle the case with null hrv data values
    if checks['analysis']['hrv']:
        res.append({
            'hrv_average': extracted_data['average_hrv'],
            'hrv_min': min(extracted_data['hrv']['items']),
            'hrv_max': max(extracted_data['hrv']['items'])
        })
    else:
        res.append({
            'hrv_average': None,
            'hrv_min': None,
            'hrv_max': None
        })

    # Movement - how much did you move during the night? - taken every 30 minutes
    # 30-second movement classification for the period where every character corresponds to:
    # '1' = no motion,
    # '2' = restless,
    # '3' = tossing and turning
    # '4' = active

    if not checks['analysis']['movement']:
        res.append({
            'movement_30_sec': None
        })
    else:
        mapping = {
            '1': 'no motion', 
            '2': 'restless',
            '3': 'tossing and turning',
            '4': 'active'
        }
        movement = extracted_data['movement_30_sec']
        length = len(movement)
        cntr = Counter(movement)
        mapped_dict = {}
        for key, freq in cntr.items():
            mapped_dict.update({mapping[key]: (freq /length)})
        res.append(mapped_dict)


    # Normal Sleep Metrics
    res.append(extracted_data['readiness'])

    # Durations - provided in seconds convert to hours and minutes
    res.append({
        'total_sleep_duration': f"{extracted_data['total_sleep_duration'] // 3600} hours and {((extracted_data['total_sleep_duration'] % 3600) // 60)} minutes",
        'time_in_bed': f"{extracted_data['time_in_bed'] // 3600} hours and {((extracted_data['time_in_bed'] % 3600) // 60)} minutes",
        'rem_sleep_duration': f"{extracted_data['rem_sleep_duration'] // 3600} hours and {((extracted_data['rem_sleep_duration'] % 3600) // 60)} minutes",
        'light_sleep_duration': f"{extracted_data['light_sleep_duration'] // 3600} hours and {((extracted_data['light_sleep_duration'] % 3600) // 60)} minutes",
        'deep_sleep_duration': f"{extracted_data['deep_sleep_duration'] // 3600} hours and {((extracted_data['deep_sleep_duration'] % 3600) // 60)} minutes",
        'awake_time': f"{extracted_data['awake_time'] // 3600} hours and {((extracted_data['awake_time'] % 3600) // 60)} minutes"
    })

    # JSON dumps? List[dicts] into a JSON string?
    return res

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
    try:
        response = requests.request("GET", URL, headers=headers, params=params).json()
        print(f"Response: {response}")
    except Exception as e:
        return f"Unable to retrieve sleep data due to {e}"

    # Format response for LLM consumption
    checks = response_checks.check_response(response, "oura", "analysis")
    if not checks['basic']:
        return "Data for the specified date appears to be unavailable or empty"
        
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

    if not response or "data" not in response:
        return "Unable to retrieve stress data"

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
# Returns: str - the heart rate data between the start and end date - formatted as a string
def get_heart_rate_data(start_date: str, end_date: str, user_key: str) -> str:
    """
    Get the user heart rate data from the Oura API between the start and end date
    
    Args:
    start_date: the start date of the heart rate data - format %Y-%m-%d
    end_date: the end date of the heart rate data - format %Y-%m-%d
    user_key: the API key for the user

    Returns:
    heart_rate_data(dict): the heart rate data between the start and end date
    """
    # Get the API Key

    # Build the GET Request Components
    URL = "https://api.ouraring.com/v2/usercollection/heartrate" # specific endpoint for heart rate data
    headers = {'Authorization': f'Bearer {user_key}'}
    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    # Make the GET Request
    response = requests.request("GET", URL, headers=headers, params=params).json()

    if not response or "data" not in response or not response['data']:
        return "Unable to retrieve heart rate data"

    # Extract the maximum "bpm" seen
    # Extract the minimum "bpm" seen
    # Extract the average "bpm" for workout sourse
    # Extract the average "bpm" for non-workout sources
    # Array of dictionaries 
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

# Andrew Huberman Podcast Transcripts
# Returns: str - semantic search results - returning top 5 results from the vector db
# consolidate with get_insights()
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

def get_insights(query:str, scope:str = "all") -> str:
    """
    Given the user query, search the Pinecone VectorDB for the most relevant insights from the given scope
    When using information from this tool - ensure that you note to the user that this information is from the given scope

    Args:
    query: the query to search for in the Pinecone Vector DB
    scope: the scope of the insights to search for - options are "Andrew Huberman", "all" (default)
    """
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key = settings.PINECONE_API_KEY)
        index = pc.Index(host = settings.PINECONE_HOST)
        embeddings = HuggingFaceEmbeddings(model_name = settings.PINECONE_EMBEDDING_MODEL)

       # Convert query to vector space using embeddings model
        queryVec = embeddings.embed_query(query)

        # Deteremine the namespace based on the scope
        namespace = settings.PINECONE_NAMESPACE_2 if scope == "Andrew Huberman" else settings.PINECONE_NAMESPACE_1

        results = index.query(
            namespace = namespace,
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
