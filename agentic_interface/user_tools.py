# User Tools - loading user specific information from the UI

# Libraries
from DataSources.oura_data_aggregation import OuraData
from datetime import datetime, timedelta
import json
import os
from fastapi import HTTPException

# Work ToDo
# TODO: Add the average for the heart rate data - over the course of the day
# TODO: narrow the scope only to the previous day 
# TODO: Add the provisions for other devices

# CONSTANTS
MAIN_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"../shared/user_state.json"))

# Load Consolidated User Data from previous day
# Compatability: Oura Ring
# Returns: dict[str, str|int|float] - the result of the device loading
# Error Handling:
# 400 or 500 error from Device API -> dict["detail"] = "Error Message"
# Device type not supported -> raised 400 error here
async def load_user_devices_service(device: dict) -> dict[str, str|int|float]:
    device_type = device["device_type"]
    result_data = {}

    if device_type == "Oura Ring":
        # Create OuraRing Object
        start_date = datetime.today() - timedelta(days=1)
        end_date = datetime.today()
        oura_ring = OuraData(device["api_key"], str(start_date).split(" ")[0], str(end_date).split(" ")[0])
        data_result = oura_ring.pre_load_user_data()
        if "detail" in data_result.keys():
            result_data["Error"] = data_result["detail"]
        else:
            sleep_data = data_result["sleep_data"]
            stress_data = data_result["stress_data"]
            heart_rate_data = data_result["heart_rate_data"]

            # Main Metrics Consolidation
            if sleep_data:
                result_data["sleep_score"] = sleep_data[0]["score"]
            if stress_data:
                result_data["stress_score"] = stress_data[0]["stress_high"]
            if heart_rate_data:
                result_data["heart_rate_data"] = heart_rate_data[0]["bpm"] # Just take the first value for now -> replace with an average later
    else:
        raise HTTPException(status_code=400, detail=f"Device type {device_type} not supported")
    return result_data

# Load the user's goals from the database - for goal element in chat_page.ejs
# Returns: dict[str, dict[str, str|list[dict]]] - the result of the user goals loading
# Error Handling: Returns {"Error": "Error Message"} if error occurs
async def load_user_goals_service(user_id: str) -> dict[str, dict[str, str|list[dict]]]:
    """
    Load the user's goals from the database
    """
    with open(MAIN_DB_PATH, 'r') as file:
        user_db = json.load(file)
        return user_db[user_id]["goals"]