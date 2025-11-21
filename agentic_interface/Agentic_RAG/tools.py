# Tools for the Agent 

# Libraries
import requests
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings

import pandas as pd
from database.user_db_call import UserDbOperations
from config.settings import settings

# Create Instance of UserDbOperations
user_db_operations = UserDbOperations()


# Oura Ring Tools

# Get the user sleep data from the Oura API between the start and end date
# Returns: str - the sleep data between the start and end date - formatted as a string
def get_sleep_data(start_date: str, end_date: str, user_id: str) -> str:
        """
        Get the user sleep data from the Oura API between the start and end date
        
        Args:
        start_date: the start date of the sleep data - format YYYY-MM-DD
        end_date: the end date of the sleep data - format YYYY-MM-DD

        Returns:
        sleep_data(dict): the sleep data between the start and end date
        """

        # Get the API Key
        key = __get_device_api_key(user_id, "Oura Ring")

        # Build the GET Request Components
        URL = "https://api.ouraring.com/v2/usercollection/daily_sleep" # specific endpoint for sleep data
        headers = {'Authorization': f'Bearer {key}'}
        params = {
            'start_date': start_date,
            'end_date': end_date
        }

        # Make the GET Request
        response = requests.request("GET", URL, headers=headers, params=params).json()

        # Extract Content from the response to pass as message to LLM
        print("Response: ", response)
        response_messages = []
        for result in response["data"]:
            # Extract Score, Contributors, and Day
            score = result["score"]
            contributors = result["contributors"]
            day = result["day"]
            response_messages.append(f"Score: {score}, Contributors: {str(contributors)}, Day: {day}")

        return "\n".join(response_messages)

# Get the user stress data from the Oura API between the start and end date
# Returns: str - the stress data between the start and end date - formatted as a string
def get_stress_data(start_date: str, end_date: str, user_id: str) -> str:
    """
    Get the user stress data from the Oura API between the start and end date
    
    Args:
    start_date: the start date of the stress data - format YYYY-MM-DD
    end_date: the end date of the stress data - format YYYY-MM-DD

    Returns:
    stress_data(dict): the stress data between the start and end date
    """

    # Get the API Key
    key = __get_device_api_key(user_id, "Oura Ring")

    # Build the GET Request Components
    URL = "https://api.ouraring.com/v2/usercollection/daily_stress" # specific endpoint for stress data
    headers = {'Authorization': f'Bearer {key}'}
    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    # Make the GET Request
    response = requests.request("GET", URL, headers=headers, params=params).json()

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
def get_heart_rate_data(start_date: str, end_date: str, user_id: str) -> str:
    """
    Get the user heart rate data from the Oura API between the start and end date
    
    Args:
    start_date: the start date of the heart rate data - format %Y-%m-%d
    end_date: the end date of the heart rate data - format %Y-%m-%d
    user_id: the id of the user - used to access the correct API key

    Returns:
    heart_rate_data(dict): the heart rate data between the start and end date
    """
    # Get the API Key
    key = __get_device_api_key(user_id, "Oura Ring")

    # Build the GET Request Components
    URL = "https://api.ouraring.com/v2/usercollection/heartrate" # specific endpoint for heart rate data
    headers = {'Authorization': f'Bearer {key}'}
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

# Vector DB Tools

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
            namespace = settings.PINECONE_INDEX,
            vector = queryVec,
            top_k = 5,
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


# User Management and Memory Tools

# # Get the user preferences from the database
# # Returns: list[str] - the user preferences
# def get_user_preferences(user_id: str) -> list[str]:
#     """
#     Get the user preferences from the database

#     Args:
#     user_id (str): the id of the user

#     Returns:
#     preferences(list[str]): the user preferences
#     """
#     with open(MAIN_DB_PATH, 'r') as file:
#         user_db = json.load(file)
#         return user_db[user_id]["preferences"]

# Set the user preferences in the database
# # Returns: str - confirmation that the preference has been added
# def set_user_preferences(user_id: str, preference: str) -> str:
#     """
#     Whenever the user provides a preference, update the user preferences in the database

#     Args:
#     user_id (str): the id of the user
#     preference (str): the preference to add to the user preferences

#     Returns:
#     confirmation (str): confirmation that the preference has been added
#     """
#     with open(MAIN_DB_PATH, 'r') as file:
#         user_db = json.load(file)

#     with open(MAIN_DB_PATH, 'w') as file:
#         user_db[user_id]["preferences"].append(preference)
#         json.dump(user_db, file, indent=4)
#     return f"Preference {preference} has been added to the user preferences"


# Create a user goal in the database
# Returns: str - confirmation that the goal has been created
# def create_user_goal(
#     user_id: str,
#     goal_name: str,
#     goal_description: str,
#     goal_start_date: str,
#     goal_end_date: str,
#     goal_status: str,
#     goal_created_at: str,
#     goal_updated_at: str,
#     goal_notes: str,
#     goal_plans: str,
#     ) -> str:
#     """
#     Create a goal defined by the user - this goal is the mission that you will be tracking and trying to make the user achieve

#     Args:
#     user_id: str - the id of the user
#     goal_name: str - a given name for the goal - short and concise
#     goal_description: str - a description of what the user is trying to achieve
#     goal_start_date: str - the start date of the goal - format YYYY-MM-DD
#     goal_end_date: str - the end date of the goal - format YYYY-MM-DD
#     goal_status: str - the status of the goal - options are "active", "completed", "archived", "not started"
#     goal_created_at: str - the date the goal was created - format YYYY-MM-DD
#     goal_updated_at: str - the date the goal was last updated - format YYYY-MM-DD
#     goal_notes: str - any important pieces of data that correspond to the goal that you want to keep track of for future reference
#     goal_plans: str - the plans for the goal - this is the steps that you will be taking to help the user achieve the goal

#     Returns:
#     confirmation (str): confirmation that the goal has been created
#     """
#     goal_upload = {
#         goal_name : {
#             "goal_description" : goal_description,
#             "goal_start_date" : goal_start_date,
#             "goal_end_date" : goal_end_date,
#             "goal_status" : goal_status,
#             "goal_created_at" : goal_created_at,
#             "goal_updated_at" : goal_updated_at,
#             "goal_notes" : goal_notes,
#             "goal_plans" : goal_plans,
#             "goal_evidence" : []
#         }
#     }
#     # Update with evidence - this is a list of GoalEvidence objects
#     goal_upload["goal_evidence"] = []
#     # Update the user db with the new goal
#     with open(MAIN_DB_PATH, 'r') as file:
#         user_db = json.load(file)

#     with open(MAIN_DB_PATH, 'w') as file:
#         user_db[user_id]["goals"].update(goal_upload)
#         json.dump(user_db, file, indent=4)

#     return f"Goal {goal_upload['goal_name']} has been created"

# Add evidence to a goal in the database
# Returns: str - confirmation that the evidence has been added to the goal
# def add_goal_evidence(
#     user_id: str,
#     goal_name: str,
#     evidence_name: str,
#     evidence_description: str,
#     evidence_date: str,
#     evidence_metric: str,
#     evidence_value: str,
#     ) -> str:
#     """
#     Add evidence to a goal - this is a list of GoalEvidence objects

#     Args:
#     user_id: str - the id of the user
#     goal_name: str - the name of the goal
#     evidence_name: str - the name of the evidence
#     evidence_description: str - the description of the evidence
#     evidence_date: str - the date of the evidence - format YYYY-MM-DD
#     evidence_metric: str - the metric of the evidence
#     evidence_value: str - the value of the evidence

#     Returns:
#     confirmation (str): confirmation that the evidence has been added to the goal
#     """

#     evidence = {
#         "evidence_name" : evidence_name,
#         "evidence_description" : evidence_description,
#         "evidence_date" : evidence_date,
#         "evidence_metric" : evidence_metric,
#         "evidence_value" : evidence_value
#     }

#     with open(MAIN_DB_PATH, 'r') as file:
#         user_db = json.load(file)
#         user_db[user_id]["goals"][goal_name]["goal_evidence"].append(evidence)
#     with open(MAIN_DB_PATH, 'w') as file:
#         json.dump(user_db, file, indent=4)
#     return f"Evidence {evidence['evidence_name']} has been added to the goal {goal_name}"

# Delete a goal from the database
# Returns: str - confirmation that the goal has been deleted
# def delete_goal(
#     user_id: str,
#     goal_name: str,
#     ) -> str:
#     """
#     Delete a goal from the user's goals

#     Args:
#     user_id: str - the id of the user
#     goal_name: str - the name of the goal that you want to delete

#     Returns:
#     confirmation (str): confirmation that the goal has been deleted
#     """
#     with open(MAIN_DB_PATH, 'r') as file:
#         user_db = json.load(file)
#         del user_db[user_id]["goals"][goal_name]
#     with open(MAIN_DB_PATH, 'w') as file:
#         json.dump(user_db, file, indent=4)
#     return f"Goal {goal_name} has been deleted"

# # Internal Functions for Tools to get API Keys
# # Get the API key for the user's device
# # Returns: str - the API key for the user's device
def __get_device_api_key(user_id: str, device_type: str) -> str:
    """
    Get the API key for the user - query via the user_db_call class
    """
    key = user_db_operations.get_api_key(user_id, device_type)
    return key
    
# # Get the Pinecone API key
# # Returns: str - the Pinecone API key
# def __get_pinecone_api_attributes() -> tuple[str, str, str, str]:
#     """
#     Get the Pinecone API key
#     """
#     with open(CONFIG_PATH, 'r') as file:
#         contents = yaml.safe_load(file)
#         return contents["PINECONE_API_KEY"], contents["PINECONE_HOST"], contents["PINECONE_INDEX"], contents["PINECONE_EMBEDDING_MODEL"]
